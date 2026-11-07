---
title: "[MeowTractive] 전투 파이프라인 & 매료 시스템"
published: 2026-11-07
description: "데미지는 메타 어트리뷰트로, CC는 태그/어트리뷰트로 역할을 나누고, 행인의 매료도는 GAS 밖 전용 컴포넌트(FastArray)로 관리해 '같은 스킬, 다른 판정'을 구현했다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "GAS", "FastArray"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/kAqtlTn8P-k" title="전투와 매료" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

같은 매료 스킬이 행인에게는 '매료', 적 고양이에게는 '공격'으로 갈라지는 이중 판정이 이 게임의 핵심 요구사항이었습니다.

## 데미지 — 메타 어트리뷰트 한 곳에서

데미지는 `Hp`에 바로 감소시키지 않고 메타 어트리뷰트 `IncomingDamage`를 거쳐 `PostGameplayEffectExecute` 한 곳에서 클램핑·사망 판정을 모읍니다(방어력·무적 같은 처리를 붙일 자리도 여기 하나).

```text
공격 GA → GE_CatDamage(SetByCaller Data.Damage) → 타깃 IncomingDamage 가산
  → PostGameplayEffectExecute: Hp -= IncomingDamage, Hp==0 → Die(가해자)
```

## CC — 태그와 어트리뷰트로 나누기

CC는 <strong>On/Off 상태(스턴)는 태그(`State.Stun`), 크기·중첩이 있는 상태(감속)는 어트리뷰트(`MoveSpeedMult`, Multiply 연산으로 여러 감속이 자동 곱연산 합성)</strong>로 나눴습니다. GE는 태그/수치만 주고, 실제 이동 제어는 캐릭터가 태그·어트리뷰트 변화를 구독해 CMC를 재계산합니다. 연출은 GameplayCue로 서버에서 한 줄(`ExecuteGameplayCue`)이면 전 클라 전파됩니다.

## 매료도 — GAS 밖 전용 컴포넌트

행인의 매료도는 '행인 × 플레이어당 1개'라 ASC당 고정 세트인 어트리뷰트와 궁합이 나쁩니다. 그래서 행인의 ASC는 접수 창구로만 쓰고, 실제 장부는 `UMTAttractiveComponent`가 <strong>FastArray로 델타 복제</strong>합니다. 100 도달·팬 탈취·7초 회복 정지 같은 규칙도 이 컴포넌트(서버 권위)가 처리하고, `State.AttractiveInProgress/Invulnerable/Attracted` 태그로 GAS와 연결됩니다. "전부 GAS로" 하지 않고, GAS는 적용 통로로만 쓰는 하이브리드입니다.

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 데미지 | 메타 어트리뷰트(IncomingDamage) | 클램핑·사망·(미래의)방어력 처리를 한 곳에 |
| CC | 태그(스턴)/어트리뷰트(감속) | On·Off는 태그, 크기·중첩은 어트리뷰트 |
| 매료도 | GAS 밖 컴포넌트+FastArray | 플레이어별 동적 수치는 어트리뷰트와 궁합 나쁨, 델타 복제로 트래픽 절감 |
