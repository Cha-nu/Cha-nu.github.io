---
title: "[ArcRaiders: Wasp] DataTable 기반 확률 스폰"
published: 2026-11-07
description: "웨이브마다 박스 수·적 구성 비율이 달라지는 난이도 곡선을 데이터로 관리했습니다."
category: 핵심 기술
project: arc-wasp
tags: ["Unreal Engine", "DataTable", "스폰"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/R-iTnh7GvgU" title="확률 스폰" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

아이템 종류와 확률을 C++ 분기에 직접 작성하면 밸런스 변경마다 재컴파일이 필요하고, 확률 합을 정확히 100으로 강제하면 기획 데이터 입력이 번거롭습니다.

---
## 상대 가중치 선택

`FItemSpawnRow`는 `ItemName`, `ItemClass`, `SpawnChance`를 가집니다. 모든 행의 `SpawnChance` 합을 구하고 그 구간에서 난수를 만든 뒤, 행별 누적합이 난수를 처음 넘는 대상을 선택합니다. 따라서 `70:20:10`과 `7:2:1`은 같은 분포이며 합계를 1이나 100으로 맞출 필요가 없습니다.

```cpp
// UDataTable::GetAllRows로 후보 로드, 유효 행만 순회해 전체 가중치 계산
float TotalChance = 0.f;
for (const FItemSpawnRow* Row : Rows) { TotalChance += Row->SpawnChance; }

// 구간 [0, TotalChance)에서 난수 생성, 누적 가중치 비교로 클래스 결정
float Pick = FMath::FRandRange(0.f, TotalChance);
float Cumulative = 0.f;
for (const FItemSpawnRow* Row : Rows)
{
    Cumulative += Row->SpawnChance;
    if (Pick <= Cumulative) { SelectedClass = Row->ItemClass; break; }
}
```

---
## 스폰 위치

스폰 위치는 Box Extent 안에서 로컬 임의 좌표를 만든 뒤 Box Rotation을 적용해 월드 좌표로 변환합니다. 회전된 Volume이라도 균일하게 샘플링됩니다.

| 결정 | 선택 | 이유 |
| --- | --- | --- |
| 확률 데이터 | DataTable 외부화 | 기획 값 변경과 코드 변경 분리, 재컴파일 불필요 |
| 확률 합 | 상대 가중치(누적합 비교) | 합계를 100으로 맞출 필요 없음 — 70:20:10 = 7:2:1 |
| 스폰 위치 | Box Extent 로컬 좌표 + Rotation 적용 | 회전된 Volume에서도 균일한 샘플링 |
