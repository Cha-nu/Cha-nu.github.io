---
title: "증강 알까기 (Augmented Alkagi)"
summary: "뽑은 증강으로 내 알을 강화하는 UE5.8 C++ 1~4인 물리 알까기 대전 (AI · 핫시트 · Steam 온라인)"
start: "2026-07"
period: "2026.07 ~ 진행 중"
status: 진행 중
team: "1인 개발"
role: "1인 개발"
engine: "Unreal Engine 5.8"
stack: ["C++", "GAS", "Chaos Physics", "Online Subsystem Steam", "CommonUI", "Enhanced Input"]
cover: https://i.ytimg.com/vi/-8LXdlx8KaM/hqdefault.jpg
video: https://youtu.be/-8LXdlx8KaM
links:
  - { label: "GitHub", url: "https://github.com/Cha-nu/ProjectA" }
order: 10
---

## 어떤 프로젝트인가

바둑판 위에서 알을 당겼다 놓아 상대 알을 장외로 밀어내는 알까기에, 매치 도중 뽑은 **증강 카드로 내 알의 규칙 자체를 바꾸는 증강 드래프트**를 결합한 1\~4인 개인전입니다. 알이 머스킷을 쏘는 전열보병, 랜스를 든 나이트, 비숍, 얼음 알, UAV 편대를 거느린 모선으로 변신하거나, 서로 다른 아군 알을 직접 발사해 몸통으로 두 번 맞힌 상대 알을 내 편으로 포섭하는 등 증강이 한 판의 흐름을 뒤집습니다.

같은 보드·증강 규칙과 온라인 공통 실행기를 공유하고, **턴 정책과 모드별 진행 로직을 분리해** 세 가지 모드를 제공하는 것이 구조의 핵심입니다.

| 모드 | 진행 방식 |
| --- | --- |
| 일반전 | 싱글플레이와 같은 순차 턴 |
| 동시확정전 | 전원이 비공개로 조준을 확정하고, 서버가 같은 물리 프레임에 일괄 발사 |
| 난장판전 | 알 5개로 동시에 쏘고 받는 실시간 |

핵심 키워드: Actor 기반 GAS, 공통 실행기와 모드별 턴 진행(순차·동시확정·실시간), PhysicsResolutionId 기반 정산, 데이터·실행 분리 증강 파이프라인, Steam 호스트 마이그레이션, 2D 물리 예측 기반 로컬·온라인 AI

---
## 인게임 흐름

![증강 알까기 온라인 인게임 흐름: 턴 정책별 진행](/images/projects/augmented-alkagi/ingame_flow.png)

세 모드 모두 "발사 → 물리 정지 → 정산"을 거쳐 생존 좌석을 판정합니다. 난장판전만 전투 시간 5초마다 주기적으로 정산합니다.

---
## 내가 맡은 것

1인 개발입니다. 게임플레이·네트워크·UI를 C++ 중심으로 구현했습니다.

---
## 사용 기술

| 기술 | 어떻게 썼나 |
| --- | --- |
| Gameplay Ability System | 캐릭터가 아닌 바둑알(`AActor`)이 ASC를 소유하고, 물리 파라미터를 어트리뷰트로 사용 |
| 데이터 주도 설계 | 증강 데이터(C++ Database 테이블)와 실행 규칙(규칙 서브시스템)을 분리하고, 두 목록이 어긋나면 테스트에서 걸러냄 |
| Chaos Physics | 드래그 플릭 충격량과 물리 템포 조절, 임시 효과의 수명을 물리 정산 시점에 묶음 |
| Replication · 서버 권한 | 리슨 서버 판정. 온라인 공통 GameMode와 모드별 서브클래스로 세 모드가 보드·증강 규칙을 공유 |
| Online Subsystem Steam | SteamSockets 리슨 서버, 로비·초대·비밀번호 방·재접속·호스트 마이그레이션 |
| 점수형 게임 AI | 실제 월드를 건드리지 않는 경량 2D 물리 예측으로 샷 후보를 평가하는 휴리스틱 탐색. 로컬 상대와 서버 전용 온라인 AI 좌석 지원 |
| CommonUI · CommonInput · Enhanced Input | Activation Stack으로 입력 모드·포커스 복원, 키보드·게임패드·터치 입력 통합. Slate 입력 전처리기와 커스텀 Analog Cursor로 게임패드 확정 키와 메뉴 포인터 분리 |
| 렌더링 · 연출 | 형태별(바둑알·당구공·폰 등) 사전 분할 메시로 파괴 연출, CustomDepth 스텐실 + 포스트 프로세스 8방향 샘플링 아웃라인 |
| 현지화 · 로딩 | `LOCTEXT` → `.po` → `.locres` 파이프라인으로 5개 언어, 별도 모듈 로딩 스크린이 씬 준비까지 대기 |
