from planelib import *
f=np.float32
N=60*60*30
ax_=np.array([3.0,1.0,0.0]);a=np.radians(np.hypot(180,60))/60
D=axis_angle(ax_,a).astype(f);M=np.eye(3,dtype=f)
for i in range(N): M=(M@D).astype(f)
M=M.astype(np.float64)
U,S,Vt=np.linalg.svd(M);Q=U@Vt
E=M-Q;K=150
Mx=Q.T@(Q+K*E)          # 같은 자세로 돌려 놓고 오차만 K배
def ang(a,b):return np.degrees(np.arccos(a@b/np.linalg.norm(a)/np.linalg.norm(b)))
print("real err",np.abs(M.T@M-np.eye(3)).max(),"angles",ang(Mx[:,0],Mx[:,1]),ang(Mx[:,0],Mx[:,2]),ang(Mx[:,1],Mx[:,2]),"lens",np.linalg.norm(Mx,axis=0))
fig=plt.figure(figsize=(13,6.2),dpi=150)
for i,(R,t,s) in enumerate([(np.eye(3),"정상: 세 축이 직각, 길이 1","회전만 있는 깨끗한 행렬"),
                            (Mx,"30분 뒤: 기체가 쪼그라들고 축이 기운다",f"float32 행렬을 30분 누적한 실제 오차를 {K}배 과장")]):
    ax=fig.add_axes([i*0.5,0.0,0.5,0.84],projection="3d");setup(ax,lim=2.3,elev=24,azim=212)
    if i: plane(ax,np.eye(3),alpha=0.12)
    plane(ax,R)
    ex,ey,ez=R[:,0],R[:,1]@np.diag([1,1,1]),R[:,2]
    arrow(ax,(0,0,0),R@UEX*3.4,RED,"X",lpos=1.12);arrow(ax,(0,0,0),R@UEY*3.4,GREEN,"Y",lpos=1.12);arrow(ax,(0,0,0),R@UEZ*2.4,BLUE,"Z",lpos=1.15)
    xy=ang(R@UEX,R@UEY);xz=ang(R@UEX,R@UEZ)
    ax.text2D(0.5,0.08,f"X–Y 사이 {xy:.1f}° · X–Z 사이 {xz:.1f}°",transform=ax.transAxes,ha="center",fontsize=14,fontweight="bold",color=["#222",RED][i])
    fig.text(i*0.5+0.25,0.93,t,ha="center",fontsize=17,fontweight="bold",color=["#222",RED][i])
    fig.text(i*0.5+0.25,0.875,s,ha="center",fontsize=11.5,color="#555")
fig.savefig("fig/06_matrix_drift.png",facecolor="white");plt.close(fig);trim("fig/06_matrix_drift.png")
