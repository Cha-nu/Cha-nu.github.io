# 그림 05~06: 정규화 유무에 따른 이동 속도, 도착 처리 (sim.py의 result.json을 읽는다)
import json
from lib import *

R = json.load(open("result.json", encoding="utf-8"))
dt = R["dt"]; C = R["chase"]

# 05 정규화하지 않으면 거리에 따라 속도가 달라진다 -------------------------------
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), dpi=150)
for ax, mode, title in [(axs[0], "raw", "❌ 정규화 없이: 위치 += 적까지의 벡터 × 속도 × dt"),
                        (axs[1], "norm", "✅ 정규화 후: 위치 += 방향 × 속도 × dt")]:
    n = int(2.0 / dt)
    t = np.arange(n) * dt
    ax.plot(t, C[f"{mode}_3"]["v"][:n], color=GRAY, lw=2.4, label="적이 3칸 떨어짐")
    ax.plot(t, C[f"{mode}_100"]["v"][:n], color=RED, lw=2.4, label="적이 100칸 떨어짐")
    ax.set_yscale("log"); ax.set_ylim(0.3, 1500); ax.set_xlim(0, 2)
    ax.set_xlabel("시간 (초)", fontsize=11); ax.set_ylabel("이동 속도 (칸/초, 로그 눈금)", fontsize=11)
    ax.set_title(title.replace("❌ ", "").replace("✅ ", ""), fontsize=12, fontweight="bold")
    ax.grid(True, which="major", color="#eee"); clean(ax); ax.legend(frameon=False, fontsize=10.5)
axs[0].annotate(f"시작 속도 {C['raw_100']['v0']:.0f}칸/초", (0, C['raw_100']['v0']), (0.35, 900), fontsize=11, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
axs[0].text(0.04, 24, f"시작 속도 {C['raw_3']['v0']:.0f}칸/초", fontsize=10.5, color=GRAY)
axs[1].text(1.0, 8.5, "두 경우 모두 5칸/초", fontsize=11.5, color=RED, ha="center")
axs[1].text(1.0, 1.2, "3칸짜리는 0.6초에 도착해서 멈춘다", fontsize=10.5, color=GRAY, ha="center")
fig.suptitle("정규화하지 않으면 100칸 떨어진 적에게 500칸/초로 달려간다 (의도한 속도 5칸/초)", fontsize=14, fontweight="bold", y=1.02)
fig.text(0.5, -0.04, "단순화 모델: 2D, 1/60초 고정 스텝, 속도 5칸/초. 수치는 Python 시뮬레이션의 참고값입니다.", ha="center", fontsize=9.5, color="#777")
fn = "fig/05_normalize_speed.png"; fig.savefig(fn, facecolor="white", bbox_inches="tight"); trim(fn); plt.close(fig)

# 06 도착할 때 한 걸음이 남은 거리보다 크면 떨린다 ---------------------------------
A = R["arrive"]; naive = np.array(A["naive"]); safe = np.array(A["safe"])
f0 = 44; f1 = 66
fr = np.arange(len(naive))
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
ax.axhline(0, color=INK, lw=1); ax.text(f1 + 0.3, 0, "적 위치", va="center", fontsize=10.5, color=INK)
ax.plot(fr[f0:f1], naive[f0:f1], "o-", color=RED, lw=1.8, ms=5, label="문제: 정규화만, 매 프레임 0.083칸씩 이동")
ax.plot(fr[f0:f1], safe[f0:f1], "s-", color=BLUE, lw=1.8, ms=4.5, label="해결: 한 걸음을 남은 거리로 자르고, 길이 0이면 멈춤")
ax.set_xlim(f0, f1 + 3); ax.set_ylim(-0.12, 0.62)
ax.set_xlabel("프레임 (60fps)", fontsize=11); ax.set_ylabel("적까지 남은 거리 (칸)\n음수 = 지나침", fontsize=11)
ax.annotate("0.076칸 앞 ↔ 0.007칸 뒤를\n영원히 오간다", (60, -0.0074), (55.5, -0.095), fontsize=10.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
ax.legend(frameon=False, fontsize=10.5, loc="upper right"); clean(ax); ax.grid(True, color="#f0f0f0")
fig.suptitle(f"한 걸음(0.083칸)보다 가까워지면 정규화만으로는 멈추지 못하고 떨린다", fontsize=14, fontweight="bold", y=1.0)
fig.text(0.5, -0.04, "플레이어 (2, 4) → 적 (5, 1), 거리 4.24칸, 속도 5칸/초. 남은 거리는 처음 방향 기준 부호를 붙였습니다.", ha="center", fontsize=9.5, color="#777")
fn = "fig/06_arrival_jitter.png"; fig.savefig(fn, facecolor="white", bbox_inches="tight"); trim(fn); plt.close(fig)
print("ok")
