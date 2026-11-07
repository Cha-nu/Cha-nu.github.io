---
title: "[MeowTractive] Steam 온라인 아키텍처"
published: 2026-11-07
description: "리슨 서버 + Steam OSS로 인프라 없이 방 목록·재접속·초대를 처리하고, Widget→GameInstance→SessionSubsystem 3층으로 흐름과 I/O를 분리했다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "Online Subsystem Steam", "리슨 서버"]
draft: false
---

4인 파티게임, 매치 3분 — 데디케이티드 인프라 없이 <strong>리슨 서버 + Steam OSS</strong>로 방 목록·NAT 릴레이·친구 초대를 전부 무료로 해결했습니다. 개발 중에는 AppId 480(Spacewar)으로 스토어 등록 없이 전부 테스트했습니다.

<iframe src="https://www.youtube-nocookie.com/embed/w24qL32UedA" title="Steam 온라인 흐름" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 3층 구조

위젯은 맵 전환 때 파괴되는 객체라 흐름의 주인이 될 수 없습니다. 그래서 <strong>Widget(표현) → GameInstance(Flow, 트래블 전담) → SessionSubsystem(I/O, IOnlineSession 래핑)</strong> 3층으로 책임을 잘랐습니다.

```text
[Widget]  HostGame()/JoinGame() 호출 + 결과 이벤트 구독만. 네트워크·트래블 금지
[Flow]    UMTGameInstance — ServerTravel/ClientTravel, 빠른시작 상태머신, 중복클릭 가드
[I/O]     UMTSessionSubsystem — Create/Find/Join/Destroy/Update, 결과만 방송
```

## 세션 순환

방 생성 → 세션 광고(방이름·비번유무·모드·맵을 커스텀 키로 기록, 접속 없이 검색에 노출) → `ServerTravel("Lobby?listen")` → 로비에서 설정 변경 시 광고 갱신 → 매치 시작 시 `SetSessionJoinable(false)`로 검색 숨김/조인 거부 → 종료 후 다시 모집, 순서로 세션 하나가 순환합니다.

세션 인터페이스는 반드시 <strong>Initialize에서 획득, Deinitialize에서 해제</strong>해야 합니다. 생성자에서 잡으면 CDO가 SharedPtr을 영구 보유해 엔진 종료 시 ensure가 터집니다.

```ini
[OnlineSubsystem]
DefaultPlatformService=Steam
[OnlineSubsystemSteam]
bEnabled=true
SteamDevAppId=480
[/Script/Engine.GameEngine]
+NetDriverDefinitions=(DefName="GameNetDriver",
  DriverClassName="/Script/SocketSubsystemSteamIP.SteamNetDriver",
  DriverClassNameFallback="/Script/OnlineSubsystemUtils.IpNetDriver")
```

## 결정 정리

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 서버 모델 | 리슨 서버 | 4인 파티게임 — 데디 인프라 무가치, 비용 0, 호스트 이점 수용 |
| 백엔드 | Steam OSS | 방 목록+NAT 릴레이+초대 무료, OSS 추상화로 Null(LAN)과 코드 수정 없이 호환 |
| 구조 | Widget→GameInstance→SessionSubsystem | 트래블 주체는 맵 전환에서 살아남는 객체여야 함 |
