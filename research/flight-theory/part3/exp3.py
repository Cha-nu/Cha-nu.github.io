from model3 import *
print("CL_MAX",CL_MAX,"Vstall real",np.sqrt(2*W/(rho*S*CL_MAX)))
a40=W/(q(40)*S)/CLA;print("linear 40m/s level alpha deg",np.degrees(a40))
print("100m/s alpha40 linear G",q(100)*S*CLA*np.radians(40)/W,"real max G",q(100)*S*CL_MAX/W)
# 실험: 150 m/s 수평에서 풀 스틱 3초
dt=1/120
def run(mode,T=8,v0=150.0,NMAX=None,AMAX=np.radians(12)):
    trim=W/(q(v0)*S)/CLA
    p=np.zeros(2);vel=np.array([v0,0.0]);pitch=trim;out=[]
    for i in range(int(T/dt)+1):
        t=i*dt
        acc,a,n=accel(vel,pitch,T_MAX,cl_stall)
        v=np.hypot(*vel);out.append((t,p[0],p[1],pitch,a,v,n))
        stick=1.0 if t<3 else 0.0
        if mode=="rate":
            rate=stick*np.radians(20)
        else:
            amax=AMAX
            if NMAX is not None:
                amax=min(AMAX,NMAX*W/(q(v)*S)/CLA)
            acmd=stick*amax if stick>0 else trim
            rate=np.clip(4.0*(acmd-a),-np.radians(30),np.radians(30))
        pitch+=rate*dt
        vel=vel+acc*dt;p=p+vel*dt
    return np.array(out)
R=run("rate");L=run("limit")
for name,r in [("rate",R),("limit",L)]:
    print(name,"max alpha",round(np.degrees(r[:,4].max()),1),"min v",round(r[:,5].min(),1),"z@8",round(r[-1,2]),"max z",round(r[:,2].max()),"maxG",round(r[:,6].max(),2))
    for tt in [1,2,3,4,6,8]:
        j=int(tt/dt);print("   t",tt,"alpha",round(np.degrees(r[j,4]),1),"v",round(r[j,5]),"z",round(r[j,2]),"G",round(r[j,6],2))
np.save("pull.npy",{"rate":R,"limit":L},allow_pickle=True)
# 고속 문제: 300 m/s에서 리미터만 vs G 리미터
H=run("limit",T=4,v0=300.0);HG=run("limit",T=4,v0=300.0,NMAX=9.0)
print("300 limit-only maxG",H[:,6].max(),"with G limit",HG[:,6].max())
np.save("highspeed.npy",{"aoa":H,"g":HG},allow_pickle=True)
# doghouse
V=np.linspace(50,400,351);n_a=q(V)*S*CLA*np.radians(12)/W;n=np.minimum(n_a,9)
om=lambda n,V:np.degrees(g*np.sqrt(np.clip(n*n-1,0,None))/V)
i=np.argmax(om(n,V));print("corner",V[i],om(n,V)[i],"Vs@12",np.sqrt(2*W/(rho*S*CLA*np.radians(12))))
print("om at 300 aoa only",om(q(300)*S*CLA*np.radians(12)/W,300),"G",q(300)*S*CLA*np.radians(12)/W)
np.save("dog.npy",np.vstack([V,om(n_a,V),om(n,V),n_a,n]))
