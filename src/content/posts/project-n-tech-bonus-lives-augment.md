---
title: "[Project N] 판정 파이프라인을 건드리지 않는 증강"
published: 2026-11-07
description: "방어막 대신 생명 추가(bonusLives)로 설계해 공격 판정 코드를 무수정으로 유지했습니다."
category: 핵심 기술
project: project-n
tags: ["Unity", "Netcode for GameObjects", "증강"]
draft: false
---

방어막 대신 생명 추가(bonusLives)로 설계해 공격 판정 코드를 무수정으로 유지했습니다.

---
## 증강 드래프트

게임 시작 시 각 플레이어가 증강 1개를 고르고, 서버가 선택을 확정합니다.

| 증강 | 효과 | 발동 |
| --- | --- | --- |
| Fake Hammer | 깃발 존에 깃발을 세우는 척하는 미끼를 남기고 본체는 옆으로 숨음 (미끼를 때리면 공격이 소모됨) | N 키 (1회 충전) |
| Cloaking | 일정 시간 은신, 맞거나 망치를 들면 해제 | N 키 (1회 충전) |
| Add Life | 최대 생명 +2 | 선택 즉시 |

---
## 왜 방어막을 버렸나

처음엔 <strong>Shield</strong>(공격 1회 막기 + 1초 무적)였습니다. 그런데 이를 구현하려면 공격 판정 코드 안에 `TryBlockIncomingAttackWithShield()` 분기와 무적 코루틴, 막기 연출 RPC가 들어가야 했습니다. 증강 하나 때문에 <strong>모든 공격이 지나가는 판정 파이프라인</strong>이 증강 종류를 알아야 하는 구조였습니다.

그래서 같은 "한 번 더 버티기" 경험을 <strong>생명 수치</strong>로 옮겼습니다. 판정은 그대로 `TakeDamage → LoseLife`만 호출하고, 증강은 생명 상한만 바꿉니다.

```csharp
// PlayerHealth (서버 전용)
public int MaxLives => maxLives + bonusLives.Value;

public bool TryAddLives(int amount)
{
    if (!IsServer || amount <= 0 || isDead || isSpectator.Value) return false;
    bonusLives.Value += amount;
    currentLives.Value += amount;
    return true;
}
```

---
## 서버 검증

- `SelectAugmentServerRpc`: 이미 고른 경우·정의되지 않은 enum 값·None은 <strong>서버가 거절</strong> → 중복 선택·값 위조 차단
- 발동 RPC도 서버에서 `SelectedAugment`·충전 여부·게임 종료 여부를 다시 확인
- 선택 결과는 `NetworkVariable`(Server Write)로만 복제

> <strong>기여: 본인</strong> · 증강 드래프트 시스템·UI (`3b7a2690`), 방어막 증강 제거 후 bonusLives 기반 생명 추가 증강으로 재설계 (`70c35551`)
