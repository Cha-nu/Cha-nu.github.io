---
title: "[증강 알까기] Steam Listen Server 세션·재접속·호스트 마이그레이션"
published: 2026-11-07
description: "방 생성·검색·빠른 매칭·비밀번호·재접속을 GameInstance 서브시스템 한 곳에 모으고, 호스트가 나가도 전원 ACK된 체크포인트로 후계 호스트가 매치를 이어받는 호스트 마이그레이션을 구현했다."
category: 핵심 기술
project: augmented-alkagi
tags: ["Unreal Engine", "Online Subsystem Steam", "호스트 마이그레이션"]
draft: false
---

## 요구사항

1~4인이 온라인으로 방을 만들고 찾아 들어와 끝까지 경기를 마칠 수 있어야 했다. 방 생성·검색·빠른 매칭·비밀번호·재접속을 지원하고, 리슨 서버의 약점인 <strong>호스트가 나가면 판 전체가 끝나는</strong> 문제도 막아야 했다.

## 왜 이 기술을 선택했나

개인 프로젝트 규모에서 전용 서버를 운영할 수 없어 <strong>호스트가 서버를 겸하는 Listen Server</strong>로 구성했다. 초기에는 EOS 세션을 썼고, 2026.09 말 <strong>Steam Online Subsystem으로 전환</strong>하면서 Steam 프로필 아바타 표시까지 함께 붙였다. 10월에 EOS 크로스플레이(네이티브 인증·서버 권한 가드)를 한 차례 준비했지만 Steam 우선 출시로 방향을 정해 Steam OSS로 되돌리고, EOS 구현은 아카이브 브랜치에 보존했다.

| 항목 | 설정 |
| --- | --- |
| 플러그인 | `OnlineSubsystemSteam` 활성, `OnlineSubsystemEOS` · `EOSShared` 비활성 |
| NetDriver | `SteamSocketsNetDriver` · P2P Relay (NAT 걱정 없이 리슨 서버 접속) |
| 인증 | `SteamAuthComponentModuleInterface` 패킷 핸들러 |
| 세션 | Steam 로비(`bUseLobbiesIfAvailable`) · Presence · 초대 |

## 어떻게 구현했나

`UAAOnlineSessionSubsystem`(GameInstance 서브시스템)이 로그인부터 세션 파괴까지 전 구간을 소유하고, 모든 비동기 경로가 `CompleteOperation(bSuccess, Message)` 하나로 수렴해 UI는 결과와 메시지만 받는다.

### 방 광고 정보

방 목록에서 바로 판단할 수 있도록 <strong>빌드 ID · 룰셋(모드) · 맵 ID · 방 이름 · 빈 슬롯 수</strong>를 세션 키로 광고한다. 빌드 ID가 다르면 참가 전에 걸러지고, 로컬 참가자 수를 반영한 빈 슬롯 갱신으로 "들어가 보니 만석"인 경우를 없앴다. 빠른 매칭(`AAQuickMatchPolicy`)은 2인 일반전으로 고정했고, 대기 중인 로비끼리는 3초마다 서로를 찾아 <strong>id가 낮은 쪽으로 결정적으로 합친다.</strong> 30초 안에 상대를 못 찾으면 로컬 AI 대전을 제안한다.

OSS Steam은 로비 문자열을 ANSI로 변환해 읽기 때문에 한글 방 이름이 방 목록에서 깨졌다. `AASessionRoomName::Read`가 Steam 로비 데이터의 UTF-8 원문(`<key>_s`)을 직접 읽고, 없을 때만 세션 설정 값으로 되돌아가도록 우회했다.

### 비밀번호 — 평문을 세션에 올리지 않기

세션 설정은 검색하는 누구에게나 보이므로 비밀번호를 그대로 올릴 수 없다.

```text
호스트: Salt 생성 → BuildPasswordVerifier(4096회 해시) → AA_PASSWORD_SALT / NONCE 광고
참가자: 입력한 비밀번호 + Salt + Nonce + 내 계정 ID → JoinToken 생성 → 접속 URL에 첨부
서버:   PreLogin에서 ValidateHostedJoinToken → 실패 시 AA_INVALID_JOIN_TOKEN 으로 거부
```

강퇴한 플레이어는 `IsBannedFromHostedRoom`으로 재입장을 막는다.

### 재접속 정책

매치가 시작돼 명단이 확정되면, `PreLogin`은 <strong>끊긴 플레이어 목록에 있고 예산이 남은 계정만</strong> 받는다(그 외 `AA_RECONNECT_UNAVAILABLE`).

- 계정마다 <strong>매치당 60초 재접속 예산</strong>(`FAAReconnectBudget`)을 실시간 기준으로 차감한다.
- 끊긴 플레이어의 PlayerState는 `bRetainForReconnect`로 보존하고, 호스트 권한으로 매치를 일시정지한다.
- 로비에서는 슬롯을 즉시 지우지 않고 `bReservedForReconnect`로 예약해, 전원 준비 판정과 활성 인원에서 제외한다.

### 서버 보호

모든 행동 RPC는 `FAARpcBudget` 토큰 버킷을 거친다.

| 버킷 | 초당 / 버스트 |
| --- | --- |
| 조준 · 행동 | 20 / 40 |
| 소셜(이모트 등) | 4 / 8 |
| 인증 입력 | 12 / 8 |
| 로비 · 로비 채팅 · 퇴장 | 8/16 · 2/4 · 1/2 |

### 호스트 마이그레이션

`UAAHostMigrationSubsystem`이 매치 중 계속 복구 지점을 만들어 둔다.

```text
호스트: 숨김 Steam 로비(랑데부) 생성 → 2초 간격으로 체크포인트 캡처 시도(FAAMigrationStateCodec, v17, 최대 1MiB; 이전 전송·ACK 대기 중이면 건너뜀)
      → 4KB 청크 · CRC32로 전 클라이언트에 전송 → 전원 ACK 후에만 로비 메타데이터에 커밋
클라:   최근 3개 보관 → 호스트 이탈 감지 시 최대 60초 대기
선출:   FAAHostDeparturePolicy — 다음 연결 좌석이 후계 호스트, 로비 소유권 이전
후계:   새 리슨 세션 생성 → "target" 키 공개 → 나머지가 재참가(원 멤버 id + 32자 티켓 검증)
      → 체크포인트 복원 후 매치 재개
```

- 체크포인트는 GameMode · GameState · 플레이어 · 알 · 증강 액터 · 주사위의 ProjectA `UPROPERTY`를 리플렉션으로 직렬화하고, 리플렉션으로 잡히지 않는 네이티브 상태만 따로 쓴다.
- 증강 연출 컴포넌트(전기 충격 · 랜서 · 포섭 · 탑 쌓기)는 `UCLASS(Transient)`로 체크포인트에서 제외하고, 복원된 게임플레이 상태로부터 다시 만든다. 연출 객체까지 직렬화하면 복원 시 중복·고아 컴포넌트가 생겼기 때문이다.
- 알의 트랜스폼은 기본 루트 스케일까지 포함한 월드 변환으로 저장하고 `OverrideRootScale`로 스폰해, 당구공 변신처럼 크기가 바뀐 알도 복원 후 스케일과 충돌 형상이 그대로 유지된다.
- 복원 대기 중에는 종이 다이얼로그 스타일의 Slate 오버레이(`SAAHostMigrationOverlay`)가 입력과 키보드 포커스를 잡고, 복원이 끝나면 이전 포커스로 돌려준다.
- 생존 <strong>플레이어 좌석이 2개</strong>이고 그중 하나가 호스트이며 다른 생존 좌석이 연결돼 있다면, 마이그레이션 대신 남은 플레이어의 즉시 승리로 처리하고 전적에 기록한다.
- 복원 대상은 온라인 GameMode 3종과 검증된 맵 경로로만 화이트리스트했다.

## 결과

- 비밀번호 토큰은 <strong>계정 ID와 방의 Nonce에 묶어 검증</strong>한다. 다른 계정이나 다른 Nonce의 방에 그대로 재사용하는 요청을 거부한다.
- 여러 번 끊겨도 재접속 총합이 60초를 넘지 않아 고의 지연을 막는다.
- 조작된 클라이언트가 초당 수백 번 커밋·증강 RPC를 보내도 서버 처리량이 고정된다.
- <strong>ACK가 모두 모인 체크포인트만 커밋</strong>하므로, 일부 클라이언트만 가진 상태로 복원되는 일이 없다. 조작된 체크포인트로 임의 맵·모드를 열 수도 없다.

> Steam 테스트용 AppId(480) 기준으로 검증했다. 마이그레이션은 `AA.MigrationAudit`과, AI 좌석을 포함한 3인 매치에서 변신 증강 상태가 체크포인트 왕복 후에도 유지되는지 보는 자동화 테스트로 확인한다.
