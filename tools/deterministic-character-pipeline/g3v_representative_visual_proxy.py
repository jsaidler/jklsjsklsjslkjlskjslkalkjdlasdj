import bpy
import hashlib
import importlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

BACKGROUND = (0.050, 0.056, 0.066)
ID_COLORS = {
    "skin": (0.95, 0.08, 0.08),
    "hair": (0.08, 0.92, 0.18),
    "cloth": (0.08, 0.22, 0.95),
    "metal": (0.95, 0.82, 0.08),
}
PALETTES = {
    "skin": [(0.18,0.09,0.055),(0.31,0.16,0.095),(0.48,0.28,0.16),(0.67,0.45,0.27)],
    "hair": [(0.012,0.012,0.018),(0.030,0.030,0.042),(0.060,0.060,0.082),(0.105,0.105,0.135)],
    "cloth": [(0.18,0.15,0.105),(0.31,0.27,0.185),(0.48,0.43,0.31),(0.66,0.60,0.45)],
    "metal": [(0.12,0.135,0.15),(0.25,0.28,0.31),(0.45,0.49,0.53),(0.70,0.74,0.77)],
}


def cli_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    a = cli_args()
    for i, v in enumerate(a):
        if v == name and i + 1 < len(a):
            return a[i + 1]
    return default


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mpfb_class(submodule, name):
    roots = []
    for modname in list(sys.modules):
        if modname == "mpfb" or modname.endswith(".mpfb"):
            roots.append(modname)
    for explicit in ("bl_ext.roguelite_g3v.mpfb", "bl_ext.blender_org.mpfb", "mpfb"):
        if explicit not in roots:
            try:
                importlib.import_module(explicit)
                roots.append(explicit)
            except Exception:
                pass
    for root in roots:
        try:
            mod = importlib.import_module(root + "." + submodule)
            if hasattr(mod, name):
                return getattr(mod, name), root
        except Exception:
            pass
    raise RuntimeError("MPFB extension is not loaded/enabled; searched roots: " + repr(roots))


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def configure_camera(camera, pitch_deg, target):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (target.x, target.y - distance * math.cos(p), target.z + distance * math.sin(p))
    look_at(camera, target)


def bone_world(rig, name, tail=False):
    pb = rig.pose.bones.get(name)
    if pb is None:
        raise RuntimeError("Missing target bone: " + name)
    p = pb.tail if tail else pb.head
    return rig.matrix_world @ p


def add_material(obj, rgb, name):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.0)
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def tag_semantic(obj, semantic):
    obj["g3v_semantic"] = semantic
    obj.color = (*ID_COLORS[semantic], 1.0)


def parent_bone(obj, rig, bone_name):
    world = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone_name
    obj.matrix_world = world


def add_uv_ellipsoid(name, center, scale, semantic, rig, bone):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    for p in obj.data.polygons:
        p.use_smooth = False
    add_material(obj, PALETTES[semantic][2], name + "_MAT")
    tag_semantic(obj, semantic)
    parent_bone(obj, rig, bone)
    return obj


def add_box(name, center, scale, semantic, rig, bone, rotation=(0.0,0.0,0.0)):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=center, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    add_material(obj, PALETTES[semantic][2], name + "_MAT")
    tag_semantic(obj, semantic)
    parent_bone(obj, rig, bone)
    return obj


def add_shackle(name, center, radius, semantic, rig, bone):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=radius*0.28, major_segments=10, minor_segments=4, location=center)
    obj = bpy.context.object
    obj.name = name
    add_material(obj, PALETTES[semantic][2], name + "_MAT")
    tag_semantic(obj, semantic)
    parent_bone(obj, rig, bone)
    return obj


def evaluated_points(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    try:
        mw = ev.matrix_world
        return [mw @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def bbox_world(objects):
    pts = []
    for obj in objects:
        if obj.type == "MESH" and not obj.hide_render:
            pts.extend(evaluated_points(obj))
    if not pts:
        raise RuntimeError("No visible representative mesh points")
    xs=[p.x for p in pts]; ys=[p.y for p in pts]; zs=[p.z for p in pts]
    return Vector((min(xs),min(ys),min(zs))), Vector((max(xs),max(ys),max(zs)))


def bbox_px(scene, camera, objects):
    xs=[]; ys=[]
    for obj in objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        for p in evaluated_points(obj):
            co = world_to_camera_view(scene, camera, p)
            xs.append(co.x * scene.render.resolution_x)
            ys.append(co.y * scene.render.resolution_y)
    return min(xs), max(xs), min(ys), max(ys)


def calibrate_camera(scene, camera, objects, target_px):
    camera.data.ortho_scale = 5.0
    for _ in range(6):
        bpy.context.view_layer.update()
        _,_,y0,y1 = bbox_px(scene,camera,objects)
        h = y1-y0
        if h <= 0:
            raise RuntimeError("Projected G3V height is zero")
        camera.data.ortho_scale *= h/float(target_px)
    bpy.context.view_layer.update()


def load_rgba(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    try:
        w,h = int(img.size[0]), int(img.size[1])
        px = [0.0]*(w*h*4)
        img.pixels.foreach_get(px)
        return w,h,px
    finally:
        bpy.data.images.remove(img)


def save_rgba(path,w,h,px):
    img=bpy.data.images.new(path.stem,width=w,height=h,alpha=True,float_buffer=False)
    try:
        img.pixels.foreach_set(px)
        img.filepath_raw=str(path)
        img.file_format="PNG"
        img.save()
    finally:
        bpy.data.images.remove(img)


def rgb(px,i):
    j=i*4
    return (px[j],px[j+1],px[j+2])


def put(px,i,c):
    j=i*4
    px[j]=c[0]; px[j+1]=c[1]; px[j+2]=c[2]; px[j+3]=1.0


def d2(a,b):
    return sum((a[k]-b[k])**2 for k in range(3))


def classify_id(c):
    best=(None,d2(c,BACKGROUND))
    for sem,ic in ID_COLORS.items():
        dd=d2(c,ic)
        if dd < best[1]: best=(sem,dd)
    if best[0] is None or best[1] > 0.12:
        return None
    return best[0]


def quantile(vals,q):
    if not vals: return 0.5
    s=sorted(vals)
    pos=(len(s)-1)*q
    lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi: return s[lo]
    t=pos-lo
    return s[lo]*(1-t)+s[hi]*t


def build_visible_outputs(frame_records, output_dir):
    all_luma=[]
    cached=[]
    for rec in frame_records:
        w,h,idpx=load_rgba(Path(rec["id_pass"]))
        w2,h2,lpx=load_rgba(Path(rec["light_pass"]))
        if (w,h)!=(w2,h2): raise RuntimeError("ID/light pass size mismatch")
        sems=[None]*(w*h)
        for i in range(w*h):
            sem=classify_id(rgb(idpx,i)); sems[i]=sem
            if sem:
                c=rgb(lpx,i); all_luma.append(0.2126*c[0]+0.7152*c[1]+0.0722*c[2])
        cached.append((rec,w,h,sems,lpx))
    cuts=[quantile(all_luma,0.22),quantile(all_luma,0.50),quantile(all_luma,0.78)]
    outputs=[]
    for rec,w,h,sems,lpx in cached:
        flat=[0.0]*(w*h*4); pix=[0.0]*(w*h*4)
        for i,sem in enumerate(sems):
            if sem is None:
                put(flat,i,BACKGROUND); put(pix,i,BACKGROUND); continue
            put(flat,i,PALETTES[sem][2])
            c=rgb(lpx,i); lum=0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
            band=0 if lum<cuts[0] else 1 if lum<cuts[1] else 2 if lum<cuts[2] else 3
            put(pix,i,PALETTES[sem][band])
        flat_path=output_dir/f"g3v_flat_f{rec['frame']:04d}.png"
        pixel_path=output_dir/f"g3v_pixel_f{rec['frame']:04d}.png"
        save_rgba(flat_path,w,h,flat); save_rgba(pixel_path,w,h,pix)
        outputs += [
            {"variant":"flat_representative","frame":rec["frame"],"file":str(flat_path),"sha256":sha256_file(flat_path)},
            {"variant":"pixel_4band_semantic","frame":rec["frame"],"file":str(pixel_path),"sha256":sha256_file(pixel_path)},
        ]
    return cuts,outputs


def render_pass(scene, path, semantic_objects, mode):
    if mode=="id":
        scene.display.shading.light="FLAT"; scene.display.shading.color_type="OBJECT"
        for obj in semantic_objects: obj.color=(*ID_COLORS[obj["g3v_semantic"]],1.0)
    elif mode=="light":
        scene.display.shading.light="STUDIO"; scene.display.shading.color_type="OBJECT"
        for obj in semantic_objects: obj.color=(0.67,0.67,0.67,1.0)
    else: raise RuntimeError("Unknown pass mode")
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if not path.exists() or path.stat().st_size==0:
        raise RuntimeError("Render missing: "+str(path))


def main():
    output_dir=Path(arg("--output-dir","")).resolve()
    g2_blend=Path(arg("--g2-blend","")).resolve()
    g2_manifest=Path(arg("--g2-manifest","")).resolve()
    pitch=float(arg("--pitch","26")); hero_px=int(arg("--hero-px","128"))
    if not g2_blend.exists() or not g2_manifest.exists(): raise RuntimeError("G2 artifacts missing")
    output_dir.mkdir(parents=True,exist_ok=True)

    HumanService, mpfb_root = mpfb_class("services.humanservice","HumanService")
    TargetService, _ = mpfb_class("services.targetservice","TargetService")

    meta=json.loads(g2_manifest.read_text(encoding="utf-8-sig"))
    samples=meta.get("samples",[])
    if len(samples)<10: raise RuntimeError("G2 manifest has too few samples")
    frames=[int(samples[i]["frame"]) for i in (0,3,6,9)]

    bpy.ops.wm.open_mainfile(filepath=str(g2_blend))
    scene=bpy.context.scene
    source=bpy.data.objects.get("G2_CANONICAL_RIG")
    if source is None or source.type!="ARMATURE" or not source.animation_data or not source.animation_data.action:
        raise RuntimeError("G2 canonical animated rig missing")

    for obj in list(scene.objects):
        if obj.type in {"MESH","CAMERA","LIGHT"}: obj.hide_render=True
    source.hide_render=True

    macro=TargetService.get_default_macro_info_dict()
    macro.update({"gender":1.0,"age":0.48,"muscle":0.40,"weight":0.36,"proportions":0.56,"height":0.52,"cupsize":0.42,"firmness":0.55})
    body=HumanService.create_human(mask_helpers=True,detailed_helpers=True,extra_vertex_groups=True,feet_on_ground=True,scale=0.1,macro_detail_dict=macro)
    body.name="G3V_BODY"
    for p in body.data.polygons: p.use_smooth=False
    add_material(body,PALETTES["skin"][2],"G3V_SKIN")
    tag_semantic(body,"skin")
    body.hide_render=False

    rig=HumanService.add_builtin_rig(body,"cmu_mb",import_weights=True)
    if rig is None: raise RuntimeError("MPFB cmu_mb rig creation failed")
    rig.name="G3V_CMU_RIG"
    required=["Hips","Spine1","Neck1","Head","LeftArm","LeftForeArm","LeftHand","RightArm","RightForeArm","RightHand","LeftUpLeg","LeftLeg","LeftFoot","RightUpLeg","RightLeg","RightFoot"]
    missing=[b for b in required if rig.pose.bones.get(b) is None]
    if missing: raise RuntimeError("MPFB cmu_mb missing bones: "+", ".join(missing))

    matching=[]
    for pb in rig.pose.bones:
        spb=source.pose.bones.get(pb.name)
        if spb:
            pb.rotation_mode=spb.rotation_mode; matching.append(pb.name)
    rig.animation_data_create(); rig.animation_data.action=source.animation_data.action.copy(); rig.animation_data.action.name="G3V_CMU_NORMALWALK"
    rig.location=source.location.copy(); rig.rotation_euler=source.rotation_euler.copy(); rig.scale=source.scale.copy()

    scene.frame_set(frames[0]); bpy.context.view_layer.update()
    lo,hi=bbox_world([body]); h=max(0.5,hi.z-lo.z)
    head=bone_world(rig,"Head",True); neck=bone_world(rig,"Neck1"); spine=bone_world(rig,"Spine1"); hips=bone_world(rig,"Hips")

    extras=[]
    extras.append(add_uv_ellipsoid("G3V_HAIR_UPPER",(head+neck)*0.5,(h*0.105,h*0.060,h*0.18),"hair",rig,"Head"))
    extras.append(add_uv_ellipsoid("G3V_HAIR_MID",(neck+spine)*0.5+Vector((0,h*0.045,-h*0.06)),(h*0.115,h*0.055,h*0.22),"hair",rig,"Neck1"))
    extras.append(add_uv_ellipsoid("G3V_HAIR_LOWER",(spine+hips)*0.5+Vector((0,h*0.055,-h*0.05)),(h*0.12,h*0.050,h*0.24),"hair",rig,"Spine1"))
    chest=(bone_world(rig,"Spine1")+bone_world(rig,"Neck1"))*0.5
    extras.append(add_box("G3V_CLOTH_WRAP",chest,(h*0.105,h*0.055,h*0.10),"cloth",rig,"Spine1",(0.0,0.0,math.radians(-7))))
    extras.append(add_box("G3V_CLOTH_WAIST",hips+Vector((0,-h*0.015,-h*0.03)),(h*0.11,h*0.06,h*0.045),"cloth",rig,"Hips"))
    extras.append(add_box("G3V_CLOTH_DRAPE",hips+Vector((h*0.045,-h*0.02,-h*0.18)),(h*0.07,h*0.045,h*0.18),"cloth",rig,"Hips",(0.0,math.radians(-8),math.radians(-8))))
    for side,bone in (("L","LeftHand"),("R","RightHand")):
        extras.append(add_shackle("G3V_WRIST_"+side,bone_world(rig,bone),h*0.035,"metal",rig,bone))
    for side,bone in (("L","LeftFoot"),("R","RightFoot")):
        extras.append(add_shackle("G3V_ANKLE_"+side,bone_world(rig,bone),h*0.040,"metal",rig,bone))

    semantic_objects=[body]+extras
    for o in semantic_objects: o.hide_render=False

    for obj in list(scene.objects):
        if obj.type=="CAMERA": bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.object.camera_add(); camera=bpy.context.object; camera.name="G3V_CAMERA"; camera.data.type="ORTHO"; scene.camera=camera

    scene.render.engine="BLENDER_WORKBENCH"
    scene.render.resolution_x=640; scene.render.resolution_y=360; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
    scene.display.shading.show_shadows=False; scene.display.shading.show_cavity=False; scene.display.shading.show_specular_highlight=False
    scene.display.shading.background_type="VIEWPORT"; scene.display.shading.background_color=BACKGROUND
    try: scene.display.render_aa="OFF"
    except Exception: pass
    try:
        scene.view_settings.view_transform="Standard"; scene.view_settings.look="None"; scene.view_settings.exposure=0.0; scene.view_settings.gamma=1.0
    except Exception: pass

    scene.frame_set(frames[0]); bpy.context.view_layer.update(); lo,hi=bbox_world(semantic_objects); target=(lo+hi)*0.5
    configure_camera(camera,pitch,target); calibrate_camera(scene,camera,semantic_objects,hero_px); locked_ortho=camera.data.ortho_scale

    records=[]
    for frame in frames:
        scene.frame_set(frame); bpy.context.view_layer.update(); lo,hi=bbox_world(semantic_objects); target=(lo+hi)*0.5
        configure_camera(camera,pitch,target); camera.data.ortho_scale=locked_ortho
        idp=output_dir/f"g3v_id_f{frame:04d}.png"; lightp=output_dir/f"g3v_light_f{frame:04d}.png"
        render_pass(scene,idp,semantic_objects,"id"); render_pass(scene,lightp,semantic_objects,"light")
        records.append({"frame":frame,"id_pass":str(idp),"light_pass":str(lightp)})

    cuts,outputs=build_visible_outputs(records,output_dir)
    blend=output_dir/"g3v_representative_proxy.blend"; bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    manifest={
        "gate":"G3V","status":"REVIEW_REQUIRED","mpfb_module_root":mpfb_root,
        "baseline":{"native_raster":[640,360],"camera_pitch_deg":pitch,"hero_px":hero_px,"ortho_scale":locked_ortho},
        "macro":macro,"rig":"cmu_mb","matching_motion_bones":len(matching),"required_bones_missing":missing,
        "source_frames":frames,"semantic_objects":[{"name":o.name,"semantic":o["g3v_semantic"]} for o in semantic_objects],
        "luminance_cuts":cuts,"outputs":outputs,"debug_passes":records,"blend":str(blend),
        "review_rule":"Judge whether representative continuous female geometry plus persistent hair/cloth/metal can survive deterministic native-grid translation. If this still reads only as generic 3D pixelization, reject hidden-3D as the direct visible-art generator before Exilada production modeling."
    }
    mp=output_dir/"g3v_manifest.json"; mp.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("G3V_REPRESENTATIVE_PROXY=REVIEW_REQUIRED")
    print("G3V_MPFB_ROOT="+mpfb_root)
    print("G3V_MATCHING_MOTION_BONES="+str(len(matching)))
    print("G3V_FRAMES="+",".join(map(str,frames)))
    print("G3V_MANIFEST="+str(mp))

if __name__=="__main__":
    main()
