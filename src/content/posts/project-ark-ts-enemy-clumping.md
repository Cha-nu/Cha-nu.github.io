---
title: "[Project: ARK] 적 AI 일렬 뭉침 문제"
published: 2026-11-07
description: "적들이 한 지점으로 몰리지 않도록 개체별 랜덤 각도 + 전방 트레이스 회피를 구현했다."
category: 트러블슈팅
project: project-ark
tags: ["Unreal Engine", "AI", "NavMesh"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/RqAT6RFOm1s" title="적 AI 뭉침" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 원인

모든 AI가 매 Tick 플레이어의 정확히 같은 좌표로 `MoveToLocation()`을 요청하면 경로의 마지막 구간이 하나로 수렴해 한 줄로 뭉치고, 목표가 거의 같아도 Move 요청이 반복되어 경로 계산 비용이 증가합니다.

## 해결

생성 시 각 적에 `TargetOffsetAngle`(0~30°)을 부여하고, 플레이어 중심에서 각 적의 `AttackRange × 0.8`만큼 떨어진 지점을 개인 목적지로 계산합니다. 근접·중거리·원거리 적이 각자 필요한 거리에서 접근을 멈출 수 있습니다.

```cpp
// 개인 목적지 = 플레이어 중심 + (AttackRange × 0.8) 방향으로 오프셋 각도만큼 회전
FVector PersonalGoal = PlayerLoc + Rotate(TargetOffsetAngle) * (AttackRange * 0.8f);
// 전방 Trace가 Pawn/WorldStatic/WorldDynamic을 감지하면 목표 각도를 FlankRotationSpeed*DT만큼 이동
// NavMesh 위로 보정 실패 시 플레이어 위치 투영 → 그것도 실패하면 현재 위치로 폴백
FNavLocation Projected;
if (!NavSys->ProjectPointToNavigation(PersonalGoal, Projected, FVector(200,200,300))) { /* fallback */ }
```

새 목표가 마지막 목표에서 2D 거리 `100cm` 이상 달라졌거나 기존 이동이 끝난 경우에만, 그리고 최소 `0.25초` 간격을 두고서만 `MoveToLocation()`을 다시 요청해 Tick 단위 경로 재계산을 막습니다.

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 접근 지점 | 공격 사거리 기반 개인 목적지 + 오프셋 각도 | 역할별 사거리를 실제 정지 위치에 반영, 완전 균등 슬롯보다 저비용 |
| 장애물 대응 | 전방 Trace 감지 시 목표 각도 회전 | 선두 적·고정 장애물에 막히면 다른 진입 방향 탐색 |
| 이동 재요청 | 100cm 임계값 + 0.25초 게이트 | Tick 단위 경로 재계산 비용 절감 |

## 한계와 다음 단계

현재 `TargetOffsetAngle`은 0~30° 범위의 초기 난수라 360° 슬롯을 균등 보장하지 않습니다. 확장 방향으로는 활성 AI 수 기준 슬롯 매니저, 근거리 RVO Avoidance, EQS 점수화 등을 고려할 수 있습니다.
