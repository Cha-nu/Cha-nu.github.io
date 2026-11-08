---
title: "[MeowTractive] 고양이 스킬 시스템 (클래스 1개 + TMap)"
published: 2026-11-07
description: "캐릭터 클래스는 하나, 스킬 구성은 TMap 데이터로 분리해 입력↔스킬 결합을 끊고 새 고양이 추가를 BP 데이터 한 줄로 만들었습니다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "GAS", "데이터 주도"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/faFvQW0iPWg" title="고양이 스킬" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

고양이 4종마다 스킬이 다르지만, 캐릭터 클래스는 `AMTPlayerCharacter` <strong>하나</strong>뿐입니다. 종류별 스킬은 `TMap<EMTCatType, FMTCatAbilitySet>` 데이터가 결정합니다.

---
## ASC를 PlayerState가 아니라 Character에 둔 이유

Lyra 등 대부분의 레퍼런스는 ASC를 PlayerState에 둬 리스폰 간 상태를 유지하지만, 묘력만점은 매치가 수 분인 파티게임이라 그 장점이 필요 없었습니다. Owner==Avatar라 `InitAbilityActorInfo` 초기화 순서가 단순해지고, ASC Replication Mode는 Full로 둬 클라에서도 GE/태그를 그대로 볼 수 있게 했습니다.

```cpp
USTRUCT(BlueprintType)
struct FMTCatAbilitySet
{
    TSubclassOf<UGameplayAbility> SkillA;
    TSubclassOf<UGameplayAbility> SkillB;
    TArray<TSubclassOf<UGameplayAbility>> Passives;
};
TArray<TSubclassOf<UGameplayAbility>> DefaultAbilities;   // 전 고양이 공통
TMap<EMTCatType, FMTCatAbilitySet> CatAbilities;          // 종류별
```

---
## 슬롯 번호만 아는 입력

입력 코드는 "지금 Q에 어떤 스킬이 있는지" 모릅니다. `AbilityLocalInputPressed((int32)EMTAbilitySlot::SkillA)`처럼 <strong>슬롯 번호만</strong> GAS에 넘기고, 실제 어빌리티는 `PossessedBy`에서 선택된 고양이의 `FMTCatAbilitySet`을 Grant하는 시점에 결정됩니다. 덕분에 새 고양이 추가 = <strong>C++ 수정 없이 BP에서 TMap 한 줄</strong>입니다. 전 고양이 공통 스킬(대시·매료빔·펀치)은 전용 입력 + `TryActivateAbilitiesByTag`로 태그 발동하는 혼합 구조입니다.

---
## 태그는 전부 네이티브 선언

모든 GameplayTag는 문자열 조회 대신 <strong>C++ 네이티브로 선언</strong>해 오타를 컴파일 타임에 잡습니다(`Skill.*` / `Cooldown.*` / `State.*` / `Event.*` / `Data.*` 접두사로 역할 고정). `State.Casting` 태그 하나로 "시전 중 다른 액션 스킬 금지"를 GA의 `ActivationBlockedTags`에 선언만 하면 끝입니다.

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| ASC 위치 | Character (Full 복제) | 매치가 짧은 파티게임 — 리스폰 간 유지 불필요 |
| 고양이 4종 | 클래스 1개 + TMap | 입력↔스킬 결합 제거, 새 고양이 = BP 데이터 추가 |
| 태그 | 전부 네이티브 선언 | 오타를 컴파일 타임에 |
