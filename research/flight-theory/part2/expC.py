from model import *
ACMD=np.radians(8)
def acc(v):
    gam=np.arctan2(v[1],v[0]);return forces(v,gam+ACMD,T_MAX)
def sim_frames(frame_dts,method,fixed=None):
    p=np.zeros(2);v=np.array([200.0,0]);t=0;acc_t=0;traj=[(0,*p)]
    for fdt in frame_dts:
        if fixed is None:
            a=acc(v);p,v=step(p,v,a,fdt,method)
        else:
            acc_t+=fdt
            while acc_t>=fixed-1e-12:
                a=acc(v);p,v=step(p,v,a,fixed,"semi");acc_t-=fixed
        t+=fdt;traj.append((t,*p))
    return np.array(traj)
def ref(T):
    p=np.zeros(2);v=np.array([200.0,0]);dt=1/4000;out=[(0,*p)]
    f=lambda s:np.concatenate([s[2:],acc(s[2:])])
    s=np.concatenate([p,v])
    for i in range(int(T/dt)):
        k1=f(s);k2=f(s+dt/2*k1);k3=f(s+dt/2*k2);k4=f(s+dt*k3);s=s+dt/6*(k1+2*k2+2*k3+k4)
        if (i+1)%40==0:out.append(((i+1)*dt,*s[:2]))
    return np.array(out)
T=20
R=ref(T);pref=R[-1,1:]
print("ref end",np.round(pref,1))
rng=np.random.default_rng(3)
out={"ref":R}
for fps in [30,60,144]:
    d=np.full(int(T*fps),1/fps)
    for meth in ["explicit"]:
        tr=sim_frames(d,meth);out[f"{meth}_{fps}"]=tr
        print(meth,fps,"end",np.round(tr[-1,1:],1),"err m",round(np.linalg.norm(tr[-1,1:]-pref),1))
    tr=sim_frames(d,None,fixed=1/120);out[f"fixed_{fps}"]=tr
    print("fixed120",fps,"end",np.round(tr[-1,1:],3),"err m",round(np.linalg.norm(tr[-1,1:]-pref),2))
# 프레임 시간이 흔들릴 때 (8~33ms)
d=rng.uniform(1/120,1/30,size=2000);d=d[np.cumsum(d)<=T];d=np.append(d,T-d.sum())
tr=sim_frames(d,"explicit");out["explicit_jitter"]=tr;print("explicit jitter err",round(np.linalg.norm(tr[-1,1:]-pref),1))
tr=sim_frames(d,None,fixed=1/120);out["fixed_jitter"]=tr;print("fixed jitter end",np.round(tr[-1,1:],3),"err",round(np.linalg.norm(tr[-1,1:]-pref),2))
np.save("expC.npy",out,allow_pickle=True)

# ---- 60초, 시간에 따른 오차 (차트용)
T=60;R=ref(T)
def err_curve(tr):
    xs=np.interp(tr[:,0],R[:,0],R[:,1]);zs=np.interp(tr[:,0],R[:,0],R[:,2])
    return tr[:,0],np.hypot(tr[:,1]-xs,tr[:,2]-zs)
rows=[]
ends={}
for fps in [30,60,144]:
    d=np.full(int(T*fps),1/fps)
    for name,tr in [(f"explicit_{fps}",sim_frames(d,"explicit")),(f"fixed_{fps}",sim_frames(d,None,fixed=1/120))]:
        t,e=err_curve(tr);ends[name]=tr[-1,1:]
        for tt in range(0,T+1,5):
            i=np.argmin(abs(t-tt));rows.append((name,tt,round(float(e[i]),2)))
for r in rows:
    if r[1] in(30,60):print(r)
print("explicit 30 vs 144 gap",np.linalg.norm(ends["explicit_30"]-ends["explicit_144"]))
print("fixed 30 vs 144 gap",np.linalg.norm(ends["fixed_30"]-ends["fixed_144"]))
import json;json.dump(rows,open("errC.json","w"))
np.save("refloop.npy",R)
