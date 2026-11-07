---
title: "[Project: ARK] 판정 방식별 무기 시스템"
published: 2026-11-07
description: "유탄(투사체)·저격(히트스캔)·근접 3종의 서로 다른 충돌·데미지 처리를 각각 구현했다."
category: 핵심 기술
project: project-ark
tags: ["Unreal Engine", "무기 시스템", "충돌"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/YNVKlA3tXzw" title="무기 시스템" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

모든 공격을 하나의 Trace로 통일하지 않고, 무기의 목적에 맞게 Projectile, Hitscan, Sweep, Radial Damage를 선택했습니다. 기본 사격은 탄속과 회피 가능성이, Q 스킬은 다수 적을 정리하는 범위가, E 스킬은 즉시성과 관통력이, 근접 공격은 모션과 판정 프레임의 일치가 각각 핵심입니다.

| 공격 | 판정 방식 | 주요 수치·처리 | 의도한 감각 |
| --- | --- | --- | --- |
| 기본 Bullet | 실제 Projectile + Box Overlap | 적 캐스팅 후 단일 피해, Impact FX, 파괴 | 탄속과 궤적이 보이는 기본 사격 |
| Q Shoulder Bomb | Sphere 충돌 + Radial Damage | 속도 2000, 반경 300, 피해 80 | 여러 적을 정리하는 범위기 |
| E Sniper | 카메라 기반 Multi Line Trace | 거리 10000, 적당 피해 100, Pawn 관통 | 즉시성과 관통력이 강한 정밀 사격 |
| Crunch 근접 | 전방 Sphere Sweep | 반경 75, 거리 150, 피해 30 | 모션과 맞는 근접 타격 |
| Wraith/Howitzer | 총구 소켓 Projectile | Notify 프레임에 생성, 상체 조준 | 발사 모션과 탄 생성의 일치 |

각 무기는 자신의 방식으로 Hit 대상을 구하지만, 판정 이후에는 `ApplyDamage`로 모아 피격 대상이 무기의 구체적인 Trace 구현을 알 필요가 없게 했습니다.

```text
Input / AI Decision → Weapon-specific Query → Valid Target Filtering
  → ApplyDamage → Health / Hit Reaction / Death → Niagara / Sound / HUD Feedback
```

## 중복 판정 방지

무기별로 다르게 처리합니다.

- Sniper: `TSet<AActor*>`로 같은 액터의 여러 컴포넌트 Hit를 한 번으로 합칩니다.
- Crunch: `bHasAppliedDamageThisAttack`으로 같은 공격의 Notify 중복 피해를 막습니다.
- Shoulder Bomb: 폭발 시 자신과 Instigator를 대상에서 제외합니다.
