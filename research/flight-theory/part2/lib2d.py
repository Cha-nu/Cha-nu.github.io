import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Arc
plt.rcParams["font.family"]="Noto Sans CJK KR"; plt.rcParams["axes.unicode_minus"]=False
RED="#d9452b"; GREEN="#3f9b3f"; BLUE="#2f6fd6"; PURPLE="#8a4fd0"; GRAY="#8c8c8c"; ORANGE="#f08a24"; INK="#222"
BODY=np.array([(1.0,0.0),(0.8,0.07),(0.55,0.13),(0.25,0.14),(0.0,0.08),(-0.6,0.06),(-0.82,0.36),(-1.0,0.36),(-0.97,0.04),(-1.02,0.0),(-0.6,-0.06),(0.6,-0.07),(0.85,-0.04)])
WING=np.array([(0.2,-0.02),(-0.35,-0.02),(-0.42,-0.06),(0.12,-0.06)])
CANOPY=np.array([(0.62,0.11),(0.42,0.17),(0.22,0.14),(0.38,0.09)])
def plane2d(ax,x,z,pitch,size=1.0,alpha=1.0,color="#c4c8cc",z_order=3):
    c,s=np.cos(pitch),np.sin(pitch);R=np.array([[c,-s],[s,c]])
    for pts,fc in((BODY,color),(WING,"#9aa3ab"),(CANOPY,"#4a6a8a")):
        P=(R@(pts*size).T).T+[x,z]
        ax.add_patch(Polygon(P,closed=True,fc=fc,ec=(0,0,0,0.45*alpha),lw=0.8,alpha=alpha,zorder=z_order))
def arr(ax,p,v,color,label=None,lw=3,off=(0,0),fs=13,ha="center",ms=22,ls="-"):
    p=np.asarray(p,float);v=np.asarray(v,float)
    ax.add_patch(FancyArrowPatch(p,p+v,arrowstyle="-|>",mutation_scale=ms,color=color,lw=lw,zorder=5,linestyle=ls))
    if label:ax.text(*(p+v+np.asarray(off)),label,color=color,fontsize=fs,ha=ha,va="center",fontweight="bold",zorder=6)
def trim(fn,pad=24):
    from PIL import Image, ImageChops
    im=Image.open(fn).convert("RGB");bg=Image.new("RGB",im.size,(255,255,255))
    bb=ImageChops.difference(im,bg).point(lambda v:255 if v>8 else 0).getbbox()
    if bb:
        l,t,r,b=bb;im=im.crop((max(l-pad,0),max(t-pad,0),min(r+pad,im.width),min(b+pad,im.height)))
    im.save(fn)
def clean(ax):
    for s in ["top","right"]:ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#bbb");ax.spines["bottom"].set_color("#bbb")
    ax.tick_params(colors="#555",labelsize=10.5)
