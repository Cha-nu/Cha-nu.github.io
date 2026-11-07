---
title: "[MeowTractive] 쿨다운 하이브리드 & 충전형 대시"
published: 2026-11-07
description: "쿨다운 수치는 GA, 태그는 스킬별 GE에 두는 하이브리드로 공용 GE의 컴파일 에러·오판을 피하고, 대시는 어트리뷰트+Cost GE+ASC 타이머로 3회 충전을 구현했다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "GAS"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/KMUyEzhkHfw" title="쿨다운과 충전형 대시" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

스킬 10개마다 쿨다운 GE를 따로 만들면 에셋이 폭발하고, 공용 GE 1개로 합치면 UE5가 컴파일 에러를 내거나(태그 없음) 스킬끼리 쿨다운을 오판합니다(태그 공유).

## 쿨다운 — 수치는 GA, 태그 그릇은 스킬별 GE

엔진은 `CooldownGameplayEffectClass`로 지정한 GE가 정적 `GrantedTags`를 하나도 안 가지면 블루프린트 컴파일 에러를 냅니다. 그렇다고 공용 GE에 태그 하나만 박아 통과시키면, `GetCooldownTags()`가 <strong>GE의 정적 태그 + GA의 CooldownTags를 병합</strong>하기 때문에 모든 스킬이 같은 정적 태그를 공유해 <strong>서로 무관한 스킬까지 쿨다운 중으로 오판</strong>합니다.

```cpp
// 정착한 하이브리드 — 수치는 GA, 태그 그릇은 스킬별 GE(정적 태그 1개)
UPROPERTY(EditDefaultsOnly) float CooldownDuration = 0.f;       // GA에서 튜닝
UPROPERTY(EditDefaultsOnly) FGameplayTagContainer CooldownTags;  // 동적 부여
// 쿨다운 GE: Duration = SetByCaller(Data.Cooldown), 수치 없음. 정적 GrantTags는 스킬당 1개
```

## 충전형 대시 — 세 조각으로 조립

"대시 3회 스택, 10초마다 1회 순차 재충전"은 쿨다운이 0/1뿐이라 표현이 안 돼, <strong>어트리뷰트(DashCharges/MaxDashCharges) + GE_DashCost(Instant, Cost GE로 지정) + GA의 재충전 타이머</strong> 세 조각으로 완전히 별도 조립했습니다. 충전 0이면 GAS의 표준 `CheckCost`가 발동 자체를 막아 직접 체크 코드가 필요 없습니다.

<strong>함정 — EndAbility가 타이머를 전부 죽인다.</strong> `UGameplayAbility::EndAbility`는 내부에서 `ClearAllTimersForObject(this)`를 호출해, 대시 종료(0.1초 뒤) 시 GA에 걸어둔 재충전 타이머(10초)까지 같이 삭제됩니다. ([트러블슈팅 글](/posts/meowtractive-ts-endability-timer/))

```cpp
// 타이머를 ASC에 바인딩해 EndAbility의 ClearAllTimersForObject(this)에서 살아남게 함
FTimerDelegate::CreateWeakLambda(ASC, [WeakThis = TWeakObjectPtr<UGA_Dash>(this)]() {
    if (WeakThis.IsValid()) { WeakThis->OnRechargeTick(); }
});
```

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 쿨다운 | 스킬별 GE(태그 1개) + SetByCaller | 공용 GE는 컴파일 에러이거나 태그 공유로 오판 |
| 충전형 대시 | 어트리뷰트+Cost GE+ASC 타이머 | 표준 CheckCost 재사용, EndAbility 타이머 삭제 회피 |
