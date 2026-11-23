---
title: "툰 셰이딩 3편: 디테일과 색감"
published: 2026-11-22T23:00:00+09:00
description: "2편의 셰이더에 노멀·MatCap·머리카락 하이라이트를 더하고, 베일 반투명, 텍스처 색 외곽선, 앞머리에 비치는 눈썹과 눈, 캐릭터 전체 밝기 조절까지 다듬은 과정입니다."
category: 언리얼 엔진
tags: ["Unreal Engine", "툰 셰이딩", "머티리얼", "포스트 프로세스", "실습"]
image: /images/toon-shading-3/00_cover.png
project: toonshader
draft: false
---

> **툰 셰이딩 시리즈** — [1편 셀 셰이딩의 원리](/posts/toon-shading-1/) · [2편 언리얼 머티리얼 구현](/posts/toon-shading-2/) · **3편 디테일과 색감** · [4편 애니메이션과 Kawaii Physics](/posts/toon-shading-4/) · [5편 원리와 HLSL](/posts/toon-shading-5/) · [6편 흰 조명 맞추기와 회고](/posts/toon-shading-6/)
>
> 언리얼 엔진 5.8 기준입니다. 이 글의 수치는 프로젝트 머티리얼과 인스턴스에 실제로 들어 있는 값입니다.

> **팬메이드·학습 목적 고지** — 이 글에 나오는 캐릭터 모델, 텍스처, 게임 화면의 저작권은 명조: 워더링 웨이브(Wuthering Waves)의 개발사 Kuro Games에 있습니다. 셰이더 공부를 위한 비상업적 팬메이드 작업이며, 모델과 텍스처 파일은 배포하지 않습니다. 문제가 되는 경우 알려 주시면 내리겠습니다.

---
## 들어가며

2편에서 만든 셰이더는 명암 단계와 얼굴 그림자까지는 나왔지만, 디퓨즈 텍스처 한 장만 써서 옷 주름과 금속 광택이 없었고 베일은 불투명했습니다. 외곽선은 순검정이었고, 앞머리에 가려진 눈썹은 보이지 않았습니다.

이번 글은 2편 끝에 적어 둔 할 일을 하나씩 처리한 기록입니다. 텍스처 채널을 읽어 디테일을 더하고, 원작 화면과 비교하며 색을 맞췄습니다. 애니메이션과 천 물리는 분량이 길어져 4편으로 나눴습니다.

<strong>AI 활용</strong>: 2편과 같이 각 절 제목 아래에 누가 만들었는지 적었습니다. 머티리얼 노드는 대부분 AI 어시스턴트(Claude)의 안내를 받아 직접 구성하고 검토를 받았습니다. 인스턴스 값 입력과 일부 머티리얼 수정은 AI가 언리얼 에디터의 MCP 연결로 직접 했습니다.

![이번 글의 작업을 마친 뒤 캐릭터 얼굴을 가까이 잡은 에디터 뷰포트 화면](/images/toon-shading-3/00_cover.png)

작업을 마친 뒤의 에디터 뷰포트 화면입니다. 앞머리 위로 눈썹과 눈이 비치고, 이마 중간에 옅은 하이라이트 띠가 있습니다. 붉은 선은 에디터의 캡슐 표시입니다.

![목표로 삼은 원작 게임 화면. 캐릭터가 밤 배경 앞에 정면으로 서 있습니다.](/images/toon-shading-3/01_reference.png)

비교 기준으로 삼은 원작 화면입니다. 출처: 명조: 워더링 웨이브(Kuro Games) 게임 화면.

---
## 원본 포맷으로 모델 다시 가져오기

<strong>만든 사람</strong>: 슬롯 구성 확인은 AI가 했습니다.

2편에서는 블렌더를 거쳐 FBX로 가져왔습니다. 그 메시는 기준 자세가 팔을 모은 포즈로 구워져 있었고, 눈을 감는 모프 타겟을 켜면 팔까지 늘어났습니다(4편). 그래서 이번에는 UEFormat 플러그인으로 `.uemodel`과 `.ueanim` 파일을 직접 가져왔습니다. 원본 스켈레톤과 애니메이션을 그대로 쓰기 위해서입니다.

머티리얼 슬롯은 여덟 개이고, 이름만으로는 헷갈리는 것이 있어 모델을 읽어 확인했습니다.

| 슬롯 | 실제 부위 |
| --- | --- |
| Bangs / Hair | 앞머리 / 뒷머리와 땋은 머리 |
| Alpha | 베일과 반투명 소매 |
| Up / Cloth | 리본·금속 장식·꽃 / 치마와 허리 |
| Down | 다리와 몸 피부 |
| Face / Eye | 얼굴 / 눈 |

몸 피부가 `Down` 슬롯에 들어 있다는 점은 뒤에서 얼굴색을 맞출 때 중요했습니다.

---
## 광택은 Emissive가 아니라 Base Color로

<strong>만든 사람</strong>: 직접 (AI 안내·검토)

처음에는 MatCap과 프레넬 광택을 `MM_ToonLit`의 Emissive에 더했는데 화면에 아무 변화가 없었습니다. 2편의 `PP_Toon`은 스텐실이 1인 픽셀을 GBuffer의 Diffuse로 다시 칠하기 때문에 Emissive는 버려집니다. 그래서 광택을 전부 Base Color에 더하도록 바꿨습니다.

```text
BaseColor 텍스처.RGB
  → Power(BaseColorPower)
  → × BaseColorBrightness
  → × BaseColorTint
  → Desaturation(Fraction = 1 - BaseSaturation)
  → + [광택 합계]
  → Base Color

[광택 합계] = MatCap + Fresnel + 머리카락 하이라이트
MatCap  = MatCapTex × SmoothStep(0.7, 0.9, TypeMask.G) × MatCapIntensity
Fresnel = SmoothStep(FresnelRangeMin, FresnelRangeMax, 1 - Saturate(Dot(PixelNormalWS, CameraVector)))
          × FresnelColor × FrenelIntensity
```

노멀 맵은 `UseNormalMap` 스위치로 켜고 `NormalStrength`로 세기를 조절합니다.

![MM_ToonLit 그래프의 Base Color 구간](/images/toon-shading-3/02_lit_base_graph.png)

텍스처 RGB가 `Power`, 밝기, 색조, `Desaturation`을 거친 뒤 광택 합계(`EmssiveColor`)와 더해져 Base Color로 들어갑니다. Emissive Color 핀은 비어 있습니다.

![MM_ToonLit 그래프의 Normal 묶음과 MatCap 묶음](/images/toon-shading-3/03_lit_matcap_graph.png)

위쪽이 노멀 맵 묶음, 아래쪽이 MatCap 묶음입니다. `TypeMask`의 G 채널을 `SmoothStep(0.7, 0.9)`로 자른 값을 MatCap에 곱하고, 오른쪽에서 프레넬과 머리카락 하이라이트를 차례로 더합니다.

![MM_ToonLit 그래프의 프레넬 광택 구간](/images/toon-shading-3/04_lit_fresnel_graph.png)

프레넬 광택 구간입니다. 노멀과 카메라 방향의 내적을 뒤집어 `SmoothStep`으로 범위를 자르고, 색과 세기를 곱합니다.

### MatCap 마스크

`TypeMask`는 `_FTM` 텍스처입니다. G 채널에 부위 구분 값이 계단처럼 들어 있고, 금속은 대략 0.75보다 큰 값이었습니다. 처음에는 G 채널을 그대로 MatCap에 곱했는데, 금속이 아닌 옷에도 값이 있어서 옷 색이 하얗게 날아갔습니다. `SmoothStep(0.7, 0.9)`를 거쳐 금속 영역만 남겼습니다.

![MatCap이 옷 전체에 더해져 색이 하얗게 날아간 캐릭터 전신](/images/toon-shading-3/05_matcap_washout.png)

마스크를 자르기 전의 화면입니다. 옷과 피부의 색이 전체적으로 바랬습니다.

### 노드 순서에 따라 베일이 검게 나온 문제

`Desaturation` 뒤에 `Multiply(Tint)`를 두면 베일(`Alpha` 슬롯) 겉면이 검게 나왔습니다. 순서를 `Multiply(Tint)` → `Desaturation`으로 바꾸면 정상이었습니다. 테스트용 복사본으로 같은 현상을 재현했지만 원인은 찾지 못했습니다.

---
## 베일을 반투명으로

<strong>만든 사람</strong>: 직접 (AI 안내)

베일과 소매는 Blend Mode를 Masked, Two Sided로 두고 디더링으로 반투명을 냈습니다. Translucent로 바꾸면 GBuffer에 쓰이지 않아 `PP_Toon`의 툰 처리에서 빠지기 때문입니다.

```text
Opacity Mask = DitherTemporalAA( Lerp(VeilOpacity 0.85, 1, Fresnel) )
```

`UseOpacityMask` 스위치로 켭니다. 프레넬로 가장자리를 더 불투명하게 해서 천이 겹친 느낌을 냈습니다. 이 슬롯 인스턴스의 프레넬 값은 세기 0.15, 범위 0.1\~0.4입니다.

![MM_ToonLit 그래프의 Opacity 묶음](/images/toon-shading-3/06_lit_opacity_graph.png)

`VeilOpacity`와 1을 프레넬로 섞어 `DitherTemporalAA`에 넣고, `UseOpacityMask` 스위치를 거쳐 Opacity Mask로 보냅니다.

![베일과 소매가 반투명으로 비치는 캐릭터 상반신](/images/toon-shading-3/07_veil_sleeve.png)

적용한 뒤의 플레이 화면입니다. 소매 너머로 팔과 치마가 비칩니다.

---
## 외곽선에 텍스처 색 입히기

<strong>만든 사람</strong>: AI (MCP로 머티리얼과 인스턴스 수정)

외곽선은 2편과 같은 뒤집힌 메시 방식입니다. 색만 순검정에서 텍스처 색을 어둡게 한 값으로 바꿨습니다. 원본 머티리얼 덤프의 `_OL` 파일에 슬롯마다 외곽선 색이 들어 있어서 그 값을 옮겼습니다.

```text
MainTex.RGB → Power(OutlineColorPower) → × OutlineColorTint
  → UseMainTex 스위치(False면 OutlineColor) → Emissive Color
```

- `MainTex`에는 슬롯의 `_D` 텍스처를 넣었습니다.
- `OutlineColorPower`는 1, 머리카락 두 슬롯만 1.25입니다.
- 얼굴은 텍스처 대신 단색 `OutlineColor` (0.2, 0.129, 0.118)을 씁니다.

![M_ToonOutline 그래프의 외곽선 색 구간](/images/toon-shading-3/08_outline_graph.png)

`MainTex`에 `Power`와 색조를 적용한 값과 단색 `OutlineColor` 중 하나를 `UseMainTex` 스위치로 골라 Emissive Color에 넣습니다.

화면 전체에 거는 8방향 후처리 외곽선도 가져와 봤지만 캐릭터 바깥 윤곽만 그려서, 옷 안쪽 선까지 나오는 뒤집힌 메시 방식을 유지했습니다.

---
## 앞머리에 비치는 눈썹과 눈

<strong>만든 사람</strong>: 직접 (AI가 방법을 설계하고 여러 차례 검토). 눈 영역 마스크용 인스턴스 값은 AI가 넣었습니다.

원작에서는 앞머리가 눈을 덮어도 눈썹과 눈이 옅게 비칩니다. 얼굴 메시를 한 번 더 그리되 깊이 검사를 끄고 반투명으로 덧그리는 방법을 썼습니다.

- `M_BrowSeeThrought`: Translucent, Unlit, Disable Depth Test, After DOF입니다.
- 캐릭터 블루프린트에 같은 메시를 쓰는 컴포넌트를 두 개 더 붙였습니다. `BrowOverlay`는 얼굴 슬롯만, `EyeOverlay`는 눈 슬롯만 이 머티리얼을 쓰고 나머지 슬롯은 보이지 않는 머티리얼(`M_Invisible`)입니다.
- 두 컴포넌트 모두 Construction Script에서 `Set Leader Pose Component`로 본체 포즈를 따라갑니다.

깊이 검사를 끄면 얼굴 전체가 머리 위로 덮이므로 마스크 세 개로 범위를 줄였습니다.

| 마스크 | 방식 | 역할 |
| --- | --- | --- |
| Area Mask | UV 범위 (U 0.2\~0.8, V 0.67 이상) | 눈썹·속눈썹 텍스처 영역만 통과 |
| Cover Mask | 씬 깊이와의 차이 D | 무언가에 가려진 픽셀만 통과 |
| Eye Mask | 스키닝 전 로컬 위치 | 눈꺼풀이 열린 타원 안만 통과 |

```text
Cover Mask = Step(D ≥ 0.3) × (1 - SmoothStep(4, 8, D)) × (씬 BaseColor 합 ≥ 0.01)
Eye Mask   = 1 - SmoothStep(0.9, 1.05, Length( (|X| - 3.19) / 1.65, (Z - 125.36) / 0.82 ))
최종 불투명도 = 마스크 × Strength 0.4
```

- Cover Mask의 거리 상한(4\~8)은 가까운 앞머리에만 비치고, 멀리 있는 물체 위로는 비치지 않게 합니다.
- 눈 메시는 홍채 원판과, 눈구멍보다 큰 흰자 평면으로 되어 있습니다. 그대로 덧그리면 눈 주변 피부 위까지 흰자가 번져서, 눈이 열린 위치를 기준으로 타원 마스크를 걸었습니다.
- 쌍꺼풀 위 음영 조각은 Area Mask에서 작은 사각형(U 0.40\~0.60, V 0.860\~0.875)을 빼서 지웠습니다.

![M_BrowSeeThrought 그래프의 Area Mask 구간](/images/toon-shading-3/09_brow_area_graph.png)

Area Mask 구간입니다. UV의 U와 V를 `Step`으로 잘라 범위를 만들고, 위쪽 가지에서 만든 음영 조각 사각형을 `1-x`로 뒤집어 곱합니다.

![M_BrowSeeThrought 그래프의 Cover Mask 구간과 최종 합성](/images/toon-shading-3/10_brow_cover_graph.png)

위쪽이 Cover Mask입니다. 씬 깊이와 픽셀 깊이의 차이 D에 `Step`과 `SmoothStep`을 걸고, 씬의 BaseColor 합이 0.01 이상인 조건을 곱합니다. 아래쪽에서 세 마스크와 `Strength`를 곱해 Opacity로 내보냅니다.

![M_BrowSeeThrought 그래프의 Eye Mask 구간](/images/toon-shading-3/11_brow_eye_graph.png)

Eye Mask 구간입니다. 스키닝 전 로컬 위치의 X와 Z를 눈 중심 기준으로 정규화해 길이를 구하고, `SmoothStep(0.9, 1.05)`를 뒤집어 타원 안쪽만 남깁니다.

언리얼 5.8에서 "Pre-Skinned Local Position" 노드는 찾을 수 없었습니다. `Local Position` 노드의 Local Origin을 Pre-Skinned Instance로 두고 `VertexInterpolator`를 거쳐 썼습니다.

---
## 머리카락 하이라이트

<strong>만든 사람</strong>: 직접 (AI가 텍스처 채널을 분석하고 노드를 안내). 인스턴스 값은 AI가 넣었습니다.

머리카락에는 `_HN`, `_HM` 텍스처가 따로 있습니다. AI가 파일의 채널 값을 읽어 다음과 같이 해석했습니다.

| 텍스처 | 채널 | 내용 |
| --- | --- | --- |
| `_HN` | R / G | 가닥을 가로지르는 좌표 / 가닥을 따라가는 좌표 |
| `_HM` | R / G | 하이라이트 줄무늬 / 가닥 결 광택 |

띠는 가닥 방향 좌표가 특정 값 근처인 곳에만 `_HM`의 줄무늬를 남기는 방식입니다.

```text
Band = Saturate(1 - Abs(HN.G - HLPosition) / HLWidth)
Highlight = (HM.R × HLColor × Band + Saturate(HM.G - 0.4) × HL2Intensity) × HLIntensity
```

입력이 텍스처 좌표뿐이라 띠는 머리카락 표면에 고정됩니다. 카메라나 빛 방향에 따라 움직이지 않습니다.

![MM_ToonLit 그래프의 앞머리 하이라이트 구간](/images/toon-shading-3/12_lit_bangs_graph.png)

앞머리 하이라이트 구간입니다. 아래쪽 `BangsUVMap`의 G 채널로 띠를 만들고, 위쪽 `BangsMask`의 R 채널과 색을 곱합니다. G 채널에서 0.4를 뺀 두 번째 항은 앞머리에만 있습니다.

![하이라이트를 넣은 앞머리를 가까이 본 화면. 가닥을 따라 흰 줄무늬가 보입니다.](/images/toon-shading-3/13_hair_highlight.png)

하이라이트를 넣은 뒤 앞머리를 가까이 본 화면입니다. `_HM`의 줄무늬가 가닥을 따라 흰 선으로 나타납니다. 이때는 세기가 강해서 이후 0.3으로 낮췄습니다.

| 파라미터 | 뒷머리 | 앞머리 |
| --- | --- | --- |
| HLPosition | 0.57 | 0.62 |
| HLWidth / HLIntensity | 0.18 / 0.3 | 0.18 / 0.3 |
| HLColor | (0.6, 0.7, 1.0) | (0.6, 0.7, 1.0) |

`HLPosition`은 값이 클수록 띠가 머리끝 쪽으로 내려갑니다. 앞머리는 0.55에서 화관 바로 아래, 0.7에서 눈썹 높이였고, 0.62에서 이마 중간쯤에 놓였습니다. 에디터 화면과 플레이 화면에서 띠 높이를 픽셀로 재 보니, 화관과 눈 사이에서 각각 위에서 17%, 9% 지점이었습니다(0.55일 때). 앞머리가 둥글게 휘어 있어 카메라 각도에 따라 보이는 높이가 달라지므로, 위치는 플레이 화면을 기준으로 맞추는 것이 좋습니다.

---
## 리본 디테일

<strong>만든 사람</strong>: AI (원인 분석과 값 수정)

리본과 리본 끈이 흰색 한 덩어리로 보였습니다. 텍스처에 무늬가 없는 것인지 확인하려고 `Up_D` 텍스처의 해당 영역을 읽어 보았습니다. 리본 영역의 평균 밝기는 255 중 236, 끈은 223이었습니다. 거의 흰색 위에 옅은 회색으로 주름과 격자가 그려져 있어, `BaseColorPower`가 1이면 차이가 드러나지 않았습니다.

`Up` 슬롯 인스턴스의 `BaseColorPower`를 1에서 2로 올렸습니다. 밝은 색은 거의 그대로 두고 중간 톤만 내려가서 대비가 생깁니다.

![BaseColorPower 1일 때. 리본이 주름 없이 평평한 흰색으로 보입니다.](/images/toon-shading-3/14_ribbon_before.png)

`BaseColorPower` 1일 때입니다. 리본에 주름이 없고 끈의 격자도 거의 보이지 않습니다.

![BaseColorPower 2일 때. 리본에 주름 음영이 생기고 끈에 마름모 격자가 보입니다.](/images/toon-shading-3/15_ribbon_after.png)

`BaseColorPower` 2일 때입니다. 리본에 주름 음영이 생기고 끈에 마름모 격자가 보입니다. 같은 슬롯의 금속 장식은 색이 조금 진해졌습니다.

---
## 캐릭터 전체 밝기

<strong>만든 사람</strong>: 밝기 값 조절은 직접, 얼굴·눈 가지의 노드 추가는 AI (MCP)

캐릭터가 전체적으로 밝아 `PP_Toon`의 `BaseColorBrightness`를 낮췄더니 얼굴과 눈만 밝게 남았습니다. 얼굴과 눈은 Unlit이라 Diffuse가 0이고, 2편의 마스크에서 빠져 원래 화면 색(`SceneColor`)으로 그대로 지나가기 때문입니다.

`SceneColor` 쪽에도 같은 파라미터를 곱하되, 스텐실 마스크로 캐릭터 픽셀에만 걸었습니다.

```text
[StencilMask] = Saturate(1 - Abs(Stencil - StencilValue))
[Final] = Lerp( SceneColor × Lerp(1, BaseColorBrightness, StencilMask), Toon, Mask )
```

배경은 `StencilMask`가 0이라 영향을 받지 않습니다.

![PP_Toon 그래프의 마지막 Lerp 구간](/images/toon-shading-3/16_pp_end_graph.png)

`PP_Toon`의 끝부분입니다. 마지막 `Lerp`의 A에는 원래 `SceneColor`가 직접 들어갔는데, 지금은 아래쪽으로 내려갔다가 돌아오는 선이 연결되어 있습니다.

![PP_Toon 그래프에 추가한 Lerp와 Multiply 노드](/images/toon-shading-3/17_pp_new_graph.png)

추가한 두 노드입니다. `Lerp`(A = 1, B = `BaseColorBrightness`, Alpha = 스텐실 마스크)의 결과를 `SceneColor`에 곱합니다. AI가 MCP로 넣으면서 기존 묶음에서 떨어진 자리에 놓여 선이 깁니다.

![BaseColorBrightness 0.7일 때의 플레이 화면. 전체가 어둡고 꽃과 피부가 탁합니다.](/images/toon-shading-3/18_brightness_07.png)

`BaseColorBrightness` 0.7일 때입니다. 곱하기로 내리면 흰색이 사라져 꽃이 회색이 되고 피부가 탁해졌습니다. 이 화면은 조명 방향도 바뀐 상태라 얼굴에 각진 그림자가 넓게 잡혔습니다.

값을 0.9로 올리고, 원작에 맞추려고 넣었던 머리카락 색 보정도 완화했습니다.

| 항목 | 이전 | 변경 |
| --- | --- | --- |
| `PP_Toon` BaseColorBrightness | 0.7 | 0.9 |
| 머리카락 BaseColorTint | (0.85, 1.0, 1.1) | (1, 1, 1) |
| 머리카락 BaseSaturation | 1.5 | 1.2 |

이와 별개로 그림자 색(`ShadowColor`, `ShadowOuterColor`)은 2편의 (0.55, 0.45, 0.65)에서 (0.62, 0.62, 0.72)로 바꿔 채도를 낮췄습니다.

전체를 더 낮추고 싶을 때는 곱하기 대신 `BaseColorPower`를 올리는 편이 밝은 영역을 지킬 수 있다고 생각합니다.

![얼굴과 눈에도 밝기를 적용한 뒤의 에디터 뷰포트 화면](/images/toon-shading-3/19_face_brightness.png)

얼굴·눈 가지에 밝기를 적용한 직후의 에디터 뷰포트 화면입니다. 얼굴색과 어깨·가슴 피부색이 이어집니다.

---
## 막힌 점과 해결

- 문제: 얼굴은 진하고 몸은 하얗게 보였습니다.
  - 원인: 얼굴 머티리얼(`MM_ToonFace`)의 `BaseColorPower`만 2로 남아 있었고, 몸 피부가 든 `Down` 슬롯은 1이었습니다.
  - 해결: 둘 다 1.2로 맞췄습니다.

![얼굴은 분홍빛으로 진하고 다리와 팔은 하얗게 보이는 캐릭터 전신](/images/toon-shading-3/20_face_body_mismatch.png)

값을 맞추기 전의 화면입니다. 얼굴만 색이 진하고 팔과 다리는 하얗습니다.

- 문제: 인스턴스에 넣은 값이 원래대로 돌아갔습니다.
  - 원인: 해당 인스턴스가 에디터에 열려 있는 동안 MCP로 값을 넣었고, 에디터 쪽 상태가 다시 덮어쓴 것으로 보입니다.
  - 해결: 열려 있는 머티리얼과 인스턴스는 AI가 수정하지 않고, 탭을 닫은 뒤에 적용하도록 했습니다.

---
## 마치며

디테일은 새 기법보다 원본 텍스처의 채널을 읽는 데서 나왔습니다. 금속 마스크, 머리카락 좌표, 리본의 옅은 주름이 모두 텍스처에 들어 있었고, 그것을 어느 범위로 잘라 쓰느냐가 결과를 정했습니다.

색감은 원작 수치에 가깝게 맞춘 값이 항상 보기 좋지는 않았습니다. 원작 화면은 야간 조명이라, 밝기를 곱해서 따라가면 흰색이 사라져 캐릭터가 탁해졌습니다.

[4편](/posts/toon-shading-4/)에서는 눈 깜빡임, 제자리 회전과 대시, Kawaii Physics로 넣은 천 흔들림을 정리합니다.

아래는 이번 시리즈에서 하지 못하고 남긴 항목입니다.

- [ ] 원작과 같은 조명 조건에서 다시 비교하기
- [ ] 베일의 별 무늬와 광택 추가
- [ ] 뒷머리 두 번째 하이라이트 층
- [ ] 재질마다 그림자 색을 다르게 주는 램프 텍스처
- [ ] 깊이 기반 림라이트
