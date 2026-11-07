---
title: "[Project: ARK] 적 AI 로직 (역할별 사거리 & NavMesh 추적)"
published: 2026-11-07
description: "근접·중거리·원거리 세 역할이 하나의 공통 베이스에서 파생되어 각자의 전투 거리를 유지하도록 설계한 AI 이동/공격 로직"
category: 핵심 기술
project: project-ark
tags: ["Unreal Engine", "AI", "NavMesh"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/RqAT6RFOm1s" title="적 AI" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Project Ark의 적 AI는 하나의 공통 베이스 클래스에서 파생된 세 가지 역할이 서로 다른 이동속도와 공격 사거리를 유지하도록 설계했습니다. 개별 AI를 새로 작성하는 대신 공통 의사결정 로직을 재사용하고 역할별 수치만 다르게 부여함으로써, 플레이어가 근접·중거리·원거리 압박을 동시에 받는 전투 구도를 만드는 것이 핵심 의도입니다.

## 역할 구성

세 파생 클래스는 동일한 베이스 로직 위에서 이동속도와 공격 사거리, 공격 방식만 다르게 설정되어 있습니다.

| 역할 | 성격 | 이동속도 | 공격 사거리 | 공격 방식 |
| --- | --- | --- | --- | --- |
| Crunch | 근접 압박 | 450 | 150 | 3연속 콤보 / 전방 Sphere Sweep |
| Howitzer | 중거리 견제 | 350 | 800 | 총구 소켓 Projectile |
| Wraith | 고속 원거리 | 600 | 1000 | 총구 소켓 Projectile |

## 의사결정 흐름

매 Tick마다 아래 흐름을 따라 이동과 공격 여부를 판단합니다.

```text
1. 체력 / 공격 대기시간 / 공격 중 상태를 확인한다
2. 플레이어와 AAIController의 유효성을 확인한다
3. 전방 장애물 및 다른 적 유닛을 감지해 측면 이동각도를 갱신한다
4. 갱신된 각도로 개인 목표점을 계산하고 NavMesh 위로 투영한다
5. 목표점이 공격 사거리 안에 들어오면 이동을 멈추고 플레이어 방향으로 회전한다
6. 사거리 밖이면, 목표점이 이전과 크게 달라졌거나 이전 이동이 끝났을 때만 이동을 재요청한다
7. 사망 시 이동과 공격을 즉시 중지하고 GameMode에 사망을 통지한다
```

## NavMesh 안정화 설정

적이 NavMesh 밖으로 밀려나거나 이동 요청이 매 프레임 반복되는 문제를 막기 위해 아래 설정을 사용했습니다.

```text
NavAgentRadius       : 42
NavAgentHeight       : 192
MaxStepHeight        : 75
ProjectPointToNavigation 탐색 범위 : (200, 200, 300)

목표점 투영 실패 시 폴백 체인으로 재탐색
Move 재요청 조건 : 마지막 목표점과 100cm 이상 차이 나거나, 이전 이동이 종료되었을 때만
요청 간격 : 최소 0.25초
```

목표점을 임의의 좌표가 아니라 NavMesh 위로 투영된 좌표로 제한하고, 재요청 조건에 거리 임계값과 최소 간격을 함께 두어 다수의 적이 동시에 활동할 때도 경로 재계산 빈도를 낮추도록 했습니다. (관련: [적 AI 일렬 뭉침 문제](/posts/project-ark-ts-enemy-clumping/))

## 공격 프레임 동기화

공격 판정은 애니메이션의 실제 접촉/발사 프레임에 맞춰 발생하도록 AnimNotify를 경유합니다.

```text
AI 공격 결정
  → 공격 Montage 재생
    → EnemyAttackImpact Notify 발생
      → HandleAttackImpact() 호출
        → 근접: 전방 Sphere Sweep 실행
        → 원거리: 총구 소켓에서 Projectile Spawn
```

근접 공격의 경우 Sweep 판정 시점에 `HasAuthority()`, 현재 공격 상태 여부, 그리고 이번 공격에서 이미 피해를 적용했는지 여부를 함께 확인하여 한 번의 콤보 모션에서 중복 피해가 들어가지 않도록 처리했습니다.

## 결과와 다음 단계

세 유형의 적이 이동속도와 사거리 차이만으로 서로 다른 압박 패턴을 만들어내고, 공격 판정이 애니메이션의 접촉·발사 프레임과 어긋나지 않으며, 이동 목표가 항상 NavMesh 위의 유효한 좌표로 제한되고, 불필요한 Move 재요청이 줄어들어 다수의 적이 동시에 존재하는 상황에서도 경로 재계산 부담이 낮게 유지되었습니다.

다만 현재는 기본 AAIController와 Tick 기반 의사결정 구조를 그대로 사용하고 있어, 향후 적의 수나 상태 종류가 늘어날 경우 감지·이동·공격 상태를 StateTree로 분리하고 역할별로 갱신 주기를 다르게 조절할 수 있는 구조로 확장하는 것이 더 적합할 것으로 판단됩니다.
