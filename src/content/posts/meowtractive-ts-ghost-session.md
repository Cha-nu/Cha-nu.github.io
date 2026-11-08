---
title: "[MeowTractive] 유령 세션 & 재접속 실패"
published: 2026-11-07
description: "NetDriver 연결과 Steam 로비 멤버십을 같은 상태로 취급해, 호스트 종료 후 세션이 남고 클라 재접속이 막혔습니다."
category: 트러블슈팅
project: meowtractive
tags: ["Unreal Engine", "Online Subsystem Steam"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/6z5pvkQODL0" title="유령 세션 버그" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---
## 증상

호스트가 강제 종료되면 서버는 없는데 방 목록엔 세션이 남고, 반대로 클라이언트가 튕기면 같은 방에 재접속이 안 됐습니다.

---
## 원인

"NetDriver 연결 종료"와 "Steam 로비 멤버십 탈퇴"를 같은 사건으로 취급했습니다. 호스트가 사라져도 클라가 로비 멤버로 남아 있으면 세션 광고가 계속 살아 있고, 클라 강제 종료 시엔 서버에 이전 컨트롤러·슬롯이 잠시 남아 재접속을 막았습니다.

```cpp
void UMTGameInstance::HandleDestroySession(bool bWasSuccessful)
{
    CompleteSessionCleanup(bWasSuccessful);   // 완료 콜백을 기다린 뒤 메인메뉴로 이동 (5초 안전 타임아웃)
}
// PreLogin: 동일 Steam ID의 기존 원격 컨트롤러 제거 후 새 연결 허용
if (ExistingPC && ErrorMessage.IsEmpty()) { ExistingPC->Destroy(); }
```

---
## 해결

- `DestroySession()` 완료 콜백을 기다린 뒤 메인메뉴로 이동합니다(5초 안전 타임아웃 포함). 로컬 Named Session이 없을 때도 성공으로 처리하는 <strong>멱등 연산</strong>으로 만들어 중복 파괴 요청도 하나로 합쳤습니다.
- `PreLogin`에서 동일 Steam ID의 기존 컨트롤러를 찾아 정리 후 새 연결을 허용합니다. `Destroyed()`가 `GameMode::Logout` 경로를 그대로 태워 별도 정리 코드가 필요 없습니다.
- NetDriver 커넥션 타임아웃을 20초로 조정했습니다.
- 접속 승인 실패(PreLogin 거부) 시에도 로컬 세션을 먼저 파괴해 `AlreadyInSession` 재발을 막습니다.

---
## 결과

호스트 종료 시 각 클라이언트가 세션 탈퇴 후 방 광고가 즉시 사라지고, 클라이언트는 재실행 후 동일 계정으로 기존 로비에 재접속할 수 있습니다.

<iframe src="https://www.youtube-nocookie.com/embed/WbG6ls1aIF0" title="유령 세션 수정 결과" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

| 개념 | transient connection (연결) | persistent session membership (세션 소속) |
| --- | --- | --- |
| 성격 | 복구 가능한 네트워크 상태 | 정책으로 다뤄야 하는 상태(예: 강퇴) |
| 정리 시점 | 타임아웃/재연결로 자연 해소 | 명시적 탈퇴(DestroySession) 필요 |

이 둘을 분리해서 다루는 원칙은 [강퇴된 플레이어의 재접속 차단](/posts/meowtractive-ts-kick-reconnect-block/)에서 그대로 재사용됩니다.
