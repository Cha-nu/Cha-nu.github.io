---
title: "[증강 알까기] 로비 채팅을 갱신하면 PIE 종료 시 에디터가 비정상 종료"
published: 2026-11-07
description: "채팅을 갱신할 때마다 위젯을 새로 만들어 에디터 Undo 버퍼가 파괴된 위젯을 참조했습니다. 위젯은 하나로 고정하고 텍스트만 교체해 해결."
category: 트러블슈팅
project: augmented-alkagi
tags: ["Unreal Engine", "CommonUI", "UMG"]
draft: false
---

## 증상

채팅을 한 번도 쓰지 않으면 PIE가 정상 종료되지만, <strong>메시지를 한 번이라도 갱신하면 PIE 종료 시 에디터가 함께 종료</strong>됐습니다.

---
## 해결 과정

재현 조건을 먼저 좁혔습니다.

| 조건 | 결과 |
| --- | --- |
| 채팅 미사용 | 정상 종료 |
| 채팅 1회 이상 사용 | 항상 크래시 |

처음엔 위젯 생성 방식을 의심해 `NewObject`를 `WidgetTree->ConstructWidget`으로 교체했지만 동일하게 재현됐습니다. <strong>생성 API를 바꾸는 것은 해법이 아니었습니다.</strong>

---
## 원인

참조 추적 로그에서 에디터의 Undo 버퍼인 `TransBuffer`가 이미 파괴된 위젯 또는 `WidgetTree`를 계속 참조하는 경로를 확인했습니다. 문제는 생성 방식이 아니라 <strong>매 갱신마다 위젯을 버리고 새로 만들었다는 것</strong> 자체였습니다.

---
## 해결

위젯은 고정하고 내용만 교체했습니다.

| 구분 | 구현 |
| --- | --- |
| 수정 전 | 갱신마다 `ClearChildren()` 후 텍스트 위젯 N개 재생성 |
| 수정 후 | `ChatScrollBox`에 `ChatLogText` <strong>하나만 고정</strong>, 최근 50개 메시지를 합쳐 `SetText()` |

반복 테스트에서 종료 크래시는 사라졌습니다.

---
## 배운 점

자주 갱신되는 UI는 위젯을 매번 만들고 버리기보다 <strong>위젯 수명을 고정하고 데이터만 바꾸는 쪽</strong>이 안전합니다. 증상이 나는 API(생성 함수)를 바꾸기 전에, 무엇이 파괴된 객체를 붙잡고 있는지 참조 경로부터 확인해야 합니다.
