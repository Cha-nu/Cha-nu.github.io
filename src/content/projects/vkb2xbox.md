---
title: "VKB to Xbox"
summary: "VKB 조이스틱을 비롯한 플라이트 스틱 입력을 가상 Xbox 360 컨트롤러로 바꿔 주는 Windows용 매핑 프로그램"
start: "2026-11"
period: "2026.11 ~"
status: 진행 중
team: "개인"
stack: ["Python", "pygame", "vgamepad", "ViGEmBus", "Tkinter"]
cover: /images/devlog/vkb2xbox/2026-11-12/01_gui_stick_connected.png
links:
  - { label: "GitHub", url: "https://github.com/Cha-nu/vkb2xbox" }
order: 80
draft: false
---

## 어떤 프로젝트인가

vkb2xbox는 플라이트 스틱의 축, 버튼, 햇 입력을 가상 Xbox 360 컨트롤러의 입력으로 바꿔 주는 프로그램입니다. 에이스 컴뱃 8을 VKB Gladiator EVO R로 하려고 만들었습니다.

게임이 이 스틱을 지원하지 않지만 Xbox 360 컨트롤러는 지원합니다. 그래서 스틱 입력을 가상 Xbox 360 컨트롤러에 매핑하면 게임은 평범한 Xbox 360 패드가 연결된 것으로 인식합니다. 어떤 스틱 입력을 어떤 패드 입력으로 보낼지는 GUI에서 스틱을 직접 움직여 지정합니다.

---
## 기술적으로 어려웠던 점

- [펌웨어와 캘리브레이션](/posts/vkb2xbox-2026-11-11-firmware-calibration/): 스틱을 처음 연결하고 초기 설정을 한 기록입니다.
- [Xbox 패드 매핑](/posts/vkb2xbox-2026-11-12-joystick-to-xbox-mapping/): 화면 없이 도는 프로그램이 장치를 꽂고 뽑는 것을 감지하지 못한 문제와, 가상 패드가 자기 출력을 다시 읽는 문제를 다뤘습니다.
