from planelib import *
from matplotlib.patches import FancyBboxPatch
# ---- 07 쿼터니언 = 축 + 각도
n=np.array([0.35,-0.45,0.82]);n/=np.linalg.norm(n);th=70
fig=plt.figure(figsize=(10,7),dpi=150);ax=fig.add_axes([0,0,0.62,0.86],projection="3d");setup(ax,lim=2.8,elev=20,azim=212)
plane(ax,alpha=0.15);plane(ax,axis_angle(n,np.radians(th)))
arrow(ax,-n*1.8,n*5.0,PURPLE,"회전축 n",lw=3,lpos=1.06,fs=14)
tip=np.array([-0.4,-2.95,0.05])
path(ax,lambda a:axis_angle(n,np.radians(a)),tip*1.05,0,th,PURPLE,lw=3,hn=n)
mid=axis_angle(n,np.radians(th/2))@tip*1.25
ax.text(*mid,f"θ = {th}°",color=PURPLE,fontsize=15,fontweight="bold",ha="center")
fig.text(0.5,0.945,"쿼터니언 = \"이 축을 중심으로 이만큼\"",ha="center",fontsize=18,fontweight="bold")
fig.text(0.5,0.9,"오일러처럼 축 3개를 차례로 돌리지 않고, 축 하나로 한 번에 돌린다",ha="center",fontsize=11.5,color="#555")
x0=0.63
fig.text(x0,0.62,"숫자 4개로 저장",fontsize=14,fontweight="bold",color="#222")
fig.text(x0,0.55,"w = cos(θ/2)",fontsize=14,family="DejaVu Sans Mono",color=PURPLE)
fig.text(x0,0.50,"(x, y, z) = sin(θ/2) · n",fontsize=14,family="DejaVu Sans Mono",color=PURPLE)
fig.text(x0,0.39,f"이 그림: θ = {th}°  →  w = cos {th//2}° ≈ {np.cos(np.radians(th/2)):.3f}",fontsize=12.5,color="#222")
fig.text(x0,0.26,"→ 사람이 읽기엔 어렵지만\n    곱셈이 싸고 짐벌락이 없다",fontsize=12,color="#444",linespacing=1.6)
fig.savefig("fig/07_quaternion.png",facecolor="white");plt.close(fig);trim("fig/07_quaternion.png")

# ---- 08 처리 흐름
fig=plt.figure(figsize=(14,4.4),dpi=150);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,14);ax.set_ylim(0,4.4);ax.axis("off")
steps=[("입력","-1 ~ 1\n(스틱, 키보드)"),("× 도/초 × DeltaTime","FRotator ΔRot\n(Pitch, Yaw, Roll)"),("ΔRot.Quaternion()","FQuat ΔQ"),
       ("Q × ΔQ","오른쪽 곱\n= 로컬 축 기준"),("Normalize()","오차 정리\n(길이 = 1)"),("SetActorRotation","엔진·복제로\n전달")]
W,H,G=1.95,1.55,0.37;x=0.2;centers=[]
for i,(t,s) in enumerate(steps):
    human=i<2;fc="#fdf0e2" if human else "#e6eefb";ec=ORANGE if human else BLUE
    ax.add_patch(FancyBboxPatch((x,1.0),W,H,boxstyle="round,pad=0.02,rounding_size=0.12",fc=fc,ec=ec,lw=2))
    ax.text(x+W/2,1.0+H*0.7,t,ha="center",va="center",fontsize=12.5,fontweight="bold",color="#222")
    ax.text(x+W/2,1.0+H*0.3,s,ha="center",va="center",fontsize=10.5,color="#444",linespacing=1.3)
    if i<len(steps)-1: ax.annotate("",(x+W+G-0.03,1.0+H/2),(x+W+0.03,1.0+H/2),arrowprops=dict(arrowstyle="-|>",color="#666",lw=1.8))
    centers.append(x);x+=W+G
def bracket(x1,x2,label,col):
    ax.plot([x1,x1,x2,x2],[2.75,2.95,2.95,2.75],color=col,lw=2);ax.text((x1+x2)/2,3.2,label,ha="center",fontsize=13.5,fontweight="bold",color=col)
bracket(centers[0],centers[1]+W,"사람이 만지는 곳: 오일러 각 (도/초)",ORANGE)
bracket(centers[2],centers[5]+W,"엔진이 쌓는 곳: 쿼터니언",BLUE)
ax.text(7,0.45,"매 프레임 Tick에서 왼쪽 → 오른쪽 순서로 실행",ha="center",fontsize=11,color="#666")
ax.text(7,4.0,"하이브리드 회전 처리 흐름",ha="center",fontsize=17,fontweight="bold")
fig.savefig("fig/08_pipeline.png",facecolor="white");plt.close(fig);trim("fig/08_pipeline.png")
