"""툰 셰이딩 5편 그림. 실제 렌더링이 아니라 공식으로 계산한 설명용 그림입니다.

수치는 프로젝트의 머티리얼/애니메이션 블루프린트에 들어 있는 값을 그대로 씁니다.
  앞머리 띠: BangsHLPosition 0.62, BangsHLWidth 0.18
  눈 타원: 중심 (|X| 3.19, Z 125.36), 반지름 (1.65, 0.82), SmoothStep(0.9, 1.05)
  Cover Mask: Step(D >= 0.3) * (1 - SmoothStep(4, 8, D))
  리본: BaseColorPower 1 -> 2
  치마 충돌: 골반 구 중심에서 치마 본까지 10.7cm, 구 9.5 + 본 3 -> 구 8.3 + 본 2
"""
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import Circle

for p in ["C:/Windows/Fonts/NotoSansKR-Regular.ttf", "C:/Windows/Fonts/NotoSansKR-Bold.ttf"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = ["Noto Sans KR", "Malgun Gothic"]
plt.rcParams["axes.unicode_minus"] = False

OUT = "fig"
os.makedirs(OUT, exist_ok=True)
BG = "#eceef1"
INK = "#2b2f36"
SUB = "#6b7280"
ACC = "#e07a2f"
GRAY = "#b8bcc4"
NOTE = "설명용 그림 (공식으로 계산, 실제 렌더링 아님)"


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def style(ax):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(SUB)
    ax.tick_params(colors=SUB, labelsize=10)


def save(fig, name):
    fig.text(0.99, 0.01, NOTE, ha="right", va="bottom", fontsize=8.5, color=SUB)
    fig.savefig(os.path.join(OUT, name), dpi=150, facecolor=BG)
    plt.close(fig)


def fig_band():
    pos, width = 0.62, 0.18
    x = np.linspace(0, 1, 600)
    band = np.clip(1 - np.abs(x - pos) / width, 0, 1)
    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=BG)
    style(ax)
    ax.plot(x, band, color=ACC, lw=3)
    ax.fill_between(x, 0, band, color=ACC, alpha=0.18)
    ax.axvline(pos, color=INK, lw=1, ls="--")
    ax.annotate("Position 0.62", (pos, 1.0), (pos + 0.03, 1.04), color=INK, fontsize=11)
    ax.annotate("", (pos, 0.5), (pos + width / 2, 0.5), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.annotate("", (pos - width, 0.06), (pos, 0.06), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(pos - width / 2, 0.10, "Width 0.18", ha="center", color=INK, fontsize=11)
    ax.text(0.02, 0.9, "머리 뿌리 쪽", color=SUB, fontsize=10)
    ax.text(0.98, 0.9, "머리끝 쪽", color=SUB, fontsize=10, ha="right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("가닥 방향 좌표 (UV 맵의 G 채널)", color=INK, fontsize=11)
    ax.set_ylabel("띠 세기", color=INK, fontsize=11)
    ax.set_title("띠는 좌표가 0.62일 때 1, 0.18만큼 벗어나면 0이 되는 삼각형이다", color=INK, fontsize=13, pad=12)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "01_band.png")


def fig_ellipse():
    cx, cz, rx, rz = 3.19, 125.36, 1.65, 0.82
    X, Z = np.meshgrid(np.linspace(-7, 7, 900), np.linspace(123.2, 127.5, 300))
    e = np.sqrt(((np.abs(X) - cx) / rx) ** 2 + ((Z - cz) / rz) ** 2)
    mask = 1 - smoothstep(0.9, 1.05, e)
    fig, ax = plt.subplots(figsize=(9, 3.9), facecolor=BG)
    style(ax)
    img = np.ones(mask.shape + (3,)) * np.array([0.925, 0.933, 0.945])
    acc = np.array([0.878, 0.478, 0.184])
    img = img * (1 - mask[..., None] * 0.85) + acc * (mask[..., None] * 0.85)
    ax.imshow(img, extent=(-7, 7, 123.2, 127.5), origin="lower", aspect="equal")
    for s in (-1, 1):
        ax.plot([s * cx], [cz], "o", color=INK, ms=4)
    ax.annotate("", (cx, cz), (cx + rx, cz), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(cx + rx / 2, cz + 0.12, "1.65", ha="center", color=INK, fontsize=10)
    ax.annotate("", (cx, cz), (cx, cz + rz), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(cx - 0.12, cz + rz / 2, "0.82", ha="right", va="center", color=INK, fontsize=10)
    ax.text(cx, cz - 1.25, "중심 (3.19, 125.36)", ha="center", color=INK, fontsize=10)
    ax.text(-cx, cz - 1.25, "abs(X)로 같은 식이\n반대쪽 눈에도 적용", ha="center", color=SUB, fontsize=10, va="top")
    ax.axvline(0, color=GRAY, lw=1, ls=":")
    ax.set_xlabel("스키닝 전 로컬 X (cm)", color=INK, fontsize=11)
    ax.set_ylabel("로컬 Z (cm)", color=INK, fontsize=11)
    ax.set_title("중심을 빼고 반지름으로 나누면 타원이 반지름 1인 원이 된다", color=INK, fontsize=13, pad=12)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save(fig, "02_ellipse.png")


def fig_cover():
    d = np.linspace(-1, 10, 1100)
    cover = (d >= 0.3) * (1 - smoothstep(4, 8, d))
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor=BG)
    style(ax)
    ax.plot(d, cover, color=ACC, lw=3)
    ax.fill_between(d, 0, cover, color=ACC, alpha=0.18)
    ax.axvline(0.3, color=INK, lw=1, ls="--")
    ax.axvspan(4, 8, color=GRAY, alpha=0.35)
    ax.text(0.45, 1.05, "0.3부터 가려진 것으로 판정", color=INK, fontsize=10.5)
    ax.text(6, 1.05, "4~8 사이에서 서서히 0으로", color=INK, fontsize=10.5, ha="center")
    ax.text(-0.45, 0.5, "가려지지 않음", color=SUB, fontsize=10, rotation=90, va="center")
    ax.text(9.1, 0.12, "먼 물체는 제외", color=SUB, fontsize=10, ha="center")
    ax.set_xlim(-1, 10)
    ax.set_ylim(0, 1.18)
    ax.set_xlabel("D = 내 픽셀 깊이 - 화면에 이미 그려진 깊이 (cm)", color=INK, fontsize=11)
    ax.set_ylabel("Cover Mask", color=INK, fontsize=11)
    ax.set_title("앞에 가까이 있는 것(0.3~4cm)에 가려졌을 때만 비친다", color=INK, fontsize=13, pad=12)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "03_cover.png")


def fig_power():
    x = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(7.2, 5.4), facecolor=BG)
    style(ax)
    ax.plot(x, x, color=GRAY, lw=2.5, label="Power 1")
    ax.plot(x, x ** 2, color=ACC, lw=3, label="Power 2")
    for v in (0.9, 0.5):
        ax.plot([v, v], [v ** 2, v], color=INK, lw=1, ls="--")
        ax.plot([v], [v ** 2], "o", color=ACC, ms=6)
        ax.plot([v], [v], "o", color=GRAY, ms=6)
        ax.text(v + 0.015, v ** 2 - 0.045, f"{v} → {v**2:.2f}", color=INK, fontsize=10.5)
    ax.plot([1], [1], "o", color=INK, ms=6)
    ax.text(0.985, 1.03, "1은 그대로 1", color=INK, fontsize=10.5, ha="right")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("텍스처 값", color=INK, fontsize=11)
    ax.set_ylabel("Power를 거친 값", color=INK, fontsize=11)
    ax.legend(frameon=False, loc="upper left", fontsize=11)
    ax.set_title("제곱하면 흰색은 남고 그 아래만 내려가 차이가 벌어진다", color=INK, fontsize=13, pad=12)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "04_power.png")


def fig_clearance():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.9), facecolor=BG)
    dist = 10.7
    for ax, (rs, rb, title) in zip(axes, [(9.5, 3.0, "구 9.5 + 본 3 = 12.5 > 10.7  → 밀려남"),
                                          (8.3, 2.0, "구 8.3 + 본 2 = 10.3 < 10.7  → 닿지 않음")]):
        ax.set_facecolor(BG)
        ax.set_aspect("equal")
        ax.axis("off")
        hit = rs + rb > dist
        ax.add_patch(Circle((0, 0), rs, fc=GRAY, ec=INK, lw=1.2, alpha=0.6))
        ax.add_patch(Circle((dist, 0), rb, fc=ACC if hit else "#ffffff", ec=ACC, lw=2, alpha=0.75))
        ax.plot([0, dist], [0, 0], color=INK, lw=1, ls="--")
        ax.plot([0, dist], [0, 0], "o", color=INK, ms=4)
        ax.text(dist / 2, -1.3, "거리 10.7", ha="center", color=INK, fontsize=10.5)
        ax.text(0, rs + 0.9, f"골반 충돌 구 {rs}", ha="center", color=INK, fontsize=10.5)
        ax.text(dist, rb + 0.9, f"치마 본 {rb:g}", ha="center", color=INK, fontsize=10.5)
        ax.set_xlim(-11, 15.5)
        ax.set_ylim(-11.5, 12.5)
        ax.set_title(title, color=ACC if hit else INK, fontsize=12)
    fig.suptitle("기준 자세에서 두 반지름의 합이 거리보다 크면 서 있기만 해도 치마가 뜬다", color=INK, fontsize=13)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    save(fig, "05_clearance.png")


if __name__ == "__main__":
    fig_band()
    fig_ellipse()
    fig_cover()
    fig_power()
    fig_clearance()
    print("done")
