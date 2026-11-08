---
title: "[Project: ARK] Bullet 터널링 문제"
published: 2026-11-07
description: "고속탄 터널링을 충돌체 크기 확대, 검사 스텝 간격 축소, 관통 저격의 라인 트레이스 전환으로 해결"
category: 트러블슈팅
project: project-ark
tags: ["Unreal Engine", "무기 시스템", "충돌"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/wi0z0JIKriQ" title="총알 터널링" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---
## 증상

고속으로 날아가는 총알(투사체)이 얇은 벽이나 근접한 적을 한 프레임에 그대로 통과해버려, 충돌 판정 자체가 발생하지 않는 터널링 현상이 발생했습니다.

---
## 원인

투사체의 이동 속도가 빨라 한 프레임 동안 이동하는 거리가 콜리전 두께 및 충돌 검사 주기보다 커지면서, 벽이나 적 사이를 "건너뛰는" 구간이 생겼습니다.

---
## 해결

```cpp
// 해결 1) 콜리전(구체) 크기 확대로 판정 폭 자체를 넓힘
BoxComponent->SetBoxExtent(FVector(WiderExtent));
// 해결 2) Substepping/검사 Step 간격 축소로 이동 경로 사각지대 최소화
ProjectileMovement->bSweepCollision = true;   // 이동 중 스윕 검사 강제
// 해결 3) 관통이 필수인 저격은 투사체 대신 즉시 계산되는 Line Trace로 전환
GetWorld()->LineTraceMultiByObjectType(Hits, Start, End, ObjectQueryParams);
```

1. 불릿의 콜리전(구체) 크기를 키워 판정이 걸리는 폭 자체를 넓혔습니다.
2. 매 프레임 충돌 검사 Step 간격을 더 촘촘하게 줄여, 이동 경로 사이의 사각지대를 최소화했습니다.
3. 그럼에도 관통이 필수적인 저격 스킬은 투사체 방식 대신 Line Trace(멀티 트레이스)로 전환하여, 판정을 이동 시뮬레이션이 아닌 즉시 계산 방식으로 바꿨습니다.

| 구분 | 기존(터널링 발생) | 수정 후 |
| --- | --- | --- |
| 충돌체 크기 | 좁은 Box/Sphere | 판정 폭 확대 |
| 검사 방식 | 느슨한 Step 간격 | 촘촘한 Step + Sweep 검사 |
| 관통 저격 | 고속 Projectile | 즉시 계산되는 Line Trace로 전환 |

---
## 결과

터널링 현상이 원천적으로 제거되었고, 관통이 필요한 저격 스킬도 정확도와 성능을 모두 확보할 수 있었습니다.
