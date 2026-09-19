#!/usr/bin/env python3
"""Local Video Studio behavior-profile / motion-unit extractor v1.

Stdlib + ffmpeg only. It can inspect segmentation without pose, but a profile is
"complete" only when a normalized pose JSONL track is supplied.

Pose JSONL line:
{"t": 1.234, "schema": "coco_wholebody_133", "keypoints": [[x,y,score], ...]}
Coordinates must be normalized to [0,1].
"""

from __future__ import annotations
import argparse, array, csv, json, math, shutil, statistics, subprocess, sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

SOURCE = Path(r"Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4")
OUT = Path(r"Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885")
FPS, W, H = 6.0, 128, 72
ARATE, A_MS = 16000, 50
MIN_U, TARGET_U, MAX_U, STEP = .8, 2.2, 3.8, .1
CONF = .20

class Error(RuntimeError): pass

@dataclass(frozen=True)
class TV:
    t: float
    v: float

@dataclass(frozen=True)
class PF:
    t: float
    schema: str
    kp: tuple[tuple[float|None,float|None,float|None], ...]

def exe(name: str) -> str:
    p = Path(name)
    if p.is_file(): return str(p)
    found = shutil.which(name)
    if not found: raise Error(f"Executable not found: {name}")
    return found

def pct(xs: Sequence[float], q: float) -> float:
    if not xs: return 0.0
    s = sorted(xs); p = max(0,min(1,q))*(len(s)-1); lo=int(p); hi=math.ceil(p)
    return s[lo] if lo==hi else s[lo]*(hi-p)+s[hi]*(p-lo)

def norm(xs: Sequence[float]) -> list[float]:
    lo, hi = pct(xs,.10), pct(xs,.90)
    if hi <= lo+1e-12: return [0.0]*len(xs)
    return [max(0,min(1,(x-lo)/(hi-lo))) for x in xs]

def exe_probe(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd,capture_output=True,text=True)

def probe(src: Path, ffprobe: str) -> dict[str,Any]:
    r = exe_probe([ffprobe,"-v","error","-show_streams","-show_format","-of","json",str(src)])
    if r.returncode: raise Error(r.stderr.strip())
    j=json.loads(r.stdout); vs=[s for s in j["streams"] if s.get("codec_type")=="video"]
    aud=[s for s in j["streams"] if s.get("codec_type")=="audio"]
    if not vs: raise Error("No video stream.")
    v=vs[0]; d=j.get("format",{}).get("duration") or v.get("duration")
    return {"path":str(src),"file":src.name,"duration_s":float(d),"width":int(v["width"]),
            "height":int(v["height"]),"video_codec":str(v.get("codec_name","")),"has_audio":bool(aud)}

def readn(stream, n: int) -> bytes:
    chunks=[]; left=n
    while left:
        b=stream.read(left)
        if not b: break
        chunks.append(b); left-=len(b)
    return b"".join(chunks)

def motion(src: Path, ffmpeg: str) -> list[TV]:
    fs=W*H
    cmd=[ffmpeg,"-hide_banner","-loglevel","error","-i",str(src),"-an","-vf",
         f"fps={FPS},scale={W}:{H}:flags=area,format=gray","-f","rawvideo","-pix_fmt","gray","pipe:1"]
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE); assert p.stdout
    raw=[]; prev=None
    while True:
        b=readn(p.stdout,fs)
        if len(b)!=fs: break
        raw.append(0.0 if prev is None else sum(abs(a-c) for a,c in zip(b,prev))/(fs*255.0))
        prev=b
    p.stdout.close(); err=p.stderr.read() if p.stderr else b""; rc=p.wait()
    if rc: raise Error("ffmpeg motion decode failed: "+err.decode("utf-8","replace"))
    return [TV(i/FPS,v) for i,v in enumerate(norm(raw))]

def audio(src: Path, ffmpeg: str) -> tuple[list[TV],list[TV]]:
    ns=max(1,int(ARATE*A_MS/1000)); size=ns*4
    cmd=[ffmpeg,"-hide_banner","-loglevel","error","-i",str(src),"-vn","-ac","1","-ar",str(ARATE),
         "-f","f32le","pipe:1"]
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE); assert p.stdout
    rms=[]
    while True:
        b=readn(p.stdout,size)
        if not b: break
        usable=len(b)-len(b)%4
        a=array.array("f"); a.frombytes(b[:usable])
        if sys.byteorder!="little": a.byteswap()
        if not a: break
        rms.append(math.sqrt(sum(float(x)*float(x) for x in a)/len(a)))
        if len(b)<size: break
    p.stdout.close(); err=p.stderr.read() if p.stderr else b""; rc=p.wait()
    if rc: raise Error("ffmpeg audio decode failed: "+err.decode("utf-8","replace"))
    dt=A_MS/1000
    return ([TV(i*dt,v) for i,v in enumerate(norm(rms))],
            [TV(i*dt,20*math.log10(max(v,1e-12))) for i,v in enumerate(rms)])

def near(xs: Sequence[TV], t: float) -> float:
    if not xs: return 0.0
    dt=xs[1].t-xs[0].t if len(xs)>1 else 1.0
    return xs[max(0,min(len(xs)-1,round(t/max(dt,1e-9))))].v

def span(xs: Sequence[TV], a: float, b: float) -> list[float]:
    return [x.v for x in xs if a<=x.t<b]

def speech_threshold(a: Sequence[TV]) -> float:
    v=[x.v for x in a]
    return max(.08,min(.45,pct(v,.20)+.35*(pct(v,.65)-pct(v,.20)))) if v else 1.0

def pause_len(a: Sequence[TV], t: float, th: float, direction: int) -> float:
    if not a: return 0.0
    dt=a[1].t-a[0].t if len(a)>1 else A_MS/1000
    i=max(0,min(len(a)-1,round(t/max(dt,1e-9)))); total=0.0
    while 0<=i<len(a) and total<1.5 and a[i].v<th:
        total+=dt; i+=direction
    return min(1.5,total)

def score_boundary(t: float, target: float, m: Sequence[TV], a: Sequence[TV], th: float) -> tuple[float,str]:
    mv,av=near(m,t),near(a,t); paused=av<th
    score=.45*(1-av)+.35*(1-mv)+.15*(1 if paused else 0)+.05*max(0,1-abs(t-target)/TARGET_U)
    return max(0,min(1,score)), ("pause+low_motion" if paused and mv<=.35 else "pause" if paused else "low_motion")

def boundaries(d: float, m: Sequence[TV], a: Sequence[TV], th: float) -> list[tuple[float,str,float]]:
    out=[(0.0,"source_start",1.0)]; start=0.0
    while d-start>MAX_U:
        target=min(d,start+TARGET_U); t=start+MIN_U; cand=[]
        while t<=min(d,start+MAX_U)+1e-9:
            s,r=score_boundary(t,target,m,a,th); cand.append((s,-abs(t-target),t,r)); t+=STEP
        s,_,cut,r=max(cand)
        cut=round(cut,3); out.append((cut,r,s)); start=cut
    if out[-1][0]<d: out.append((round(d,3),"source_end",1.0))
    return out

def load_pose(path: Path) -> list[PF]:
    out=[]
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip(): continue
        j=json.loads(line); pts=[]
        for k in j["keypoints"]: pts.append(tuple(None if x is None else float(x) for x in k[:3]))
        out.append(PF(float(j["t"]),str(j.get("schema") or "unknown"),tuple(pts)))
    if not out: raise Error(f"Empty pose track: {path}")
    return sorted(out,key=lambda x:x.t)

def nearest_pose(fs: Sequence[PF], t: float) -> PF|None:
    return min(fs,key=lambda f:abs(f.t-t)) if fs else None

def mean_xy(f: PF, ids: Sequence[int]) -> tuple[float,float]|None:
    pts=[]
    for i in ids:
        if i>=len(f.kp): continue
        x,y,c=f.kp[i]
        if x is not None and y is not None and c is not None and c>=CONF: pts.append((x,y))
    if not pts: return None
    return (sum(x for x,_ in pts)/len(pts),sum(y for _,y in pts)/len(pts))

def dist(a,b) -> float|None:
    return None if a is None or b is None else math.hypot(a[0]-b[0],a[1]-b[1])

def activity(fs: Sequence[PF], ids: Sequence[int]) -> dict[str,float]|None:
    if len(fs)<2: return None
    speeds=[]
    for p,c in zip(fs,fs[1:]):
        dt=c.t-p.t; d=dist(mean_xy(p,ids),mean_xy(c,ids))
        if dt>1e-6 and d is not None: speeds.append(d/dt)
    net=dist(mean_xy(fs[0],ids),mean_xy(fs[-1],ids))
    if not speeds and net is None: return None
    return {"mean_speed_norm_s":round(statistics.fmean(speeds) if speeds else 0,6),
            "peak_speed_norm_s":round(max(speeds) if speeds else 0,6),
            "net_displacement_norm":round(net or 0,6)}

def snap(f: PF|None) -> dict[str,Any]|None:
    if f is None: return None
    return {"schema":f.schema,"timestamp_s":round(f.t,3),
            "keypoints":[[None if x is None else round(x,6),None if y is None else round(y,6),
                          None if c is None else round(c,6)] for x,y,c in f.kp]}

def pose_metrics(fs: Sequence[PF], a: float, b: float) -> dict[str,Any]:
    sel=[f for f in fs if a<=f.t<=b]
    if len(sel)<2: sel=[f for f in (nearest_pose(fs,a),nearest_pose(fs,b)) if f is not None]
    l=list(range(91,112)); r=list(range(112,133))
    return {"pose_start":snap(nearest_pose(fs,a)),"pose_end":snap(nearest_pose(fs,b)),
            "head_motion":activity(sel,[0,1,2,3,4]),
            "hand_activity":{"left":activity(sel,l),"right":activity(sel,r),"combined":activity(sel,l+r)},
            "body_activity":activity(sel,[5,6,7,8,9,10,11,12])}

def units(src: Path, d: float, m: Sequence[TV], a: Sequence[TV], adb: Sequence[TV], poses: Sequence[PF]) -> list[dict[str,Any]]:
    th=speech_threshold(a); bs=boundaries(d,m,a,th); out=[]
    for i in range(len(bs)-1):
        st,sr,ss=bs[i]; en,er,es=bs[i+1]; mv=span(m,st,en); av=span(a,st,en); db=span(adb,st,en)
        ratio=sum(v>=th for v in av)/len(av) if av else 0.0
        pm=pose_metrics(poses,st,en) if poses else {"pose_start":None,"pose_end":None,"head_motion":None,
            "hand_activity":{"left":None,"right":None,"combined":None},"body_activity":None}
        out.append({"id":f"{src.stem}_u{i+1:04d}","source_file":src.name,"start_s":round(st,3),
            "end_s":round(en,3),"duration_s":round(en-st,3),
            "rgb_span":{"source_path":str(src),"start_s":round(st,3),"end_s":round(en,3)},**pm,
            "motion_energy":{"mean":round(statistics.fmean(mv) if mv else 0,6),"peak":round(max(mv) if mv else 0,6),
                             "entry":round(near(m,st),6),"exit":round(near(m,en),6)},
            "speech":{"class":"speech" if ratio>=.70 else "pause" if ratio<=.15 else "mixed",
                      "speech_ratio":round(ratio,6),"pause_before_s":round(pause_len(a,st,th,-1),3),
                      "pause_after_s":round(pause_len(a,en,th,1),3)},
            "prosody":{"rms_db_mean":None if not db else round(statistics.fmean(db),3),
                       "rms_db_peak":None if not db else round(max(db),3),
                       "energy_norm_mean":round(statistics.fmean(av) if av else 0,6),"pitch_hz_mean":None},
            "transition":{"entry_score":round(ss,6),"exit_score":round(es,6),"boundary_reason":f"{sr}->{er}"}})
    return out

def write_csv(path: Path, us: Sequence[dict[str,Any]]) -> None:
    cols=["id","start_s","end_s","duration_s","speech_class","speech_ratio","motion_mean","motion_peak",
          "prosody_energy","entry_score","exit_score","pose_available"]
    with path.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for u in us:
            w.writerow({"id":u["id"],"start_s":u["start_s"],"end_s":u["end_s"],"duration_s":u["duration_s"],
                "speech_class":u["speech"]["class"],"speech_ratio":u["speech"]["speech_ratio"],
                "motion_mean":u["motion_energy"]["mean"],"motion_peak":u["motion_energy"]["peak"],
                "prosody_energy":u["prosody"]["energy_norm_mean"],"entry_score":u["transition"]["entry_score"],
                "exit_score":u["transition"]["exit_score"],
                "pose_available":u["pose_start"] is not None and u["pose_end"] is not None})

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE); p.add_argument("--output",type=Path,default=OUT)
    p.add_argument("--pose-track",type=Path); p.add_argument("--allow-missing-pose",action="store_true")
    p.add_argument("--ffmpeg",default="ffmpeg"); p.add_argument("--ffprobe",default="ffprobe"); args=p.parse_args()
    src=args.source.resolve(); out=args.output.resolve()
    if not src.is_file(): raise Error(f"Source not found: {src}")
    ffmpeg,ffprobe=exe(args.ffmpeg),exe(args.ffprobe)
    poses=[]; pose_backend=None
    if args.pose_track:
        pp=args.pose_track.resolve()
        if not pp.is_file(): raise Error(f"Pose track not found: {pp}")
        poses=load_pose(pp); pose_backend=f"external_pose_track:{poses[0].schema}"
    elif not args.allow_missing_pose:
        raise Error("Pose track required for a complete profile; --allow-missing-pose is inspection-only.")
    meta=probe(src,ffprobe)
    if not meta["has_audio"]: raise Error("Canonical source must contain audio.")
    print("motion...",flush=True); m=motion(src,ffmpeg)
    print("prosody...",flush=True); a,adb=audio(src,ffmpeg)
    print("units...",flush=True); us=units(src,meta["duration_s"],m,a,adb,poses)
    profile={"schema_version":"behavior-profile/v1","profile_id":f"joao/{src.stem}","subject_id":"joao",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),"status":"complete" if poses else "incomplete_pose",
        "source":meta,"analysis":{"motion_backend":f"ffmpeg gray {W}x{H}@{FPS:g}fps + frame MAD",
        "prosody_backend":f"ffmpeg mono f32le {ARATE}Hz + {A_MS}ms RMS","pose_backend":pose_backend,
        "motion_sample_fps":FPS,"audio_window_ms":A_MS,"speech_threshold":round(speech_threshold(a),6),
        "pitch_available":False,"rms_db_note":"Windowed mono PCM dBFS; energy is normalized per source.",
        "cut_policy":{"min_unit_s":MIN_U,"target_unit_s":TARGET_U,"max_unit_s":MAX_U,
                      "boundary_priority":"pause + low motion + target duration"}},"motion_units":us}
    out.mkdir(parents=True,exist_ok=True)
    (out/"manifest.json").write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding="utf-8")
    write_csv(out/"motion_units.csv",us)
    print(f"status={profile['status']} units={len(us)}")
    print(out/"manifest.json"); print(out/"motion_units.csv")
    if not poses: print("WARNING: incomplete_pose is not a valid behavior gate.",file=sys.stderr)
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Error as e:
        print("ERROR:",e,file=sys.stderr); raise SystemExit(2)
