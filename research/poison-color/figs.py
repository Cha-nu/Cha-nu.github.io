"""독 색 글의 그림. 데이터가 아닌 설명용 예시 디자인입니다. (수치는 예시)"""
import os
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle, Polygon

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
HP = "#d64545"        # 체력바 빨강
HEAL = "#5fd35f"      # 회복 초록
PURPLE = "#8e44c9"    # 지속 피해 독
PURPLE_D = "#5b2a86"
GREEN = "#7cfc3a"     # 맹독 (형광 초록)
GREEN_D = "#2f7d12"
GRAY = "#b8bcc4"


def rbox(ax, x, y, w, h, fc, ec="none", r=0.02, lw=1.5, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def _k(ax):
    """축의 가로/세로 비. 원이 찌그러지지 않게 세로 길이에 곱한다."""
    bb = ax.get_position()
    w, h = ax.figure.get_size_inches()
    return (bb.width * w) / (bb.height * h)


def drop(ax, cx, cy, s, fc, ec):
    """물방울 아이콘 (s는 가로 반지름, 축 좌표)"""
    k = _k(ax)
    ax.add_patch(Polygon([[cx - s * 0.8, cy + s * k * 0.6], [cx, cy + s * k * 2.1], [cx + s * 0.8, cy + s * k * 0.6]],
                         fc=fc, ec=ec, lw=2, zorder=4, joinstyle="round"))
    ax.add_patch(Ellipse((cx, cy), 2 * s, 2 * s * k, fc=fc, ec=ec, lw=2, zorder=5))
    ax.add_patch(Polygon([[cx - s * 0.7, cy + s * k * 0.6], [cx, cy + s * k * 1.9], [cx + s * 0.7, cy + s * k * 0.6]],
                         fc=fc, ec="none", zorder=6))
    ax.add_patch(Ellipse((cx - s * 0.35, cy + s * k * 0.2), s * 0.36, s * 0.36 * k, fc="white", alpha=.7, zorder=7))


def skull(ax, cx, cy, s, fc, ec):
    """해골 아이콘"""
    k = _k(ax)
    ax.add_patch(Ellipse((cx, cy + s * k * 0.2), 2 * s, 1.9 * s * k, fc=fc, ec=ec, lw=2, zorder=5))
    ax.add_patch(FancyBboxPatch((cx - s * 0.5, cy - s * k * 1.05), s * 1.0, s * k * 0.7,
                                boxstyle=f"round,pad=0,rounding_size={s*0.15}", fc=fc, ec=ec, lw=2, zorder=4))
    for dx in (-0.4, 0.4):
        ax.add_patch(Ellipse((cx + dx * s, cy + s * k * 0.15), s * 0.55, s * 0.6 * k, fc=ec, zorder=6))
    ax.add_patch(Polygon([[cx - s * 0.1, cy - s * k * 0.35], [cx, cy - s * k * 0.15], [cx + s * 0.1, cy - s * k * 0.35]],
                         fc=ec, zorder=6))
    for dx in (-0.22, 0, 0.22):
        ax.add_patch(Rectangle((cx + dx * s - s * 0.035, cy - s * k * 1.0), s * 0.07, s * k * 0.4, fc=ec, zorder=6))


def bar(ax, x, y, w, h, ratio, fill, tint=None, label=None):
    rbox(ax, x, y, w, h, "#3a3f47", r=0.01)
    rbox(ax, x + 0.004, y + 0.006, (w - 0.008) * ratio, h - 0.012, fill, r=0.008, z=2)
    if tint:  # 독에 걸렸을 때 체력바 위에 덧씌우는 색
        ax.add_patch(Rectangle((x + 0.004 + (w - 0.008) * (ratio - 0.18), y + 0.006), (w - 0.008) * 0.18, h - 0.012,
                               fc=tint, alpha=.85, zorder=3))
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color="white", fontsize=11,
                fontweight="bold", zorder=4)


# ── 그림 1: 두 독의 기원과 색 ─────────────────────────────
def fig1():
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.93, "보라색 독은 투구꽃에서, 초록색 독은 비소 안료에서 왔다",
            ha="center", fontsize=16, fontweight="bold", color=INK)
    cards = [
        (0.05, PURPLE, PURPLE_D, "동양 · 보라색", "투구꽃(Aconitum)",
         "꽃은 푸른 보라색,\n뿌리에 맹독 아코니틴", "#8e44c9"),
        (0.53, "#50c878", GREEN_D, "서양 · 초록색", "파리 그린(Paris green)",
         "구리·비소로 만든\n에메랄드빛 안료,\n물감·벽지·살충제에 쓰였다", "#50c878"),
    ]
    for x, c, cd, head, name, desc, hexc in cards:
        rbox(ax, x, 0.1, 0.42, 0.7, "white", r=0.03)
        rbox(ax, x + 0.03, 0.18, 0.12, 0.54, c, r=0.02, z=2)
        ax.text(x + 0.09, 0.21, hexc, ha="center", fontsize=9, color="white", zorder=3)
        ax.text(x + 0.175, 0.66, head, fontsize=12, color=cd, fontweight="bold")
        ax.text(x + 0.175, 0.55, name, fontsize=12.5, color=INK, fontweight="bold")
        ax.text(x + 0.175, 0.2, desc, fontsize=11, color=SUB, linespacing=1.6)
    ax.text(0.5, 0.03, "색 견본은 대표색을 고른 예시입니다. 실제 꽃·안료의 색은 개체와 입자 크기에 따라 다릅니다.",
            ha="center", fontsize=9, color=SUB)
    fig.savefig(f"{OUT}/01_origin_colors.png", facecolor=BG, bbox_inches="tight")


# ── 그림 2: 빨간 체력바에서 초록 독은 회복과 헷갈린다 ─────────────
def hpbar(ax, x, y, w, h, ratio, seg, mode):
    """mode="poison": 현재 체력 끝 seg만큼을 덧칠(깎일 구간), mode="heal": 현재 체력 뒤로 seg만큼(찰 구간)"""
    iw, ih = w - 0.008, h - 0.012
    rbox(ax, x, y, w, h, "#3a3f47", r=0.01)
    rbox(ax, x + 0.004, y + 0.006, iw * ratio, ih, HP, r=0.008, z=2)
    sx = x + 0.004 + iw * (ratio - 0.18 if mode == "poison" else ratio)
    ax.add_patch(Rectangle((sx, y + 0.006), iw * 0.18, ih, fc=seg, alpha=.9, zorder=3))
    ax.text(x + w / 2, y + h / 2, "72 / 100", ha="center", va="center", color="white", fontsize=10.5,
            fontweight="bold", zorder=4)


def fig2():
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.5, 0.93, "회복이 초록색이면 초록 독은 회복과 잘 구분되지 않는다",
            ha="center", fontsize=16, fontweight="bold", color=INK)
    for x, pc, title, verdict in [
        (0.05, HEAL, "초록 독", "독인지 회복인지 한 번 더 봐야 한다"),
        (0.53, PURPLE, "보라 독", "독과 회복이 바로 갈린다"),
    ]:
        rbox(ax, x, 0.1, 0.42, 0.72, "#1f2329", r=0.03)
        ax.text(x + 0.03, 0.73, title, fontsize=13, color="white", fontweight="bold")
        for y, lab, seg, mode in [(0.5, "독", pc, "poison"), (0.34, "회복", HEAL, "heal")]:
            ax.text(x + 0.03, y + 0.045, lab, fontsize=11, color="#aab0ba", va="center")
            hpbar(ax, x + 0.1, y, 0.29, 0.09, 0.72, seg, mode)
        ax.text(x + 0.03, 0.17, verdict, fontsize=11.5, color="white")
    ax.text(0.5, 0.03, "직접 만든 예시 UI입니다. 실제 게임 화면이 아닙니다. 체력바는 빨강, 회복은 초록으로 가정했습니다.",
            ha="center", fontsize=9, color=SUB)
    fig.savefig(f"{OUT}/02_hpbar_contrast.png", facecolor=BG, bbox_inches="tight")


# ── 그림 3: 내 규칙. 보라 = 지속 피해, 초록 = 맹독 ─────────────
def fig3():
    fig = plt.figure(figsize=(10, 6.4), dpi=150)
    fig.patch.set_facecolor(BG)
    fig.suptitle("보라색은 천천히 깎는 독, 초록색은 한 번에 끝내는 독", fontsize=16, fontweight="bold",
                 color=INK, y=0.97)
    specs = [
        (0.06, "중독 (지속 피해)", PURPLE, PURPLE_D, "drop",
         "1초마다 최대 체력의 3%\n10초 지속 · 겹치면 시간 갱신\n해독하지 않아도 버틸 수 있다"),
        (0.53, "맹독 (즉사급)", GREEN, GREEN_D, "skull",
         "5초 뒤 남은 체력 전부\n그 전에 해독하면 무효\n화면 가장자리도 초록으로"),
    ]
    for x, name, c, cd, icon, rule in specs:
        top = fig.add_axes([x, 0.52, 0.41, 0.36]); top.axis("off")
        top.set_xlim(0, 1); top.set_ylim(0, 1)
        rbox(top, 0, 0, 1, 1, "#1f2329", r=0.05)
        if icon == "drop":
            drop(top, 0.15, 0.4, 0.06, c, "white")
        else:
            skull(top, 0.15, 0.5, 0.075, c, "#14210c")
        top.text(0.3, 0.75, name, fontsize=12.5, color=c, fontweight="bold", va="center")
        top.text(0.3, 0.38, rule, fontsize=10.5, color="#dfe3ea", va="center", linespacing=1.6)

        g = fig.add_axes([x + 0.03, 0.1, 0.36, 0.32]); g.set_facecolor(BG)
        t = [i * 0.5 for i in range(25)]
        if icon == "drop":
            hp = [max(100 - 3 * int(s), 70) if s <= 10 else 70 for s in t]
            g.step(t, hp, where="post", color=c, lw=2.5)
            g.text(6.3, 90, "조금씩 계단처럼", color=cd, fontsize=10)
        else:
            hp = [100 if s < 5 else 0 for s in t]
            g.step(t, hp, where="post", color=GREEN_D, lw=2.5)
            g.axvline(5, color=GREEN_D, ls=":", lw=1)
            g.text(5.4, 50, "5초에 0", color=GREEN_D, fontsize=10)
        g.set_ylim(-5, 110); g.set_xlim(0, 12)
        g.set_xlabel("시간 (초)", fontsize=9, color=SUB); g.set_ylabel("체력", fontsize=9, color=SUB)
        for s in g.spines.values():
            s.set_color(GRAY)
        g.tick_params(colors=SUB, labelsize=8)
    fig.text(0.5, 0.005, "수치는 규칙을 설명하려고 정한 예시입니다. 특정 게임의 데이터가 아닙니다.",
             ha="center", fontsize=9, color=SUB)
    fig.savefig(f"{OUT}/03_my_rule.png", facecolor=BG, bbox_inches="tight")


fig1(); fig2(); fig3()
