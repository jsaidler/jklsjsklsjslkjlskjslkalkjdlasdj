import bpy
from mathutils import Matrix, Vector


_ATTACHMENT_REGISTRY = {}
_AUDIT_DONE = False


def _rigid_bone_world_matrix(rig, bone_name):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError("G3V rigid attachment missing bone: " + bone_name)
    world = rig.matrix_world @ pb.matrix
    location, rotation, _scale = world.decompose()
    return Matrix.Translation(location) @ rotation.to_matrix().to_4x4()


def _bake_local_scale_to_mesh(obj):
    """Bake authored object scale into mesh vertices and reset transform scale to 1.

    Representative proxy primitives are authored by setting obj.scale after primitive
    creation. Keeping that scale inside matrix_world made the attachment transform path
    vulnerable to armature/bone transform semantics. Baking it into local geometry makes
    physical size explicit and leaves the attachment matrix rigid (translation+rotation).
    """
    if obj.type != "MESH":
        return
    sx, sy, sz = (float(obj.scale.x), float(obj.scale.y), float(obj.scale.z))
    if abs(sx - 1.0) < 1e-9 and abs(sy - 1.0) < 1e-9 and abs(sz - 1.0) < 1e-9:
        return
    obj.data.transform(Matrix.Diagonal((sx, sy, sz, 1.0)))
    obj.scale = (1.0, 1.0, 1.0)
    obj.data.update()


def _world_dimensions(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def _skeleton_height(rig):
    def bone_point(name, tail=False):
        pb = rig.pose.bones.get(name)
        if pb is None:
            raise RuntimeError("G3V attachment audit missing bone: " + name)
        point = pb.tail if tail else pb.head
        return rig.matrix_world @ point

    head = bone_point("Head", True)
    left = bone_point("LeftFoot")
    right = bone_point("RightFoot")
    h = head.z - min(left.z, right.z)
    if h <= 1e-5:
        h = (head - (left + right) * 0.5).length
    return max(0.5, float(h))


def install_rigid_bone_attachments(target_globals):
    """Replace Blender BONE parenting for representative proxy pieces.

    G3V only needs deterministic visual attachments at this gate. Proxy primitive scale
    is first baked into mesh vertices. Each object then stores a rigid transform relative
    to its owning bone and is reconstructed after every frame change. Translation and
    rotation follow the bone; parent scale and object-scale multiplication are removed.
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

        pre_scale = tuple(float(v) for v in obj.scale)
        _bake_local_scale_to_mesh(obj)
        if any(abs(float(v) - 1.0) > 1e-7 for v in obj.scale):
            raise RuntimeError(f"G3V failed to bake local scale for {obj.name}: {tuple(obj.scale)}")

        object_world = obj.matrix_world.copy()
        parent_rigid = _rigid_bone_world_matrix(rig, bone_name)
        relative = parent_rigid.inverted_safe() @ object_world

        obj.parent = None
        obj.parent_type = "OBJECT"
        obj.parent_bone = ""
        obj.matrix_world = object_world
        obj["g3v_attachment_mode"] = "rigid_relative_matrix"
        obj["g3v_attachment_bone"] = bone_name
        obj["g3v_authored_scale_baked"] = list(pre_scale)

        _ATTACHMENT_REGISTRY[obj.name] = {
            "object_name": obj.name,
            "rig_name": rig.name,
            "bone_name": bone_name,
            "relative": relative.copy(),
        }
        dims = _world_dimensions(obj)
        print(
            f"G3V_ATTACHMENT_CREATED={obj.name} bone={bone_name} "
            f"authored_scale={pre_scale} world_dims=({dims[0]:.6f},{dims[1]:.6f},{dims[2]:.6f})"
        )

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

    def audit_attachment_dimensions():
        global _AUDIT_DONE
        if _AUDIT_DONE or len(_ATTACHMENT_REGISTRY) < 10:
            return
        rigs = [bpy.data.objects.get(v["rig_name"]) for v in _ATTACHMENT_REGISTRY.values()]
        rig = next((r for r in rigs if r is not None and r.type == "ARMATURE"), None)
        if rig is None:
            return
        h = _skeleton_height(rig)
        failures = []
        for entry in _ATTACHMENT_REGISTRY.values():
            obj = bpy.data.objects.get(entry["object_name"])
            if obj is None:
                continue
            dims = _world_dimensions(obj)
            largest = max(dims)
            print(
                f"G3V_ATTACHMENT_AUDIT={obj.name} dims=({dims[0]:.6f},{dims[1]:.6f},{dims[2]:.6f}) "
                f"largest_over_skeleton={largest / h:.4f}"
            )
            if largest > h * 0.80:
                failures.append(
                    f"{obj.name}: dims={tuple(round(v, 6) for v in dims)}, "
                    f"largest/skeleton={largest / h:.4f}, bone={entry['bone_name']}"
                )
        _AUDIT_DONE = True
        if failures:
            raise RuntimeError(
                "G3V representative attachment exceeds sane physical size after scale bake: "
                + " | ".join(failures)
            )
        print("G3V_ATTACHMENT_DIMENSION_AUDIT=PASS")

    def attachment_aware_bbox_world(objects):
        update_rigid_attachments()
        audit_attachment_dimensions()
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
    print("G3V_ATTACHMENT_LOCAL_SCALE=BAKED_TO_MESH")
