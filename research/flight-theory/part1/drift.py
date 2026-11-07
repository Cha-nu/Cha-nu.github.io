import numpy as np
f=np.float32
rng=np.random.default_rng(7)
N=60*60*10  # 10 min @60fps
def rot(axis,a):
    axis=axis/np.linalg.norm(axis);x,y,z=axis;c,s=np.cos(a),np.sin(a);C=1-c
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def qmul(a,b):
    w1,x1,y1,z1=a;w2,x2,y2,z2=b
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2,w1*x2+x1*w2+y1*z2-z1*y2,w1*y2-x1*z2+y1*w2+z1*x2,w1*z2+x1*y2-y1*x2+z1*w2],dtype=f)
M=np.eye(3,dtype=f);q=np.array([1,0,0,0],f);qn=q.copy()
out=[]
for i in range(N):
    ax=rng.normal(size=3);a=np.radians(rng.uniform(0,3))  # up to 180deg/s
    D=rot(ax,a).astype(f)
    h=np.sin(a/2)*ax/np.linalg.norm(ax);dq=np.array([np.cos(a/2),*h],f)
    M=(M@D).astype(f)
    q=qmul(q,dq);qn=qmul(qn,dq);qn=(qn/np.linalg.norm(qn)).astype(f)
    if i%600==0 or i==N-1:
        e=np.abs(M.T.astype(np.float64)@M-np.eye(3)).max()
        scale=np.linalg.norm(M.astype(np.float64)[:,0])
        out.append((i/60,e,abs(np.linalg.norm(q.astype(np.float64))-1),abs(np.linalg.norm(qn.astype(np.float64))-1),scale))
for r in out[::10]+[out[-1]]:print(r)
np.savetxt('drift.csv',np.array(out),delimiter=',')
