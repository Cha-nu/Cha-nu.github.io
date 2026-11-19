"""툰 셰이딩 1편 그림. 실제 렌더링이 아니라 공식으로 계산한 설명용 그림입니다.

임계값은 프로젝트의 PP_Toon / MM_ToonShader 기본값을 그대로 씁니다.
  ShadowStartRange 0.35, ShadowSmoothness 0.05
  OuterShadowStartRange 0.40, OuterShadowSmoothness 0.01
  ShadowColor 0.38, ShadowOuterColor 0.589 (MM_ToonShader 기본 회색)
  Rim: Fresnel(Exponent 2, BaseReflect 0.02) -> SmoothStep(0.70 - 0.45, 0.70 + 0.45)
"""
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

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
ACC = "#e07a2f"      # 강조색 하나
GRAY = "#b8bcc4"
BASE = np.array([0.80, 0.70, 0.90])  # 예시 물체 색 (연보라)

# 프로젝트 기본값
SH_S, SH_K = 0.35, 0.05
OU_S, OU_K = 0.40, 0.01
SH_C, OU_C = 0.38, 0.589
LIGHT = np.array([-0.85, 0.40, -0.05])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def sphere(n=400):
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]
    r2 = x * x + y * y
    mask = r2 <= 1
    z = np.sqrt(np.clip(1 - r2, 0, 1))
    N = np.stack([x, y, z], -1)
    return N, mask


def toon_factor(L):
    draw_shadow = smoothstep(SH_S - SH_K, SH_S + SH_K, L)
    draw_outer = smoothstep(OU_S - OU_K, OU_S + OU_K, L)
    a = SH_C + (OU_C - SH_C) * draw_shadow
    return a + (1 - a) * draw_outer


def show_sphere(ax, rgb, mask, title):
    img = np.ones(mask.shape + (3,))
    img[:] = np.array([0.925, 0.933, 0.945])
    img[mask] = np.clip(rgb[mask], 0, 1)
    ax.imshow(img, extent=(-1, 1, -1, 1))
    ax.set_title(title, color=INK, fontsize=12)
    ax.axis("off")


def fig_spheres():
    N, mask = sphere()
    ndl = N @ LIGHT
    lambert = np.clip(ndl, 0, 1)
    half = ndl * 0.5 + 0.5
    toon = toon_factor(half)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.9), facecolor=BG)
    show_sphere(axs[0], lambert[..., None] * BASE, mask, "Lambert  max(N·L, 0)")
    show_sphere(axs[1], half[..., None] * BASE, mask, "Half-Lambert  N·L×0.5+0.5")
    show_sphere(axs[2], toon[..., None] * BASE, mask, "Half-Lambert + SmoothStep 2단계")
    fig.suptitle("같은 빛이라도 명암을 계단으로 자르면 셀 애니메이션처럼 보입니다", color=INK, fontsize=14, y=0.99)
    fig.text(0.5, 0.02, "설명용 계산 그림 · 빛은 왼쪽 옆 · 임계값은 프로젝트 기본값(0.35±0.05, 0.40±0.01)",
             ha="center", color=SUB, fontsize=9)
    fig.savefig(f"{OUT}/01_spheres.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def fig_curves():
    ndl = np.linspace(-1, 1, 801)
    lam = np.clip(ndl, 0, 1)
    half = ndl * 0.5 + 0.5
    toon = toon_factor(half)
    fig, ax = plt.subplots(figsize=(8.2, 4.4), facecolor=BG)
    ax.set_facecolor(BG)
    ax.plot(ndl, lam, color=GRAY, lw=2.5, label="Lambert")
    ax.plot(ndl, half, color=SUB, lw=2, ls="--", label="Half-Lambert")
    ax.plot(ndl, toon, color=ACC, lw=3, label="툰 (3단계)")
    for v, lab in [((SH_S - 0.5) * 2, "그림자 경계\nL=0.35"), ((OU_S - 0.5) * 2, "중간톤 경계\nL=0.40")]:
        ax.axvline(v, color=INK, lw=0.8, ls=":")
    ax.text(-0.98, 0.42, "어두운 그림자 0.38", color=INK, fontsize=10)
    ax.text(-0.98, 0.62, "중간톤 0.589 (아주 좁음)", color=INK, fontsize=10)
    ax.text(0.15, 1.04, "밝은 면 1.0", color=INK, fontsize=10)
    ax.set_xlabel("N·L  (빛을 정면으로 받으면 1, 정반대면 -1)", color=INK)
    ax.set_ylabel("밝기 계수", color=INK)
    ax.set_ylim(-0.05, 1.15)
    ax.set_title("툰 곡선은 L=0.35 부근에서 한 번에 꺾여 면이 셋으로 나뉩니다", color=INK, fontsize=13)
    ax.legend(frameon=False, loc="lower right")
    for s in ax.spines.values():
        s.set_color(GRAY)
    ax.tick_params(colors=SUB)
    fig.text(0.5, -0.02, "설명용 계산 그림 · L = N·L×0.5+0.5", ha="center", color=SUB, fontsize=9)
    fig.savefig(f"{OUT}/02_curves.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc="white", ec=GRAY, color=INK, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=color,
            fontsize=10.5, fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, color=SUB):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14, color=color, lw=1.5))


def fig_pipeline():
    fig, ax = plt.subplots(figsize=(10.5, 4.6), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    ax.text(0.2, 4.25, "A. 셰이더 안에서 직접 계산 (Emissive 출력)", color=INK, fontsize=12, fontweight="bold")
    xs = [0.2, 2.35, 4.5, 6.65]
    labels = ["텍스처", "N·L 직접 계산\n(라이트 방향 노드)", "툰 단계 처리", "Emissive"]
    for i, (x, t) in enumerate(zip(xs, labels)):
        box(ax, x, 3.1, 1.85, 0.8, t)
        if i:
            arrow(ax, xs[i - 1] + 1.85, 3.5, x, 3.5)
    box(ax, 8.75, 3.1, 1.6, 0.8, "그림자 맵\n안 들어옴", fc="#fbe3d3", ec=ACC, color=ACC, bold=True)
    arrow(ax, 6.65 + 1.85, 3.5, 8.75, 3.5, color=ACC)

    ax.text(0.2, 2.35, "B. 엔진 조명을 쓰고 후처리에서 단계 처리 (이번 구현)", color=INK, fontsize=12, fontweight="bold")
    xs = [0.2, 2.35, 4.5, 6.65, 8.75]
    labels = ["Base Color\n= 텍스처", "엔진 조명\n(그림자 맵 포함)", "화면 색 ÷ Diffuse\n= 빛의 양 L", "툰 단계 처리\n(PP_Toon)", "출력"]
    for i, (x, t) in enumerate(zip(xs, labels)):
        hl = i == 2
        box(ax, x, 1.2, 1.6 if i == 4 else 1.85, 0.8, t, fc="#fbe3d3" if hl else "white",
            ec=ACC if hl else GRAY, color=ACC if hl else INK, bold=hl)
        if i:
            arrow(ax, xs[i - 1] + 1.85, 1.6, x, 1.6)
    ax.text(5.25, 0.55, "다른 물체가 드리운 그림자까지 L에 들어 있어서, 그 값을 계단으로 자르면 그림자도 툰 톤이 됩니다",
            ha="center", color=SUB, fontsize=10)
    fig.suptitle("그림자를 받으려면 조명 계산을 엔진에 맡겨야 합니다", color=INK, fontsize=14, y=1.0)
    fig.savefig(f"{OUT}/03_pipeline.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def fig_rim():
    N, mask = sphere()
    V = np.array([0, 0, 1.0])
    ndv = np.clip(N @ V, 0, 1)
    fres = 0.02 + 0.98 * (1 - ndv) ** 2
    rim = smoothstep(0.70 - 0.45, 0.70 + 0.45, fres)
    half = (N @ LIGHT) * 0.5 + 0.5
    base = toon_factor(half)[..., None] * BASE
    rim_col = base + rim[..., None] * (np.array([1.0, 0.97, 1.0]) - base)
    fig = plt.figure(figsize=(10.5, 4.0), facecolor=BG)
    ax1 = fig.add_axes([0.02, 0.08, 0.28, 0.78])
    ax2 = fig.add_axes([0.33, 0.08, 0.28, 0.78])
    ax3 = fig.add_axes([0.68, 0.18, 0.30, 0.66])
    show_sphere(ax1, base, mask, "림라이트 없음")
    show_sphere(ax2, rim_col, mask, "Fresnel 림라이트")
    ang = np.linspace(0, 90, 400)
    f = 0.02 + 0.98 * (1 - np.cos(np.radians(ang))) ** 2
    ax3.set_facecolor(BG)
    ax3.plot(ang, f, color=SUB, lw=2, label="Fresnel")
    ax3.plot(ang, smoothstep(0.25, 1.15, f), color=ACC, lw=3, label="SmoothStep 후")
    ax3.set_xlabel("표면과 시선 사이 각도 (도)", color=INK)
    ax3.set_title("가장자리로 갈수록 값이 커집니다", color=INK, fontsize=11)
    ax3.legend(frameon=False, fontsize=9)
    for s in ax3.spines.values():
        s.set_color(GRAY)
    ax3.tick_params(colors=SUB)
    fig.suptitle("시선과 거의 수직인 테두리만 밝혀 실루엣을 띄웁니다", color=INK, fontsize=14, y=1.0)
    fig.text(0.5, -0.01, "설명용 계산 그림 · Exponent 2, BaseReflect 0.02, SmoothStep(0.25, 1.15)", ha="center",
             color=SUB, fontsize=9)
    fig.savefig(f"{OUT}/04_rim.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def fig_sdf():
    n = 300
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]
    face = (x / 0.78) ** 2 + (y / 0.95) ** 2 <= 1
    # 가상 SDF: 왼쪽 볼에서 오른쪽으로 갈수록 커지는 값. 코 근처를 살짝 휘게 만든다.
    sdf = np.clip(0.5 + 0.5 * (x / 0.78) + 0.08 * np.exp(-((x - 0.05) ** 2 + (y + 0.05) ** 2) / 0.02), 0, 1)
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.4), facecolor=BG)
    img = np.ones((n, n, 3)) * 0.93
    img[face] = np.stack([sdf] * 3, -1)[face]
    axs[0].imshow(img, extent=(-1, 1, -1, 1))
    axs[0].set_title("SDF 텍스처 (회색값)", color=INK, fontsize=11)
    skin = np.array([0.98, 0.90, 0.86])
    shade = skin * np.array([0.95, 0.74, 0.69])
    for ax, deg in zip(axs[1:], [0, 60, 110]):
        fdotl = np.cos(np.radians(deg))
        th = 0.5 - 0.5 * fdotl
        lit = smoothstep(th - 0.01, th + 0.01, sdf)
        col = shade + (skin - shade) * lit[..., None]
        im = np.ones((n, n, 3)) * 0.93
        im[face] = col[face]
        ax.imshow(im, extent=(-1, 1, -1, 1))
        ax.set_title(f"빛이 정면에서 {deg}°  (경계 {th:.2f})", color=INK, fontsize=11)
    for ax in axs:
        ax.axis("off")
    fig.suptitle("빛 각도로 임계값만 바꿔 미리 그린 그림자 경계를 잘라 씁니다", color=INK, fontsize=14, y=1.02)
    fig.text(0.5, -0.02, "설명용 가상 SDF · 실제 얼굴 텍스처가 아님 · 경계 = 0.5 - 0.5×cos(각도)", ha="center",
             color=SUB, fontsize=9)
    fig.savefig(f"{OUT}/05_sdf.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def fig_hull():
    fig, ax = plt.subplots(figsize=(8, 4.6), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_aspect("equal")
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-2.2, 1.9)
    ax.axis("off")
    ax.add_patch(Circle((0, 0), 1.15, fc=INK, ec="none", zorder=1))
    ax.add_patch(Circle((0, 0), 1.0, fc="#c9b6e4", ec="none", zorder=3))
    th = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    for t in th:
        p = np.array([np.cos(t), np.sin(t)])
        ax.add_patch(FancyArrowPatch(p * 1.0, p * 1.32, arrowstyle="-|>", mutation_scale=9, color=ACC, lw=1.2, zorder=4))
    ax.text(0, 0, "원래 메시", ha="center", va="center", color=INK, fontsize=11, zorder=5)
    ax.text(1.55, 1.25, "노멀 방향으로\n부풀린 복제 메시\n(앞면은 버리고 뒷면만 그림)", color=INK, fontsize=10)
    ax.text(-3.1, -1.75, "카메라 쪽에서 보면 원래 메시 바깥으로\n삐져나온 뒷면만 남아 테두리가 됩니다", color=SUB, fontsize=10)
    ax.add_patch(FancyArrowPatch((0, -2.15), (0, -1.3), arrowstyle="-|>", mutation_scale=14, color=SUB, lw=1.5))
    ax.text(0.15, -2.05, "카메라", color=SUB, fontsize=10)
    fig.suptitle("Inverted Hull: 메시를 한 번 더 부풀려 그려 외곽선을 만듭니다", color=INK, fontsize=14, y=0.98)
    fig.savefig(f"{OUT}/06_hull.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    fig_spheres()
    fig_curves()
    fig_pipeline()
    fig_rim()
    fig_sdf()
    fig_hull()
    print("ok")
