from model import *
CL_LEVEL=W/(q(200)*S*1.0)       # 200 m/s 수평비행에 필요한 계수
print("CL_level",CL_LEVEL,"alpha deg",np.degrees(CL_LEVEL/CLA))
def drag_thrust(v):  # 수평비행 유지 추력 근사
    return q(v)*S*(CD0+K*CL_LEVEL**2)
def run(mode,v0,pitch_fn,T=8,dt=1/120,thrust=None):
    p=np.zeros(2);v=np.array([v0,0.0]);out=[];t=0
    while t<=T+1e-9:
        pt=pitch_fn(t);out.append((t,p[0],p[1],pt,np.hypot(*v)))
        th=thrust if thrust is not None else drag_thrust(np.hypot(*v))
        a=forces(v,pt,th,mode,CL_LEVEL);p,v=step(p,v,a,dt,"semi");t+=dt
    return np.array(out)
res={}
# A) 280 m/s, 기수 수평 고정 (aoa 모델은 기수=트림 받음각 만큼)
trim200=CL_LEVEL/CLA
res["A_fixed"]=run("fixed",280,lambda t:0.0)
res["A_aoa"]=run("aoa",280,lambda t:0.0)
# B) 200 m/s, 1초 동안 기수를 10도 들고 유지
pf=lambda t:trim200+np.radians(10)*min(t,1.0)
res["B_fixed"]=run("fixed",200,lambda t:np.radians(10)*min(t,1.0))
res["B_aoa"]=run("aoa",200,pf)
for k,r in res.items():
    i=int(4*120);j=-1
    gam=lambda r,i:None
    print(k,"t4 x,z",np.round(r[i,1:3]),"t8 x,z",np.round(r[j,1:3]),"v",round(r[j,4],1))
np.save("expB.npy",res,allow_pickle=True)
