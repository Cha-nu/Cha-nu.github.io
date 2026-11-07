---
title: "[MeowTractive] EndAbility가 재충전 타이머를 전부 죽인다"
published: 2026-11-07
description: "EndAbility의 ClearAllTimersForObject(this)가 대시 재충전 타이머까지 삭제해 충전이 영영 회복되지 않았다."
category: 트러블슈팅
project: meowtractive
tags: ["Unreal Engine", "GAS"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/RMzECymsP14" title="대시 재충전 버그" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 증상

대시 3회 충전 후 10초 재충전을 구현했는데, 시전 직후 충전이 영원히 돌아오지 않는 버그가 발생했습니다.

## 원인

`UGameplayAbility::EndAbility`가 내부에서 `ClearAllTimersForObject(this)`를 호출합니다. 대시가 끝나는 순간(0.1초 뒤) GA에 걸어둔 재충전 타이머(10초)가 함께 삭제됐습니다.

## 해결

어빌리티 수명을 넘겨야 하는 타이머는 GA가 아니라 <strong>ASC에 바인딩</strong>했습니다.

```cpp
FTimerDelegate::CreateWeakLambda(ASC, [WeakThis = TWeakObjectPtr<UGA_Dash>(this)]() {
    if (WeakThis.IsValid()) { WeakThis->OnRechargeTick(); }
});
```

`CreateWeakLambda(ASC, ...)`라 타이머의 소유 객체가 ASC가 되고, GA 쪽은 약참조로 잡아 GC에도 안전합니다.

## 결과

대시 종료 후에도 재충전 타이머가 정상 유지되어 10초마다 충전이 회복됩니다.
