import numpy as np
f=np.float32
def rot(axis,a):
    axis=axis/np.linalg.norm(axis);x,y,z=axis;c,s=np.cos(a),np.sin(a);C=1-c
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def qmul(a,b):
    w1,x1,y1,z1=a;w2,x2,y2,z2=b
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2,w1*x2+x1*w2+y1*z2-z1*y2,w1*y2-x1*z2+y1*w2+z1*x2,w1*z2+x1*y2-y1*x2+z1*w2],dtype=f)
N=60*60*30
# constant input: roll 180deg/s + pitch 60deg/s (aileron roll while pulling)
ax=np.array([3.0,1.0,0.0]);a=np.radians(np.hypot(180,60))/60
D=rot(ax,a).astype(f);h=np.sin(a/2)*ax/np.linalg.norm(ax);dq=np.array([np.cos(a/2),*h],f)
M=np.eye(3,dtype=f);q=np.array([1,0,0,0],f);qn=q.copy()
out=[]
for i in range(N+1):
    if i%3600==0:
        Md=M.astype(np.float64)
        out.append((i/3600,np.abs(Md.T@Md-np.eye(3)).max(),abs(np.linalg.norm(q.astype(np.float64))-1),abs(np.linalg.norm(qn.astype(np.float64))-1)))
    M=(M@D).astype(f);q=qmul(q,dq);qn=qmul(qn,dq);qn=(qn/np.linalg.norm(qn)).astype(f)
for r in out[::5]:print(r)
np.savetxt('drift2.csv',np.array(out),delimiter=',')
