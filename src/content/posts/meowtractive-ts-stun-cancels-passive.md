---
title: "[MeowTractive] 스턴 한 번에 패시브가 영구 취소"
published: 2026-11-07
description: "스턴 콜백의 CancelAllAbilities()가 grant-once 패시브까지 취소해 리스폰 전까지 돌아오지 않았습니다."
category: 트러블슈팅
project: meowtractive
tags: ["Unreal Engine", "GAS", "리플리케이션"]
draft: false
---

## 증상

스턴을 맞으면 패시브 스킬 효과가 풀린 뒤 리스폰 전까지 돌아오지 않는 버그가 있었습니다.

<iframe src="https://www.youtube-nocookie.com/embed/9S4ZC0b8IoM" title="스턴 후 패시브 소멸 버그" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

100% "스턴 직후"에만 재현돼 처음엔 GC(가비지 컬렉션)를 의심했지만, 참조 체인이 멀쩡하고 발생 패턴이 GC답지 않아(비주기적이 아니라 트리거와 1:1) 곧 기각했습니다.

---
## 원인

스턴 태그 콜백이 이동 잠금과 함께 `AbilitySystemComponent->CancelAllAbilities()`를 호출해, 시전 중이던 스킬뿐 아니라 <strong>grant-once 패시브까지 전부 취소</strong>했습니다.

```cpp
void AMTPlayerCharacter::OnStunTagChanged(const FGameplayTag Tag, int32 NewCount)
{
    if (!IsLocallyControlled()) return;   // 이동 권위 게이트
    if (bStunned) {
        Move->DisableMovement();
        AbilitySystemComponent->CancelAllAbilities();   // 범인 — 패시브까지 전부 취소
    }
}
```

패시브(`UGA_EyeBeamRangePassive` 등)는 `OnGiveAbility`에서 <strong>단 한 번만</strong> 자동 발동해 무한 GE를 유지하는 구조라, 취소되면 `EndAbility`가 GE를 회수하고 <strong>재발동 트리거가 없어 영구 소멸</strong>합니다.

`IsLocallyControlled()` 게이트 때문에 콜백이 <strong>피해자를 조작 중인 머신에서만</strong> 실행돼, 호스트가 맞으면 서버 권위 취소로 패시브가 진짜 죽고, 클라가 맞으면 클라 단독(비권위) 취소로 시전 중이던 스킬만 서버와 어긋납니다. "패키징에서만 재현"의 정체는 빌드가 아니라 <strong>호스트가 직접 맞았는가</strong>였습니다.

---
## 해결

취소의 범위를 줄이고(태그 한정), 권위를 바로잡았습니다(스킬 취소는 서버, 이동 잠금은 소유 클라).

```cpp
void AMTPlayerCharacter::OnStunTagChanged(const FGameplayTag Tag, int32 NewCount)
{
    if (HasAuthority() && NewCount > 0) { CancelActiveSkills(); }  // 서버 권위, 액티브(Skill.*)만
    if (!IsLocallyControlled()) return;
    // 이동 잠금/복원은 기존과 동일 — CancelAllAbilities만 제거
}
// 이중 방어: 패시브는 애초에 취소 불가로
UGA_EyeBeamRangePassive::UGA_EyeBeamRangePassive() { bIsCancelable = false; }
```

---
## 결과

스턴 전후로 패시브가 유지되고, 클라 피해자의 스킬 먹통 증상도 함께 해소됐습니다.

| 교훈 | 내용 |
| --- | --- |
| CancelAllAbilities는 산탄총 | 시전 중인 것만 끊고 싶으면 반드시 태그 필터(`CancelAbilities(&Tags)`) |
| grant-once 패시브는 취소에 약합니다 | 취소되면 영구 소멸 — `bIsCancelable=false`로 처음부터 보호 |
| 태그 콜백은 머신마다 다르게 돕니다 | 한 콜백 안에서도 "이 일의 권위는 어디인가"를 항목별로 분리 |
| "패키징에서만"은 대부분 착시 | 진짜 변수는 빌드가 아니라 네트워크 역할(호스트/클라) |
