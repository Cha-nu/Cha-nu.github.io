---
title: "[증강 알까기] 결과 화면이 안 나오는 버그"
published: 2026-11-07
description: "게임 종료 처리는 정상이었고, 결과 UI를 넣은 WBP와 실제로 실행되는 HUD WBP가 달랐다. BindWidgetOptional이 빠진 위젯을 숨기고 있었다."
category: 트러블슈팅
project: augmented-alkagi
tags: ["Unreal Engine", "CommonUI", "UMG"]
draft: false
---

## 증상

마지막 상대가 탈락하면 게임 진행은 멈췄지만 <strong>승패 문구와 종료 버튼이 나타나지 않았다.</strong> 보드만 남은 화면에서 아무것도 할 수 없었다.

## 해결 과정

처음엔 GameOver 상태 전이나 복제 문제를 의심했다. 확인 결과 <strong>상태 머신은 전부 정상</strong>이었고, 문제는 UI 쪽에 있었다. 그래서 종료 UI를 만든 에셋과 실제로 화면에 뜨는 HUD 클래스를 비교했다.

## 원인

종료 UI는 `WBP_AAInGamePersistentHUD`에 만들어두었는데, 프로젝트 설정의 `PersistentHUDClass`는 <strong>`WBP_AAAlkagiHUD`를 가리키고 있었다.</strong> 작업한 에셋과 실행되는 에셋이 달랐다.

```cpp
// 문제 발생 당시의 선택적 바인딩 예시
UPROPERTY(meta=(BindWidgetOptional))
TObjectPtr<UWidget> VictoryOverlay;   // 실행 HUD에 없어도 nullptr로 통과
```

`BindWidgetOptional`이라 실행 HUD에 위젯이 없어도 에러 없이 `nullptr`로 넘어갔다.

## 해결

당시에는 `PersistentHUDClass`와 종료 UI를 가진 HUD의 연결을 맞추고, 실제 실행 클래스를 함께 확인하도록 검증 항목을 보완했다.

<strong>현재 구현:</strong> `Config/DefaultGame.ini`의 `PersistentHUDClass`는 `/Game/AA/UI/InGame/WBP_AAAlkagiHUD.WBP_AAAlkagiHUD_C`를 가리킨다. `VictoryOverlay`는 이제 `BindWidget` 필수 바인딩이며, 결과 화면은 로컬 PlayerController가 별도로 생성·갱신하는 `UAAEndMatchPanel`이 담당한다. 과거의 선택적 바인딩 예시와 현재 종료 패널 경로를 구분해야 한다.

## 배운 점

`BindWidgetOptional`은 크래시를 막아줬지만, 대신 <strong>필수 UI가 빠졌다는 사실을 끝까지 숨겼다.</strong>

> null 검사는 크래시를 막을 뿐, 기능이 존재하는지를 보장하지 않는다. <strong>없으면 안 되는 디자이너 위젯은 `BindWidget`으로 선언해 Widget Blueprint 컴파일 단계에서 누락을 확인하는 게 맞다.</strong>
