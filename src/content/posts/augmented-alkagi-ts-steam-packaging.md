---
title: "[증강 알까기] 멀티 패키징 오류"
published: 2026-11-07
description: "패키지에서만 Steam 멀티가 동작하지 않았습니다. Steam 테스트 설정이 패키지에서 빠지고, Shipping EXE를 직접 실행하면 App ID를 못 찾는 두 원인을 각각 고쳤습니다."
category: 트러블슈팅
project: augmented-alkagi
tags: ["Unreal Engine", "Online Subsystem Steam", "패키징"]
draft: false
---

## 증상

에디터 PIE와 Standalone에서는 Steam 로그인·방 생성이 되는데, <strong>패키지 빌드에서만 온라인 기능이 통째로 동작하지 않았습니다.</strong> 로그상으로는 Steam 대신 NULL OSS로 폴백해 방 검색·참가가 의미가 없어진 상태였습니다.

---
## 해결 과정

NULL OSS 폴백의 원인 후보로 Steam 설정 누락을 의심해, 패키지에 Steam 설정이 실제로 들어갔는지부터 확인했습니다. 패키지의 Config 폴더에 테스트용 Steam 설정이 없는 것을 발견해 스테이징 단계를 고쳤습니다. 그 뒤 Development 패키지는 동작했지만, Shipping EXE를 Steam 밖에서 직접 실행하는 경우는 여전히 Steamworks 초기화에 실패해 따로 원인을 찾았습니다.

---
## 원인

| 원인 | 내용 |
| --- | --- |
| 커스텀 설정 누락 | Steam 테스트 App ID(480)는 출시 설정과 섞이지 않도록 `Config/Custom/SteamTest/DefaultEngine.ini`에 분리해 뒀는데, UAT에 `-CustomConfig=SteamTest`만 넘기면 <strong>Custom 폴더가 스테이징에서 제외</strong>됐습니다 |
| Shipping App ID 부재 | Development 빌드는 `steam_appid.txt`로 App ID를 찾지만, <strong>Shipping은 Steam 클라이언트가 넘겨주는 환경 변수에 의존</strong>합니다. Steam 라이브러리를 거치지 않으면 App ID가 없습니다 |

---
## 해결

- <strong>Cook</strong>: `-AdditionalCookerOptions="-CustomConfig=SteamTest"`로 쿠커에도 같은 프로필을 전달했습니다.
- <strong>Stage</strong>: `PackageCandidate.ps1`이 `Config/Custom/SteamTest`를 패키지에 명시적으로 복사합니다. SteamTest 프로필은 Shipping 선택을 거부해 480이 출시 빌드에 섞이지 않게 했습니다.
- <strong>Shipping</strong>: `PostConfigInit` 단계에 로드되는 별도 런타임 모듈 `ProjectASteamBootstrap`을 추가했습니다. 설정 파일이 읽힌 직후, OSS 초기화 <strong>전</strong>에 실행됩니다. 플랫폼 서비스가 Steam이고 App ID가 <strong>480일 때만</strong>, `SteamAppId`와 `SteamGameId`가 <strong>둘 다 없을 때만</strong> `SteamAppId=480`을 프로세스 환경 변수에 설정합니다. `SteamGameId`는 직접 설정하지 않습니다. 에디터·커맨드릿·전용 서버, Win64 이외 플랫폼에서는 동작하지 않습니다.
- <strong>검증</strong>: SteamTest Development 패키지에서 `[AppId: 480] Client API initialized`와 Steam 사용자 인식을 확인했고, 자동 진단(`AASteamAudit`)이 45초 뒤 정상 종료하는 것까지 확인했습니다.

---
## 배운 점

"패키지에서만 안 된다"는 코드보다 <strong>패키지에 무엇이 들어갔는지</strong>부터 봐야 합니다. 테스트용 설정은 출시 설정과 분리하되, 분리한 설정이 실제로 스테이징되는지와 출시 빌드에 섞이지 않는지를 함께 막아야 합니다.

> 초기 단계의 `Unknown Cook Failure`도 실제로는 에셋 경로 불일치(`/Game/UI` → `/Game/AA/UI`)·플러그인 스캔 범위·생성자에서의 물리 머티리얼 적용 세 원인이었습니다. 그때부터 검증 기준을 "로그 성공"이 아니라 <strong>실행 화면에 메인 메뉴가 실제로 보이는지</strong>까지로 잡았습니다. 실제 App ID 발급 후 재검증이 필요합니다.
