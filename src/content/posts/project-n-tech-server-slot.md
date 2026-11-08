---
title: "[Project N] 서버 발급 좌석(slot) 단일 진실"
published: 2026-11-07
description: "색·스폰·세이프존·승리 표기가 전부 서버가 준 좌석 값 하나만 참조합니다."
category: 핵심 기술
project: project-n
tags: ["Unity", "Netcode for GameObjects", "서버 권위"]
draft: false
---

색·스폰·세이프존·승리 표기가 전부 서버가 준 좌석 값 하나만 참조합니다.

---
## 문제의식

NGO의 `OwnerClientId`는 <strong>접속 순번이 아닙니다.</strong> 호스트는 0이지만, 나갔다 다시 들어온 클라이언트는 3, 4, 5…처럼 계속 증가합니다. 이를 `clientId % 4`로 좌석처럼 쓰면 두 플레이어가 같은 색·같은 세이프존을 받는 일이 생깁니다. ([트러블슈팅 글](/posts/project-n-ts-slot-index/))

---
## 구조

- 서버가 스폰 시점에 `playerSlotIndex`(`NetworkVariable<int>`, <strong>Server Write / Everyone Read</strong>)를 한 번 발급
- 이후 모든 표현·규칙은 이 값만 읽음

| 소비처 | 이전 | 이후 |
| --- | --- | --- |
| 스폰 위치 | `clientId % spawnPoints.Length` | 발급 순번 `index` |
| 플레이어·깃발 색 | `OwnerClientId % 4` | `playerSlotIndex` |
| 세이프존 | `OwnerClientId % 4 + 1` | `playerSlotIndex + 1` |
| 리스폰 위치 | `OwnerClientId % spawnPoints.Length` | `playerSlotIndex` |
| HUD 색 / 승리 표기 | clientId 기반 | `Player {slot + 1} Win!` |

```csharp
// GameManager.SpawnPlayer (서버)
int index = currentSpawnIndex % spawnPoints.Length;
movement.playerSlotIndex.Value = index;   // 좌석은 서버만 쓴다
netObj.SpawnAsPlayerObject(clientId, true);
currentSpawnIndex++;
```

---
## 설계 포인트

- <strong>단일 진실(Single Source of Truth)</strong>: 같은 계산을 여러 곳에서 하지 않고, 서버가 한 번 정한 값을 복제만 함
- 클라이언트는 좌석을 바꿀 수 없음(Write 권한 Server) → 색·세이프존 위조 불가
- 새 기능(예: 팀전)도 `playerSlotIndex`만 참조하면 되어 확장 비용이 낮음

> <strong>기여 (공동)</strong> · 서버 발급 playerSlotIndex 도입(스폰·색·세이프존·승리 표기): 팀원 (`b8de8fc7`) / 남아 있던 clientId 기반 리스폰 위치·HUD 색상·깃발 색을 좌석 값으로 이전, 깃발 스폰 위치 서버 결정: <strong>본인</strong> (`96de4eef`, `70c35551`, `7b5df17e`)
