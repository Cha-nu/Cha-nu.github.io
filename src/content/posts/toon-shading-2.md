---
title: "툰 셰이딩 2편: 언리얼 머티리얼 구현"
published: 2026-11-19
description: "1편의 기법을 언리얼 엔진 5.8 머티리얼 노드로 구성한 방법입니다. 후처리 셀 셰이딩, 얼굴 SDF, 눈, 외곽선, 그리고 캐릭터 조작과 카메라까지 정리합니다."
category: 언리얼 엔진
tags: ["Unreal Engine", "툰 셰이딩", "머티리얼", "포스트 프로세스", "실습"]
image: /images/toon-shading-2/00_cover.png
project: toonshader
draft: false
---

> **툰 셰이딩 시리즈** — [1편 셀 셰이딩의 원리](/posts/toon-shading-1/) · **2편 언리얼 머티리얼 구현**
>
> 언리얼 엔진 5.8 기준입니다. 이 글의 수치는 프로젝트 머티리얼의 기본값이며, 머티리얼 인스턴스에서 바꾼 값은 따로 적었습니다.

> **팬메이드·학습 목적 고지** — 이 글에 나오는 캐릭터 모델, 텍스처, 게임 화면의 저작권은 명조: 워더링 웨이브(Wuthering Waves)의 개발사 Kuro Games에 있습니다. 셰이더 공부를 위한 비상업적 팬메이드 작업이며, 모델과 텍스처 파일은 배포하지 않습니다. 문제가 되는 경우 알려 주시면 내리겠습니다.

---
## 들어가며

1편에서 정리한 기법을 실제 머티리얼과 블루프린트로 어떻게 만들었는지 정리합니다. 노드 연결은 그래프 순서대로 적고, 파라미터 이름과 기본값을 함께 적었습니다.

<strong>AI 활용</strong>: 각 절 제목 아래에 누가 만들었는지 적었습니다. AI 어시스턴트(Claude)는 언리얼 에디터의 MCP 연결로 머티리얼과 블루프린트를 직접 수정하거나, 노드 구성을 안내하고 결과를 검토하는 방식으로 참여했습니다.

<iframe src="https://www.youtube-nocookie.com/embed/O5YsP1ajFg8" title="툰 셰이딩 완성본" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

![완성한 툰 셰이딩 캐릭터를 카메라로 가까이 잡은 화면](/images/toon-shading-2/00_cover.png)

완성 화면입니다. 몸은 후처리로 명암 단계를 나누고, 얼굴과 눈은 별도 머티리얼로 그렸습니다.

---
## 모델 준비

원작 모델을 블렌더로 가져와 머티리얼 슬롯마다 텍스처를 Principled BSDF의 Base Color에 연결했습니다. 이 상태로 FBX로 내보내 언리얼에 가져왔습니다.

![블렌더 셰이딩 탭에서 눈 텍스처를 Principled BSDF에 연결한 화면](/images/toon-shading-2/01_blender_texture.png)

눈 슬롯(`MI_R2T1LiliMd10011Eye`)에 `Eye_D` 텍스처를 연결한 모습입니다. 언리얼에서는 이 텍스처들을 머티리얼 인스턴스의 파라미터로 다시 연결했습니다.

목표로 삼은 원작 화면은 아래와 같습니다. 명암이 두세 단계로 끊기고, 머리카락과 베일에 채도가 높게 유지됩니다.

![목표로 삼은 원작 게임 화면](/images/toon-shading-2/02_reference.png)

출처: 명조: 워더링 웨이브(Kuro Games) 게임 화면.

---
## 전체 구성

| 에셋 | 역할 | 셰이딩 | 만든 방식 |
| --- | --- | --- | --- |
| `MM_ToonLit` | 몸·옷·머리 | Default Lit | 직접 구성 (AI 조언) |
| `PP_Toon` | 명암 단계, 하이라이트, 림 | Post Process | 직접 구성(AI 조언) → AI 재구현 → 직접 정리 |
| `MM_ToonFace` | 얼굴 SDF 그림자 | Unlit | 직접 구성 (AI 노드 안내·검토) |
| `MM_ToonEye` | 눈 시차, 광택막 | Unlit | 직접 구성, 광택 2단은 AI 추가 |
| `M_ToonOutline` | 외곽선 | Unlit, Masked | 직접 구성 (기존) |

몸은 엔진 조명을 받고 후처리에서 단계 처리합니다. 얼굴과 눈은 Unlit이라 GBuffer의 Diffuse가 0이 되어 후처리 마스크에서 자동으로 빠집니다.

---
## 기존 셰이더와 문제

<strong>만든 사람</strong>: 직접 (참고 강의: [Unreal Engine 5 - Toon Shader Tutorial](https://youtu.be/GAkxpwy9xtg))

처음 셰이더 `MM_ToonShader`는 Default Lit이지만 Base Color를 비우고 결과를 Emissive로 출력했습니다. 명암은 `SkyAtmosphereLightDirection`과 `PixelNormalWS`의 내적으로 직접 계산했습니다.

```text
NDotL          = dot(SkyAtmosphereLightDirection, PixelNormalWS) * 0.5 + 0.5
DrawShadow     = SmoothStep(ShadowStart - Smooth, ShadowStart + Smooth, NDotL)
DrawOuterShadow= SmoothStep(OuterStart - Smooth, OuterStart + Smooth, NDotL)
DrawHighlight  = SmoothStep(HighlightStart ± Smooth, 1 - NDotL)
DrawRimLight   = SmoothStep(RimStart ± Smooth, Fresnel(Exponent, BaseReflect))
BaseTexture    = Power(Texture, BaseColorPower) * BaseColorBrightness
Final          = 위 마스크로 Lerp 연결 → Emissive
```

![MM_ToonShader의 Texture, DrawHighlight, LimLight 구간](/images/toon-shading-2/10_old_shader_graph.png)

`Texture` 묶음에서 `Power`와 `Multiply`로 기본 색을 만들고, 오른쪽 `DrawHighlight`와 `LimLight` 묶음에서 마스크를 만듭니다.

<iframe src="https://www.youtube-nocookie.com/embed/RmAcXpPYezE" title="첫 번째 툰 셰이더 둘러보기" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

첫 번째 셰이더의 그래프와 부위별 머티리얼 인스턴스를 둘러본 영상입니다.

AI와 원인을 분석한 결과는 다음과 같습니다.

| 증상 | 원인 |
| --- | --- |
| 다른 물체의 그림자가 지지 않음 | Emissive 출력이라 엔진 조명과 그림자 맵을 건너뜀 |
| 눈이 탁하고 그림자가 짐 | 눈도 같은 명암 계산을 받음 |
| 원작보다 밝게 뜸 | `HighlightColor` (5,5,5), 노출의 영향을 받는 Emissive 출력 |

![첫 번째 툰 셰이더를 적용한 캐릭터](/images/toon-shading-2/03_first_shader.png)

오른쪽 캐릭터가 첫 번째 툰 셰이더입니다. 바닥에는 그림자가 지지만 캐릭터 몸에는 지지 않고, 전체가 균일하게 밝습니다.

<video src="/videos/toon-shading/first-shadow.mp4" controls muted playsinline></video>

첫 번째 셰이더에서 Directional Light를 돌려 본 모습입니다.

인스턴스에서는 `BaseColorPower`를 3.5, `ShadowStartRange`를 0.04로 바꿔 쓰고 있었습니다. Power가 크면 밝은 색이 크게 어두워지고 색이 진해집니다.

---
## MM_ToonLit: 몸은 평범한 Lit으로

<strong>만든 사람</strong>: 직접 (AI 조언)

엔진이 그림자를 계산하도록 Base Color에 텍스처를 넣습니다. 툰 처리는 하지 않습니다.

```text
TextureSampleParameter2D(BaseColor).RGB
  → Power(Exp = BaseColorPower 2.0)
  → Multiply(BaseColorBrightness 1.0)
  → Base Color
Constant 0 → Specular
Constant 1 → Roughness
```

- `Power`는 텍스처 RGB 핀에서 받습니다. RGBA를 넣으면 알파까지 보정됩니다.
- Specular 0, Roughness 1은 반사광이 후처리의 빛의 양 계산을 흐트러뜨리지 않게 하려는 설정입니다.

후처리로 바꾼 직후에는 아래처럼 색이 바래고 피부와 머리카락이 하얗게 떴습니다.

![후처리 툰 셰이딩으로 바꾼 직후의 캐릭터](/images/toon-shading-2/04_second_shader.png)

![기존 셰이더와 후처리 셰이더를 나란히 비교한 화면](/images/toon-shading-2/05_first_vs_second.png)

왼쪽이 기존 셰이더, 오른쪽이 후처리 셰이더입니다. 두 쪽 모두 같은 텍스처를 씁니다. 차이는 기존 셰이더에 있던 `BaseColorPower` 3.5였습니다. 색을 3.5제곱하면 밝은 색이 크게 어두워지며 진해집니다. 그래서 `MM_ToonLit`에 `Power`를 넣고 2에서 시작해 맞췄습니다. Power를 후처리가 아니라 Base Color 쪽에 넣어야 엔진 조명, GBuffer의 Diffuse, 빛의 양 계산이 같은 색을 기준으로 맞물립니다.

![MM_ToonLit 그래프](/images/toon-shading-2/11_toonlit_graph.png)

텍스처 RGB를 `Power`와 `Multiply`를 거쳐 Base Color에 연결합니다.

---
## PP_Toon: 후처리 셀 셰이딩

<strong>만든 사람</strong>: AI의 조언을 받아 직접 구성했습니다. 그런데 AI가 MCP로 상태를 확인하면서 머티리얼을 다시 컴파일하는 바람에, 적용하지 않은 편집이 저장본으로 되돌아갔습니다(아래 "막힌 점과 해결" 참고). 그 뒤 AI에게 같은 구조로 다시 구현해 달라고 맡겼고, 결과를 Named Reroute로 정리하고 그림자 색을 조정했습니다.

Material Domain은 Post Process, Blendable Location은 `Scene Color Before DOF`입니다. 처음에는 `Before Bloom`이었습니다. 이 위치는 안티에일리어싱(TSR) 뒤라서, 프레임마다 흔들리는 스텐실 경계가 정리되지 않고 외곽선이 떨리는 원인으로 보고 TSR 앞으로 옮겼습니다.

### 1. 입력과 빛의 양

```text
SceneTexture:PostProcessInput0 → Mask(RGB) → [SceneColor]
SceneTexture:DiffuseColor      → Mask(RGB) → [Diffuse]
SceneTexture:WorldNormal       → Mask(RGB) → [WorldNormal]
SceneTexture:CustomStencil     → Mask(R)   → [Stencil]

SceneColor ÷ Max(Diffuse, 0.001)
  → Dot((0.3, 0.59, 0.11))
  → ÷ LightScale(1.0)
  → Saturate → [L]
```

`SceneTexture`의 출력은 RGBA 4채널입니다. 3채널 상수와 Dot하거나 출력으로 내보낼 때 크기가 맞도록 바로 Mask(RGB)를 거칩니다.

### 2. 단계 마스크

```text
[DrawShadow]      = SmoothStep(0.35 - 0.05, 0.35 + 0.05, L)
[DrawOuterShadow] = SmoothStep(0.40 - 0.01, 0.40 + 0.01, L)

[NDotL]           = Dot(WorldNormal, SkyAtmosphereLightDirection) * 0.5 + 0.5
[DrawHighlight]   = SmoothStep(0.40 - 0.01, 0.40 + 0.01, 1 - NDotL)
[HighlightMask]   = (1 - DrawHighlight) * DrawOuterShadow   // 그림자 안에는 하이라이트 없음

Fresnel(Exponent 2, BaseReflect 0.02, Normal = WorldNormal)
[DrawRimLight]    = SmoothStep(0.70 - 0.45, 0.70 + 0.45, Fresnel)
```

L은 그림자 맵이 포함된 빛의 양이라 밝은 면이 전부 1 근처로 꽉 찹니다. 그래서 하이라이트 띠는 L 대신 기존 셰이더처럼 Half-Lambert(NDotL)로 정했습니다. `SkyAtmosphereLightDirection`은 레벨에 Sky Atmosphere가 있고 Directional Light의 Atmosphere Sun Light가 켜져 있어야 값이 나옵니다.

### 3. 톤 합성과 마스크

```text
[Base]  = Diffuse * BaseColorBrightness(1.0)
Lerp(Base*ShadowColor, Base*ShadowOuterColor, DrawShadow)
  → Lerp(위, Base, DrawOuterShadow)
  → Lerp(위, 위*HighlightColor, HighlightMask)
  → Lerp(위, 위*RimLightColor, DrawRimLight)              → [Toon]

[Mask]  = Saturate(1 - Abs(Stencil - StencilValue 1))
        * Saturate(Dot(Diffuse, (0.3, 0.59, 0.11)) * 1000)  // Diffuse가 0인 얼굴·눈 제외
[Final] = Lerp(SceneColor, Toon, Mask) → Emissive Color
```

| 파라미터 | 기본값 |
| --- | --- |
| ShadowColor / ShadowOuterColor | (0.55, 0.45, 0.65) 둘 다 |
| HighlightColor / RimLightColor | (1, 1, 1) |
| LightScale / StencilValue | 1 / 1 |

그림자 색은 처음에 회색(0.38, 0.589)이었는데, 원작처럼 그림자에 색이 돌도록 연보라로 바꿨습니다. `RimLightColor`가 (1, 1, 1)이면 곱해도 색이 바뀌지 않으므로, 림라이트를 보려면 1보다 크게 줘야 합니다.

![PP_Toon 전체 그래프](/images/toon-shading-2/15_pp_overview.png)

PP_Toon 전체 그래프입니다. 입력, 빛의 양, 단계 마스크, 톤 합성 순서로 왼쪽에서 오른쪽으로 흐릅니다.

<iframe src="https://www.youtube-nocookie.com/embed/3ffV4GPJbQ0" title="후처리 툰 셰이더 둘러보기" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

MM_ToonLit, PP_Toon, MM_ToonEye, MM_ToonFace, 캐릭터 블루프린트, Post Process Volume 설정을 차례로 둘러본 영상입니다.

![PP_Toon의 SceneTexture 입력과 단계 마스크 구간](/images/toon-shading-2/12_pp_input.png)

`PP` 묶음에서 SceneTexture 네 개를 Mask로 자르고 이름을 붙입니다. `DotProduct` 묶음이 `NDotL`을 만들고, 오른쪽 묶음들이 `DrawOuterShadow`, `DrawHighlight`, `HighlightMask`를 만듭니다.

![PP_Toon의 DrawHighlight, DrawRimLight, Mask 구간](/images/toon-shading-2/13_pp_masks.png)

`DrawRimLight`는 `WorldNormal`을 넣은 Fresnel에서, `Mask`는 스텐실 값에서 만듭니다.

![PP_Toon의 톤 합성 구간](/images/toon-shading-2/14_pp_tone.png)

`Emissive` 묶음에서 그림자 색, 중간톤, 하이라이트, 림라이트 순서로 Lerp를 이어 붙이고, 마지막 Lerp에서 `Mask`로 원래 화면 색(`SceneColor`)과 섞어 `Final`을 만듭니다.

<video src="/videos/toon-shading/second-shadow.mp4" controls muted playsinline></video>

후처리 셰이더에서 Directional Light를 돌려 본 모습입니다.

### 4. 함께 바꾼 설정

| 위치 | 설정 |
| --- | --- |
| Project Settings | Custom Depth-Stencil Pass = Enabled with Stencil |
| 캐릭터 메시 | Render CustomDepth Pass 켜기, Stencil Value 1 |
| Post Process Volume | Infinite Extent, Post Process Materials에 PP_Toon, Exposure Manual |
| Post Process Volume | Apply Physical Camera Exposure 끄기 |
| 레벨 | Sky Atmosphere, Sky Light 추가 |

![Project Settings의 Custom Depth-Stencil Pass 설정](/images/toon-shading-2/20_project_custom_depth.png)

Project Settings에서 `Custom Depth-Stencil Pass`를 `Enabled with Stencil`로 바꿉니다.

![Post Process Volume의 Infinite Extent 설정](/images/toon-shading-2/21_ppv_unbound.png)

Post Process Volume은 `Infinite Extent (Unbound)`를 켜서 레벨 전체에 적용합니다.

Exposure를 Manual로 바꾼 직후 화면 전체가 거의 검게 나왔습니다. Apply Physical Camera Exposure가 켜진 채라 카메라 기본값(ISO 100, f/4)으로 노출을 계산한 것이 원인으로 보여 이 옵션을 껐습니다.

---
## MM_ToonFace: 얼굴 SDF 그림자

<strong>만든 사람</strong>: 직접 (AI가 노드 구성을 안내하고 두 차례 검토)

Shading Model은 Unlit입니다.

```text
SkyAtmosphereLightDirection → Mask(RG) → Normalize → [Lxy]
Constant3(0,1,0) → Transform(Local→World) → Mask(RG) → Normalize → [Fwd]
Constant3(1,0,0) → Transform(Local→World) → Mask(RG) → Normalize → [Right]

[FdotL] = Dot(Fwd, Lxy)
[RdotL] = Dot(Right, Lxy)
[FlipUV]= Append(1 - TexCoord.R, TexCoord.G)
[UV]    = If(A = RdotL, B = 0, A>B: FlipUV, A==B: TexCoord, A<B: TexCoord)
[SDF]   = TextureSample(T_FemaleMFace_SDF, UV).R
[Threshold] = 0.5 - 0.5 * FdotL
[Lit]   = SmoothStep(Threshold - FaceSmooth, Threshold + FaceSmooth, SDF)   // FaceSmooth 0.01
[Base]  = Power(FaceTex.RGB, BaseColorPower 2) * Brightness 1
Lerp(Base * FaceShadowColor(0.95, 0.74, 0.69), Base, Lit) → Emissive Color
```

- 메시의 정면 축은 스켈레탈 메시 에디터에서 확인했습니다. 메시 Yaw가 -90°라 로컬 +Y가 정면입니다.
- `BaseColorPower`는 몸(`MM_ToonLit`)과 같은 2로 맞춰야 얼굴만 하얗게 뜨지 않습니다.

검토에서 고친 실수는 세 가지였습니다.

| 실수 | 결과 | 수정 |
| --- | --- | --- |
| Transform 입력에 빛 방향을 연결 | Fwd·Right가 빛 방향이 되어 그림자가 안 움직임 | 입력을 상수 (0,1,0)/(1,0,0)으로 |
| FlipUV에 V가 빠짐 | UV가 1차원 | `Append`로 V를 붙임 |
| Lerp의 A·B가 반대 | 밝은 면이 그림자 색 | A = Base×그림자색, B = Base |

![MM_ToonFace 그래프](/images/toon-shading-2/16_face_graph.png)

왼쪽 `UV` 묶음에서 `RdotL`에 따라 일반 UV와 `FlipUV` 중 하나를 골라 SDF를 샘플링합니다. 오른쪽 `Lit` 묶음은 `Threshold`±`FaceSmooth`로 SmoothStep을, `Texture` 묶음은 Power와 Brightness로 `Base`를 만듭니다.
<video src="/videos/toon-shading/second-shadow.mp4" controls muted playsinline></video>

Directional Light를 돌리면 몸은 후처리로, 얼굴은 SDF 경계로 그림자가 함께 움직입니다.

---
## MM_ToonEye: 눈

<strong>만든 사람</strong>: 직접 (AI 안내·검토). 두 번째 광택과 광택 세기 파라미터는 AI가 추가했습니다.

```text
[Mask]  = OneMinus(Saturate(Distance(TexCoord, (0.5, 0.5)) * 2))
[EyeUV] = BumpOffset(TexCoord, Height = Mask, HeightRatio = ParallaxHeight 0.1)
[Base]  = Power(EyeTex(EyeUV).RGB, EyePower 1) * Brightness 1

[HL_UV] = (TexCoord - HL_Position.RG) / (HL_Scale * HL_Width.RG) + 0.5
        → CustomRotator(Angle = HL_Rotate 0.24, Center 0.5)
[HL]    = TextureSample(T_EyesSecondHeightLight05_EG, HL_UV).R
HL2_UV  = (TexCoord - HL2_Position.RG) / (HL_Scale * HL2_Width.RG) + 0.5
HL2     = TextureSample(같은 텍스처, HL2_UV).B

Emissive = Base * EyeShade(1)
         + (HL * HL_Intensity 0.15 + HL2 * HL2_Intensity 0.1) * HL_Color
```

| 파라미터 | 값 |
| --- | --- |
| HL_Position / HL_Width | (0.48, 0.54) / (0.93, 0.86) |
| HL2_Position / HL2_Width | (0.155, 0.474) / (0.867, 0.768) |
| HL_Scale | 0.43 |
| HL_Color | (2.95, 2.47, 3.0) |

- 하이라이트 텍스처는 Sampler Source를 Clamp로, Mip Gen Settings를 NoMipmaps로 둡니다. Wrap이면 반대편에 반복되고, 밉맵이 있으면 멀리서 눈 전체가 뿌옇게 번집니다.
- 광택 텍스처는 R 채널에 첫 번째, B 채널에 두 번째 광택이 들어 있고 G 채널은 비어 있습니다. AI가 원본 텍스처 파일의 채널 값을 읽어 확인했습니다.

만드는 과정에서 눈에 생긴 문제 두 가지입니다.

![눈동자에 흰 얼룩처럼 크게 뜬 하이라이트](/images/toon-shading-2/06_eye_highlight_blob.png)

광택 텍스처를 작은 반짝이 점으로 잘못 해석해 `HL_Color` (2.95, 2.47, 3.0)를 그대로 더했을 때입니다. 넓은 초승달 모양 광택이 하얗게 타면서 눈동자 가운데에 흰 얼룩이 생겼습니다. 지금은 `HL_Intensity` 0.15를 곱해 약한 광택막으로 씁니다.

![멀리서 본 캐릭터의 눈이 뿌옇게 번진 화면](/images/toon-shading-2/07_eye_far_blur.png)

카메라가 멀어졌을 때입니다. 작은 밉맵에서 광택이 눈 전체로 번진 것으로 보고, 광택 텍스처의 밉맵을 껐습니다.

![MM_ToonEye 그래프](/images/toon-shading-2/17_eye_graph.png)

`Emissive` 묶음입니다. 두 광택(`HL`, `HL2`)에 각각 세기를 곱해 더하고 `HL_Color`를 곱한 뒤, `Base`×`EyeShade`에 더해 출력합니다.
![밝기와 광택 세기를 고친 뒤의 캐릭터 정면](/images/toon-shading-2/18_eye_after.png)

밝기를 1로 되돌리고 광택을 약하게 더한 뒤의 모습입니다. 눈동자의 흰 얼룩이 사라지고 텍스처에 그려진 반짝임이 보입니다.

---
## 외곽선

<strong>만든 사람</strong>: 직접 (기존). 리더 포즈 설정은 AI가 추가했습니다.

`M_ToonOutline`은 Unlit, Masked, Two Sided입니다. World Position Offset에 `VertexNormalWS × OutlineThickness(0.1)`를 넣고, 마스크 텍스처나 정점 색으로 두께를 조절하는 스태틱 스위치가 있습니다. 캐릭터 블루프린트에는 본체와 같은 메시를 `Outline` 컴포넌트로 하나 더 붙였습니다.

Construction Script에서 `Outline → Set Leader Pose Component(Mesh)`를 호출해, 애니메이션 중에도 외곽선 메시가 본체 포즈를 그대로 따라가게 했습니다.

![M_ToonOutline 그래프](/images/toon-shading-2/19_outline_graph.png)

`VertexNormalWS`에 `OutlineThickness`를 곱해 World Position Offset으로 내보냅니다. 스태틱 스위치로 마스크 텍스처와 정점 색 중 두께 기준을 고릅니다.

<iframe src="https://www.youtube-nocookie.com/embed/fHGjnniIrnk" title="외곽선 머티리얼 둘러보기" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

외곽선 머티리얼과 부위별 인스턴스, 캐릭터 블루프린트의 Outline 컴포넌트를 둘러본 영상입니다.

---
## 캐릭터 조작과 카메라

<strong>만든 사람</strong>: AI가 MCP로 입력 에셋, 블루프린트 그래프, 애니메이션 블루프린트를 만들었습니다. 동작 확인과 수치 조정 요청은 직접 했습니다.

| 입력 | 키 | 동작 |
| --- | --- | --- |
| IA_Move | WASD | 카메라 기준 이동 |
| IA_Look | 마우스 | 카메라 회전 |
| IA_Zoom | 마우스 휠 | 카메라 거리 40\~700 |
| IA_Walk | Left Ctrl | 걷기(120)·달리기(300) 전환 |
| IA_Jump / IA_Action | Space / 좌클릭 | 점프 / 대기 액션 재생 |

- <strong>카메라</strong>: SpringArm(Use Pawn Control Rotation)에 위치 지연 8, 회전 지연 14를 줬습니다. 이동 중 마우스를 1.2초 움직이지 않으면 카메라가 캐릭터 뒤로 천천히 돌아옵니다.
- <strong>얼굴 줌</strong>: 카메라 거리가 250에서 80으로 줄어드는 동안 SpringArm의 Target Offset을 머리 본 위치로 옮겨, 당길수록 얼굴을 중심으로 잡습니다.
- <strong>애니메이션</strong>: 대기(두 동작 랜덤), 걷기, 달리기를 속도로 블렌드합니다. 속도는 FInterpTo로 보간해 멈출 때 끊기지 않게 했습니다. 이동 입력이 들어오면 재생 중인 액션을 0.2초 블렌드로 멈춥니다.

<iframe src="https://www.youtube-nocookie.com/embed/O5YsP1ajFg8" title="캐릭터 조작과 카메라 시연" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

완성 영상에서 이동, 마우스 휠 줌, 카메라 회전을 볼 수 있습니다.

---
## 막힌 점과 해결

- 문제: 열려 있는 머티리얼을 AI가 다시 컴파일하자, 적용하지 않은 편집이 사라졌습니다.
  - 원인: 머티리얼 에디터는 Apply 전까지 임시 복사본을 편집하는데, 원본을 다시 컴파일하자 에디터가 저장본으로 새로고침됐습니다.
  - 해결: 이후로는 편집 중인 머티리얼은 Apply·Save 후 탭을 닫고 나서 수정하게 했습니다.
- 문제: 에디터를 다시 켜자 애니메이션 블루프린트가 컴파일되지 않았습니다.
  - 원인: 도구로 만든 애니메이션 블루프린트에 대상 스켈레톤이 비어 있었습니다.
  - 해결: 스켈레톤 에셋에서 Create → Anim Blueprint로 새로 만들고 그래프를 다시 구성했습니다.
- 문제: 블루프린트 기본값을 바꿨는데 레벨에 놓인 캐릭터에는 적용되지 않았습니다.
  - 원인: 레벨 인스턴스가 이전 값을 따로 들고 있었습니다.
  - 해결: BeginPlay에서 이동·카메라 설정을 다시 적용하는 `ApplySetup` 함수를 두었습니다.
- 문제: 치마와 스카프 흔들림을 위해 Kawaii Physics 플러그인을 넣었지만 더 어색해졌습니다.
  - 해결: 우선 노드를 제거했습니다. 본 사슬별 설정을 다시 다듬어 다음 편에서 개선하려 합니다.
- 문제: Standalone 실행에서 화면이 픽셀처럼 깨져 보였습니다.
  - 원인: 데스크톱 기본 화면 비율 설정(`r.ScreenPercentage.Default.Desktop.Mode=1`)이 모니터 해상도에 따라 내부 해상도를 낮춘 것으로 판단했습니다.
  - 해결: `DefaultEngine.ini`에 `r.ScreenPercentage.Default.Desktop.Mode=0`, `r.ScreenPercentage.Default=100`을 넣었습니다.

---
## 마치며

명암 단계는 후처리로, 얼굴과 눈은 Unlit으로 나눠 처리하면서 그림자를 받는 툰 캐릭터를 만들 수 있었습니다. 다만 재질마다 그림자 색을 다르게 주는 램프 텍스처, 두께가 일정한 깊이 기반 림라이트, 머리카락 하이라이트, 정지·시작 애니메이션의 루트 모션은 아직 남아 있습니다.

다음 편에서는 이번에 뺀 Kawaii Physics를 다시 다듬어 치마, 베일, 스카프의 흔들림을 개선해 오겠습니다.

- [ ] Kawaii Physics로 천 흔들림 개선
- [ ] 깊이 기반 림라이트
- [ ] 머리카락 하이라이트(천사 고리)와 MatCap
- [ ] 루트 본을 정리해 정지·시작 애니메이션 적용
