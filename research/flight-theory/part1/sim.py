import numpy as np
f32=np.float32
def Rx(a):c,s=np.cos(a),np.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a):c,s=np.cos(a),np.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a):c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def euler(p,y,r):return Rz(y)@Ry(-p)@Rx(r)   # nose-up positive pitch
def fwd_angles(R):
    f=R@np.array([1,0,0]);return np.degrees(np.arcsin(f[2])),np.degrees(np.arctan2(f[1],f[0]))
# A: banked 90 deg, pull stick 45 deg/s for 2s
dt=1/60;rate=np.radians(45)
P=0.0;Y=0.0;Rr=np.radians(90)
Rl=euler(0,0,Rr)
trA=[]
for i in range(121):
    t=i*dt
    trA.append((t,*fwd_angles(euler(P,Y,Rr)),*fwd_angles(Rl)))
    P+=rate*dt
    Rl=Rl@Ry(-rate*dt)
for t,a,b,c,d in trA[::30]:print(f"t={t:.2f} euler climb={a:6.1f} head={b:6.1f} | local climb={c:6.1f} head={d:6.1f}")
np.savetxt('bank.csv',np.array(trA),delimiter=',',fmt='%.3f')
# Gimbal: at pitch 90, yaw vs roll same axis
for p in [0,89.9,90]:
    base=euler(np.radians(p),0,0)
    dy=euler(np.radians(p),np.radians(10),0);dr=euler(np.radians(p),0,np.radians(10))
    ax=lambda M:(lambda w:w)(np.round(np.degrees(np.arccos(np.clip((np.trace(base.T@M)-1)/2,-1,1))),2))
    # axis of delta in world
    def waxis(M):
        D=M@base.T;w=np.array([D[2,1]-D[1,2],D[0,2]-D[2,0],D[1,0]-D[0,1]]);return w/np.linalg.norm(w)
    print(p, 'yaw axis',np.round(waxis(dy),3),'roll axis',np.round(waxis(dr),3), 'dot',round(float(abs(waxis(dy)@waxis(dr))),4))
