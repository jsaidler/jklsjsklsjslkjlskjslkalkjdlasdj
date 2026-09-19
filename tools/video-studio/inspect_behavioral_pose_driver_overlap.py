#!/usr/bin/env python3
"""Numeric QA for overlap-based synthesized behavioral pose drivers.

No inference and no automatic pass/fail threshold. For v2 plans, the transition
interval is read directly from overlap_start_s / overlap_end_s.
"""
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path

CONF=.20
GROUPS={"body_head":list(range(0,13)),"face":list(range(23,91)),"left_hand":list(range(91,112)),"right_hand":list(range(112,133))}
OOB_GROUPS={"coarse_head":list(range(0,5)),"upper_body":list(range(5,13)),"lower_body_foot":list(range(13,23)),"face":list(range(23,91)),"left_hand":list(range(91,112)),"right_hand":list(range(112,133))}
LIMBS={"left_upper_arm":(5,7),"left_forearm":(7,9),"right_upper_arm":(6,8),"right_forearm":(8,10)}

def finite(v): return v is not None and math.isfinite(float(v))
def pct(vals,q):
    s=sorted(float(v) for v in vals if finite(v))
    if not s:return None
    p=max(0,min(1,q))*(len(s)-1); lo=int(math.floor(p)); hi=int(math.ceil(p))
    return s[lo] if lo==hi else s[lo]*(hi-p)+s[hi]*(p-lo)
def quant(vals):
    s=[float(v) for v in vals if finite(v)]
    return {"q10":pct(s,.1),"median":pct(s,.5),"q90":pct(s,.9),"max":max(s) if s else None}
def load_track(path):
    rows=[]
    for n,line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(),1):
        if not line.strip():continue
        r=json.loads(line)
        if r.get("schema")!="coco_wholebody_133" or len(r.get("keypoints") or [])!=133: raise SystemExit(f"Invalid pose row line {n}")
        rows.append(r)
    if len(rows)<2:raise SystemExit("Need at least two frames")
    return rows
def shoulder(kp):
    a,b=kp[5],kp[6]
    if not all(finite(v) for v in (*a[:3],*b[:3])) or float(a[2])<CONF or float(b[2])<CONF:return None
    return math.hypot(float(a[0])-float(b[0]),float(a[1])-float(b[1]))
def group_jump(a,b,ids):
    scales=[x for x in (shoulder(a),shoulder(b)) if x and x>1e-8]
    if not scales:return None
    ds=[]
    for i in ids:
        pa,pb=a[i],b[i]
        if not all(finite(v) for v in (*pa[:3],*pb[:3])) or float(pa[2])<CONF or float(pb[2])<CONF:continue
        dx=float(pb[0])-float(pa[0]); dy=float(pb[1])-float(pa[1]); ds.append(dx*dx+dy*dy)
    if len(ds)<2:return None
    return math.sqrt(statistics.fmean(ds))/statistics.fmean(scales)
def pair_dist(kp,a,b):
    pa,pb=kp[a],kp[b]
    if not all(finite(v) for v in (*pa[:3],*pb[:3])) or float(pa[2])<CONF or float(pb[2])<CONF:return None
    return math.hypot(float(pa[0])-float(pb[0]),float(pa[1])-float(pb[1]))
def mean_xy(kp,ids):
    pts=[]
    for i in ids:
        x,y,c=kp[i]
        if finite(x) and finite(y) and finite(c) and float(c)>=CONF:pts.append((float(x),float(y)))
    if len(pts)<2:return None
    return statistics.fmean(x for x,_ in pts),statistics.fmean(y for _,y in pts)
def intereye(kp):
    a=mean_xy(kp,range(59,65)); b=mean_xy(kp,range(65,71))
    return None if a is None or b is None else math.hypot(b[0]-a[0],b[1]-a[1])
def oob_stats(frames,ids=None):
    bad=tot=0
    for r in frames:
        kp=r["keypoints"]
        for i in (ids if ids is not None else range(133)):
            x,y,c=kp[i]
            if not (finite(x) and finite(y) and finite(c) and float(c)>=CONF):continue
            tot+=1
            if float(x)<0 or float(x)>1 or float(y)<0 or float(y)>1:bad+=1
    return {"count":bad,"considered":tot,"ratio":bad/tot if tot else 0.0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--track",type=Path,required=True); ap.add_argument("--plan",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    frames=load_track(args.track); plan=json.loads(args.plan.read_text(encoding="utf-8-sig"))
    fps=float(plan.get("fps") or 0); start=float(plan.get("overlap_start_s")); end=float(plan.get("overlap_end_s"))
    if fps<=0 or not (end>start):raise SystemExit("Plan lacks valid fps/overlap interval")
    times=[float(r["t"]) for r in frames]
    trans_pairs=set(i for i in range(1,len(times)) if times[i]>=start-1e-9 and times[i]<=end+1e-9)
    jumps={g:[] for g in GROUPS}; normal={g:[] for g in GROUPS}; trans={g:[] for g in GROUPS}
    for i in range(1,len(frames)):
        a,b=frames[i-1]["keypoints"],frames[i]["keypoints"]
        for g,ids in GROUPS.items():
            v=group_jump(a,b,ids)
            if v is None:continue
            jumps[g].append(v); (trans[g] if i in trans_pairs else normal[g]).append(v)
    cont={}
    for g in GROUPS:
        nq,tq=quant(normal[g]),quant(trans[g]); q=nq["q90"]
        cont[g]={"nontransition":nq,"transition":tq,
                 "transition_q90_to_nontransition_q90":(tq["q90"]/q if tq["q90"] is not None and q and q>1e-12 else None),
                 "transition_max_to_nontransition_q90":(tq["max"]/q if tq["max"] is not None and q and q>1e-12 else None)}
    oob={g:oob_stats(frames,ids) for g,ids in OOB_GROUPS.items()}
    transition_frames=[frames[i] for i in range(len(frames)) if start<=times[i]<=end]
    oob_trans={g:oob_stats(transition_frames,ids) for g,ids in OOB_GROUPS.items()}
    limb={k:[] for k in LIMBS}; eye=[]; rootL=[]; rootR=[]
    for r in frames:
        kp=r["keypoints"]; sw=shoulder(kp)
        if not sw or sw<=1e-8:continue
        for k,(a,b) in LIMBS.items():
            d=pair_dist(kp,a,b)
            if d is not None:limb[k].append(d/sw)
        e=intereye(kp)
        if e is not None:eye.append(e/sw)
        dl=pair_dist(kp,9,91); dr=pair_dist(kp,10,112)
        if dl is not None:rootL.append(dl/sw)
        if dr is not None:rootR.append(dr/sw)
    result={"schema":"behavioral-pose-driver-overlap-qa/v1","frames":len(frames),"fps":fps,"duration_s":float(plan.get("duration_s") or 0),
            "plan_schema":plan.get("schema"),"base_source_order":plan.get("base_source_order"),
            "transition_interval_s":[start,end],"transition_duration_s":end-start,
            "planner":{"base_continuity":plan.get("base_boundary_continuity"),"face_continuity":plan.get("face_pair_continuity"),
                       "hand_continuity":plan.get("hand_pair_continuity"),"predicted_hand_inframe_ratio":plan.get("predicted_hand_inframe_ratio")},
            "continuity":cont,"oob_by_group":oob,"oob_during_transition_by_group":oob_trans,
            "geometry":{"limb_length_over_shoulder":{k:quant(v) for k,v in limb.items()},"intereye_over_shoulder":quant(eye),
                        "left_hand_root_to_wrist_over_shoulder":quant(rootL),"right_hand_root_to_wrist_over_shoulder":quant(rootR)}}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("BEHAVIORAL POSE DRIVER v2 NUMERIC QA")
    print("====================================")
    print(f"Frames: {len(frames)} / fps={fps} / duration={result['duration_s']} s")
    print(f"Plan schema: {result['plan_schema']}")
    print(f"Base source order: {result['base_source_order']}")
    print(f"Transition overlap: {start:.3f}-{end:.3f}s ({end-start:.3f}s)")
    print(f"Planner: {result['planner']}")
    print("Confidence-qualified OOB by group:")
    for g,s in oob.items():print(f"  {g}: {s['count']}/{s['considered']} ({s['ratio']:.6f})")
    print("Transition continuity vs non-transition q90:")
    for g,c in cont.items():
        print(f"  {g}: normal q90={c['nontransition']['q90']} transition q90/max={c['transition']['q90']}/{c['transition']['max']} q90-ratio={c['transition_q90_to_nontransition_q90']} max-ratio={c['transition_max_to_nontransition_q90']}")
    print("Transition-only OOB by group:")
    for g,s in oob_trans.items():print(f"  {g}: {s['count']}/{s['considered']} ({s['ratio']:.6f})")
    print(f"Left hand-root/wrist: {result['geometry']['left_hand_root_to_wrist_over_shoulder']}")
    print(f"Right hand-root/wrist: {result['geometry']['right_hand_root_to_wrist_over_shoulder']}")
    print(f"JSON: {args.output}")
    return 0
if __name__=="__main__":raise SystemExit(main())
