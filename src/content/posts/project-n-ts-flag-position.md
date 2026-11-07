---
title: "[Project N] 깃발이 플레이어마다 다른 위치에 세워짐"
published: 2026-11-07
description: "클라이언트가 보낸 좌표를 그대로 깃발 위치로 써서, 서 있던 자리마다 깃발 위치가 달라졌다."
category: 트러블슈팅
project: project-n
tags: ["Unity", "Netcode for GameObjects", "서버 권위"]
draft: false
---

## 증상

깃발을 세운 플레이어가 존 안 어디에 서 있었느냐에 따라 깃발 위치가 제각각이었습니다.

## 원인

클라이언트가 보낸 자기 위치(`transform.position`)를 깃발 스폰 좌표로 그대로 사용했습니다.

```csharp
// Before: 클라이언트가 위치를 정해서 서버에 보냄
SpawnFlagServerRpc(transform.position);

[ServerRpc]
void SpawnFlagServerRpc(Vector3 spawnPosition)
{
    if (!FlagZone.Instance.IsInsideZone(spawnPosition)) return;
    Instantiate(prefab, spawnPosition, ...);
}
```

- 존 안이기만 하면 <strong>어느 좌표든</strong> 통과 → 위치가 매번 다름
- 게임 규칙에 영향을 주는 값을 클라이언트 입력으로 받는 구조라, 좌표를 조작하면 원하는 위치에 깃발을 세울 수도 있음

## 해결

ServerRpc 파라미터에서 좌표를 없애고, 서버가 `FlagZone.GetFlagSpawnPosition()`으로 위치를 결정합니다.

```csharp
// After: 클라이언트는 "세우겠다"는 의도만 보내고, 위치는 서버가 정함
SpawnFlagServerRpc();

[ServerRpc]
void SpawnFlagServerRpc()
{
    Vector3 spawnPosition = FlagZone.Instance.GetFlagSpawnPosition();   // bounds.center + offset
    ...
}
```

- 오프셋(`flagSpawnOffset`)은 `[SerializeField]`로 빼서 디자이너가 씬에서 조정 가능

## 결과

누가 세워도 깃발이 존 중앙(+오프셋)에 고정되고, 클라이언트 좌표 조작 여지도 사라졌습니다.

## 배운 점

ServerRpc에는 <strong>의도(intent)만</strong> 담고, 결과값(위치·데미지 등)은 서버가 계산한다. 프로젝트 학습 목표였던 "무엇을 서버가 결정해야 하는가"의 대표 사례입니다.

> <strong>기여: 본인</strong> · 깃발 스폰 위치 서버 결정 (`70c35551`, FlagZone.GetFlagSpawnPosition)
