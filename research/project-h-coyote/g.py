"""ProjectH 코요테 타임 글의 그림. sim.py가 남긴 result.json을 읽습니다."""
import json, os
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for p in ["C:/Windows/Fonts/NotoSansKR-Regular.ttf", "C:/Windows/Fonts/NotoSansKR-Bold.ttf"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = ["Noto Sans KR", "Malgun Gothic"]
plt.rcParams["axes.unicode_minus"] = False
BG, INK, SUB, GRAY, ACC = "#eceef1", "#2b2f36", "#6b7280", "#b8bcc4", "#e0567a"
os.makedirs("fig", exist_ok=True)
R = json.load(open("result.json", encoding="utf8"))

# 01: 발판을 벗어난 뒤 몇 번째 프레임까지 점프가 나가나
fig, ax = plt.subplots(figsize=(9, 3.4), facecolor=BG); ax.set_facecolor(BG)
rows = [("0.10초", R["window"]["0.10"]), ("0.15초 (현재)", R["window"]["0.15"])]
for r, (label, ok) in enumerate(rows):
    yy = 1 - r
    for k, j in enumerate(ok, start=1):
        ax.add_patch(plt.Rectangle((k - .42, yy - .32), .84, .64, fc=ACC if j else GRAY, ec="none"))
        ax.text(k, yy, "점프" if j else "낙하", ha="center", va="center", fontsize=9, color="white" if j else INK)
    ax.text(.3, yy, label, ha="right", va="center", fontsize=11, color=INK)
for k in range(1, 13):
    ax.text(k, -.62, f"{k}", ha="center", fontsize=10, color=INK)
    ax.text(k, -.92, f"{R['drop_px'][str(k)]:.0f}px", ha="center", fontsize=8.5, color=SUB)
ax.text(.3, -.62, "프레임", ha="right", fontsize=10, color=SUB); ax.text(.3, -.92, "떨어진 높이", ha="right", fontsize=8.5, color=SUB)
ax.set_xlim(-1.4, 12.6); ax.set_ylim(-1.15, 1.5); ax.axis("off")
ax.set_title("코요테 타임 0.15초면 발판을 벗어난 뒤 9프레임째(약 25px 낙하)까지 점프가 나간다", fontsize=12, color=INK, loc="left")
fig.text(.01, .01, "1/60초 고정 스텝, web/game.js의 점프 판정을 옮긴 시뮬레이션 (research/project-h-coyote/sim.py)", fontsize=8, color=SUB)
fig.tight_layout(); fig.savefig("fig/01_coyote_window.png", dpi=160, facecolor=BG); plt.close(fig)

# 02: 같은 타이밍(8프레임째)에 눌렀을 때의 궤적
fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=BG); ax.set_facecolor(BG)
ax.add_patch(plt.Rectangle((0, 396), 120, 20, fc="#8a7f73", ec="none")); ax.text(60, 430, "발판", ha="center", color=SUB, fontsize=10)
ax.axhline(576, color="#8a7f73", lw=3); ax.text(10, 568, "바닥", color=SUB, fontsize=10)
for name, color, lw, label in (("late_010", INK, 2, "0.10초: 8프레임째 입력이 무시되어 떨어짐"), ("late_015", ACC, 3, "0.15초: 8프레임째 입력으로 점프")):
    p = R["paths"][name]; xs = [q[1] for q in p if q[1] < 520]; ys = [q[2] for q in p if q[1] < 520]
    ax.plot(xs, ys, color=color, lw=lw, label=label, ls="-")
ax.axvline(132, color=SUB, lw=1, ls=":"); ax.text(135, 300, "발판 판정 끝\n(가장자리 +12px)", color=SUB, fontsize=9)
ax.set_ylim(600, 150); ax.set_xlim(0, 520)
ax.set_xlabel("x (px)", color=SUB); ax.set_ylabel("y (px, 아래로 증가)", color=SUB)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(colors=SUB)
ax.legend(loc="upper right", frameon=False, fontsize=9.5)
ax.set_title("같은 늦은 입력도 0.15초 창 안에서는 점프로 이어진다", fontsize=12, color=INK, loc="left")
fig.text(.01, .01, "오른쪽 300px/s 걷기, 중력 1650px/s², 점프 속도 810px/s. 시뮬레이션 값이며 게임 화면 캡처가 아닙니다.", fontsize=8, color=SUB)
fig.tight_layout(); fig.savefig("fig/02_trajectories.png", dpi=160, facecolor=BG); plt.close(fig)
print("ok")
