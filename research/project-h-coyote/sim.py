"""ProjectH 코요테 타임 실험.
web/game.js의 updatePlayer에서 점프·중력·발판 판정 부분만 그대로 옮긴 시뮬레이션입니다.
조건: 1/60초 고정 스텝, 오른쪽으로 걷기(최고 300px/s), 높이 396px 발판(폭 120px, 양쪽 판정 여유 12px), 바닥 576px.
결과는 result.json에 남깁니다."""
import json

DT = 1 / 60
FLOOR = 576
PLAT = dict(x=0.0, y=396.0, w=120.0)
JUMP_V, GRAV, VMAX, RUN, ACC = -810, 1650, 1100, 300, 2400


def run(coyote_time, press_frame, frames=60):
    """발판 위를 오른쪽으로 걷다 끝에서 떨어진다. 발판을 벗어난 뒤 press_frame번째 프레임에 점프를 누른다.
    반환: (점프가 나갔는지, 궤적[(t, x, y)], 발판을 벗어난 프레임)"""
    x, y, vx, vy, grounded = PLAT['x'] + PLAT['w'] - 10, PLAT['y'], RUN, 0.0, True
    coyote = jump_buffer = 0.0
    left_at, jumped, path = None, False, []
    for f in range(frames):
        pressed = left_at is not None and f == left_at + press_frame
        if pressed:
            jump_buffer = .12
        jump_buffer -= DT
        coyote = coyote_time if grounded else coyote - DT
        if jump_buffer > 0 and coyote > 0:
            vy, grounded, jump_buffer, coyote, jumped = JUMP_V, False, 0, 0, True
        vx += max(-ACC * DT, min(ACC * DT, RUN - vx))
        old_y = y
        vy = min(VMAX, vy + GRAV * DT); x += vx * DT; y += vy * DT; grounded = False
        p = PLAT
        if p['x'] - 12 < x < p['x'] + p['w'] + 12 and old_y <= p['y'] + 3 and y >= p['y'] and vy >= 0:
            y, vy, grounded = p['y'], 0.0, True
        if y >= FLOOR:
            y, vy, grounded = FLOOR, 0.0, True
        if left_at is None and not grounded:
            left_at = f
        path.append((f * DT, x, y))
    return jumped, path, left_at


def main():
    out = {'window': {}, 'drop_px': {}, 'paths': {}}
    for ct in (.10, .15):
        ok = []
        for k in range(1, 13):
            jumped, path, left = run(ct, k)
            ok.append(jumped)
        out['window'][f'{ct:.2f}'] = ok
        last = max(k for k, j in zip(range(1, 13), ok) if j)
        print(f'코요테 {ct:.2f}s: 벗어난 뒤 {last}프레임({last * DT * 1000:.0f}ms)까지 점프 가능')
    # 벗어난 뒤 k프레임째에 이미 떨어진 높이
    _, fall, left = run(.15, 99)
    for k in range(1, 13):
        out['drop_px'][k] = round(fall[left + k][2] - PLAT['y'], 1)
    print('벗어난 뒤 떨어진 높이(px):', out['drop_px'])
    for name, ct, k in (('fall', .15, 99), ('late_015', .15, 8), ('late_010', .10, 8)):
        out['paths'][name] = run(ct, k, 70)[1]
    apex = run(.15, 1, 80)[1]
    print('점프 최고 높이(발판 기준, px):', round(PLAT['y'] - min(p[2] for p in apex), 1))
    print('발판을 벗어나 0.15초 동안 이동한 거리(px):', round(RUN * .15, 1))
    json.dump(out, open('result.json', 'w', encoding='utf8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
