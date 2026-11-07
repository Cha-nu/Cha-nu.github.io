from planelib import *
# ---- 04 짐벌락
fig=plt.figure(figsize=(13,6.4),dpi=150)
for i,p in enumerate([0,90]):
    ax=fig.add_axes([i*0.5,0.02,0.5,0.82],projection="3d");setup(ax,lim=3.3,elev=18,azim=215)
    y=0;R=euler(p,y,0)
    plane(ax,R,scale=0.8)
    ring(ax,UEZ,(0,0,0),3.3,BLUE,lw=3)
    ring(ax,yaw_r(y)@UEY,(0,0,0),2.95,GREEN,lw=3)
    ring(ax,R@UEX,(0,0,0),2.6,RED,lw=3)
    arrow(ax,(0,0,0),UEZ*3.9,BLUE,None,lw=2)
    arrow(ax,(0,0,0),R@UEX*(3.2 if p==0 else 3.4),RED,None,lw=2 if p==0 else 2.6,ls="-" if p==0 else (0,(4,3)))
    arrow(ax,(0,0,0),yaw_r(y)@UEY*3.6,GREEN,None,lw=2)
    if p==0:
        ax.text(0,0,4.35,"요 축",color=BLUE,fontsize=13,fontweight="bold",ha="center")
        ax.text(*(UEX*3.75),"롤 축",color=RED,fontsize=13,fontweight="bold",ha="center")
        ax.text(*(UEY*4.1),"피치 축",color=GREEN,fontsize=13,fontweight="bold",ha="center")
    else:
        ax.text(0,0,4.45,"요 축 = 롤 축",color="#333",fontsize=14,fontweight="bold",ha="center")
        ax.text(*(UEY*4.1),"피치 축",color=GREEN,fontsize=13,fontweight="bold",ha="center")
    t=["피치 0°: 세 축이 모두 다르다","피치 90°: 요 링과 롤 링이 겹친다"][i]
    s=["요·피치·롤 입력이 각각 다른 방향으로 기체를 돌린다","요와 롤이 같은 축을 돈다 → 돌릴 수 있는 방향이 3개에서 2개로"][i]
    fig.text(i*0.5+0.25,0.93,t,ha="center",fontsize=17,fontweight="bold",color=["#222",RED][i])
    fig.text(i*0.5+0.25,0.875,s,ha="center",fontsize=11.5,color="#555")
fig.text(0.5,0.01,"링 = 각 입력이 기체를 돌리는 방향 (언리얼 에디터의 회전 기즈모와 같은 모양) · 파랑 요, 초록 피치, 빨강 롤",ha="center",fontsize=11,color="#666")
fig.savefig("fig/04_gimbal_lock.png",facecolor="white");plt.close(fig);trim("fig/04_gimbal_lock.png")

# ---- 05 로컬 vs 월드
fig=plt.figure(figsize=(9.5,7),dpi=150);ax=fig.add_axes([0,0,1,0.86],projection="3d");setup(ax,lim=3.0,elev=20,azim=205)
R=roll_r(90);plane(ax,R)
arrow(ax,(0,0,0),UEY*3.6,GRAY,"월드 Y\n(지면과 수평)",lw=2.2,ls=(0,(5,3)),lpos=1.22,fs=12)
arrow(ax,(0,0,0),R@UEY*3.3,GREEN,"로컬 Y\n(= 오른쪽 날개 방향)",lw=3,lpos=1.25,fs=12)
arrow(ax,(0,0,0),UEX*3.4,RED,"X 전방",lw=2.4,lpos=1.3,fs=12)
NOSE=np.array([2.9,0,0])
path(ax,lambda t:pitch_u(t)@R,NOSE,0,40,GRAY,lw=2.5,hn=UEY,ls=(0,(5,3)))
path(ax,lambda t:R@pitch_u(t),NOSE,0,40,GREEN,lw=3,hn=UEZ)
ax.text(*(pitch_u(42)@R@NOSE+np.array([0,0,0.45])),"ΔR · R : 월드 Y 기준 → 기수가 하늘로",color="#555",fontsize=11.5,ha="center")
ax.text(*(R@pitch_u(42)@NOSE+np.array([0,-0.2,-0.55])),"R · ΔR : 로컬 Y 기준 → 수평 선회",color=GREEN,fontsize=11.5,ha="center",fontweight="bold")
fig.text(0.5,0.94,"같은 \"피치\"도 어느 축을 도느냐가 전부다",ha="center",fontsize=17,fontweight="bold")
fig.text(0.5,0.895,"오른쪽으로 90° 누운 기체 · 곱하는 순서가 축을 정한다",ha="center",fontsize=11.5,color="#555")
fig.savefig("fig/05_local_vs_world.png",facecolor="white");plt.close(fig);trim("fig/05_local_vs_world.png")
