---
title: "[MeowTractive] 로비→매치 상태머신 & Seamless Travel 설계"
published: 2026-11-07
description: "PostLogin/HandleSeamlessTravelPlayer 핸드셰이크로 로딩을 동기화하고, PlayerIndex를 매료도·타게팅의 키로 삼아 로비→매치 전환을 설계했다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "로비", "Seamless Travel"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/q4_OPXGMVfk" title="로비에서 매치로 전환" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

스플래시→메인메뉴→로비→전환→인게임까지, 모든 상태 변경은 서버 권한(`HasAuthority`)이 원칙입니다. 맵마다 전용 GameMode(`AMTLobbyGameMode`/`AMTMatchGameMode`)를 두고, 세션·매치·인원 데이터는 GameState·PlayerState로 복제합니다.

## 로딩 동기화

로딩 화면 자체는 Async Loading Screen(검정 화면)이 트래블 중 자동으로 진행되지만, <strong>전원이 로딩을 마친 뒤 동시에 시작</strong>시키는 동기화는 별도로 필요했습니다. 그래서 클라 RPC 없이 엔진 훅만으로 처리했습니다.

```cpp
// 서버가 각 플레이어의 로딩 완료를 훅에서 직접 표시 — 클라 RPC 불필요
HandleSeamlessTravelPlayer(seamless) / PostLogin(non-seamless) → bIsLoaded=true
ReadyToStartMatch(): NumTravellingPlayers==0 && 전원 bIsLoaded → true → StartMatch()
```

## PlayerIndex가 핵심 메커닉의 연결점

서버가 `PostLogin`에서 빈 슬롯(0~3)을 부여해 `AMTPlayerState::PlayerIndex`로 복제하면, 이 값이 스폰 슬롯 매핑·스코어보드 순서뿐 아니라 <strong>행인 매료도 배열(`TArray<float> CharmByPlayer`)의 키</strong>, 적/아군 판별 기준으로 그대로 재사용됩니다. 로스터는 `StartMatch` 직전 확정되고, `CharmByPlayer` 초기화도 그 이후 서버에서 이뤄집니다.

Seamless Travel에서는 `SelectedCatType`/`TeamId`만 `CopyProperties`로 운반하고, `bIsLoaded`/`bIsReady`는 레벨마다 새로 리셋합니다. ASC는 (이 설계 문서 기준으로는) PlayerState에 두어 리스폰이 잦아도 어트리뷰트·매료도·태그가 유지되게 했습니다.

## 예외 처리

60초 타임아웃 시 초과 클라를 `GameSession->KickPlayer`로 정리 후 남은 인원으로 강제 시작하고, 호스트 증발은 클라의 `OnNetworkFailure`가 로컬 `OpenLevel(MainMenu)`로 자동 복귀시킵니다.

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 로딩 동기화 | PostLogin/HandleSeamlessTravelPlayer 핸드셰이크 | 별도 클라 RPC 없이 엔진 훅만으로 처리 |
| PlayerIndex | 서버 발급 슬롯(0~3) | 스폰·UI·매료도 배열·적아 판별의 단일 키 |
| 로딩 화면 | Async Loading Screen | 트래블 중 자동 표시 — 별도 Trans_Map 불필요(기본은 직행) |
