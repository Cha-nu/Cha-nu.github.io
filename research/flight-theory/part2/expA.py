from model import *
# 문제 상황 & 결과: 250 m/s로 수직 상승 30초
def rail(T,dt=1/120):
    t=np.arange(0,T+1e-9,dt);return t,np.full_like(t,250.0),250*t
def phys_climb(T,dt=1/120,thrust=T_MAX):
    p=np.zeros(2);v=np.array([0.0,250.0]);ts=[];vs=[];zs=[];t=0
    while t<=T+1e-9:
        ts.append(t);vs.append(np.hypot(*v));zs.append(p[1])
        a=forces(v,np.pi/2,thrust);p,v=step(p,v,a,dt,"semi");t+=dt
        if np.hypot(*v)<1:break
    return np.array(ts),np.array(vs),np.array(zs)
t,vs,zs=phys_climb(40)
for tt in [0,10,20,30]:
    i=int(tt*120);print("climb t",tt,"v",round(vs[i],1),"z",round(zs[i]))
print("v<1 at",t[-1],"zmax",zs.max())
# 엔진 끄고 수평 자세(기수 수평 고정) 60초 활공
p=np.array([0.0,3000.0]);v=np.array([200.0,0]);dt=1/120
for i in range(int(60/dt)):
    a=forces(v,np.radians(3),0.0);p,v=step(p,v,a,dt,"semi")
    if i%(10*120)==0:print("glide",i*dt,np.round(p),np.round(np.hypot(*v),1))
print("glide end",np.round(p),round(np.hypot(*v),1))
np.save("climb.npy",np.vstack([t,vs,zs]))
