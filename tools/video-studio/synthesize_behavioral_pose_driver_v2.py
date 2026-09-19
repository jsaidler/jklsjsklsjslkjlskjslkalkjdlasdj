#!/usr/bin/env python3
"""Synthesize a short multi-source João behavioral driver in COCO-133 pose space (v2).

v2 responds to first-driver QA evidence:
- body-source pair selection gives much more weight to actual pose continuity;
- base and hand retrieval include source-frame safety;
- hand selection is joint with the chosen base so retargeted hands are predicted in-frame;
- face and hand donors are selected as continuity-aware pairs;
- source change uses a symmetric overlap/crossfade with quintic easing, not an incremental
  0.25 s copy/blend.

No Wan-Animate-2 or DWPose inference is invoked.
"""
from __future__ import annotations
import argparse, array, json, math, shutil, statistics, subprocess, sys
from pathlib import Path

CONF=.20
FACE_OFFSET=23; FACE_COUNT=68
EYE_A=tuple(range(36,42)); EYE_B=tuple(range(42,48))
LEFT_HAND=list(range(91,112)); RIGHT_HAND=list(range(112,133))
BODY_EDGES=[(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12)]
HAND_REL_EDGES=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),(0,17),(17,18),(18,19),(19,20)]

def clamp(v,lo,hi): return max(lo,min(hi,v))
def finite(v): return v is not None and math.isfinite(float(v))
def smooth5(x):
    x=clamp(x,0.0,1.0)
    return x*x*x*(10.0+x*(-15.0+6.0*x))

def load_json(path:Path):
    if not path.is_file(): raise SystemExit(f"Missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))

def load_pose(path:Path):
    if not path.is_file(): raise SystemExit(f"Pose track missing: {path}")
    out=[]
    for n,line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(),1):
        if not line.strip(): continue
        r=json.loads(line)
        if r.get("schema")!="coco_wholebody_133" or len(r.get("keypoints") or [])!=133:
            raise SystemExit(f"Invalid pose row line {n}: {path}")
        out.append(r)
    if not out: raise SystemExit(f"Empty pose track: {path}")
    return out

def interp_point(a,b,f):
    ax,ay,ac=a; bx,by,bc=b
    if not (finite(ax) and finite(ay)): return [bx,by,bc]
    if not (finite(bx) and finite(by)): return [ax,ay,ac]
    acv=float(ac) if finite(ac) else 0.0; bcv=float(bc) if finite(bc) else 0.0
    return [float(ax)*(1-f)+float(bx)*f,float(ay)*(1-f)+float(by)*f,acv*(1-f)+bcv*f]

def sample_track(rows,t):
    if t<=float(rows[0]["t"]): return [list(p) for p in rows[0]["keypoints"]]
    if t>=float(rows[-1]["t"]): return [list(p) for p in rows[-1]["keypoints"]]
    lo,hi=0,len(rows)-1
    while lo+1<hi:
        m=(lo+hi)//2
        if float(rows[m]["t"])<=t: lo=m
        else: hi=m
    a,b=rows[lo],rows[hi]; ta,tb=float(a["t"]),float(b["t"])
    f=0.0 if tb<=ta else clamp((t-ta)/(tb-ta),0.0,1.0)
    return [interp_point(pa,pb,f) for pa,pb in zip(a["keypoints"],b["keypoints"])]

def mean_xy(kp,ids,conf=CONF):
    pts=[]
    for i in ids:
        x,y,c=kp[i]
        if finite(x) and finite(y) and finite(c) and float(c)>=conf:
            pts.append((float(x),float(y)))
    if not pts: return None
    return statistics.fmean(x for x,_ in pts),statistics.fmean(y for _,y in pts)

def shoulder_geom(kp):
    a,b=kp[5],kp[6]
    if not all(finite(v) for v in (a[0],a[1],b[0],b[1])): return None
    ax,ay,bx,by=map(float,(a[0],a[1],b[0],b[1]))
    vx,vy=bx-ax,by-ay; w=math.hypot(vx,vy)
    if w<=1e-8: return None
    return {"center":((ax+bx)/2,(ay+by)/2),"width":w,"angle":math.atan2(vy,vx)}

def similarity(src,dst):
    s,d=shoulder_geom(src),shoulder_geom(dst)
    if s is None or d is None: return None
    return {"src_center":s["center"],"dst_center":d["center"],"scale":d["width"]/s["width"],"angle":d["angle"]-s["angle"]}

def apply_similarity(kp,tr):
    if tr is None: return [list(p) for p in kp]
    ca,sa=math.cos(tr["angle"]),math.sin(tr["angle"])
    sx,sy=tr["src_center"]; dx,dy=tr["dst_center"]; sc=tr["scale"]; out=[]
    for x,y,c in kp:
        if not (finite(x) and finite(y)): out.append([x,y,c]); continue
        rx=(float(x)-sx)*sc; ry=(float(y)-sy)*sc
        out.append([dx+rx*ca-ry*sa,dy+rx*sa+ry*ca,c])
    return out

def blend_pose(a,b,f): return [interp_point(pa,pb,f) for pa,pb in zip(a,b)]

def hand_retarget(donor,target,left=True):
    elbow,wrist=((7,9) if left else (8,10)); ids=LEFT_HAND if left else RIGHT_HAND; root_idx=ids[0]
    de,dw=donor[elbow],donor[wrist]; te,tw=target[elbow],target[wrist]; root=donor[root_idx]
    vals=(de[0],de[1],dw[0],dw[1],te[0],te[1],tw[0],tw[1],root[0],root[1])
    if not all(finite(v) for v in vals): return
    dv=(float(dw[0])-float(de[0]),float(dw[1])-float(de[1]))
    tv=(float(tw[0])-float(te[0]),float(tw[1])-float(te[1]))
    dl,tl=math.hypot(*dv),math.hypot(*tv)
    if dl<=1e-8 or tl<=1e-8: return
    ang=math.atan2(tv[1],tv[0])-math.atan2(dv[1],dv[0]); ca,sa=math.cos(ang),math.sin(ang); sc=tl/dl
    rx0,ry0=float(root[0]),float(root[1]); tx0,ty0=float(tw[0]),float(tw[1])
    for idx in ids:
        x,y,c=donor[idx]
        if not (finite(x) and finite(y)): continue
        rx=(float(x)-rx0)*sc; ry=(float(y)-ry0)*sc
        target[idx]=[tx0+rx*ca-ry*sa,ty0+rx*sa+ry*ca,c]
    target[root_idx]=[tx0,ty0,donor[root_idx][2]]

def face_transform(kp):
    ea=mean_xy(kp,[FACE_OFFSET+i for i in EYE_A]); eb=mean_xy(kp,[FACE_OFFSET+i for i in EYE_B])
    if ea is None or eb is None: return None
    vx,vy=eb[0]-ea[0],eb[1]-ea[1]; sc=math.hypot(vx,vy)
    if sc<=1e-8: return None
    return {"center":((ea[0]+eb[0])/2,(ea[1]+eb[1])/2),"scale":sc,"angle":math.atan2(vy,vx)}

def normalize_face(kp):
    tr=face_transform(kp)
    if tr is None: return None
    cx,cy=tr["center"]; ca,sa=math.cos(tr["angle"]),math.sin(tr["angle"]); sc=tr["scale"]; coords={}
    for rel in range(FACE_COUNT):
        idx=FACE_OFFSET+rel; x,y,c=kp[idx]
        if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF): continue
        dx,dy=float(x)-cx,float(y)-cy
        coords[rel]=((dx*ca+dy*sa)/sc,(-dx*sa+dy*ca)/sc,float(c))
    return tr,coords

def wrap_angle(a):
    while a>math.pi: a-=2*math.pi
    while a<-math.pi: a+=2*math.pi
    return a

def transfer_face_and_head(donor,donor_ref,target):
    dn=normalize_face(donor); dr=normalize_face(donor_ref); bt=face_transform(target)
    if dn is None or dr is None or bt is None: return
    dtr,dcoords=dn; rtr,_=dr
    base_sh=shoulder_geom(target); donor_sh=shoulder_geom(donor); ref_sh=shoulder_geom(donor_ref)
    tcx,tcy=bt["center"]
    if base_sh and donor_sh and ref_sh:
        cur=(dtr["center"][0]-donor_sh["center"][0],dtr["center"][1]-donor_sh["center"][1])
        ref=(rtr["center"][0]-ref_sh["center"][0],rtr["center"][1]-ref_sh["center"][1])
        tcx+=(cur[0]-ref[0])/max(ref_sh["width"],1e-8)*base_sh["width"]
        tcy+=(cur[1]-ref[1])/max(ref_sh["width"],1e-8)*base_sh["width"]
    tang=bt["angle"]+wrap_angle(dtr["angle"]-rtr["angle"])
    ratio=clamp(dtr["scale"]/max(rtr["scale"],1e-8),.85,1.15)
    tscale=bt["scale"]*ratio; ca,sa=math.cos(tang),math.sin(tang)
    for rel,(nx,ny,c) in dcoords.items():
        target[FACE_OFFSET+rel]=[tcx+tscale*(nx*ca-ny*sa),tcy+tscale*(nx*sa+ny*ca),c]
    dcx,dcy=dtr["center"]; dca,dsa=math.cos(dtr["angle"]),math.sin(dtr["angle"]); dsc=dtr["scale"]
    for idx in range(5):
        x,y,c=donor[idx]
        if not (finite(x) and finite(y)): continue
        ddx,ddy=float(x)-dcx,float(y)-dcy
        nx=(ddx*dca+ddy*dsa)/dsc; ny=(-ddx*dsa+ddy*dca)/dsc
        target[idx]=[tcx+tscale*(nx*ca-ny*sa),tcy+tscale*(nx*sa+ny*ca),c]

def normalized_boundary_distance(a,b):
    def norm(kp):
        g=shoulder_geom(kp)
        if g is None: return None
        cx,cy=g["center"]; sc=g["width"]; ca,sa=math.cos(g["angle"]),math.sin(g["angle"]); out={}
        for i in range(13):
            x,y,c=kp[i]
            if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF): continue
            dx,dy=float(x)-cx,float(y)-cy
            out[i]=((dx*ca+dy*sa)/sc,(-dx*sa+dy*ca)/sc)
        return out
    na,nb=norm(a),norm(b)
    if not na or not nb: return 1.0
    ids=set(na)&set(nb)
    if len(ids)<4: return 1.0
    return math.sqrt(statistics.fmean((na[i][0]-nb[i][0])**2+(na[i][1]-nb[i][1])**2 for i in ids))

def face_shape_distance(a,b):
    na,nb=normalize_face(a),normalize_face(b)
    if na is None or nb is None: return 1.0
    ca,cb=na[1],nb[1]; ids=set(ca)&set(cb)&set(range(17,68))
    if len(ids)<12: return 1.0
    return math.sqrt(statistics.fmean((ca[i][0]-cb[i][0])**2+(ca[i][1]-cb[i][1])**2 for i in ids))

def normalized_hand_coords(kp,left):
    elbow,wrist=((7,9) if left else (8,10)); ids=LEFT_HAND if left else RIGHT_HAND
    e,w=kp[elbow],kp[wrist]
    if not all(finite(v) for v in (e[0],e[1],w[0],w[1])): return {}
    vx,vy=float(w[0])-float(e[0]),float(w[1])-float(e[1]); sc=math.hypot(vx,vy)
    if sc<=1e-8: return {}
    ang=math.atan2(vy,vx); ca,sa=math.cos(ang),math.sin(ang); wx,wy=float(w[0]),float(w[1]); out={}
    for rel,idx in enumerate(ids):
        x,y,c=kp[idx]
        if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF): continue
        dx,dy=float(x)-wx,float(y)-wy
        out[rel]=((dx*ca+dy*sa)/sc,(-dx*sa+dy*ca)/sc)
    return out

def hand_shape_distance(a,b):
    vals=[]
    for left in (True,False):
        ca,cb=normalized_hand_coords(a,left),normalized_hand_coords(b,left); ids=set(ca)&set(cb)
        if len(ids)>=6:
            vals.append(math.sqrt(statistics.fmean((ca[i][0]-cb[i][0])**2+(ca[i][1]-cb[i][1])**2 for i in ids)))
    return statistics.fmean(vals) if vals else 1.0

def inframe_ratio(kp,ids,margin=.02):
    good=inside=0
    for i in ids:
        x,y,c=kp[i]
        if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF): continue
        good+=1
        if margin<=float(x)<=1-margin and margin<=float(y)<=1-margin: inside+=1
    return inside/good if good else 0.0

def safe_axis(v,lo,hi):
    if v<0 or v>1: return 0.0
    if lo<=v<=hi: return 1.0
    if v<lo: return clamp(v/max(lo,1e-8),0,1)
    return clamp((1-v)/max(1-hi,1e-8),0,1)

def percentile(xs,q):
    s=sorted(xs)
    if not s:return 0.0
    p=clamp(q,0,1)*(len(s)-1); lo=int(math.floor(p)); hi=int(math.ceil(p))
    return s[lo] if lo==hi else s[lo]*(hi-p)+s[hi]*(p-lo)

def audio_targets(audio:Path|None,duration,windows,ffmpeg):
    if audio is None: return [{"energy":.5,"speech_class":"mixed"} for _ in range(windows)]
    exe=shutil.which(ffmpeg) or ffmpeg
    cmd=[exe,"-hide_banner","-loglevel","error","-i",str(audio),"-t",f"{duration:.6f}","-vn","-ac","1","-ar","16000","-f","f32le","pipe:1"]
    p=subprocess.run(cmd,capture_output=True)
    if p.returncode: raise SystemExit("Audio decode failed: "+p.stderr.decode("utf-8","replace"))
    arr=array.array("f"); arr.frombytes(p.stdout[:len(p.stdout)-len(p.stdout)%4])
    if sys.byteorder!="little": arr.byteswap()
    rms=[]; frame=800
    for i in range(0,len(arr),frame):
        ch=arr[i:i+frame]
        if not ch: break
        rms.append(math.sqrt(sum(float(x)*float(x) for x in ch)/len(ch)))
    if not rms: return [{"energy":0.0,"speech_class":"pause"} for _ in range(windows)]
    lo,hi=percentile(rms,.1),percentile(rms,.9)
    norm=[0 if hi<=lo+1e-12 else clamp((x-lo)/(hi-lo),0,1) for x in rms]
    th=clamp(percentile(norm,.2)+.35*(percentile(norm,.65)-percentile(norm,.2)),.08,.45); out=[]
    for w in range(windows):
        a=int(len(norm)*w/windows); b=int(len(norm)*(w+1)/windows); vals=norm[a:max(a+1,b)]
        energy=statistics.fmean(vals) if vals else 0; ratio=sum(v>=th for v in vals)/len(vals) if vals else 0
        cls="speech" if ratio>=.70 else "pause" if ratio<=.15 else "mixed"
        out.append({"energy":round(energy,6),"speech_class":cls})
    return out

def candidate_score(u,role,target,target_duration):
    rr=u["roles"][role]; q=float(rr["weight"])
    energy=float((u.get("prosody") or {}).get("energy_norm_mean") or 0)
    e=1-abs(energy-float(target["energy"])); cls=(u.get("speech") or {}).get("class")
    s=1.0 if cls==target["speech_class"] else .55 if {cls,target["speech_class"]}=={"speech","mixed"} else .25
    tr=u.get("transition") or {}; ts=(float(tr.get("entry_score") or 0)+float(tr.get("exit_score") or 0))/2
    d=1-min(1,abs(float(u["duration_s"])-target_duration)/max(target_duration,1e-6))
    return .45*q+.25*e+.15*s+.10*ts+.05*d

def enabled_candidates(units,role,source,target,target_duration):
    out=[]
    for u in units:
        if u["source_key"]!=source: continue
        rr=(u.get("roles") or {}).get(role) or {}
        if rr.get("enabled"): out.append((candidate_score(u,role,target,target_duration),u))
    return sorted(out,key=lambda x:x[0],reverse=True)

def unit_pose(u,alpha,track_for):
    t=float(u["source_start_s"])+clamp(alpha,0,1)*(float(u["source_end_s"])-float(u["source_start_s"]))
    return sample_track(track_for(u),t)

def base_framing(u,track_for):
    vals=[]
    for a in (0,.25,.5,.75,1):
        kp=unit_pose(u,a,track_for); body=inframe_ratio(kp,range(5,13),.015); wrists=[]
        for i in (9,10):
            x,y,c=kp[i]
            if finite(x) and finite(y) and finite(c) and float(c)>=CONF:
                wrists.append(safe_axis(float(x),.05,.95)*safe_axis(float(y),.05,.82))
        vals.append(.55*body+.45*(statistics.fmean(wrists) if wrists else 0.0))
    return statistics.fmean(vals)

def retargeted_hand_framing(base_u,hand_u,base_align,track_for):
    vals=[]
    for a in (0,.25,.5,.75,1):
        base=unit_pose(base_u,a,track_for)
        if base_align is not None: base=apply_similarity(base,base_align)
        donor=unit_pose(hand_u,a,track_for)
        hand_retarget(donor,base,True); hand_retarget(donor,base,False)
        vals.append(inframe_ratio(base,LEFT_HAND+RIGHT_HAND,.015))
    return statistics.fmean(vals)

def top_scored(cands,n,extra=None):
    scored=[]
    for raw,u in cands:
        ex=extra(u) if extra else 1.0
        scored.append((.75*raw+.25*ex,u,raw,ex))
    return sorted(scored,key=lambda x:x[0],reverse=True)[:n]

def select_base_pair(units,targets,seg_d,blend,track_for):
    overlap_start=seg_d-blend; alpha_a=overlap_start/seg_d
    options=[]
    for order in (("primary","tertiary"),("tertiary","primary")):
        lists=[]
        for i,src in enumerate(order):
            c=enabled_candidates(units,"posture",src,targets[i],seg_d)
            lists.append(top_scored(c,14,lambda u:base_framing(u,track_for)))
        for s0,u0,raw0,fr0 in lists[0]:
            p0=unit_pose(u0,alpha_a,track_for)
            for s1,u1,raw1,fr1 in lists[1]:
                p1=unit_pose(u1,0,track_for)
                dist=normalized_boundary_distance(p0,p1); cont=1/(1+5*dist)
                score=.55*((s0+s1)/2)+.45*cont
                options.append((score,cont,order,(s0,u0,raw0,fr0),(s1,u1,raw1,fr1)))
    options.sort(key=lambda x:x[0],reverse=True)
    return options[0]

def select_face_pair(units,targets,seg_d,blend,track_for):
    alpha_a=(seg_d-blend)/seg_d
    c0=enabled_candidates(units,"face","secondary",targets[0],seg_d)[:18]
    c1=enabled_candidates(units,"face","secondary",targets[1],seg_d)[:18]
    best=None
    for s0,u0 in c0:
        a=unit_pose(u0,alpha_a,track_for)
        for s1,u1 in c1:
            if u0["library_unit_id"]==u1["library_unit_id"]: continue
            b=unit_pose(u1,0,track_for); d=face_shape_distance(a,b); cont=1/(1+4*d)
            score=.68*((s0+s1)/2)+.32*cont
            rec=(score,cont,(s0,u0),(s1,u1))
            if best is None or rec[0]>best[0]: best=rec
    if best is None: raise SystemExit("No face pair")
    return best

def select_hand_pair(units,targets,seg_d,blend,base_pair,base_align,track_for):
    alpha_a=(seg_d-blend)/seg_d
    c0=enabled_candidates(units,"both_hands","primary",targets[0],seg_d)[:24]
    c1=enabled_candidates(units,"both_hands","primary",targets[1],seg_d)[:24]
    b0=base_pair[0]; b1=base_pair[1]; best=None; frame_cache={}
    def fr(base,hand,align):
        key=(base["library_unit_id"],hand["library_unit_id"],bool(align))
        if key not in frame_cache: frame_cache[key]=retargeted_hand_framing(base,hand,align,track_for)
        return frame_cache[key]
    for s0,u0 in c0:
        f0=fr(b0,u0,None)
        for s1,u1 in c1:
            if u0["library_unit_id"]==u1["library_unit_id"]: continue
            f1=fr(b1,u1,base_align); a=unit_pose(u0,alpha_a,track_for); b=unit_pose(u1,0,track_for)
            d=hand_shape_distance(a,b); cont=1/(1+2.5*d); framing=(f0+f1)/2
            score=.42*((s0+s1)/2)+.38*framing+.20*cont
            rec=(score,cont,framing,(s0,u0,f0),(s1,u1,f1))
            if best is None or rec[0]>best[0]: best=rec
    if best is None: raise SystemExit("No hand pair")
    return best

def draw_preview(frames,output:Path,fps,width=540,height=960):
    try:
        import cv2, numpy as np
    except Exception as exc: raise SystemExit(f"OpenCV/NumPy required: {exc}")
    output.parent.mkdir(parents=True,exist_ok=True)
    vw=cv2.VideoWriter(str(output),cv2.VideoWriter_fourcc(*"mp4v"),fps,(width,height))
    if not vw.isOpened(): raise SystemExit(f"Could not open preview writer: {output}")
    for rec in frames:
        img=np.zeros((height,width,3),dtype=np.uint8); kp=rec["keypoints"]
        def pt(i):
            x,y,c=kp[i]
            if not (finite(x) and finite(y) and finite(c) and float(c)>=.05): return None
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
        cv2.putText(img,f"t={rec['t']:.2f}s  base={rec['provenance']['base_unit'].split(':')[-1]}",(12,28),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1,cv2.LINE_AA)
        vw.write(img)
    vw.release()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--library",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--audio",type=Path); ap.add_argument("--duration",type=float,default=4.5); ap.add_argument("--fps",type=float,default=24.0)
    ap.add_argument("--blend-duration",type=float,default=.75); ap.add_argument("--ffmpeg",default="ffmpeg")
    args=ap.parse_args()
    if not (4<=args.duration<=5): raise SystemExit("--duration must be 4..5 s")
    if not (.5<=args.blend_duration<=1.0): raise SystemExit("--blend-duration must be 0.5..1.0 s")
    lib=load_json(args.library)
    if lib.get("schema")!="joao-motion-library/v1": raise SystemExit("Unexpected library schema")
    if args.audio is not None and not args.audio.is_file(): raise SystemExit(f"Audio missing: {args.audio}")
    units=lib.get("units") or []; targets=audio_targets(args.audio,args.duration,2,args.ffmpeg)
    seg_d=(args.duration+args.blend_duration)/2; overlap_start=seg_d-args.blend_duration; overlap_end=seg_d

    cache={}
    def track_for(u):
        p=Path(u["pose_track"])
        if p not in cache: cache[p]=load_pose(p)
        return cache[p]

    bp=select_base_pair(units,targets,seg_d,args.blend_duration,track_for)
    _,base_cont,order,b0rec,b1rec=bp; b0,b1=b0rec[1],b1rec[1]
    b0_at_overlap=unit_pose(b0,overlap_start/seg_d,track_for); b1_start=unit_pose(b1,0,track_for)
    base_align=similarity(b1_start,b0_at_overlap)

    fp=select_face_pair(units,targets,seg_d,args.blend_duration,track_for)
    _,face_cont,f0rec,f1rec=fp; f0,f1=f0rec[1],f1rec[1]
    hp=select_hand_pair(units,targets,seg_d,args.blend_duration,(b0,b1),base_align,track_for)
    _,hand_cont,hand_framing,h0rec,h1rec=hp; h0,h1=h0rec[1],h1rec[1]

    plan={
      "schema":"behavioral-pose-driver-plan/v2","duration_s":args.duration,"fps":args.fps,
      "transition_blend_s":args.blend_duration,"segment_duration_s":seg_d,
      "overlap_start_s":overlap_start,"overlap_end_s":overlap_end,
      "target_audio":str(args.audio.resolve()) if args.audio else None,"target_windows":targets,
      "base_source_order":list(order),"base_boundary_continuity":round(base_cont,6),
      "face_pair_continuity":round(face_cont,6),"hand_pair_continuity":round(hand_cont,6),
      "predicted_hand_inframe_ratio":round(hand_framing,6),"windows":[]
    }
    for i,(bu,hu,fu,brec,hrec,frec) in enumerate(((b0,h0,f0,b0rec,h0rec,f0rec),(b1,h1,f1,b1rec,h1rec,f1rec))):
        plan["windows"].append({
          "index":i,"target":targets[i],
          "base":{"unit":bu["library_unit_id"],"retrieval_score":round(brec[2],6),"base_framing":round(brec[3],6)},
          "hands":{"unit":hu["library_unit_id"],"retrieval_score":round(hrec[0],6),"predicted_inframe":round(hrec[2],6)},
          "face":{"unit":fu["library_unit_id"],"retrieval_score":round(frec[0],6)}
        })

    def compose(bu,hu,fu,progress,align=None):
        base=unit_pose(bu,progress,track_for)
        if align is not None: base=apply_similarity(base,align)
        donor=unit_pose(hu,progress,track_for); hand_retarget(donor,base,True); hand_retarget(donor,base,False)
        face=unit_pose(fu,progress,track_for); face_ref=unit_pose(fu,0,track_for); transfer_face_and_head(face,face_ref,base)
        return base

    frames=[]; count=int(round(args.duration*args.fps))
    for fi in range(count):
        t=fi/args.fps
        p0=clamp(t/seg_d,0,1); p1=clamp((t-overlap_start)/seg_d,0,1)
        if t<overlap_start:
            pose=compose(b0,h0,f0,p0,None); base_unit=b0
        elif t>overlap_end:
            pose=compose(b1,h1,f1,p1,base_align); base_unit=b1
        else:
            a=compose(b0,h0,f0,p0,None); b=compose(b1,h1,f1,p1,base_align)
            beta=smooth5((t-overlap_start)/args.blend_duration); pose=blend_pose(a,b,beta)
            base_unit=b0 if beta<.5 else b1
        prov={"base_unit":base_unit["library_unit_id"],
              "base_pair":[b0["library_unit_id"],b1["library_unit_id"]],
              "hand_pair":[h0["library_unit_id"],h1["library_unit_id"]],
              "face_pair":[f0["library_unit_id"],f1["library_unit_id"]],
              "transition_overlap":overlap_start<=t<=overlap_end}
        frames.append({"t":round(t,6),"schema":"coco_wholebody_133","keypoints":pose,"provenance":prov})

    args.output_dir.mkdir(parents=True,exist_ok=True)
    plan_path=args.output_dir/"driver_plan.json"; track_path=args.output_dir/"behavioral_driver_coco133.jsonl"; preview=args.output_dir/"behavioral_driver_pose_preview.mp4"
    plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    with track_path.open("w",encoding="utf-8",newline="\n") as fh:
        for r in frames: fh.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
    draw_preview(frames,preview,args.fps)

    print("MULTI-SOURCE BEHAVIORAL POSE DRIVER v2")
    print("======================================")
    print(f"Duration: {args.duration}s / fps={args.fps} / frames={len(frames)}")
    print(f"Base source order: {order[0]} -> {order[1]}")
    print(f"Overlap: {overlap_start:.3f}-{overlap_end:.3f}s / blend={args.blend_duration:.3f}s")
    print(f"Base continuity: {base_cont:.6f}")
    print(f"Face pair continuity: {face_cont:.6f}")
    print(f"Hand pair continuity: {hand_cont:.6f}")
    print(f"Predicted retargeted-hand in-frame ratio: {hand_framing:.6f}")
    for w in plan["windows"]:
        print(f"Window {w['index']}: base={w['base']['unit']} hands={w['hands']['unit']} face={w['face']['unit']}")
        print(f"  framing base={w['base']['base_framing']} hands={w['hands']['predicted_inframe']}")
    print(f"Plan: {plan_path}"); print(f"Pose track: {track_path}"); print(f"Preview: {preview}")
    print("Wan-Animate-2: NOT INVOKED")
    return 0
if __name__=="__main__": raise SystemExit(main())
