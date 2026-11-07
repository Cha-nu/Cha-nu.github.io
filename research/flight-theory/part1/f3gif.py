from f3 import *
from PIL import Image
import io
frames=[]
angles=list(np.linspace(0,90,37))
for a in angles:
    fig=plt.figure(figsize=(10,4.9),dpi=80);draw(fig,a)
    fig.text(0.5,0.005,f"오른쪽으로 90° 누운 상태에서 스틱을 초당 45°로 당기는 중 · {a/45:.2f}초",ha="center",fontsize=11,color="#666")
    b=io.BytesIO();fig.savefig(b,format="png",facecolor="white");plt.close(fig);b.seek(0)
    frames.append(Image.open(b).convert("RGB"))
durs=[700]+[60]*(len(frames)-2)+[1800]
pal=[f.quantize(colors=128,method=Image.MEDIANCUT) for f in frames]
pal[0].save("fig/03_bank_pull.gif",save_all=True,append_images=pal[1:],duration=durs,loop=0,optimize=True)
print(len(frames))
