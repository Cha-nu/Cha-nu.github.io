# 그림 공통 스타일 (flight-theory/part2/lib2d.py와 같은 색과 글꼴)
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon
plt.rcParams["font.family"] = "Noto Sans CJK KR"; plt.rcParams["axes.unicode_minus"] = False
RED = "#d9452b"; BLUE = "#2f6fd6"; GRAY = "#8c8c8c"; ORANGE = "#f08a24"; INK = "#222"; LIGHT = "#bdbdbd"


def arr(ax, p, v, color, label=None, lw=2.6, off=(0, 0), fs=13, ha="center", ms=20, ls="-", z=5):
    p = np.asarray(p, float); v = np.asarray(v, float)
    ax.add_patch(FancyArrowPatch(p, p + v, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw,
                                 zorder=z, linestyle=ls, shrinkA=0, shrinkB=0))
    if label:
        ax.text(*(p + v + np.asarray(off)), label, color=color, fontsize=fs, ha=ha, va="center",
                fontweight="bold", zorder=6)


def grid(ax, xr, yr, ydown=False, labels=True):
    """정수 격자와 축. ydown=True면 y축이 아래로 증가한다."""
    for x in range(xr[0], xr[1] + 1):
        ax.plot([x, x], yr, color="#ececec", lw=0.8, zorder=0)
    for y in range(yr[0], yr[1] + 1):
        ax.plot(xr, [y, y], color="#ececec", lw=0.8, zorder=0)
    ax.add_patch(FancyArrowPatch((xr[0], 0), (xr[1] + 0.4, 0), arrowstyle="-|>", mutation_scale=14, color="#777", lw=1.2, zorder=1))
    ax.add_patch(FancyArrowPatch((0, yr[0]), (0, yr[1] + 0.4), arrowstyle="-|>", mutation_scale=14, color="#777", lw=1.2, zorder=1))
    if labels:
        ax.text(xr[1] + 0.55, 0, "x", fontsize=12, color="#555", va="center")
        ax.text(0, yr[1] + 0.65, "y", fontsize=12, color="#555", ha="center")
        for x in range(1, xr[1] + 1):
            ax.text(x, -0.3 if not ydown else -0.3, str(x), fontsize=9, color="#999", ha="center", va="top" if not ydown else "bottom")
        for y in range(1, yr[1] + 1):
            ax.text(-0.25, y, str(y), fontsize=9, color="#999", ha="right", va="center")
    ax.set_aspect("equal"); ax.axis("off")
    if ydown:
        ax.invert_yaxis()


def dot(ax, p, color, label=None, off=(0.18, 0.18), fs=13, ha="left"):
    ax.plot(*p, "o", color=color, ms=9, zorder=6)
    if label:
        ax.text(p[0] + off[0], p[1] + off[1], label, color=color, fontsize=fs, fontweight="bold", ha=ha, va="center", zorder=6)


def clean(ax):
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#bbb"); ax.spines["bottom"].set_color("#bbb")
    ax.tick_params(colors="#555", labelsize=10.5)


def trim(fn, pad=24):
    from PIL import Image, ImageChops
    im = Image.open(fn).convert("RGB"); bg = Image.new("RGB", im.size, (255, 255, 255))
    bb = ImageChops.difference(im, bg).point(lambda v: 255 if v > 8 else 0).getbbox()
    if bb:
        l, t, r, b = bb; im = im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height)))
    im.save(fn)
