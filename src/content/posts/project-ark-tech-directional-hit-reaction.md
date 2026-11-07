---
title: "[Project: ARK] 방향별 피격 연출"
published: 2026-11-07
description: "내적·외적 연산으로 공격 방향을 판정해 Front/Back/Left/Right 몽타주를 자동 재생한다."
category: 핵심 기술
project: project-ark
tags: ["Unreal Engine", "애니메이션", "게임 수학"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/z-4rxAmSL7A" title="방향별 피격" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

공격 방향과 무관하게 같은 피격 모션만 재생하면 충격의 방향성이 사라지고, 방향마다 소켓·콜라이더를 추가하면 캐릭터가 늘수록 관리 비용이 커집니다. 공격자의 월드 위치를 적의 로컬 방향으로 해석해 Front/Back/Left/Right 피격 몽타주를 선택했습니다.

```cpp
const FVector Direction = (AttackerLocation - EnemyLocation).GetSafeNormal();
const float Dot = FVector::DotProduct(EnemyForward, Direction);
const FVector Cross = FVector::CrossProduct(EnemyForward, Direction);
```

| 조건 | 판정 | Montage Section |
| --- | --- | --- |
| Dot ≥ 0.5 | 정면 | Front |
| Dot ≤ -0.5 | 후면 | Back |
| -0.5 < Dot < 0.5, Cross.Z > 0 | 오른쪽 | Right |
| -0.5 < Dot < 0.5, Cross.Z ≤ 0 | 왼쪽 | Left |

내적은 앞·뒤를 나누고 옆 영역에서는 외적의 Z 부호가 좌·우를 결정해, 별도 방향 콜라이더 없이 공격자 위치 하나로 판정합니다. 피격 시에는 `DamageCauser` 위치를 저장하고 AI 이동을 즉시 정지, 이동 모드를 `MOVE_None`으로 바꿔 몽타주 재생 중 NavMovement 간섭을 막은 뒤 `HitStunTimer` 종료 후 `MOVE_Walking`으로 복구합니다.

<iframe src="https://www.youtube-nocookie.com/embed/z_B-hS5zvZs" title="방향별 피격 결과" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 한계

현재 방향 분기는 Wraith와 Howitzer의 생존 피격 반응에만 적용되어 있고, 사망은 `DeathFor` 계열 고정 모션을 사용합니다. 중복된 방향 계산과 경직 처리는 `UHitReactionComponent` 또는 `AC_EnemyBase`로 이동해 공통화할 수 있습니다.
