# -*- coding: utf-8 -*-
"""pygame(SDL2)이 dummy 비디오 드라이버에서 조이스틱 핫플러그를 감지하는지 확인한다.

가상 Xbox 360 패드(vgamepad + ViGEmBus)를 하나 꽂고 8초 동안 JOYDEVICEADDED
이벤트를 기다린 뒤, 뽑고 4초 동안 JOYDEVICEREMOVED를 기다린다.

    python hotplug_probe.py          SDL_JOYSTICK_THREAD 없이
    python hotplug_probe.py thread   SDL_JOYSTICK_THREAD=1

필요: Windows, pip install pygame vgamepad, ViGEmBus 드라이버
vkb2xbox 개발일지(2026-11-12)의 "막힌 점" 수치가 여기서 나왔다.
"""
import os
import sys
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
if "thread" in sys.argv[1:]:
    os.environ["SDL_JOYSTICK_THREAD"] = "1"

import pygame  # noqa: E402
import vgamepad as vg  # noqa: E402

pygame.display.init()
pygame.joystick.init()
print("SDL_JOYSTICK_THREAD =", os.environ.get("SDL_JOYSTICK_THREAD", "(없음)"))
print("pygame", pygame.version.ver, "SDL", ".".join(map(str, pygame.get_sdl_version())))
pygame.event.get()
before = pygame.joystick.get_count()
print("꽂기 전 장치 수:", before)

pad = None
for _ in range(6):  # 가상 장치는 첫 시도에 실패할 때가 있다
    try:
        pad = vg.VX360Gamepad()
        break
    except Exception as e:
        print("가상 패드 생성 재시도:", e)
        time.sleep(1.0)
if pad is None:
    sys.exit("가상 패드를 만들지 못했습니다.")


def watch(seconds):
    t0 = time.time()
    while time.time() - t0 < seconds:
        for e in pygame.event.get():
            if e.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                print(f"  {time.time() - t0:5.2f}s  {pygame.event.event_name(e.type)}")
        time.sleep(0.05)


print("가상 패드를 꽂고 8초 대기")
watch(8.0)
print("8초 뒤 장치 수:", pygame.joystick.get_count())

del pad
print("가상 패드를 뽑고 4초 대기")
watch(4.0)
print("4초 뒤 장치 수:", pygame.joystick.get_count())
