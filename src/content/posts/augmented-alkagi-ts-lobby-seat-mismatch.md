---
title: "[증강 알까기] 로비 인원과 실제 게임 참가자 수 불일치"
published: 2026-11-07
description: "로비→게임 사이에서 인원 정보가 URL 옵션 키 불일치, 맵 이동 중 좌석 유실, 재경기 때 이탈 좌석 복원 세 군데서 어긋났다."
category: 트러블슈팅
project: augmented-alkagi
tags: ["Unreal Engine", "온라인", "Seamless Travel"]
draft: false
---

## 증상

로비에서 본 인원과 실제 매치가 일치하지 않았다.

- 싱글 로비에서 2·3인으로 시작해도 <strong>항상 4인 보드</strong>로 열렸다.
- 멀티 2인 매치에서 좌석이 `{0, -1}` — 한 명이 <strong>좌석 없이</strong> 들어와 조준·증강을 아무것도 못 했다.
- 3명이 남은 상태로 재경기하면 <strong>알 12개·빈 좌석 3개</strong>가 생겼다.

## 해결 과정

좌석 배정이 실패해도 아무 로그가 없어서, 먼저 좌석 배정 실패에 경고 로그를 넣었다. 이 로그가 첫 번째 원인(URL 옵션 불일치)을 잡는 단서가 됐다. 이어 로비 맵에서 PIE 리슨 서버로 실제 로비 → 트래블 → 인게임 흐름을 재현해 좌석 유실을 확인했다.

좌석 유실을 고치면서 `HandleSeamlessTravelPlayer`에서 매치 시작까지 호출했더니 회귀가 생겼다. 이 콜백이 <strong>`BeginPlay`보다 먼저</strong> 실행돼 보드가 없는 상태에서 알이 바닥 아래(Z=17.4)에 생성되고, 뒤늦은 `BeginPlay`가 상태를 `WaitingForPlayers`로 되돌려 매치가 영구 정지했다.

## 원인

로비 → 게임 사이에서 인원 정보가 끊기는 지점이 세 곳이었다.

| 지점 | 원인 |
| --- | --- |
| 로비 → GameMode URL | 로비는 `Participants=N`을 넘기는데 GameMode는 `LocalCount=`만 읽어 기본값 4로 폴백 |
| 심리스 트래블 | 로비와 인게임의 PlayerController 클래스가 달라 PlayerState가 새로 생성되는데, `CopyProperties`가 없어 `SeatIndex`가 사라짐. 심리스 트래블은 `PostLogin`도 타지 않음 |
| 재경기 | 이탈한 좌석까지 기대 인원으로 다시 채움 |

## 해결

- `InitGame`이 `Participants=`를 우선 읽고 `LocalCount=`는 구버전 호환용으로만 유지, 1~4로 Clamp했다.
- `AAAlkagiPlayerState::CopyProperties`로 좌석을 보존하고, `HandleSeamlessTravelPlayer`에서 좌석을 확정했다. 로비 슬롯 순서 = 좌석 = 로비에서 고른 알 색(`StoneColors=` URL 인덱스)이라, 좌석을 새로 배정하면 <strong>알 색이 다른 사람에게 가는</strong> 2차 버그가 생긴다. 그래서 넘어온 좌석이 유효하면 유지하고, 범위를 벗어났거나 중복일 때만 경고 로그와 함께 재배정한다.
- 트래블 콜백은 <strong>좌석 배정만</strong> 하고, 매치 시작은 `BeginPlay` 이후 `Tick`의 준비 확인에 맡겨 회귀를 해결했다.
- 재경기는 연결된 참가자에게만 알을 생성한다.
- <strong>당시 검증 기록(1인 3개 규칙):</strong> 싱글 `Participants=2/3` → 알 6/9개, 멀티 PIE 트래블 후 좌석 `{0, 1}`·알 Z=417.9·`Phase=Draft`, 재경기 3명 → 알 9개·빈 좌석 0개.
- <strong>현재 코드 기준:</strong> 싱글 `SpawnInitialPieces()`와 온라인 `SpawnPieces()`는 모두 <strong>참가자당 5개</strong>를 생성하므로, 최초 배치의 기대값은 2인 10개·3인 15개다. 좌석·스폰 높이·시작 페이즈는 현재 맵과 모드 기준으로 검증해야 하며, 위 과거 수치를 현재 재실행 결과로 해석하지 않는다.

## 배운 점

맵 이동 경계(URL 옵션·PlayerState 재생성·이탈 좌석)는 각각 데이터가 끊기는 지점이다. 검증도 "매치가 시작됐다"가 아니라 <strong>기대 인원·좌석·알 수가 모든 월드에서 일치하는지</strong>로 잡아야 한다. 엔진 콜백의 호출 순서(`HandleSeamlessTravelPlayer` → `BeginPlay`)를 가정하지 않고, 상태 변경은 초기화가 끝난 뒤로 미루는 것이 안전하다.
