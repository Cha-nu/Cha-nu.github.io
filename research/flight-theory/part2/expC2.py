import json
exec(open("expC.py").read().split("T=20")[0])
T=60;R=ref(T)
def err_curve(tr):
    xs=np.interp(tr[:,0],R[:,0],R[:,1]);zs=np.interp(tr[:,0],R[:,0],R[:,2])
    return tr[:,0],np.hypot(tr[:,1]-xs,tr[:,2]-zs)
rows=[];ends={}
for fps in [30,60,144]:
    d=np.full(int(T*fps),1/fps)
    for name,tr in [(f"frame_{fps}",sim_frames(d,"semi")),(f"fixed_{fps}",sim_frames(d,None,fixed=1/120))]:
        t,e=err_curve(tr);ends[name]=tr[-1,1:]
        for tt in range(0,T+1,2):
            i=np.argmin(abs(t-tt));rows.append({"series":name,"t":tt,"err":round(float(e[i]),1)})
        np.save(f"traj_{name}.npy",tr)
for r in rows:
    if r["t"] in (20,60):print(r)
print("frame 30 vs 144 gap",np.linalg.norm(ends["frame_30"]-ends["frame_144"]))
print("fixed 30 vs 144 gap",np.linalg.norm(ends["fixed_30"]-ends["fixed_144"]))
json.dump(rows,open("errC2.json","w"))
np.save("refloop.npy",R)
