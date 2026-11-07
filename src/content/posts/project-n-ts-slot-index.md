---
title: "[Project N] 색상·세이프존·리스폰이 전부 엉뚱한 플레이어를 가리킴"
published: 2026-11-07
description: "clientId를 좌석 번호로 오용해 같은 계산이 네 곳에 각자 복제되어 있었다."
category: 트러블슈팅
project: project-n
tags: ["Unity", "Netcode for GameObjects"]
draft: false
---

## 증상

- 두 플레이어가 <strong>같은 색</strong>으로 표시됨
- 내 세이프존이 아닌 곳이 내 세이프존으로 판정됨
- 리스폰 시 처음 스폰 위치와 <strong>다른 지점</strong>에서 부활
- HUD 색과 실제 캐릭터 색이 다름

## 원인

NGO의 `OwnerClientId`는 접속할 때마다 증가하는 ID라 0~3에 딱 맞지 않습니다. 그런데 코드 곳곳에서 이를 좌석처럼 썼습니다.

```csharp
int ownerIndex          = (int)(OwnerClientId % 4UL);                 // 색
int ownerSafeZoneIndex  = (int)(OwnerClientId % 4UL) + 1;             // 세이프존
int index = (int)(OwnerClientId % (ulong)spawnPoints.Length);         // 리스폰
int index = (int)(clientId % (ulong)spawnPoints.Length);              // 최초 스폰
```

같은 의도의 계산이 네 곳에 흩어져 있었고, 일부는 나중에 순번 기반으로 바뀌어 <strong>서로 다른 결과</strong>를 냈습니다.

## 해결

1. 서버가 스폰 시점에 `playerSlotIndex`를 발급 (`NetworkVariable`, Server Write)
2. 색·세이프존·승리 표기를 `playerSlotIndex`로 교체
3. 남아 있던 `ResolveRespawnPosition()`(clientId 기반)을 삭제하고 리스폰도 좌석 기준으로 통일
4. HUD 색 매핑도 `targetPlayer.playerSlotIndex.Value`로 교체

## 결과

네 증상이 한 번에 사라졌고, 이후 "플레이어 n번"이 필요한 코드는 전부 `playerSlotIndex` 하나만 읽게 되었습니다. 핵심 기능 "서버 발급 좌석(slot) 단일 진실"로 정리했습니다.

> <strong>기여 (공동)</strong> · playerSlotIndex 도입으로 스폰·색·세이프존·승리 표기 단일화: 팀원 (`b8de8fc7`) / 남은 clientId 기반 리스폰 위치(ResolveRespawnPosition)·HUD 색상 매핑 제거로 마무리: <strong>본인</strong> (`70c35551`, `7b5df17e`)
