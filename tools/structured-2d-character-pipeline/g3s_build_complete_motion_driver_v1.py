#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

W, H, FPS, PLAYABLE = 384, 576, 16, 16
BG=(82,78,76); SKIN=(148,88,58); HAIR=(18,17,18); HAIR_HI=(35,31,31)
CLOTH=(159,143,115); CLOTH_DARK=(111,96,76); METAL=(61,65,66); OUTLINE=(31,27,25)


def fail(msg): raise RuntimeError(msg)
def read_json(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def lerp(a,b,t): return a+(b-a)*t


def sample_cycle(frames, si):
    phase=(si%PLAYABLE)*(len(frames)/PLAYABLE)
    i0=int(math.floor(phase))%len(frames); i1=(i0+1)%len(frames); t=phase-math.floor(phase)
    joints={}
    for n,a in frames[i0]["joints"].items():
        b=frames[i1]["joints"][n]
        joints[n]={"x":lerp(float(a["x"]),float(b["x"]),t),"y":lerp(float(a["y"]),float(b["y"]),t)}
    return joints,phase


def map_pose(joints, scale):
    pelvis_x=(float(joints["left_hip"]["x"])+float(joints["right_hip"]["x"]))*0.5
    foot_y=max(float(joints["left_ankle"]["y"]),float(joints["right_ankle"]["y"]))
    return {n:(192+(float(r["x"])-pelvis_x)*scale,526+(float(r["y"])-foot_y)*scale) for n,r in joints.items()}


def circle(d,p,r,fill,width=2):
    x,y=p; d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=OUTLINE,width=width)


def thick(d,pts,fill,width):
    d.line(pts,fill=OUTLINE,width=width+5,joint="curve"); d.line(pts,fill=fill,width=width,joint="curve")


def chain(d,anchor,phase,length,links,direction,lag):
    ax,ay=anchor; prev=(ax,ay)
    for i in range(1,links+1):
        u=i/links
        angle=direction+0.22*math.sin(phase*math.pi*2/8+i*0.55)+lag*u
        p=(ax+math.cos(angle)*length*u, ay+math.sin(angle)*length*u+4*math.sin(i*0.9+phase))
        d.line((prev,p),fill=OUTLINE,width=7); d.line((prev,p),fill=METAL,width=3); circle(d,p,4,METAL,2); prev=p


def draw_proxy(m,phase,fi):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    theta=2*math.pi*(fi%PLAYABLE)/PLAYABLE
    lag_x=12*math.sin(theta-0.7); lag_y=5*math.sin(theta*2-0.25); cloth_lag=10*math.sin(theta-1.0); jiggle=3*math.sin(theta*2-0.9)
    head=m["head"]; neck=m["neck"]; ls=m["left_shoulder"]; rs=m["right_shoulder"]; lh=m["left_hip"]; rh=m["right_hip"]
    pelvis=((lh[0]+rh[0])*0.5,(lh[1]+rh[1])*0.5); hx,hy=head; px,py=pelvis

    hair=[(hx-54+lag_x*.4,hy-19),(hx+48+lag_x*.2,hy-14),(max(ls[0],rs[0])+45+lag_x*.8,neck[1]+60),
          (px+44+lag_x,py+110+lag_y),(px-32+lag_x*.7,py+125+lag_y),(min(ls[0],rs[0])-44+lag_x*.5,neck[1]+78)]
    d.polygon(hair,fill=HAIR,outline=OUTLINE)
    for k in range(7):
        s=-1 if k%2==0 else 1
        d.line((hx+s*(20+(k%3)*9),hy+8+k*5,px+s*(26+k*3)+lag_x*(.6+.08*k),py+88+k*7+lag_y),fill=HAIR_HI,width=8)

    d.polygon([(ls[0],ls[1]),(rs[0],rs[1]),(rh[0]+8,rh[1]),(lh[0]-8,lh[1])],fill=SKIN,outline=OUTLINE)
    circle(d,head,22,SKIN); thick(d,[neck,head],SKIN,18)
    for side in ("left","right"):
        thick(d,[m[f"{side}_shoulder"],m[f"{side}_elbow"],m[f"{side}_wrist"]],SKIN,20)
        circle(d,m[f"{side}_elbow"],10,SKIN); circle(d,m[f"{side}_wrist"],9,SKIN)
        thick(d,[m[f"{side}_hip"],m[f"{side}_knee"],m[f"{side}_ankle"]],SKIN,29)
        circle(d,m[f"{side}_knee"],14,SKIN); circle(d,m[f"{side}_ankle"],11,SKIN); thick(d,[m[f"{side}_ankle"],m[f"{side}_toe"]],SKIN,16)

    x0,x1=sorted([ls[0],rs[0]]); chest_y=(ls[1]+rs[1])*.5+28+jiggle
    d.rounded_rectangle((x0-10,chest_y-13,x1+12,chest_y+14),radius=7,fill=CLOTH,outline=OUTLINE,width=3)
    wrap=[(lh[0]-15,lh[1]-5),(rh[0]+17,rh[1]-3),(rh[0]+26+cloth_lag*.35,py+65),(px+cloth_lag,py+112+lag_y),(lh[0]-25+cloth_lag*.25,py+67)]
    d.polygon(wrap,fill=CLOTH,outline=OUTLINE)
    for off,length in [(-35,88),(-14,116),(8,104),(28,82)]:
        top=(px+off,py+46); tip=(px+off+cloth_lag*(.65+abs(off)/100),py+length+18+lag_y)
        d.polygon([(top[0]-9,top[1]),(top[0]+9,top[1]),(tip[0]+5,tip[1]),(tip[0]-5,tip[1])],fill=CLOTH_DARK,outline=OUTLINE)
    for s in (-1,1):
        d.line((hx+s*18,hy+12,px+s*33+lag_x*.45,py+46+lag_y*.35),fill=OUTLINE,width=13)
        d.line((hx+s*18,hy+12,px+s*33+lag_x*.45,py+46+lag_y*.35),fill=HAIR,width=9)

    # The master exposes the broken chain loadout on screen-left in the current
    # reference. For this control-only proxy, follow that visible side rather than
    # inventing an anatomical-side canon that the character docs do not specify.
    wrist=min((m["left_wrist"],m["right_wrist"]),key=lambda p:p[0])
    ankle=min((m["left_ankle"],m["right_ankle"]),key=lambda p:p[0])
    circle(d,wrist,13,METAL,4); circle(d,ankle,15,METAL,4)
    chain(d,wrist,phase,78,6,1.74,.18*math.sin(theta-.6)); chain(d,ankle,phase,88,7,2.90,.24*math.sin(theta-.9))
    return im


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--guide",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    guide_path=Path(a.guide).resolve(); out=Path(a.output).resolve()
    if not guide_path.is_file(): fail(f"guide missing: {guide_path}")
    guide=read_json(guide_path); frames=guide.get("frames",[])
    if len(frames)!=8: fail(f"expected eight source gait states, got {len(frames)}")
    if abs(float(guide.get("camera",{}).get("azimuth_from_motion_heading_deg",-1))-72)>0.01: fail("complete-motion driver requires locked 72-degree guide")
    ys=[float(f["joints"][n]["y"]) for f in frames for n in ("head","left_ankle","right_ankle")]; raw=max(ys)-min(ys)
    if raw<=1: fail("invalid projected source height")
    scale=438/raw; fd=out/"frames"; fd.mkdir(parents=True,exist_ok=True); seq=[]; rec=[]
    for i in range(PLAYABLE):
        j,phase=sample_cycle(frames,i); im=draw_proxy(map_pose(j,scale),phase,i); p=fd/f"frame_{i:03d}.png"; im.save(p); seq.append(im); rec.append({"index":i,"phase":phase,"path":str(p)})
    close=fd/"frame_016.png"; seq[0].save(close); rec.append({"index":16,"phase":8.0,"path":str(close),"closure_duplicate":True})
    sheet=Image.new("RGB",(W*5,H*4),BG)
    for i,im in enumerate(seq+[seq[0]]): sheet.paste(im,((i%5)*W,(i//5)*H))
    sp=out/"complete_motion_driver_contact_sheet.png"; sheet.save(sp)
    gp=out/"complete_motion_driver_preview.gif"; q=seq+[seq[0]]; q[0].save(gp,save_all=True,append_images=q[1:],duration=round(1000/FPS),loop=0,disposal=2,optimize=False)
    marker={"gate":"G3S_COMPLETE_MOTION_DRIVER_V1","status":"PASS_DRIVER_FRAMES_READY","source_guide":str(guide_path),"canvas":[W,H],"fps":FPS,"frame_count":17,"playable_frame_count":16,"closing_frame_duplicates_first":True,"driver_only_not_game_art":True,"secondary_motion_controls":["rear/front hair lag","hip-wrap cloth lag","chest soft lag","master-visible wrist broken chain","master-visible ankle broken chain"],"frames":rec,"contact_sheet":str(sp),"preview_gif":str(gp)}
    mp=out/"complete_motion_driver.json"; mp.write_text(json.dumps(marker,indent=2)+"\n",encoding="utf-8")
    print("G3S-COMPLETE-MOTION-DRIVER: PASS_DRIVER_FRAMES_READY"); print(f"FRAMES: {fd}"); print(f"SHEET:  {sp}"); print(f"GIF:    {gp}"); print(f"MARKER: {mp}")
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as exc: print(f"G3S-COMPLETE-MOTION-DRIVER: FAIL - {exc}"); raise SystemExit(1)
