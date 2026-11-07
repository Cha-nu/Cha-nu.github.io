import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
plt.rcParams["font.family"]="Noto Sans CJK KR"; plt.rcParams["axes.unicode_minus"]=False
# 내부 계산: 오른손 좌표계 X=전방, Yl=왼쪽, Z=위.  UE의 Y(오른쪽) = -Yl
RED="#d9452b"; GREEN="#3f9b3f"; BLUE="#2f6fd6"; PURPLE="#8a4fd0"; GRAY="#8c8c8c"; ORANGE="#f08a24"
def Rx(a):c,s=np.cos(a),np.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a):c,s=np.cos(a),np.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a):c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
d=np.radians
def roll_r(a):return Rx(d(a))      # 오른쪽 날개 내림
def pitch_u(a):return Ry(-d(a))    # 기수 들기
def yaw_r(a):return Rz(-d(a))      # 기수 오른쪽
def euler(p,y,r):return yaw_r(y)@pitch_u(p)@roll_r(r)   # FRotator 합성 순서: Yaw -> Pitch -> Roll
def axis_angle(n,a):
    n=np.asarray(n,float);n/=np.linalg.norm(n);x,y,z=n;c,s=np.cos(a),np.sin(a);C=1-c
    return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def _mesh():
    F=[]
    st=[(2.7,0.0),(2.3,0.2),(1.6,0.3),(-1.0,0.27),(-2.3,0.1)]
    k=10;ang=np.linspace(0,2*np.pi,k,endpoint=False)
    rings=[[(x,r*np.cos(t),r*np.sin(t)) for t in ang] for x,r in st]
    for i in range(len(rings)-1):
        for j in range(k):
            F.append(([rings[i][j],rings[i][(j+1)%k],rings[i+1][(j+1)%k],rings[i+1][j]],"#c4c8cc"))
    F.append((rings[-1],"#bdbdbd"))
    for sgn,col in((1,"#9aa3ab"),(-1,ORANGE)):   # sgn=-1 → 오른쪽 날개(주황)
        F.append(([(0.8,0,0),(-0.1,sgn*3.0,0.05),(-0.65,sgn*3.0,0.05),(-0.5,0,0)],col))
        F.append(([(-1.6,0,0.05),(-2.05,sgn*1.15,0.08),(-2.35,sgn*1.15,0.08),(-2.25,0,0.05)],col if sgn<0 else "#9aa3ab"))
    F.append(([(-1.45,0,0.2),(-2.15,0,1.15),(-2.45,0,1.15),(-2.3,0,0.1)],"#8f8f8f"))
    F.append(([(1.9,0.0,0.22),(1.3,0.17,0.33),(0.9,0.0,0.32),(1.3,-0.17,0.33)],"#4a6a8a"))  # 캐노피
    return F
MESH=_mesh()
LS=LightSource(azdeg=225,altdeg=55)
def plane(ax,R=np.eye(3),pos=(0,0,0),alpha=1.0,scale=1.0):
    pos=np.asarray(pos)
    verts=[[pos+scale*(R@np.array(v)) for v in f] for f,_ in MESH]
    cols=[c for _,c in MESH]
    pc=Poly3DCollection(verts,facecolors=cols,edgecolors=(0,0,0,0.25*alpha),linewidths=0.4,alpha=alpha,shade=False)
    ax.add_collection3d(pc)
def arrow(ax,start,vec,color,label=None,lw=2.6,ls="-",lpos=1.12,fs=12,ha="center",bold=True):
    s=np.asarray(start,float);v=np.asarray(vec,float)
    ax.quiver(*s,*v,color=color,lw=lw,arrow_length_ratio=0.12,linestyle=ls)
    if label:ax.text(*(s+v*lpos),label,color=color,fontsize=fs,ha=ha,va="center",fontweight="bold" if bold else "normal")
def basis(n):
    n=np.asarray(n,float);n/=np.linalg.norm(n)
    t=np.array([1,0,0]) if abs(n[0])<0.9 else np.array([0,0,1])
    u=np.cross(n,t);u/=np.linalg.norm(u);v=np.cross(n,u);return n,u,v
def arc(ax,n,center,r,a0,a1,color,lw=2.4,head=True,ls="-",alpha=1):
    n,u,v=basis(n);c=np.asarray(center,float)
    t=np.radians(np.linspace(a0,a1,60))
    P=np.array([c+r*(np.cos(x)*u+np.sin(x)*v) for x in t])
    ax.plot(P[:,0],P[:,1],P[:,2],color=color,lw=lw,ls=ls,alpha=alpha)
    if head:
        sg=np.sign(a1-a0);x=t[-1];tan=sg*(-np.sin(x)*u+np.cos(x)*v)
        ax.quiver(*P[-1],*(tan*r*0.35),color=color,lw=lw,arrow_length_ratio=0.9,alpha=alpha)
    return P
def ring(ax,n,center,r,color,lw=2.2,ls="-",alpha=1):return arc(ax,n,center,r,0,360,color,lw,False,ls,alpha)
def setup(ax,lim=3.4,elev=22,azim=210,zlim=None,ortho=False):
    ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_zlim(*(zlim or(-lim,lim)))
    ax.set_box_aspect((1,1,(zlim[1]-zlim[0])/(2*lim) if zlim else 1))
    ax.view_init(elev=elev,azim=azim);ax.set_axis_off()
    ax.set_proj_type("ortho") if ortho else ax.set_proj_type("persp",focal_length=0.7)
def ground(ax,z=-2.2,lim=3.4,n=9):
    g=np.linspace(-lim,lim,n)
    for x in g:
        ax.plot([x,x],[-lim,lim],[z,z],color="#c9c9c9",lw=0.6);ax.plot([-lim,lim],[x,x],[z,z],color="#c9c9c9",lw=0.6)
UEX=np.array([1,0,0]);UEY=np.array([0,-1,0]);UEZ=np.array([0,0,1])

def head(ax,p,v,hn,color,size=0.42,alpha=1):
    v=np.asarray(v,float);v/=np.linalg.norm(v);w=np.cross(v,hn);w/=np.linalg.norm(w)
    tri=[p+v*size,p+w*size*0.45,p-w*size*0.45]
    ax.add_collection3d(Poly3DCollection([tri],facecolors=color,edgecolors=color,alpha=alpha))
def path(ax,Rfun,point,a0,a1,color,lw=3,hn=(0,0,1),ls="-",alpha=1,n=40):
    """회전 함수 Rfun(각도)로 point가 지나가는 실제 경로 + 화살촉(hn = 화살촉 평면의 법선)"""
    P=np.array([Rfun(a)@np.asarray(point,float) for a in np.linspace(a0,a1,n)])
    ax.plot(P[:,0],P[:,1],P[:,2],color=color,lw=lw,ls=ls,alpha=alpha)
    head(ax,P[-1],P[-1]-P[-3],np.asarray(hn,float),color,alpha=alpha)
    return P

def trim(fn,pad=24):
    from PIL import Image, ImageChops
    im=Image.open(fn).convert("RGB");bg=Image.new("RGB",im.size,(255,255,255))
    bb=ImageChops.difference(im,bg).point(lambda v:255 if v>8 else 0).getbbox()
    if bb:
        l,t,r,b=bb;im=im.crop((max(l-pad,0),max(t-pad,0),min(r+pad,im.width),min(b+pad,im.height)))
    im.save(fn)
