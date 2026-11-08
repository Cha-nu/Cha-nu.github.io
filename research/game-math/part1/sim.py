# 게임 수학 1편: 좌표와 벡터 — 본문 수치를 내는 시뮬레이션
# 단순화 모델: 2D, y-up, 단위는 "칸", 1/60초 고정 스텝, float64
# 결과는 result.json에 저장하고 그림 스크립트(g*.py)가 읽는다.
import json, math

DT = 1.0 / 60.0
SPEED = 5.0          # 칸/초
PLAYER = (2.0, 4.0)
ENEMY = (5.0, 1.0)


def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, s): return (a[0] * s, a[1] * s)
def length(v): return math.sqrt(v[0] * v[0] + v[1] * v[1])
def normalized(v):
    L = length(v)
    return (v[0] / L, v[1] / L)   # 길이 0이면 ZeroDivisionError (float 나눗셈이면 NaN)


out = {"dt": DT, "speed": SPEED}

# 1) 기본 연산 확인
a, b = (3.0, 4.0), (1.0, 2.0)
out["ops"] = {"sum": add(a, b), "diff": sub(a, b), "scaled": mul(a, 2), "len_a": length(a),
              "norm_a": normalized(a), "norm_len": length(normalized(a))}
out["to_enemy"] = sub(ENEMY, PLAYER)
out["to_enemy_len"] = length(sub(ENEMY, PLAYER))
out["dir"] = normalized(sub(ENEMY, PLAYER))


# 2) 정규화 안 한 이동 vs 정규화한 이동: 적까지 거리 3칸, 100칸
def chase(dist, mode, frames):
    p, e = (0.0, 0.0), (dist, 0.0)
    d_hist, v_hist = [], []
    for _ in range(frames):
        to = sub(e, p)
        d = length(to)
        if mode == "raw":
            step = mul(to, SPEED * DT)
        else:
            if d < 1e-9:
                step = (0.0, 0.0)
            else:
                step = mul(normalized(to), min(SPEED * DT, d))
        d_hist.append(d)
        v_hist.append(length(step) / DT)
        p = add(p, step)
    return d_hist, v_hist


chase_res = {}
for dist in (3.0, 100.0):
    for mode in ("raw", "norm"):
        frames = int(25 / DT)
        d, v = chase(dist, mode, frames)
        # 남은 거리가 처음의 10% 이하가 되는 시각
        t90 = next((i * DT for i, x in enumerate(d) if x <= 0.1 * dist), None)
        chase_res[f"{mode}_{int(dist)}"] = {"d": d, "v": v, "v0": v[0], "t90": t90}
out["chase"] = chase_res


# 3) 도착 처리: 남은 거리보다 한 걸음이 클 때
def arrive(mode, frames=70):
    p = PLAYER
    hist = []
    nan_frame = None
    for i in range(frames):
        to = sub(ENEMY, p)
        d = length(to)
        # 부호 있는 남은 거리: 적을 지나쳤으면 음수
        dirv = normalized(sub(ENEMY, PLAYER))
        signed = to[0] * dirv[0] + to[1] * dirv[1]
        hist.append(signed)
        if mode == "naive":          # 정규화만 하고 그대로 한 걸음
            step = mul(normalized(to), SPEED * DT)
        elif mode == "clamp_unsafe":  # 한 걸음을 남은 거리로 자르지만 길이 0 검사 없음
            if d == 0.0:
                nan_frame = i
                break
            step = mul(normalized(to), min(SPEED * DT, d))
        else:                         # 길이 검사 + 자르기
            step = (0.0, 0.0) if d < 1e-4 else mul(normalized(to), min(SPEED * DT, d))
        p = add(p, step)
    return hist, nan_frame


naive, _ = arrive("naive")
safe, _ = arrive("safe")
_, nan_frame = arrive("clamp_unsafe")
out["arrive"] = {"naive": naive, "safe": safe, "step": SPEED * DT,
                 "arrive_time": out["to_enemy_len"] / SPEED,
                 "first_zero_frame_unsafe": nan_frame,
                 "naive_tail": naive[-6:]}

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

# 본문에 쓰는 값 출력
print("ops", out["ops"])
print("to_enemy", out["to_enemy"], "len", round(out["to_enemy_len"], 3), "dir", [round(x, 3) for x in out["dir"]])
for k, r in chase_res.items():
    print(k, "v0", round(r["v0"], 2), "t90", None if r["t90"] is None else round(r["t90"], 3))
print("step", round(SPEED * DT, 4), "arrive_time", round(out["arrive"]["arrive_time"], 3))
print("naive tail", [round(x, 4) for x in naive[-6:]])
print("safe tail", [round(x, 4) for x in safe[-3:]])
print("unsafe: 남은 거리가 정확히 0이 되는 프레임", nan_frame)
