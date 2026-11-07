from lib2d import *
res=np.load("expB.npy",allow_pickle=True).item()
fig=plt.figure(figsize=(14,8.4),dpi=150)
panels=[("B","200 m/s에서 기수를 10° 들었을 때","고정 계수: 기수만 들리고 수평으로 미끄러짐 · 받음각: 궤적이 기수를 따라 휜다"),
        ("A","280 m/s에서 기수를 수평으로 유지할 때","고정 계수: 기수는 수평인데 엘리베이터처럼 솟는다 · 받음각: 스스로 필요한 α를 찾아 거의 수평")]
for i,(k,t,s) in enumerate(panels):
    ax=fig.add_axes([0.07,0.53-i*0.47,0.91,0.3]);clean(ax)
    for mode,col,lab in[("fixed",RED,"고정 계수 양력"),("aoa",BLUE,"받음각 기반 양력")]:
        r=res[f"{k}_{mode}"];ax.plot(r[:,1],r[:,2],color=col,lw=2.6,label=lab,zorder=2)
        for tt in [0,2,4,6,8]:
            j=min(int(tt*120),len(r)-1);plane2d(ax,r[j,1],r[j,2],r[j,3],size=55,alpha=1 if tt==8 else 0.55)
        ax.text(r[-1,1]+70,r[-1,2],f"{lab}\n8초 뒤 {r[-1,2]:+.0f} m",color=col,fontsize=11.5,fontweight="bold",va="center")
    ax.set_aspect("equal");ax.set_ylim(-110,360);ax.set_xlim(-120,2650)
    ax.set_xlabel("수평 거리 (m)",fontsize=10.5,color="#555");ax.set_ylabel("고도 변화 (m)",fontsize=10.5,color="#555")
    ax.axhline(0,color="#ddd",lw=1,zorder=0)
    fig.text(0.04,0.93-i*0.47,t,fontsize=15,fontweight="bold",color=INK)
    fig.text(0.04,0.895-i*0.47,s,fontsize=11,color="#555")
fig.text(0.98,0.01,"가로·세로 같은 축척 · 비행기 아이콘은 2초 간격, 크기는 과장",ha="right",fontsize=10,color="#777")
fig.savefig("fig/04_fixed_vs_aoa.png",facecolor="white");plt.close(fig);trim("fig/04_fixed_vs_aoa.png")
