---
title: "[Project N] 전원 Ready인데 시작 안 됨 / 나간 사람 때문에 시작됨"
published: 2026-11-07
description: "손으로 관리하는 복제 리스트(NetworkList)를 진실로 봤는데 실제 접속 상태와 어긋났습니다."
category: 트러블슈팅
project: project-n
tags: ["Unity", "Netcode for GameObjects", "매치메이킹"]
draft: false
---

## 증상

전원 Ready인데도 시작이 안 되거나, 나간 사람 때문에 시작되는 증상이었습니다.

---
## 상황

로비에서 `LobbyPlayerListSync.Players`(`NetworkList<PlayerLobbyInfo>`)에 접속자와 Ready 상태를 담고, 서버가 `TryStartWhenReady()`에서 전원 Ready면 게임 씬을 로드했습니다.

---
## 원인

- 판정이 `Players.Count`와 `Players[i].IsReady`만 봄 → <strong>리스트에 있는 사람 = 접속자</strong>라고 가정
- 이 리스트는 접속/해제 콜백에서 <strong>손으로 추가·삭제</strong>하는 사본이라, 콜백 순서나 정원 초과 거절 등으로 실제 접속 상태와 어긋날 수 있음
- 이름도 `Player {clientId}`라서 재접속 시 "Player 5"처럼 표시됨

---
## 해결

```csharp
// Before
if (!IsServer || IsStarting.Value || Players.Count < 2) return;
for (int i = 0; i < Players.Count; i++)
    if (!Players[i].IsReady) return;

// After: 실제 접속자 기준으로 돌고, 리스트에 없으면 실패로 처리
if (!IsServer || IsStarting.Value || net.ConnectedClientsIds.Count < 2) return;
for (int i = 0; i < net.ConnectedClientsIds.Count; i++)
    if (!TryGetPlayerReady(net.ConnectedClientsIds[i], out bool isReady) || !isReady) return;
```

- 이름은 좌석 순서 기반 `Player {index + 1}`로 바꾸고, 퇴장 시 `RefreshPlayerNames()`로 재정렬

---
## 결과

두 상태 모두에서 안전한 쪽(시작 안 함)으로 수렴합니다.

---
## 배운 점

복제용 리스트는 <strong>표시용 사본</strong>이고, 게임 시작 같은 결정은 엔진이 관리하는 실제 상태(`ConnectedClientsIds`)를 기준으로 해야 합니다. 판단이 애매하면 "시작하지 않음"으로 떨어지게 만들어 최악의 경우도 안전하게 했습니다.

> <strong>기여: 본인</strong> · Ready 판정을 ConnectedClientsIds 기준으로 변경 (`70c35551`, LobbyPlayerListSync.TryStartWhenReady)
