#!/usr/bin/env python3
"""Synthesize a short multi-source João behavioral driver in COCO-133 pose space.

This is a local QA/synthesis stage before Wan-Animate-2. It does not invoke Wan.
Body/posture comes from primary + SIENA diversity, hands from primary, and face/head
microbehavior from the secondary source. Source provenance is preserved per output frame.
"""

from __future__ import annotations

import argparse
import array
import json
import math
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

CONF = 0.20
FACE_OFFSET = 23
FACE_COUNT = 68
EYE_A = tuple(range(36, 42))
EYE_B = tuple(range(42, 48))
LEFT_HAND = list(range(91, 112))
RIGHT_HAND = list(range(112, 133))
BODY_EDGES = [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12)]
HAND_REL_EDGES = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),(0,17),(17,18),(18,19),(19,20)]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def finite(v):
    return v is not None and math.isfinite(float(v))


def load_json(path: Path):
    if not path.is_file():
        raise SystemExit(f"Missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_pose(path: Path):
    rows = []
    if not path.is_file():
        raise SystemExit(f"Pose track missing: {path}")
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("schema") != "coco_wholebody_133" or len(row.get("keypoints") or []) != 133:
            raise SystemExit(f"Invalid pose row in {path}")
        rows.append(row)
    if not rows:
        raise SystemExit(f"Empty pose track: {path}")
    return rows


def interp_point(a, b, f):
    ax, ay, ac = a
    bx, by, bc = b
    if not (finite(ax) and finite(ay)):
        return [bx, by, bc]
    if not (finite(bx) and finite(by)):
        return [ax, ay, ac]
    acv = float(ac or 0.0) if finite(ac) else 0.0
    bcv = float(bc or 0.0) if finite(bc) else 0.0
    return [float(ax)*(1-f)+float(bx)*f, float(ay)*(1-f)+float(by)*f, acv*(1-f)+bcv*f]


def sample_track(rows, t):
    if t <= float(rows[0]["t"]):
        return [list(p) for p in rows[0]["keypoints"]]
    if t >= float(rows[-1]["t"]):
        return [list(p) for p in rows[-1]["keypoints"]]
    lo, hi = 0, len(rows)-1
    while lo + 1 < hi:
        mid = (lo+hi)//2
        if float(rows[mid]["t"]) <= t:
            lo = mid
        else:
            hi = mid
    a, b = rows[lo], rows[hi]
    ta, tb = float(a["t"]), float(b["t"])
    f = 0.0 if tb <= ta else clamp((t-ta)/(tb-ta), 0.0, 1.0)
    return [interp_point(pa, pb, f) for pa, pb in zip(a["keypoints"], b["keypoints"])]


def mean_xy(kp, ids, conf=CONF):
    pts=[]
    for i in ids:
        x,y,c=kp[i]
        if finite(x) and finite(y) and finite(c) and float(c)>=conf:
            pts.append((float(x),float(y)))
    if not pts:
        return None
    return statistics.fmean(x for x,_ in pts), statistics.fmean(y for _,y in pts)


def shoulder_geom(kp):
    a, b = kp[5], kp[6]
    if not all(finite(v) for v in (a[0],a[1],b[0],b[1])):
        return None
    ax,ay,bx,by = float(a[0]),float(a[1]),float(b[0]),float(b[1])
    vx,vy=bx-ax,by-ay
    w=math.hypot(vx,vy)
    if w <= 1e-8:
        return None
    return {"center":((ax+bx)/2,(ay+by)/2),"width":w,"angle":math.atan2(vy,vx)}


def similarity(src_kp, dst_kp):
    s,d=shoulder_geom(src_kp),shoulder_geom(dst_kp)
    if s is None or d is None:
        return None
    return {"src_center":s["center"],"dst_center":d["center"],"scale":d["width"]/s["width"],"angle":d["angle"]-s["angle"]}


def apply_similarity(kp, tr):
    if tr is None:
        return [list(p) for p in kp]
    ca,sa=math.cos(tr["angle"]),math.sin(tr["angle"])
    sx,sy=tr["src_center"]; dx,dy=tr["dst_center"]; sc=tr["scale"]
    out=[]
    for x,y,c in kp:
        if not (finite(x) and finite(y)):
            out.append([x,y,c]); continue
        rx=(float(x)-sx)*sc; ry=(float(y)-sy)*sc
        out.append([dx+rx*ca-ry*sa,dy+rx*sa+ry*ca,c])
    return out


def blend_pose(a,b,f):
    return [interp_point(pa,pb,f) for pa,pb in zip(a,b)]


def hand_retarget(donor, target, left=True):
    body_elbow, body_wrist = ((7,9) if left else (8,10))
    hand_ids = LEFT_HAND if left else RIGHT_HAND
    root_idx=hand_ids[0]
    de, dw = donor[body_elbow], donor[body_wrist]
    te, tw = target[body_elbow], target[body_wrist]
    root=donor[root_idx]
    vals=(de[0],de[1],dw[0],dw[1],te[0],te[1],tw[0],tw[1],root[0],root[1])
    if not all(finite(v) for v in vals):
        return
    dv=(float(dw[0])-float(de[0]),float(dw[1])-float(de[1]))
    tv=(float(tw[0])-float(te[0]),float(tw[1])-float(te[1]))
    dl,tl=math.hypot(*dv),math.hypot(*tv)
    if dl<=1e-8 or tl<=1e-8:
        return
    ang=math.atan2(tv[1],tv[0])-math.atan2(dv[1],dv[0]); ca,sa=math.cos(ang),math.sin(ang); sc=tl/dl
    rx0,ry0=float(root[0]),float(root[1]); tx0,ty0=float(tw[0]),float(tw[1])
    for idx in hand_ids:
        x,y,c=donor[idx]
        if not (finite(x) and finite(y)):
            continue
        rx=(float(x)-rx0)*sc; ry=(float(y)-ry0)*sc
        target[idx]=[tx0+rx*ca-ry*sa,ty0+rx*sa+ry*ca,c]
    target[root_idx]=[tx0,ty0,donor[root_idx][2]]


def face_transform(kp):
    ea=mean_xy(kp,[FACE_OFFSET+i for i in EYE_A]); eb=mean_xy(kp,[FACE_OFFSET+i for i in EYE_B])
    if ea is None or eb is None:
        return None
    vx,vy=eb[0]-ea[0],eb[1]-ea[1]; sc=math.hypot(vx,vy)
    if sc<=1e-8:
        return None
    return {"center":((ea[0]+eb[0])/2,(ea[1]+eb[1])/2),"scale":sc,"angle":math.atan2(vy,vx)}


def normalize_face(kp):
    tr=face_transform(kp)
    if tr is None:
        return None
    cx,cy=tr["center"]; ca,sa=math.cos(tr["angle"]),math.sin(tr["angle"]); sc=tr["scale"]
    coords={}
    for rel in range(FACE_COUNT):
        idx=FACE_OFFSET+rel; x,y,c=kp[idx]
        if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF):
            continue
        dx,dy=float(x)-cx,float(y)-cy
        coords[rel]=((dx*ca+dy*sa)/sc,(-dx*sa+dy*ca)/sc,float(c))
    return tr,coords


def wrap_angle(a):
    while a>math.pi: a-=2*math.pi
    while a<-math.pi: a+=2*math.pi
    return a


def transfer_face_and_head(donor, donor_ref, target):
    dn=normalize_face(donor); dr=normalize_face(donor_ref); bt=face_transform(target)
    if dn is None or dr is None or bt is None:
        return
    dtr,dcoords=dn; rtr,_=dr
    base_sh=shoulder_geom(target); donor_sh=shoulder_geom(donor); ref_sh=shoulder_geom(donor_ref)
    tcx,tcy=bt["center"]
    if base_sh and donor_sh and ref_sh:
        cur_rel=(dtr["center"][0]-donor_sh["center"][0],dtr["center"][1]-donor_sh["center"][1])
        ref_rel=(rtr["center"][0]-ref_sh["center"][0],rtr["center"][1]-ref_sh["center"][1])
        dx=(cur_rel[0]-ref_rel[0])/max(ref_sh["width"],1e-8)
        dy=(cur_rel[1]-ref_rel[1])/max(ref_sh["width"],1e-8)
        tcx += dx*base_sh["width"]; tcy += dy*base_sh["width"]
    tang=bt["angle"]+wrap_angle(dtr["angle"]-rtr["angle"])
    ratio=clamp(dtr["scale"]/max(rtr["scale"],1e-8),0.85,1.15)
    tscale=bt["scale"]*ratio; ca,sa=math.cos(tang),math.sin(tang)
    for rel,(nx,ny,c) in dcoords.items():
        idx=FACE_OFFSET+rel
        target[idx]=[tcx+tscale*(nx*ca-ny*sa),tcy+tscale*(nx*sa+ny*ca),c]
    # Retarget coarse head keypoints 0..4 through the donor's current eye frame.
    dcx,dcy=dtr["center"]; dca,dsa=math.cos(dtr["angle"]),math.sin(dtr["angle"]); dsc=dtr["scale"]
    for idx in range(5):
        x,y,c=donor[idx]
        if not (finite(x) and finite(y)):
            continue
        ddx,ddy=float(x)-dcx,float(y)-dcy
        nx=(ddx*dca+ddy*dsa)/dsc; ny=(-ddx*dsa+ddy*dca)/dsc
        target[idx]=[tcx+tscale*(nx*ca-ny*sa),tcy+tscale*(nx*sa+ny*ca),c]


def normalized_boundary_distance(a,b):
    def norm(kp):
        g=shoulder_geom(kp)
        if g is None: return None
        cx,cy=g["center"]; sc=g["width"]; ca,sa=math.cos(g["angle"]),math.sin(g["angle"])
        out=[]
        for i in range(13):
            x,y,c=kp[i]
            if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF): continue
            dx,dy=float(x)-cx,float(y)-cy
            out.append((i,(dx*ca+dy*sa)/sc,(-dx*sa+dy*ca)/sc))
        return {i:(x,y) for i,x,y in out}
    na,nb=norm(a),norm(b)
    if not na or not nb: return 1.0
    ids=set(na)&set(nb)
    if len(ids)<4: return 1.0
    return math.sqrt(statistics.fmean((na[i][0]-nb[i][0])**2+(na[i][1]-nb[i][1])**2 for i in ids))


def percentile(xs,q):
    s=sorted(xs)
    if not s: return 0.0
    p=clamp(q,0,1)*(len(s)-1); lo=int(math.floor(p)); hi=int(math.ceil(p))
    return s[lo] if lo==hi else s[lo]*(hi-p)+s[hi]*(p-lo)


def audio_targets(audio: Path|None, duration: float, windows: int, ffmpeg: str):
    if audio is None:
        return [{"energy":0.5,"speech_class":"mixed"} for _ in range(windows)]
    exe=shutil.which(ffmpeg) or ffmpeg
    cmd=[exe,"-hide_banner","-loglevel","error","-i",str(audio),"-t",f"{duration:.6f}","-vn","-ac","1","-ar","16000","-f","f32le","pipe:1"]
    p=subprocess.run(cmd,capture_output=True)
    if p.returncode:
        raise SystemExit("Audio decode failed: "+p.stderr.decode("utf-8","replace"))
    arr=array.array("f"); arr.frombytes(p.stdout[:len(p.stdout)-len(p.stdout)%4])
    if sys.byteorder!="little": arr.byteswap()
    frame=800; rms=[]
    for i in range(0,len(arr),frame):
        chunk=arr[i:i+frame]
        if not chunk: break
        rms.append(math.sqrt(sum(float(x)*float(x) for x in chunk)/len(chunk)))
    if not rms:
        return [{"energy":0.0,"speech_class":"pause"} for _ in range(windows)]
    lo,hi=percentile(rms,.10),percentile(rms,.90)
    norm=[0.0 if hi<=lo+1e-12 else clamp((x-lo)/(hi-lo),0,1) for x in rms]
    p20,p65=percentile(norm,.20),percentile(norm,.65); th=clamp(p20+.35*(p65-p20),.08,.45)
    out=[]
    for w in range(windows):
        a=int(len(norm)*w/windows); b=int(len(norm)*(w+1)/windows); vals=norm[a:max(a+1,b)]
        energy=statistics.fmean(vals) if vals else 0.0; ratio=sum(v>=th for v in vals)/len(vals) if vals else 0.0
        cls="speech" if ratio>=.70 else "pause" if ratio<=.15 else "mixed"
        out.append({"energy":round(energy,6),"speech_class":cls})
    return out


def candidate_score(u, role_name, target, target_duration):
    rr=u["roles"][role_name]; q=float(rr["weight"])
    energy=float((u.get("prosody") or {}).get("energy_norm_mean") or 0.0)
    e=1.0-abs(energy-float(target["energy"]))
    cls=(u.get("speech") or {}).get("class")
    s=1.0 if cls==target["speech_class"] else 0.55 if {cls,target["speech_class"]}=={"speech","mixed"} else 0.25
    tr=u.get("transition") or {}; t=(float(tr.get("entry_score") or 0)+float(tr.get("exit_score") or 0))/2
    d=1.0-min(1.0,abs(float(u["duration_s"])-target_duration)/max(target_duration,1e-6))
    return .45*q+.25*e+.15*s+.10*t+.05*d


def best_candidate(units, role_name, source_key, target, target_duration, exclude_ids=None):
    exclude_ids=exclude_ids or set(); c=[]
    for u in units:
        if u["source_key"]!=source_key or u["library_unit_id"] in exclude_ids: continue
        rr=(u.get("roles") or {}).get(role_name) or {}
        if not rr.get("enabled"): continue
        c.append((candidate_score(u,role_name,target,target_duration),u))
    if not c: raise SystemExit(f"No candidate for role={role_name} source={source_key}")
    c.sort(key=lambda x:x[0],reverse=True); return c[0]


def draw_preview(frames, output: Path, fps: float, width=540, height=960):
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        raise SystemExit(f"OpenCV/NumPy required for preview: {exc}")
    output.parent.mkdir(parents=True,exist_ok=True)
    vw=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*"mp4v"),fps,(width,height))
    if not vw.isOpened(): raise SystemExit(f"Could not open preview writer: {output}")
    for rec in frames:
        img=np.zeros((height,width,3),dtype=np.uint8); kp=rec["keypoints"]
        def pt(i):
            x,y,c=kp[i]
            if not (finite(x) and finite(y) and finite(c) and float(c)>=0.05): return None
            return int(clamp(float(x),0,1)*(width-1)),int(clamp(float(y),0,1)*(height-1))
        for a,b in BODY_EDGES:
            pa,pb=pt(a),pt(b)
            if pa and pb: cv2.line(img,pa,pb,(220,220,220),2,cv2.LINE_AA)
        for hand in (LEFT_HAND,RIGHT_HAND):
            for ra,rb in HAND_REL_EDGES:
                pa,pb=pt(hand[ra]),pt(hand[rb])
                if pa and pb: cv2.line(img,pa,pb,(180,180,180),1,cv2.LINE_AA)
        for i in range(FACE_OFFSET,FACE_OFFSET+FACE_COUNT):
            p=pt(i)
            if p: cv2.circle(img,p,1,(255,255,255),-1,cv2.LINE_AA)
        text=f"t={rec['t']:.2f}s  base={rec['provenance']['base_unit'].split(':')[-1]}"
        cv2.putText(img,text,(12,28),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1,cv2.LINE_AA)
        vw.write(img)
    vw.release()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--library",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--audio",type=Path)
    ap.add_argument("--duration",type=float,default=4.5)
    ap.add_argument("--fps",type=float,default=24.0)
    ap.add_argument("--ffmpeg",default="ffmpeg")
    args=ap.parse_args()
    if not (4.0 <= args.duration <= 5.0): raise SystemExit("--duration must be between 4.0 and 5.0 seconds for the first gate")
    lib=load_json(args.library)
    if lib.get("schema")!="joao-motion-library/v1": raise SystemExit(f"Unexpected library schema: {lib.get('schema')}")
    if args.audio is not None and not args.audio.is_file(): raise SystemExit(f"Audio missing: {args.audio}")
    units=lib.get("units") or []; nwin=2; win_d=args.duration/nwin; targets=audio_targets(args.audio,args.duration,nwin,args.ffmpeg)

    # Force the first synthesis gate to exercise both canonical body sources.
    options=[]
    for order in (("primary","tertiary"),("tertiary","primary")):
        selected=[]; total=0.0; prev_ids=set()
        for i,source in enumerate(order):
            sc,u=best_candidate(units,"posture",source,targets[i],win_d,prev_ids); selected.append((sc,u)); prev_ids.add(u["library_unit_id"]); total+=sc
        # continuity from stored pose boundaries, normalized by shoulder geometry
        a=selected[0][1].get("pose_end") or {}; b=selected[1][1].get("pose_start") or {}
        ak=a.get("keypoints"); bk=b.get("keypoints"); dist=normalized_boundary_distance(ak,bk) if ak and bk else 1.0
        continuity=1.0/(1.0+5.0*dist); total+=.15*continuity
        options.append((total,order,selected,continuity))
    options.sort(key=lambda x:x[0],reverse=True); _,order,base_sel,continuity=options[0]

    face_sel=[]; hand_sel=[]; used_face=set(); used_hand=set()
    for i in range(nwin):
        fsc,fu=best_candidate(units,"face","secondary",targets[i],win_d,used_face); used_face.add(fu["library_unit_id"]); face_sel.append((fsc,fu))
        hsc,hu=best_candidate(units,"both_hands","primary",targets[i],win_d,used_hand); used_hand.add(hu["library_unit_id"]); hand_sel.append((hsc,hu))

    plan={
        "schema":"behavioral-pose-driver-plan/v1",
        "duration_s":args.duration,"fps":args.fps,"target_audio":str(args.audio.resolve()) if args.audio else None,
        "target_windows":targets,"base_source_order":list(order),"base_boundary_continuity":round(continuity,6),"windows":[]
    }
    for i in range(nwin):
        plan["windows"].append({"index":i,"target_start_s":i*win_d,"target_end_s":(i+1)*win_d,"target":targets[i],
            "base":{"unit":base_sel[i][1]["library_unit_id"],"score":round(base_sel[i][0],6)},
            "hands":{"unit":hand_sel[i][1]["library_unit_id"],"score":round(hand_sel[i][0],6)},
            "face":{"unit":face_sel[i][1]["library_unit_id"],"score":round(face_sel[i][0],6)}})

    cache={}
    def track_for(u):
        p=Path(u["pose_track"])
        if p not in cache: cache[p]=load_pose(p)
        return cache[p]
    unit_by_id={u["library_unit_id"]:u for u in units}
    frames=[]; prev_pose=None
    frame_count=int(round(args.duration*args.fps))
    for fi in range(frame_count):
        t=fi/args.fps; wi=min(nwin-1,int(t/win_d)); local=t-wi*win_d; alpha=clamp(local/win_d,0,1)
        bu=unit_by_id[plan["windows"][wi]["base"]["unit"]]; hu=unit_by_id[plan["windows"][wi]["hands"]["unit"]]; fu=unit_by_id[plan["windows"][wi]["face"]["unit"]]
        bt=bu["source_start_s"]+alpha*(bu["source_end_s"]-bu["source_start_s"])
        ht=hu["source_start_s"]+alpha*(hu["source_end_s"]-hu["source_start_s"])
        ft=fu["source_start_s"]+alpha*(fu["source_end_s"]-fu["source_start_s"])
        base=sample_track(track_for(bu),bt)
        if wi>0:
            first=sample_track(track_for(bu),bu["source_start_s"])
            prev_target=frames[int(round(wi*win_d*args.fps))-1]["keypoints"]
            base=apply_similarity(base,similarity(first,prev_target))
        hand=sample_track(track_for(hu),ht); hand_retarget(hand,base,True); hand_retarget(hand,base,False)
        face=sample_track(track_for(fu),ft); face_ref=sample_track(track_for(fu),fu["source_start_s"]); transfer_face_and_head(face,face_ref,base)
        if wi>0 and local<0.25 and prev_pose is not None:
            base=blend_pose(prev_pose,base,clamp(local/0.25,0,1))
        rec={"t":round(t,6),"schema":"coco_wholebody_133","keypoints":base,
             "provenance":{"base_unit":bu["library_unit_id"],"hand_unit":hu["library_unit_id"],"face_unit":fu["library_unit_id"]}}
        frames.append(rec); prev_pose=base

    args.output_dir.mkdir(parents=True,exist_ok=True)
    plan_path=args.output_dir/"driver_plan.json"; track_path=args.output_dir/"behavioral_driver_coco133.jsonl"; preview=args.output_dir/"behavioral_driver_pose_preview.mp4"
    plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    with track_path.open("w",encoding="utf-8",newline="\n") as fh:
        for r in frames: fh.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
    draw_preview(frames,preview,args.fps)
    print("MULTI-SOURCE BEHAVIORAL POSE DRIVER")
    print("===================================")
    print(f"Duration: {args.duration}s / fps={args.fps} / frames={len(frames)}")
    print(f"Base source order: {order[0]} -> {order[1]}")
    print(f"Boundary continuity score: {continuity:.6f}")
    for w in plan["windows"]:
        print(f"Window {w['index']}: base={w['base']['unit']} hands={w['hands']['unit']} face={w['face']['unit']} target={w['target']}")
    print(f"Plan: {plan_path}")
    print(f"Pose track: {track_path}")
    print(f"Preview: {preview}")
    print("Wan-Animate-2: NOT INVOKED")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
