from lib2d import *
import json
from model import *
rows=json.load(open("errC2.json"))
def ser(n):r=[x for x in rows if x["series"]==n];return [x["t"] for x in r],[x["err"] for x in r]
fig,ax=plt.subplots(figsize=(11,6.2),dpi=150);fig.subplots_adjust(left=0.08,right=0.78,top=0.8,bottom=0.12);clean(ax)
for fps,a in[(30,1.0),(60,0.65),(144,0.38)]:
    t,e=ser(f"frame_{fps}");ax.plot(t,e,color=INK,alpha=a,lw=2.2)
    ly={30:e[-1],60:e[-1],144:42}[fps]
    ax.text(61,ly,f"프레임 dt · {fps}fps  {e[-1]:.0f} m",va="center",fontsize=11.5,color=INK,alpha=max(a,0.6))
t,e=ser("fixed_30");ax.plot(t,e,color=BLUE,lw=3.4)
ax.text(61,e[-1]+15,f"고정 1/120초  {e[-1]:.1f} m",va="center",fontsize=11.5,color=BLUE,fontweight="bold")
ax.text(61,e[-1]+3,"30·60·144fps 모두 이 한 선",va="center",fontsize=10.5,color=BLUE)
ax.annotate("",(60,248),(60,50.4),arrowprops=dict(arrowstyle="<->",color=RED,lw=1.6))
ax.text(58.5,150,"플레이어 사이\n198 m 차이",ha="right",va="center",fontsize=12,color=RED,fontweight="bold")
ax.set_xlim(0,60);ax.set_ylim(0,265);ax.set_xlabel("비행 시간 (초)",fontsize=11,color="#444");ax.set_ylabel("정밀 해와의 거리 오차 (m)",fontsize=11,color="#444")
ax.grid(axis="y",color="#eee")
fig.text(0.08,0.93,"같은 루프 60초: 프레임레이트마다 다른 곳에 있던 비행기가, 고정 스텝에선 모두 같은 곳에",fontsize=14.5,fontweight="bold")
fig.text(0.08,0.875,"받음각 8° 유지 (약 5G 루프) · 기준 = RK4 1/4000초 적분",fontsize=11,color="#555")
fig.savefig("fig/05_framerate_error.png",facecolor="white");plt.close(fig);trim("fig/05_framerate_error.png")

# ---- 06 고정 타임스텝 타임라인
fig,ax=plt.subplots(figsize=(14,5.2),dpi=150);ax.set_xlim(-6,108);ax.set_ylim(-3.2,5.6);ax.axis("off")
frames=[0,16.7,50,58.3,83,104]   # ms, 들쭉날쭉한 프레임
STEP=1000/120
cols=["#fdf0e2","#f6e3cf"]
for i in range(len(frames)-1):
    a,b=frames[i],frames[i+1]
    ax.add_patch(plt.Rectangle((a,2.6),b-a,1.3,fc=cols[i%2],ec=ORANGE,lw=1.5))
    ax.text((a+b)/2,3.25,f"프레임 {i+1}\n{b-a:.0f} ms",ha="center",va="center",fontsize=10.5,color=INK)
k=0;x=0
while x+STEP<=104+1e-6:
    ax.add_patch(plt.Rectangle((x,0),STEP,1.2,fc="#e6eefb",ec=BLUE,lw=1.2));x+=STEP;k+=1
ax.text(-1,3.25,"화면\n(렌더)",ha="right",va="center",fontsize=12,fontweight="bold",color=ORANGE)
ax.text(-1,0.6,"물리\n1/120초",ha="right",va="center",fontsize=12,fontweight="bold",color=BLUE)
# 프레임 2 강조
a,b=16.7,50
s0=int(np.ceil(a/STEP-1e-9));s1=int(np.floor(b/STEP+1e-9))
for j in range(s0,s1):ax.add_patch(plt.Rectangle((j*STEP,0),STEP,1.2,fc=BLUE,alpha=0.35,ec=BLUE,lw=1.2))
ax.annotate("",(a,1.5),(a,2.55),arrowprops=dict(arrowstyle="-",color="#bbb",ls=(0,(3,2))));ax.annotate("",(b,1.5),(b,2.55),arrowprops=dict(arrowstyle="-",color="#bbb",ls=(0,(3,2))))
ax.text((a+b)/2,-1.25,f"프레임 2 (33 ms) 동안 물리 {s1-s0}번",ha="center",fontsize=12,color=BLUE,fontweight="bold")
# 마지막 남은 시간
last=k*STEP
ax.add_patch(plt.Rectangle((last,0),104-last,1.2,fc="none",ec=PURPLE,lw=1.6,ls=(0,(3,2))))
ax.annotate(f"남은 {104-last:.1f} ms → 보간 비율 α = {(104-last)/STEP:.2f}",(last+(104-last)/2,0),(80,-2.2),fontsize=11.5,color=PURPLE,ha="center",arrowprops=dict(arrowstyle="-|>",color=PURPLE,lw=1.2))
ax.text(2,-2.2,"화면 프레임 길이가 들쭉날쭉해도 물리는 항상 같은 간격으로만 진행한다",fontsize=11.5,color="#444")
ax.text(50,5.1,"고정 타임스텝: 프레임 시간을 통에 모아 1/120초씩 꺼내 쓴다",ha="center",fontsize=16,fontweight="bold")
for tk in [0,25,50,75,100]:
    ax.plot([tk,tk],[-0.05,-0.3],color="#999",lw=1);ax.text(tk,-0.5,f"{tk} ms",ha="center",va="top",fontsize=9,color="#999")
fig.savefig("fig/06_fixed_timestep.png",facecolor="white");plt.close(fig);trim("fig/06_fixed_timestep.png")

# ---- 07 결과: 상승/활공 속도
C=np.load("climb.npy")
p=np.array([0.0,3000.0]);v=np.array([200.0,0]);dt=1/120;G=[(0,200.0)]
for i in range(int(60/dt)):
    a=forces(v,np.radians(3),0.0);p,v=step(p,v,a,dt,"semi")
    if (i+1)%60==0:G.append(((i+1)*dt,np.hypot(*v)))
G=np.array(G)
fig,axs=plt.subplots(1,2,figsize=(13,5.2),dpi=150);fig.subplots_adjust(left=0.07,right=0.9,top=0.78,bottom=0.14,wspace=0.42)
ax=axs[0];clean(ax);m=C[0]<=30
ax.plot([0,30],[250,250],color=GRAY,lw=2.4);ax.text(30.6,250,"레일 250",va="center",fontsize=11,color="#666")
ax.plot(C[0][m],C[1][m],color=BLUE,lw=3);ax.text(30.6,C[1][m][-1],f"네 가지 힘 {C[1][m][-1]:.0f}",va="center",fontsize=11,color=BLUE,fontweight="bold")
ax.set_xlim(0,30);ax.set_ylim(0,280);ax.set_xlabel("시간 (초)",color="#444");ax.set_ylabel("속도 (m/s)",color="#444");ax.grid(axis="y",color="#eee")
ax.set_title("수직 상승 · 추력 최대",fontsize=13,fontweight="bold",loc="left",color=INK)
ax=axs[1];clean(ax)
ax.plot([0,60],[200,200],color=GRAY,lw=2.4);ax.text(60.8,200,"레일 200",va="center",fontsize=11,color="#666")
ax.plot(G[:,0],G[:,1],color=BLUE,lw=3);ax.text(60.8,G[-1,1],f"네 가지 힘 {G[-1,1]:.0f}",va="center",fontsize=11,color=BLUE,fontweight="bold")
ax.set_xlim(0,60);ax.set_ylim(0,230);ax.set_xlabel("시간 (초)",color="#444");ax.set_ylabel("속도 (m/s)",color="#444");ax.grid(axis="y",color="#eee")
ax.set_title("엔진 끄고 기수 3° 유지",fontsize=13,fontweight="bold",loc="left",color=INK)
fig.text(0.07,0.93,"이제 비행기가 지친다: 올라가면 느려지고, 엔진을 끄면 속도가 빠진다",fontsize=15,fontweight="bold")
fig.text(0.07,0.87,"예제 기체 (9,000 kg · 날개 28 m² · 추력 60 kN) · 1/120초 고정 스텝",fontsize=11,color="#555")
fig.savefig("fig/07_results_speed.png",facecolor="white");plt.close(fig);trim("fig/07_results_speed.png")
