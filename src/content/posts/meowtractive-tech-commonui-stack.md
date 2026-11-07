---
title: "[MeowTractive] CommonUI 3레이어 Activation Stack"
published: 2026-11-07
description: "위젯이 입력 모드·포커스를 스스로 선언하고 활성화 스택이 적용·복원을 대신하게 해, 입력 복원 누락 버그를 구조적으로 없앴다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "CommonUI", "UMG"]
draft: false
---

PC 전용 게임에 CommonUI를 넣은 이유는 크로스플랫폼이 아니라, <strong>위젯 생명주기와 z-order로 여러 개발자가 헷갈리지 않게 하기 위해서</strong>였습니다.

<iframe src="https://www.youtube-nocookie.com/embed/bASZ7Blz4qI" title="CommonUI 스택 동작" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 필수 설정

```ini
[/Script/Engine.Engine]
GameViewportClientClassName=/Script/CommonUI.CommonGameViewportClient
```

이 한 줄이 빠지면 위젯도 뜨고 버튼도 눌리는데 <strong>입력 모드만 안 먹습니다 — 에러도 경고도 안 뜹니다.</strong>

## 선언만 하고 복원은 스택에 맡기기

순정 UMG에서는 창을 열고 닫을 때 `SetInputMode`/커서/포커스 복원을 여는 쪽이 전부 직접 챙겨야 하고, 하나라도 빠뜨리면 "메뉴는 닫혔는데 캐릭터가 안 움직이는" 버그가 납니다. `UCommonActivatableWidget`은 위젯이 `GetDesiredInputConfig()` / `NativeGetDesiredFocusTarget()`으로 <strong>원하는 상태를 선언만</strong> 하게 하고, 적용·복원은 활성화 스택이 자동으로 합니다.

그리기 순서(z-order)까지 없애려면 한 걸음 더 필요합니다. 플레이어별 `UMTUIRootWidget` 아래 <strong>Menu / Modal / Loading 3개 Stack</strong>을 두고 `AddToViewport(50/60/100)` 대신 `PushWidget(Layer, Class)`로 호출부를 통일했습니다. 닫기는 전부 `DeactivateWidget()` 한 줄입니다.

## 함정 셋

1. `CommonButtonBase::OnClicked()`는 non-dynamic 델리게이트 → `NativeDestruct`에서 `RemoveAll(this)` 수동 해제 필요
2. Menu 모드 전환 시 눌려 있던 키의 release가 합성되어 홀드형 스킬이 오발 → 전환 직전 `CancelActiveSkills()`
3. Stack 풀링 — 재사용되는 위젯은 `NativeOnActivated/Deactivated`에서 초기화·방송 (NativeConstruct/Destruct 아님)

| 항목 | 순정 UMG | CommonUI |
| --- | --- | --- |
| 입력 모드 복원 | 직접 짜야 함(누락 시 먹통) | 스택이 자동 복원 |
| z-order | AddToViewport(매직넘버) | Stack 컨테이너가 관리 |
| 버튼 델리게이트 | Dynamic(UPROPERTY) | non-dynamic → 수동 RemoveAll |
