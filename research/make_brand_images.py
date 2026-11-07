"""블로그 배너·아바타 생성 스크립트.

배너는 비행 이론 3편의 2D 점질량 모델과 같은 방식(고정 타임스텝, 받음각 기반 양력,
실속 후 양력 감소)으로 여러 궤적을 적분해 그린 것이다. 장식용이라 계수는 보기 좋게 고른 값이다.
색은 사이트 테마(oklch hue 220)에서 뽑았다: 배경 #070f11 → #004357, 강조 #00b1da.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import io, os

OUT = os.path.join(os.path.dirname(__file__), "..", "public", "assets")
BG0, BG1, ACC = "#070f11", "#004357", "#00b1da"
rng = np.random.default_rng(7)

def trajectory(v0, pitch_cmd, steps=900, dt=1/60):
    """2D 점질량: 추력·항력·중력·받음각 양력. 받음각 15도 넘으면 양력이 줄어든다(실속)."""
    pos = np.zeros(2); vel = np.array([v0, 0.0]); theta = 0.0
    pts = []
    for i in range(steps):
        speed = np.linalg.norm(vel) + 1e-6
        gamma = np.arctan2(vel[1], vel[0])
        theta += pitch_cmd(i * dt) * dt
        aoa = theta - gamma
        cl = 2*np.pi*aoa if abs(aoa) < np.radians(15) else 2*np.pi*np.radians(15)*np.sign(aoa)*0.5
        q = 0.5 * speed**2 * 0.004
        lift = q * cl * np.array([-np.sin(gamma), np.cos(gamma)])
        drag = -q * (0.03 + 0.08*cl**2) * vel / speed
        thrust = 9.0 * np.array([np.cos(theta), np.sin(theta)])
        acc = lift + drag + thrust + np.array([0, -9.8])
        vel += acc * dt; pos += vel * dt
        pts.append(pos.copy())
    return np.array(pts)

def draw(w, h, path, n=14):
    fig = plt.figure(figsize=(w/100, h/100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    grad = np.linspace(0, 1, 256)[:, None]
    cmap = LinearSegmentedColormap.from_list("bg", [BG1, BG0])
    ax.imshow(grad, aspect="auto", cmap=cmap, extent=[0, 1, 0, 1], zorder=0)
    # 디버그 뷰 같은 격자
    for x in np.linspace(0, 1, 25): ax.axvline(x, color=ACC, alpha=0.05, lw=0.8, zorder=1)
    for y in np.linspace(0, 1, int(25*h/w)+1): ax.axhline(y, color=ACC, alpha=0.05, lw=0.8, zorder=1)
    for k in range(n):
        f = rng.uniform(0.15, 0.6); a = rng.uniform(0.6, 1.6); ph = rng.uniform(0, 6)
        p = trajectory(rng.uniform(55, 75), lambda t, f=f, a=a, ph=ph: a*np.sin(2*np.pi*f*t + ph))
        p -= p.min(0); span = p.max(0) - p.min(0) + 1e-6
        x = -0.05 + 1.1 * p[:, 0] / span[0]
        y = rng.uniform(0.1, 0.9) + 0.6 * (p[:, 1] - p[:, 1].mean()) / max(span[1], span[0]*0.25)
        alpha = rng.uniform(0.15, 0.55)
        for lw, al in [(6, alpha*0.12), (2.2, alpha*0.35), (0.9, alpha)]:
            ax.plot(x, y, color=ACC, lw=lw, alpha=al, solid_capstyle="round", zorder=2)
        # 진행 방향 삼각형(기체)
        j = int(len(x) * rng.uniform(0.55, 0.95))
        d = np.array([x[j+1]-x[j], (y[j+1]-y[j])*h/w]); d /= np.linalg.norm(d) + 1e-9
        nrm = np.array([-d[1], d[0]]); s = 0.008
        tip = np.array([x[j], y[j]]); sc = np.array([1, w/h])
        tri = np.array([tip + d*s*1.6*sc, tip - d*s*sc + nrm*s*0.8*sc, tip - d*s*sc - nrm*s*0.8*sc])
        ax.fill(tri[:, 0], tri[:, 1], color=ACC, alpha=min(1, alpha*1.6), zorder=3)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=100); plt.close(fig)
    Image.open(buf).convert("RGB").save(path, "WEBP", quality=88)

def avatar(path, size=512):
    fig = plt.figure(figsize=(size/100, size/100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    grad = np.linspace(0, 1, 256)[:, None]
    ax.imshow(grad, extent=[-1, 1, -1, 1], cmap=LinearSegmentedColormap.from_list("a", [BG1, BG0]), zorder=0)
    t = np.linspace(-0.85, 0.85, 200)
    ax.plot(t, 0.35*np.sin(2.2*t) - 0.15, color=ACC, lw=10, alpha=0.25, solid_capstyle="round")
    ax.plot(t, 0.35*np.sin(2.2*t) - 0.15, color=ACC, lw=3.5, solid_capstyle="round")
    ax.text(0, 0.28, "Cn", ha="center", va="center", fontsize=150, fontweight="bold", color="white", family="DejaVu Sans")
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=100); plt.close(fig)
    Image.open(buf).convert("RGB").save(path, "WEBP", quality=92)

os.makedirs(f"{OUT}/banner", exist_ok=True); os.makedirs(f"{OUT}/home", exist_ok=True)
draw(2400, 1100, f"{OUT}/banner/desktop.webp")
draw(1080, 1920, f"{OUT}/banner/mobile.webp", n=10)
for name in ("avatar.webp", "home.webp", "default-logo.webp"):
    avatar(f"{OUT}/home/{name}")
print("done")
