---
title: "ProjectD"
summary: "6명이 한 달 동안 만든 언리얼 엔진 쿼터뷰 익스트랙션 슈터 팀 프로젝트"
start: "2026-10"           # 확인 필요
period: "한 달"            # 확인 필요: 정확한 시작·종료일
status: 중단
team: "6인 팀"
role: "적 전반 디자인, 적 AI (Behavior Tree, AI Perception), 전장의 안개"
engine: "Unreal Engine"    # 확인 필요: 버전
stack: ["C++", "Behavior Tree", "AI Perception", "Fog of War"]
cover: /images/devlog/project-d/2026-11-08/06_loading_screen.png
order: 70
draft: true
---

## 어떤 프로젝트인가

ProjectD는 6명이 한 달 동안 함께 개발한 쿼터뷰 익스트랙션 슈터입니다. 레이드에 들어가 적과 싸우고 아이템을 얻은 뒤 탈출하고, 베이스에서 다음 출격을 준비하는 흐름을 목표로 했습니다.

부위별 타격, 전장의 안개, 배고픔·탈수·방사능 같은 생존 상태를 넣었고, 마감 직전에 리슨 서버 기반 멀티플레이로 방향을 바꿨습니다. 팀 프로젝트 일정은 끝났지만 게임은 미완성으로 남았습니다.

---
## 내가 맡은 것

- 적 디자인: 적의 전반적인 구성과 행동을 설계했습니다.
- 적 AI: Behavior Tree로 적의 행동 흐름을 만들었습니다.
- 적 감지: AI Perception으로 적이 플레이어를 보고 반응하는 부분을 만들었습니다.
- 전장의 안개: 플레이어 시야 밖을 어둡게 가리는 전장의 안개를 만들었습니다.

![ProjectD DebugLevel의 플레이 화면. 플레이어 주변 원과 손전등 빛이 닿는 부채꼴 영역만 밝고, 나머지는 어둡게 가려져 있습니다. 어두운 영역에도 지형과 함께 적과 물체의 윤곽이 보입니다.](/images/projects/project-d/01_fog_debuglevel.png)

*DebugLevel에서 촬영한 전장의 안개 화면입니다. 안개 속에서 지형뿐 아니라 적과 물체까지 함께 보이는 상태입니다.*

<!-- TODO: 적 종류, 행동 패턴, 감지 방식(시야·청각 등)을 받아서 구체적으로 채웁니다. -->

---
## 기술적으로 어려웠던 점

<!-- TODO: 적 AI 관련 핵심 기술·트러블슈팅 글이 생기면 연결합니다. -->

---
## 돌아보며

- [게임이 미완성으로 남은 이유](/posts/project-d-2026-11-08-unfinished-game/)
