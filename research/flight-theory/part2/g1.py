from lib2d import *
import sys; sys.path.insert(0,".")
C=np.load("climb.npy")   # t,v,z (물리)
fig,ax=plt.subplots(figsize=(9,7.6),dpi=150)
cols=[(0,"레일 방식",RED,lambda t:(250.0,250*t)),(1,"네 가지 힘",BLUE,lambda t:(C[1][int(t*120)],C[2][int(t*120)]))]
for k,name,col,f in cols:
    X=k*3.8
    ax.plot([X,X],[0,f(30)[1]/1000],color=col,lw=2,alpha=0.35,zorder=1)
    for t in [0,10,20,30]:
        v,z=f(t);zk=z/1000
        plane2d(ax,X,zk,np.pi/2,size=0.45)
        ax.text(X+0.55,zk,f"{t}초  {v:.0f} m/s",fontsize=12,va="center",color=col if t==30 else INK,fontweight="bold" if t==30 else "normal")
    ax.text(X,-1.25,name,ha="center",fontsize=16,fontweight="bold",color=col)
    v,z=f(30);ax.text(X,-1.85,f"30초 뒤 고도 +{z:,.0f} m",ha="center",fontsize=12,color="#444")
ax.set_xlim(-1.4,6.8);ax.set_ylim(-2.2,8.3);ax.set_aspect("equal");ax.axis("off")
for zk in range(0,9,2):
    ax.plot([-1.2,6.4],[zk,zk],color="#e3e3e3",lw=0.8,zorder=0);ax.text(-1.3,zk,f"{zk} km",ha="right",va="center",fontsize=10,color="#888")
fig.suptitle("250 m/s로 수직 상승 30초: 레일 방식은 지치지 않는다",fontsize=16,fontweight="bold",y=0.97)
fig.text(0.5,0.915,"레일 방식은 속도가 그대로 · 네 가지 힘은 중력과 항력이 속도를 깎는다 (추력 60 kN < 무게 88 kN)",ha="center",fontsize=11,color="#555")
fig.savefig("fig/01_rail_vs_physics_climb.png",facecolor="white");trim("fig/01_rail_vs_physics_climb.png")
