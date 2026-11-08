---
title: "[MeowTractive] 강퇴된 플레이어의 재접속 차단"
published: 2026-11-07
description: "KickPlayer는 연결만 끊을 뿐 정책 상태를 기억하지 않아, 강퇴된 플레이어가 같은 방에 다시 입장할 수 있었습니다."
category: 트러블슈팅
project: meowtractive
tags: ["Unreal Engine", "로비", "Online Subsystem Steam"]
draft: false
---

## 증상

방장이 `GameSession->KickPlayer()`로 내보내도, 이건 현재 연결만 끊을 뿐 "강퇴됐다"는 정책 상태를 기억하지 않아 강퇴된 플레이어가 서버 브라우저에서 같은 방을 다시 선택해 들어올 수 있었습니다.

<iframe src="https://www.youtube-nocookie.com/embed/p9d04F3gSxs" title="강퇴 후 재입장 버그" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---
## 원인

정상 나가기·크래시·타임아웃·강퇴는 네트워크 관점에서 전부 "연결 종료"로 동일하지만 게임 정책은 달라야 합니다(강퇴만 재접속 차단). 이 구분이 없어 강퇴가 사실상 "잠깐 쫓아내기"에 그쳤습니다.

---
## 해결

강퇴 성공 시에만(실패 시 기록 안 함) 대상의 `FUniqueNetIdRepl`을 호스트 `UMTGameInstance`의 `TSet<FString>`에 기록하고, 다음 `PreLogin`에서 `Super::PreLogin`보다 먼저 검사합니다.

```cpp
const FUniqueNetIdRepl TargetId = Target->GetUniqueId();   // Kick 전에 미리 복사
if (GameSession->KickPlayer(TargetPC, KickReason)) { GI->AddKickedPlayer(TargetId); }

// PreLogin — Super 호출 전에 검사해 "만석" 대신 명확한 강퇴 사유 반환
if (GI && GI->IsPlayerKicked(UniqueId)) {
    ErrorMessage = TEXT("이 세션에서 강퇴되어 다시 참여할 수 없습니다.");
    return;
}
```

`GameMode`는 맵 전환마다 새로 생기지만 `GameInstance`는 로비↔매치 사이에서 유지되므로, 세션이 지속되는 동안 차단 목록도 함께 유지됩니다. 거부된 클라이언트는 `JoinSession` 자체는 이미 성공했을 수 있어, `PendingConnectionFailure`에서 로컬 `DestroySession`도 함께 호출해 `AlreadyInSession` 재발을 막습니다.

<strong>부수 버그</strong>: 거부 사유를 담은 `MessageDialog`가 이전 월드에 만들어져 `?closed` 트래블에 함께 제거되며 잠깐 보이다 사라졌습니다. 해결은 사유를 `GameInstance`의 `PendingDisconnectMessage`에 먼저 저장해두고, 트래블 후 새로 뜰 메인메뉴가 `ConsumeDisconnectMessage()`로 한 번만 소비하도록 분리한 것입니다. ("튕김 사유는 GameInstance가 보관, 메뉴가 소비" 패턴 재사용)

---
## 결과

영구 밴이 아닌 <strong>현재 세션 한정</strong> 차단입니다. 호스트가 새 세션을 만들면 `KickedPlayerIds.Reset()`으로 초기화됩니다. 비정상 종료(크래시·타임아웃)는 차단 목록에 안 남아 재접속이 계속 허용됩니다.

<iframe src="https://www.youtube-nocookie.com/embed/Cb08ZSB8hBs" title="강퇴 후 재입장 차단 결과" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

| 상황 | 차단 목록 |
| --- | --- |
| 같은 로비 유지 / 매치 이동 / 로비 복귀 | 유지 |
| 호스트가 새 세션 생성 / 프로세스 종료 | 초기화 |
