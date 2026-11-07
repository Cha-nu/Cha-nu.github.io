---
title: "ArcRaiders: Wasp"
summary: "공격 드론 'Wasp'로 물자를 지키는 UE5 C++ 웨이브 디펜스"
period: "2026.04 (약 1개월)"
status: 완료
team: "1인 개발"
role: "1인 개발"
engine: "Unreal Engine 5"
stack: ["C++", "CharacterMovementComponent", "NavMesh", "DataTable", "UMG"]
cover: https://i.ytimg.com/vi/XyVbSwWjVcY/hqdefault.jpg
video: https://youtu.be/XyVbSwWjVcY
links:
  - { label: "GitHub", url: "https://github.com/Cha-nu/ArcWasp" }
order: 40
---

## 어떤 프로젝트인가

ARC Raiders의 정찰 드론 "Wasp"를 조종해, 물자를 훔쳐 달아나는 인간 레이더와 적 드론으로부터 보급품을 방어하는 웨이브 디펜스입니다. 블루프린트 의존 없이 C++ 중심으로 게임 프레임워크의 역할 분리를 설계하는 것이 목표였습니다.

핵심 키워드: FloatingPawn → CharacterMovementComponent 마이그레이션, 목표 지향 AI, NavMesh 비행 추종

## 내가 맡은 것

1인 개발입니다.

## 핵심 기능

| 기능 | 요약 |
| --- | --- |
| 6DOF 드론 비행 | 속도 기반 기체 기울임(Tilt), 고도 제어, 호버링 사운드로 드론 조작감 구현 |
| 시야 기반 락온 & 타이머 공격 시퀀스 | 넓은 후보 탐색과 정밀 가림 판정을 분리하고, 화면 중심 우선순위와 이중 총구 타이머로 락온·연사 |
| 목표 지향 AI | Searching → MovingToItem → Escaping 상태 머신으로 훔치고 도주하는 지상형·비행형 적 2종 |
| DataTable 기반 확률 스폰 | 웨이브마다 박스 수·적 구성 비율이 달라지는 난이도 곡선을 데이터로 관리 |
| 라운드 진행, 난이도 곡선과 HUD | GameState가 물자·적·시간·점수를 통합 관리하고 GameInstance와 UMG를 연결 |

## 트러블슈팅

| 문제 | 원인과 해결 |
| --- | --- |
| 이동 시 벽을 뚫고 지나감 | RootComponent로 쓴 `USceneComponent`(DefaultSceneRoot)에 충돌 볼륨이 없어 속도와 무관하게 통과 |
| 비행 적의 지형 회피 | NavMesh는 지상 보행 기준 2D 경로만 제공해 비행 폰에 그대로 쓸 수 없었음 |
