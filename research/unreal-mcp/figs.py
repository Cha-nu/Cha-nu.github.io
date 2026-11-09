# 그림 01~02: Claude Code와 Unreal Editor의 연결 구조, 도구 검색(tool search) 흐름
# 데이터가 없는 개념도다. 내용은 Epic 공식 문서와 플러그인 README(3.1.2)를 따른다.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams["font.family"] = ["Noto Sans CJK KR", "Malgun Gothic"]; plt.rcParams["axes.unicode_minus"] = False
RED = "#d9452b"; GRAY = "#8c8c8c"; INK = "#222"; BG = "#f2f2f2"; LINE = "#9a9a9a"


def box(ax, x, y, w, h, title, sub=None, accent=False, fs=12.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="white", ec=RED if accent else LINE, lw=2.2 if accent else 1.3, zorder=3))
    ty = y + h / 2 + (0.17 if sub else 0)
    ax.text(x + w / 2, ty, title, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=RED if accent else INK, zorder=4)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.22, sub, ha="center", va="center", fontsize=9.5, color="#555", zorder=4)


def arrow(ax, p, q, label=None, off=(0, 0.17), both=False, color=INK, fs=10):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=15,
                                 color=color, lw=1.5, zorder=2, shrinkA=2, shrinkB=2))
    if label:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], label, ha="center", va="bottom",
                fontsize=fs, color="#444", zorder=4)


def region(ax, x, y, w, h, label):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                fc=BG, ec="none", zorder=1))
    ax.text(x + 0.15, y + h - 0.12, label, ha="left", va="top", fontsize=11, color="#666", fontweight="bold")


# 01 연결 구조 ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=150)
ax.set_xlim(0, 12); ax.set_ylim(0, 5.2); ax.axis("off")
region(ax, 0.1, 0.25, 3.6, 4.6, "Claude Code (터미널)")
box(ax, 0.4, 3.0, 3.0, 0.95, "Claude 플러그인", "unreal-mcp 스킬 · SessionStart 훅")
box(ax, 0.4, 1.0, 3.0, 0.95, ".mcp.json", "unreal-mcp → 127.0.0.1:8000/mcp")
arrow(ax, (1.9, 2.95), (1.9, 2.0), "어떻게 쓸지", off=(0.62, -0.12))

region(ax, 5.0, 0.25, 6.85, 4.6, "Unreal Editor 5.8 (실행 중이어야 함)")
box(ax, 5.3, 2.0, 2.7, 1.2, "Unreal MCP", "ModelContextProtocol", accent=True)
box(ax, 8.85, 3.15, 2.7, 1.0, "Toolset Registry", "자동으로 켜지는 의존 플러그인")
box(ax, 8.85, 1.0, 2.7, 1.25, "All Toolsets", "실제 도구 (액터, 블루프린트,\n머티리얼, Sequencer …)", accent=True)
arrow(ax, (3.4, 1.47), (5.3, 2.35), "HTTP (localhost)", off=(-0.15, 0.3), both=True)
arrow(ax, (8.0, 2.85), (8.85, 3.5))
arrow(ax, (8.0, 2.35), (8.85, 1.75))
arrow(ax, (10.2, 2.25), (10.2, 3.15), "등록", off=(0.35, -0.15))
ax.text(6.0, 0.5, "빨간 테두리 두 개가 에디터에서 직접 켜야 하는 플러그인입니다.", fontsize=10, color=RED, ha="left")
fig.suptitle("Claude Code는 .mcp.json으로 에디터 안의 MCP 서버에 붙고, 도구는 All Toolsets가 공급한다",
             fontsize=13.5, fontweight="bold", y=0.99)
fig.savefig("fig/01_connection.png", facecolor="white", bbox_inches="tight"); plt.close(fig)

# 02 도구 검색 흐름 ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 3.6), dpi=150)
ax.set_xlim(0, 12); ax.set_ylim(0, 3.6); ax.axis("off")
steps = [("요청", "\"레벨의 액터를\n전부 보여 줘\"", False),
         ("list_toolsets", "어떤 툴셋이\n있는지 본다", True),
         ("describe_toolset", "고른 툴셋의\n함수와 인자를 읽는다", True),
         ("call_tool", "툴셋 이름, 함수 이름,\n인자를 넘겨 실행한다", True),
         ("결과 확인", "성공·실패 상태를\n읽고 다음으로", False)]
w, h, gap = 2.0, 1.55, 0.42
for i, (t, s, acc) in enumerate(steps):
    x = 0.2 + i * (w + gap)
    box(ax, x, 0.75, w, h, t, None, accent=acc, fs=12)
    ax.text(x + w / 2, 0.45, s, ha="center", va="top", fontsize=9.5, color="#555")
    if i:
        arrow(ax, (x - gap, 0.75 + h / 2), (x, 0.75 + h / 2))
ax.text(6.0, 3.15, "MCP 서버가 처음에 알려 주는 도구는 빨간 세 개뿐입니다. 나머지 수백 개는 call_tool로 부릅니다.",
        fontsize=10, color=RED, ha="center")
fig.suptitle("도구 검색이 켜져 있으면 Claude는 세 개의 메타 도구로 필요한 도구를 찾아 부른다",
             fontsize=13.5, fontweight="bold", y=1.04)
fig.savefig("fig/02_tool_search.png", facecolor="white", bbox_inches="tight"); plt.close(fig)
print("ok")
