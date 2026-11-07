from planelib import *
import sys
NOSE=np.array([2.75,0,0])
def climb_head(R):
    f=R@UEX;return np.degrees(np.arcsin(np.clip(f[2],-1,1))),abs(np.degrees(np.arctan2(-f[1],f[0])))
def draw(fig,a,title_suffix=True,trail=True):
    specs=[("오일러 각 누적","Pitch += 입력  (월드 수평면 기준)",lambda t:euler(t,0,90),RED),
           ("로컬 축 회전","Q × ΔQ  (기체 자신의 날개 축 기준)",lambda t:roll_r(90)@pitch_u(t),BLUE)]
    for i,(name,how,fn,col) in enumerate(specs):
        ax=fig.add_axes([i*0.5,0.0,0.5,0.84],projection="3d");setup(ax,lim=3.0,elev=20,azim=205)
        ground(ax,z=-2.6,lim=3.0)
        plane(ax,fn(0),alpha=0.16)
        plane(ax,fn(a))
        if a>3: path(ax,fn,NOSE*1.08,0,a,col,lw=3,hn=np.cross(fn(a)@UEX,fn(a)@UEZ) if False else fn(0)@UEY)
        c,h=climb_head(fn(a))
        mark="X" if i==0 else "O"
        fig.text(i*0.5+0.25,0.93,f"{name}",ha="center",fontsize=17,fontweight="bold",color=col)
        fig.text(i*0.5+0.25,0.875,how,ha="center",fontsize=11,color="#555")
        fig.text(i*0.5+0.25,0.06,f"상승 {c:4.1f}°   ·   수평 선회 {h:4.1f}°",ha="center",fontsize=15,fontweight="bold",color="#222",family="Noto Sans CJK KR")
if __name__=="__main__":
    fig=plt.figure(figsize=(13,6.2),dpi=150);draw(fig,45)
    fig.text(0.5,0.005,"시작: 오른쪽으로 90° 누운 상태 (반투명)  →  스틱을 초당 45°로 1초 당긴 결과  ·  선 = 기수가 지나간 경로",ha="center",fontsize=11,color="#666")
    fig.savefig("fig/03_bank_pull.png",facecolor="white");plt.close(fig);trim("fig/03_bank_pull.png")
