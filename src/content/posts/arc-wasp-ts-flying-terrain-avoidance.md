---
title: "[ArcRaiders: Wasp] 비행 적의 지형 회피"
published: 2026-11-07
description: "NavMesh는 지상 보행 기준 2D 경로만 제공해 비행 폰에 그대로 쓸 수 없었다."
category: 트러블슈팅
project: arc-wasp
tags: ["Unreal Engine", "AI", "NavMesh", "비행"]
draft: false
---

## 증상

적 드론이 목표 방향의 벽을 계속 밀고, 경사·높은 구조물·천장을 안정적으로 회피하지 못했습니다. 경로 탐색이 실패하면 장애물과 관계없이 목표로 직진하기도 했습니다.

## 원인

현재 `UpdateDroneMovement`는 `FindPathToLocationSynchronously`로 지상 NavMesh 경로를 구하고 `PathPoints[1]`을 선택한 뒤, 그 경로점의 Z를 드론의 현재 높이로 덮어씁니다.

```cpp
// 문제의 핵심 — NavMesh 경로점의 Z를 현재 고도로 강제 치환
FVector NextPoint = PathPoints[1];
NextPoint.Z = GetActorLocation().Z;   // 수직 장애물·지형 높이 정보를 여기서 버림
```

1. Recast NavMesh는 보행 표면 중심의 2.5D 데이터입니다.
2. Z를 현재 고도로 고정하면서 수직 장애물과 지형 높이 정보를 버립니다.
3. 경로가 없으면 목표 방향 벡터를 직접 사용합니다.
4. 충돌 전 방향을 바꾸는 선제적 Steering이 없습니다.

충돌 컴포넌트가 실제 관통을 막더라도 AI는 계속 벽을 밀거나 모서리에 끼일 수 있습니다.

## 개선 설계

기존 NavMesh는 장거리 XY 우회 방향 제공에만 쓰고 목표 고도는 별도 정책으로 관리합니다.

- 전방·좌우·상하로 Sphere/Capsule Sweep을 하고, 속도에 비례해 감지 거리를 확장합니다.
- Hit Normal과 거리로 회피 벡터를 계산해 `GoalDirection × GoalWeight + Avoidance × AvoidWeight`로 합성합니다.
- 아래 Trace로 지면 최소/목표 고도를 유지하고, 위 Trace로 천장 여유를 검사합니다.
- 일정 시간 이동량이 적으면 Stuck 상태로 전환합니다.
- 직접 이동 fallback은 Sweep이 통과할 때만 허용합니다.

<iframe src="https://www.youtube-nocookie.com/embed/NXAsNYJuxnQ" title="비행 적 지형 회피" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

> 현재 저장소에는 원인 분석 대상인 기존 이동 코드가 있습니다. 위 하이브리드 3D 회피는 <strong>개선 설계</strong>이며 완전 구현 완료로 표현하지 않습니다.

| 구분 | 기존 2.5D Path | 개선 Hybrid 3D Steering |
| --- | --- | --- |
| 고도 처리 | NavMesh 경로점 Z를 현재 고도로 강제 치환 | 목표 고도를 별도 정책으로 관리 |
| 회피 | 없음 — 충돌 후에야 인지 | 다방향 Sweep으로 충돌 전 선제 회피 |
| 경로 실패 시 | 목표 방향으로 직진(Direct Fallback) | Sweep 통과 확인 후에만 직접 이동 허용 |
