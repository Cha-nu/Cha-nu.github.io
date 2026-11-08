---
title: "[MeowTractive] 로비 고양이 선택 시스템"
published: 2026-11-07
description: "월드 조형물을 펀치로 순환시켜 고양이를 고르고, 데이터는 정상 복제하되 표현(머티리얼)만 숨겨 매치 입장 전까지 선택을 비공개로 유지했습니다."
category: 핵심 기술
project: meowtractive
tags: ["Unreal Engine", "로비", "GAS"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/11hdrw_EYOs" title="로비 고양이 선택" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

버튼 UI 없이, 로비 조형물에 다가가 <strong>F키로 고양이를 순환 선택</strong>합니다. 다른 플레이어 화면에는 매치 입장 전까지 검은 실루엣으로만 보입니다.

---
## 데이터는 복제, 표현만 숨기기

"숨기기"는 보안이 아니라 연출 문제로 봤습니다. `SelectedCatType`은 평범하게 전 클라 복제하고, <strong>표현 층 함수 하나(`ApplyLobbyDisguise`)</strong>에서만 내 폰은 원본으로, 남의 폰은 실루엣 머티리얼로 덮습니다. 세 고양이가 같은 스켈레탈 메시를 공유하기 때문에 머티리얼만 덮으면 종류가 완전히 숨겨집니다.

```cpp
UPROPERTY(ReplicatedUsing = OnRep_CatIndex) int32 CatIndex;
CatIndex = (CatIndex + 1) % CatOptions.Num();
OnRep_CatIndex();   // 리슨 호스트는 OnRep이 안 불려서 값 변경 직후 직접 호출
```

---
## 조형물과 상호작용

조형물은 액터를 스폰/파괴하지 않고 <strong>복제 인덱스(CatIndex) 하나만 순환</strong>시켜, 스폰/파괴 타이밍 경쟁으로 인한 유령·중복 버그를 원천 차단했습니다. 선택 판정은 GAS 어빌리티(`GA_Interact`)로 만들어 몽타주 AnimNotify(`Event.Montage.Interact.Hit`) 시점에 전방 구체 판정을 하고, 대상은 `IMTLobbySelectable` 인터페이스로만 봐 새 상호작용 대상을 GA 수정 없이 추가할 수 있습니다.

검증은 조형물(소유 슬롯)→컨트롤러(준비 상태)→게임모드(재스폰) <strong>3겹 서버 권위</strong>로 나눠 각자 자기 규칙만 압니다. 첫 고양이 배정과 조형물 사이클 시작점은 랜덤화했습니다. 순환 대상 고양이는 Fatty, Mackerel, Spotted 세 종류입니다.

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 조형물 순환 | 복제 인덱스 1개(스폰/파괴 없음) | 유령/중복 버그 원천 차단 |
| 비공개 방식 | 데이터는 복제, 표현만 숨김 | 보안 아닌 연출 문제 |
| 상호작용 | GAS 어빌리티(AnimNotify 판정) | 연출·판정 동기화, 전투 레일 재사용 |

관련 트러블슈팅: [리슨 호스트는 BeginPlay가 possession보다 먼저 온다](/posts/meowtractive-ts-listen-host-beginplay/)
