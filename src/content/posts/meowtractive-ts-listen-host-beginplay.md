---
title: "[MeowTractive] 리슨 호스트는 BeginPlay가 possession보다 먼저 옵니다"
published: 2026-11-07
description: "Seamless travel 후 호스트는 BeginPlay 시점에 아직 possession 전이라, 로컬 판정 코드가 자기 폰을 잘못 처리했습니다."
category: 트러블슈팅
project: meowtractive
tags: ["Unreal Engine", "로비", "Seamless Travel"]
draft: false
---

## 증상

로비 실루엣 시스템에서 호스트만 자기 폰이 검은 고양이로 보이는 버그가 발생했습니다.

<iframe src="https://www.youtube-nocookie.com/embed/tbJq6HEF2cY" title="호스트 실루엣 버그" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---
## 원인

리슨 서버 + seamless travel에서 <strong>호스트 폰은 BeginPlay 시점에 아직 possession 전</strong>입니다. `IsLocallyControlled()`가 이때 false를 반환해 자기 폰까지 실루엣으로 덮어버리고, possession이 온 뒤엔 복원 코드가 없어 그대로 검은 머티리얼이 남아 있었습니다.

```cpp
void AMTPlayerCharacter::ApplyLobbyDisguise()
{
    if (IsLocallyControlled() || !LobbyDisguiseMaterial) { /* 내 폰: 원본 복원 */ }
    else { /* 남의 폰: 실루엣으로 덮기 */ }
}
// BeginPlay + NotifyControllerChanged 양쪽에서 호출해야 수렴
```

---
## 해결

처리 함수를 "내 폰이면 복원 / 남의 폰이면 덮기"의 <strong>양방향</strong> 형태로 만들고, `BeginPlay` + `NotifyControllerChanged`(possession 직후) 양쪽에서 재호출했습니다. 같은 원리로 매치 GameMode의 `HandleSeamlessTravelPlayer`(신규 접속과 seamless 복귀가 합류하는 지점)에서도 팀색 배정·입력 잠금을 possession 확정 시점 기준으로 재호출하도록 정리했습니다.

---
## 결과

호스트 여부와 무관하게 항상 올바른 실루엣 상태로 수렴합니다. "멀티플레이 초기화는 몇 번 불려도 옳게 수렴하는 보정 함수로 짜라"는 일반 원칙으로 정리했습니다.

<iframe src="https://www.youtube-nocookie.com/embed/wIylYV_5K84" title="호스트 실루엣 수정 결과" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
