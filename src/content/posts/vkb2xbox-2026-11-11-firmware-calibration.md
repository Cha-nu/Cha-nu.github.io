---
title: "[VKB to Xbox] 펌웨어와 캘리브레이션"
published: 2026-11-11
description: "새로 산 VKB Gladiator EVO R에 펌웨어 v2.20.C를 올리고 VKBDevCfg로 캘리브레이션한 과정을 화면 캡처와 함께 기록합니다."
category: 개발일지
project: vkb2xbox
tags: ["VKB", "HOTAS", "조작"]
image: /images/devlog/vkb2xbox/2026-11-11/07_calibration_axes.png
draft: false
---

## 들어가며

VKB Gladiator EVO R을 새로 샀습니다. 쓰기 전에 초기 설정으로 펌웨어 플래싱(flashing)과 캘리브레이션(calibration)을 했습니다.

이 글은 그 과정을 화면 캡처 순서대로 정리한 기록입니다. VKB 공식 영상 [Gladiator NXT and NXT EVO: flashing and calibration](https://youtu.be/2ghsBvOaujg)을 따라 했습니다.

---

## 요구사항

- 스틱에 최신 펌웨어를 올립니다.
- 캘리브레이션을 마쳐 모든 축이 올바른 범위와 중심으로 읽히게 합니다.
- 완료 기준은 VKBDevCfg의 테스트 화면에서 축 값이 정상으로 보이는 것입니다.

---

## 한 일

### 1. 파일 내려받기

[VKB 다운로드 페이지](https://vkbsimcontrollers.com/pages/downloads)에서 세 가지를 받았습니다. 2026년 11월 11일 기준 버전입니다.

| 파일 | 버전 | 용도 |
| --- | --- | --- |
| Firmware for all VKB devices | v2_20_C | 스틱에 올릴 펌웨어 |
| VKB zBootloader | v1.96 | 펌웨어를 올리는 프로그램 |
| VKBDevCfg Device Configurator | v0.93.89 | 설정과 캘리브레이션 프로그램 |

![탐색기에서 본 VKB 폴더. v2_20_C 폴더, crc 텍스트 문서, VKBDevCfg-C 응용 프로그램, ZBootloader2 응용 프로그램이 있습니다.](/images/devlog/vkb2xbox/2026-11-11/01_download_folder.png)

*압축을 풀어 한 폴더에 모은 모습입니다. `v2_20_C` 폴더 안에 기종별 펌웨어 파일이 들어 있습니다.*

### 2. zBootloader에서 장치 선택

`ZBootloader2`를 실행하면 연결된 장치가 목록에 나옵니다. 부트 장치가 없다는 안내와 함께 `VKBsim Gladiator EVO R v2.20.C`가 보였고, 이 줄을 더블클릭했습니다.

![Z-Bootloader 창. 위쪽에 No Boot device라고 나오고, 아래 목록에 No bootloader found, but some NJoy32 controllers detected. Select device (DoubleClick) 안내와 VKBsim Gladiator EVO R v2.20.C 항목이 있습니다.](/images/devlog/vkb2xbox/2026-11-11/02_zbootloader_select_device.png)

*목록의 장치를 더블클릭하면 스틱이 부트로더 모드로 들어갑니다.*

장치 이름에 보이는 것처럼 출고 상태의 펌웨어가 이미 v2.20.C였습니다.

### 3. 펌웨어 파일 고르기

파일 선택 창에서 `Gladiator_NXT_series` 폴더를 열면 파일이 여섯 개 있습니다. 스틱 이름(Gladiator EVO R)에 맞는 `_Gladiator_EVO_v2_20_C.vkb`를 골랐습니다.

![파일 열기 창. Gladiator_NXT_series 폴더에 _Gladiator_EVO_OTA_v2_20_C.vkb, _Gladiator_EVO_v2_20_C.vkb, _Gladiator_NXT_OTA_v2_20_C.vkb, _Gladiator_NXT_v2_20_C.vkb, _GNX_USB_Controller_Mod_Start_v2_20_C.vkb, _GNX_USB_Controller_v2_20_C.vkb가 있고 _Gladiator_EVO_v2_20_C가 선택되어 있습니다.](/images/devlog/vkb2xbox/2026-11-11/03_firmware_file.png)

*EVO와 NXT, 그리고 각각의 OTA 파일이 따로 있습니다. 기종에 맞는 파일을 골라야 합니다.*

### 4. 플래싱

부트 장치가 잡히면 위쪽 표시가 `Boot device: detected - OK`로 바뀌고 오른쪽 버튼이 `Flash It!`이 됩니다. 이 버튼을 눌러 펌웨어를 올렸습니다.

![Z-Bootloader 창. 위쪽에 Boot device: detected - OK, 파일 칸에 _Gladiator_EVO_v2_20_C.vkb, 오른쪽에 Flash It! 버튼, 아래 로그에 Found Boot Device : zBoot Njoy32가 나옵니다.](/images/devlog/vkb2xbox/2026-11-11/04_boot_device_detected.png)

*로그에 `Found Boot Device : zBoot Njoy32`가 나오면 올릴 준비가 된 상태입니다.*

### 5. VKBDevCfg에서 확인

`VKBDevCfg-C`를 실행하면 장치 목록에 `VKBsim Gladiator EVO R  XT2 v2.20C`가 나옵니다.

![VKB Device Config v0.93.89 창. 장치 목록에 VKBsim Gladiator EVO R XT2 v2.20C가 선택되어 있고, Action 탭에 Restart, Get, Set, Load, Save 버튼이 있습니다. Global 탭의 Basic 영역에 Calibrated가 체크되어 있습니다.](/images/devlog/vkb2xbox/2026-11-11/05_devcfg_global.png)

*펌웨어 버전이 v2.20C로 표시됩니다.*

### 6. 캘리브레이션

`Tools` 탭에는 `Default`, `Start Calibr`, `End Calibr`, `Cancel Calibr.` 버튼이 있습니다. 먼저 `Default` 버튼으로 설정을 초기화했습니다. 초기화가 끝나자 캘리브레이션이 필요하니 지금 하겠느냐는 경고 창이 떴습니다.

![VKB Device Config의 Tools 탭. Default, Bootloader, Start Calibr, End Calibr, Cancel Calibr., Device Report, Make Reg File, Parking 버튼이 있고, 가운데에 Need to calibrate controller !!! Do it now ? 경고 창이 떠 있습니다. Basic 영역은 Non Calibrated로 표시됩니다.](/images/devlog/vkb2xbox/2026-11-11/06_need_calibrate.png)

*`Basic` 영역의 표시가 `Non Calibrated`로 바뀌어 있습니다.*

캘리브레이션 중에는 `Test` 탭의 `Axes1`에서 축 값을 볼 수 있습니다. 여기서 스틱을 앞뒤로 움직이고(피치), 옆으로 움직이고(롤), 비틀고(요), 스로틀을 올려 테스트했습니다. 그 뒤 `Tools` 탭의 `End Calibr` 버튼을 눌러 캘리브레이션을 마쳤습니다.

![VKB Device Config의 Test 탭 Axes1 화면. 오른쪽 위에 Calibration이라고 표시되어 있고, Axis X 32767, Axis Y 32767, Axis Z 37898, Rot X 32767, Rot Y 32767, Rot Z 32767이 슬라이더와 함께 나옵니다.](/images/devlog/vkb2xbox/2026-11-11/07_calibration_axes.png)

*축 여섯 개의 현재 값입니다. Axis Z만 37898이고 나머지는 가운데 값인 32767입니다.*

---

## 결과

캘리브레이션을 마친 뒤 축은 정상으로 읽혔습니다. 막힌 부분은 없었습니다.

---

## 다음 할 일

- [x] 스틱 입력을 Xbox 패드 입력으로 바꾸는 프로그램 만들기 → [Xbox 패드 매핑](/posts/vkb2xbox-2026-11-12-joystick-to-xbox-mapping/)
