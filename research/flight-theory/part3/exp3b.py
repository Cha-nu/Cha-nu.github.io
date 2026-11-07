from model3 import *
dt=1/120
def run(mode,T=6,v0=150.0,NMAX=None,AMAX=np.radians(12),hold=None,rate_deg=20):
    hold=T if hold is None else hold
    trim=W/(q(v0)*S)/CLA
    p=np.zeros(2);vel=np.array([v0,0.0]);pitch=trim;out=[]
    for i in range(int(T/dt)+1):
        t=i*dt
        acc,a,n=accel(vel,pitch,T_MAX,cl_stall)
        v=np.hypot(*vel);gam=np.arctan2(vel[1],vel[0])
        ldir=np.array([-vel[1],vel[0]])/v;gdot=acc@ldir/v
        out.append((t,p[0],p[1],pitch,a,v,n,np.unwrap([0,gam])[1]))
        stick=1.0 if t<hold else 0.0
        if mode=="rate":
            rate=stick*np.radians(rate_deg)
        else:
            amax=AMAX
            if NMAX is not None: amax=min(AMAX,NMAX*W/(q(v)*S)/CLA)
            acmd=stick*amax if stick>0 else trim
            rate=np.clip(gdot+6.0*(acmd-a),-np.radians(40),np.radians(40))
        pitch+=rate*dt;vel=vel+acc*dt;p=p+vel*dt
    o=np.array(out);o[:,7]=np.unwrap(np.arctan2(np.gradient(o[:,2]),np.gradient(o[:,1])));return o
for v0 in [150]:
    R=run("rate",v0=v0);L=run("limit",v0=v0)
    for name,r in [("rate",R),("limit",L)]:
        print(v0,name,"maxα",round(np.degrees(r[:,4].max()),1),"turned(path)deg",round(np.degrees(r[-1,7]),1),"v end",round(r[-1,5],1),"z",round(r[-1,2]))
        for tt in [1,2,3,4,5,6]:
            j=int(tt/dt);print("    t",tt,"α",round(np.degrees(r[j,4]),1),"G",round(r[j,6],2),"v",round(r[j,5]),"path",round(np.degrees(r[j,7]),1),"nose",round(np.degrees(r[j,3]),1))
    np.save("pull.npy",{"rate":R,"limit":L},allow_pickle=True)
H=run("limit",T=3,v0=300.0);HG=run("limit",T=3,v0=300.0,NMAX=9.0)
print("300 aoa-only maxG",round(H[:,6].max(),2),"maxα",np.degrees(H[:,4].max()),"| G-limit maxG",round(HG[:,6].max(),2),"α",np.degrees(HG[:,4].max()))
np.save("highspeed.npy",{"aoa":H,"g":HG},allow_pickle=True)
