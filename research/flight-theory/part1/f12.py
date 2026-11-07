from planelib import *
fig=plt.figure(figsize=(9,6.2),dpi=150);ax=fig.add_axes([0.0,-0.12,1,1.12],projection="3d")
setup(ax,lim=3.0,elev=24,azim=212)
plane(ax)
arrow(ax,(0,0,0),UEX*4.0,RED,"X  전방\nRoll 축",lpos=1.16)
arrow(ax,(0,0,0),UEY*4.1,GREEN,"Y  오른쪽\nPitch 축",lpos=1.18)
arrow(ax,(0,0,0),UEZ*2.9,BLUE,"Z  위\nYaw 축",lpos=1.2)
arc(ax,UEX,UEX*2.55,0.36,30,320,RED,lw=1.8)
arc(ax,UEY,UEY*2.6,0.36,30,320,GREEN,lw=1.8)
arc(ax,UEZ,UEZ*2.0,0.36,30,320,BLUE,lw=1.8)
fig.text(0.5,0.95,"언리얼 엔진 좌표계: X 전방 · Y 오른쪽 · Z 위",ha="center",fontsize=17,fontweight="bold")
fig.text(0.5,0.905,"왼손 좌표계 (Z-up) · 주황색 날개 = 오른쪽 날개",ha="center",fontsize=11.5,color="#555")
fig.subplots_adjust(0,0,1,0.95);fig.savefig("fig/01_ue_axes.png",facecolor="white",bbox_inches="tight",pad_inches=0.15);plt.close(fig)

fig=plt.figure(figsize=(15,5.4),dpi=150)
tip=(-0.4,-2.95,0.05); nose=(2.7,0,0)
panels=[("Roll · X축 회전","뒤에서 본 모습 · 오른쪽 날개가 내려간다",roll_r,35,UEX,RED,dict(elev=10,azim=180),tip),
        ("Pitch · Y축 회전","오른쪽에서 본 모습 · 기수가 올라간다",pitch_u,30,UEY,GREEN,dict(elev=0,azim=-90),nose),
        ("Yaw · Z축 회전","위에서 본 모습 · 기수가 오른쪽으로 돈다",yaw_r,35,UEZ,BLUE,dict(elev=89.5,azim=-90),nose)]
for i,(t,s,fn,a,axv,col,view,pt) in enumerate(panels):
    ax=fig.add_subplot(1,3,i+1,projection="3d");setup(ax,lim=3.2,ortho=True,**view)
    plane(ax,alpha=0.15);plane(ax,fn(a))
    path(ax,fn,np.array(pt)*1.12,4,a,col,hn=axv)
    if i!=2: arrow(ax,-axv*3.2,axv*6.4,col,None,lw=1.6,ls="--")
    else: ax.scatter([0],[0],[1.5],color=col,s=50)
    fig.text((i+0.5)/3,0.93,t,fontsize=16,fontweight="bold",color=col,ha="center")
    fig.text((i+0.5)/3,0.865,s,fontsize=11.5,color="#444",ha="center")
fig.text(0.5,0.02,"반투명 = 회전 전 · 진한 색 = 회전 후 · 점선(요: 점) = 회전축 · 주황 = 오른쪽 날개",ha="center",fontsize=11,color="#666")
fig.subplots_adjust(0,0.04,1,0.86,wspace=0);fig.savefig("fig/02_roll_pitch_yaw.png",facecolor="white",bbox_inches="tight",pad_inches=0.15);plt.close(fig)

for n in ["fig/01_ue_axes.png","fig/02_roll_pitch_yaw.png"]: trim(n)
