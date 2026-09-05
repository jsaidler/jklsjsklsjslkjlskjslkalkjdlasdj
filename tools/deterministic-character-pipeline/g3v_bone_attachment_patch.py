import bpy
from mathutils import Matrix


_ATTACHMENT_REGISTRY = {}


def _rigid_bone_world_matrix(rig, bone_name):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError("G3V rigid attachment missing bone: " + bone_name)
    world = rig.matrix_world @ pb.matrix
    location, rotation, _scale = world.decompose()
    return Matrix.Translation(location) @ rotation.to_matrix().to_4x4()


def install_rigid_bone_attachments(target_globals):
    """Replace Blender BONE parenting for representative proxy pieces.

    G3V only needs deterministic visual attachments at this gate. Blender bone parenting
    was allowing parent/bone scale semantics to inflate the cloth and cuffs even though
    the MPFB body and skeleton had sane physical heights. Store a rigid transform
    relative to the owning bone instead, and reconstruct world matrices explicitly after
    every frame change. Translation and rotation follow the bone; parent scale never
    changes the proxy piece's authored physical size.
    """
    required = ("parent_bone", "bbox_world", "main")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V rigid-attachment patch missing target symbols: " + ", ".join(missing))

    original_bbox_world = target_globals["bbox_world"]

    def rigid_attach(obj, rig, bone_name):
        if rig is None or rig.type != "ARMATURE":
            raise RuntimeError("G3V rigid attachment requires an armature")
        if rig.pose.bones.get(bone_name) is None:
            raise RuntimeError("G3V rigid attachment bone not found: " + bone_name)

        object_world = obj.matrix_world.copy()
        parent_rigid = _rigid_bone_world_matrix(rig, bone_name)
        relative = parent_rigid.inverted_safe() @ object_world

        # Explicitly keep the proxy object unparented. Its world transform is owned by
        # this deterministic attachment registry rather than Blender parent evaluation.
        obj.parent = None
        obj.parent_type = "OBJECT"
        obj.parent_bone = ""
        obj.matrix_world = object_world
        obj["g3v_attachment_mode"] = "rigid_relative_matrix"
        obj["g3v_attachment_bone"] = bone_name

        _ATTACHMENT_REGISTRY[obj.name] = {
            "object_name": obj.name,
            "rig_name": rig.name,
            "bone_name": bone_name,
            "relative": relative.copy(),
        }

    def update_rigid_attachments():
        stale = []
        for key, entry in list(_ATTACHMENT_REGISTRY.items()):
            obj = bpy.data.objects.get(entry["object_name"])
            rig = bpy.data.objects.get(entry["rig_name"])
            if obj is None or rig is None:
                stale.append(key)
                continue
            parent_rigid = _rigid_bone_world_matrix(rig, entry["bone_name"])
            obj.matrix_world = parent_rigid @ entry["relative"]
        for key in stale:
            _ATTACHMENT_REGISTRY.pop(key, None)
        bpy.context.view_layer.update()

    def attachment_aware_bbox_world(objects):
        update_rigid_attachments()
        return original_bbox_world(objects)

    target_globals["parent_bone"] = rigid_attach
    target_globals["bbox_world"] = attachment_aware_bbox_world
    target_globals["G3V_UPDATE_RIGID_ATTACHMENTS"] = update_rigid_attachments

    if target_globals["parent_bone"] is not rigid_attach:
        raise RuntimeError("G3V rigid parent replacement did not bind")
    if target_globals["bbox_world"] is not attachment_aware_bbox_world:
        raise RuntimeError("G3V attachment-aware bbox replacement did not bind")

    print("G3V_ATTACHMENT_MODE=RIGID_RELATIVE_MATRIX")
    print("G3V_ATTACHMENT_SCALE_INHERITANCE=DISABLED")
