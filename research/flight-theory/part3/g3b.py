from lib2d import *
from model3 import *
d=np.load("pull.npy",allow_pickle=True).item()
# ---- 03 궤적
fig,axs=plt.subplots(1,2,figsize=(14,6.6),dpi=150);fig.subplots_adjust(left=0.05,right=0.98,top=0.8,bottom=0.1,wspace=0.12)
specs=[("rate","리미터 없음: 스틱 = 기수 회전 (초당 20°)",RED),("limit","받음각 리미터: 스틱 = 목표 받음각 (최대 12°)",BLUE)]
for ax,(k,t,col) in zip(axs,specs):
    r=d[k];clean(ax)
    ax.plot(r[:,1],r[:,2],color=col,lw=2.8,zorder=2)
    for tt in range(0,7):
        j=min(int(tt*120),len(r)-1);x,z,p,a,v=r[j,1],r[j,2],r[j,3],r[j,4],r[j,5]
        plane2d(ax,x,z,p,size=32,alpha=1 if tt in(0,6) else 0.7)
        stalled=np.degrees(a)>14
        ax.text(x+(28 if k=="rate" else 30),z-(34 if k=="rate" else 30),f"{tt}초  α {np.degrees(a):.0f}°",fontsize=10,color=RED if stalled else "#444",fontweight="bold" if stalled else "normal")
    ax.set_aspect("equal");ax.set_xlim(-60,780);ax.set_ylim(-70,560)
    ax.set_xlabel("수평 거리 (m)",color="#555");ax.set_ylabel("고도 (m)",color="#555")
    ax.set_title(t,fontsize=13.5,fontweight="bold",color=col,loc="left")
    turned=np.degrees(r[-1,7]);ax.text(0.98,0.03,f"6초 동안 경로가 돈 각도 {turned:.0f}° · 끝 속도 {r[-1,5]:.0f} m/s",transform=ax.transAxes,ha="right",fontsize=12,fontweight="bold",color=col)
fig.text(0.05,0.93,"150 m/s에서 풀 스틱 6초: 끝까지 당긴 쪽이 덜 돈다",fontsize=16,fontweight="bold")
fig.text(0.05,0.875,"빨간 글씨 = 실속각(14°)을 넘은 순간 · 비행기 아이콘은 1초 간격, 가로·세로 같은 축척 (아이콘 크기는 과장)",fontsize=11,color="#555")
fig.savefig("fig/03_full_stick_pull.png",facecolor="white");plt.close(fig);trim("fig/03_full_stick_pull.png")

# ---- 04 α, G 시간 그래프
fig,axs=plt.subplots(1,2,figsize=(14,5.2),dpi=150);fig.subplots_adjust(left=0.06,right=0.86,top=0.78,bottom=0.13,wspace=0.42)
ax=axs[0];clean(ax)
ax.axhspan(14,80,color="#fdeee9",zorder=0);ax.text(0.15,74,"실속 영역 (α > 14°)",fontsize=10.5,color=RED)
for k,lab,col in[("rate","리미터 없음",RED),("limit","받음각 리미터",BLUE)]:
    r=d[k];ax.plot(r[:,0],np.degrees(r[:,4]),color=col,lw=2.8);ax.text(6.15,np.degrees(r[-1,4]),f"{lab}\n{np.degrees(r[-1,4]):.0f}°",color=col,fontsize=11,fontweight="bold",va="center")
ax.set_xlim(0,6);ax.set_ylim(0,80);ax.set_xlabel("시간 (초)",color="#444");ax.set_ylabel("받음각 α (도)",color="#444");ax.grid(axis="y",color="#eee")
ax.set_title("받음각",fontsize=13.5,fontweight="bold",loc="left")
ax=axs[1];clean(ax)
for k,lab,col in[("rate","리미터 없음",RED),("limit","받음각 리미터",BLUE)]:
    r=d[k];ax.plot(r[:,0],r[:,6],color=col,lw=2.8);ax.text(6.15,r[-1,6],f"{lab}\n{r[-1,6]:.1f}G",color=col,fontsize=11,fontweight="bold",va="center")
ax.set_xlim(0,6);ax.set_ylim(0,6);ax.set_xlabel("시간 (초)",color="#444");ax.set_ylabel("양력 / 무게 (G)",color="#444");ax.grid(axis="y",color="#eee")
ax.set_title("선회력 (G)",fontsize=13.5,fontweight="bold",loc="left")
fig.text(0.06,0.93,"리미터 없이 당기면 1.2초 만에 실속, 6초 뒤 선회력은 0.3G까지 무너진다",fontsize=15,fontweight="bold")
fig.text(0.06,0.87,"150 m/s, 풀 스틱 6초 · 리미터는 α 12°를 지키며 3.4~4.5G를 유지",fontsize=11,color="#555")
fig.savefig("fig/04_alpha_g_time.png",facecolor="white");plt.close(fig);trim("fig/04_alpha_g_time.png")
