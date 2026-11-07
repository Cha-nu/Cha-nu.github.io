from lib2d import *
from model3 import *
from matplotlib.patches import FancyBboxPatch
A12=np.radians(12)
D=np.load("dog.npy");V,om_a,om_g,n_a,n_g=D
# ---- 05 G vs 속도
fig,ax=plt.subplots(figsize=(11,6),dpi=150);fig.subplots_adjust(left=0.08,right=0.78,top=0.8,bottom=0.12);clean(ax)
ax.plot(V,n_a,color=RED,lw=2.8);ax.text(402,min(n_a[-1],30),"",)
ax.plot(V,n_g,color=BLUE,lw=3.4)
ax.axhline(9,color="#bbb",lw=1,ls=(0,(4,3)))
i=np.argmin(abs(V-300));ax.plot(300,n_a[i],"o",color=RED);ax.plot(300,9,"o",color=BLUE)
ax.annotate(f"300 m/s: {n_a[i]:.1f}G",(300,n_a[i]),(225,n_a[i]+1.5),fontsize=12,color=RED,fontweight="bold",arrowprops=dict(arrowstyle="-",color=RED,lw=0.8))
ax.annotate("9.0G에서 멈춤",(300,9),(310,6.2),fontsize=12,color=BLUE,fontweight="bold",arrowprops=dict(arrowstyle="-",color=BLUE,lw=0.8))
ax.text(325,23,"받음각 리미터만 (α 12° 고정)",color=RED,fontsize=11.5,fontweight="bold",va="center",ha="right")
ax.text(402,9,"받음각 + G 리미터",color=BLUE,fontsize=11.5,fontweight="bold",va="center")
ax.set_xlim(50,400);ax.set_ylim(0,26);ax.set_xlabel("속도 (m/s)",color="#444");ax.set_ylabel("풀 스틱일 때의 G",color="#444");ax.grid(axis="y",color="#eee")
fig.text(0.08,0.93,"받음각 리미터만 걸면 빠를수록 G가 속도의 제곱으로 치솟는다",fontsize=15,fontweight="bold")
fig.text(0.08,0.875,"예제 기체 · 이론값 (n = q·S·C_L / W) · 사람이 버티는 한계는 보통 9G 안팎",fontsize=11,color="#555")
fig.savefig("fig/05_g_vs_speed.png",facecolor="white");plt.close(fig);trim("fig/05_g_vs_speed.png")

# ---- 06 조종 법칙 흐름
fig=plt.figure(figsize=(14,5.6),dpi=150);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,14);ax.set_ylim(0,5.6);ax.axis("off")
def box(x,y,w,h,t,s,fc,ec):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.12",fc=fc,ec=ec,lw=2))
    ax.text(x+w/2,y+h*0.68,t,ha="center",va="center",fontsize=12.5,fontweight="bold",color=INK)
    ax.text(x+w/2,y+h*0.3,s,ha="center",va="center",fontsize=10.2,color="#444",linespacing=1.3)
def ar(x1,y1,x2,y2,col="#666"):ax.annotate("",(x2,y2),(x1,y1),arrowprops=dict(arrowstyle="-|>",color=col,lw=1.8))
Y=1.1;H=1.4
box(0.2,2.75,2.4,1.25,"받음각 한계","α_max = 12°\n저속에서 걸림","#fdeee9",RED)
box(0.2,0.35,2.4,1.25,"G 한계","9G가 되는 α\n고속에서 걸림","#fdeee9",RED)
box(3.4,Y+0.35,1.8,H,"min()","더 작은 쪽\n= α 상한","#fdeee9",RED)
box(6.0,Y+0.35,2.0,H,"× 스틱","α_cmd\n목표 받음각","#e6eefb",BLUE)
box(6.0,3.75,2.0,1.0,"스틱","0 ~ 1","#fdf0e2",ORANGE)
box(8.8,Y+0.35,2.6,H,"피치 각속도","dγ/dt + K·(α_cmd − α)\n최대 40°/s","#e6eefb",BLUE)
box(12.0,Y+0.35,1.8,H,"자세","오른쪽 곱\n(1편 방식)","#e6eefb",BLUE)
yc=Y+0.35+H/2
ar(2.6,3.37,3.45,yc+0.3);ar(2.6,0.97,3.45,yc-0.3);ar(5.2,yc,6.0,yc);ar(7.0,3.75,7.0,Y+0.35+H+0.02,ORANGE)
ar(8.0,yc,8.8,yc);ar(11.4,yc,12.0,yc)
ax.text(10.1,0.95,"현재 α를 재서 목표와의 차이만큼 기수를 돌린다",ha="center",fontsize=10.5,color=BLUE)
ax.text(7.0,5.25,"받음각 + G 리미터: 스틱은 기수가 아니라 \"받음각\"을 명령한다",ha="center",fontsize=16,fontweight="bold")
fig.savefig("fig/06_control_law.png",facecolor="white");plt.close(fig);trim("fig/06_control_law.png")
