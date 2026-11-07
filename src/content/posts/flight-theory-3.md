---
title: "게임 비행 이론 3편: 실속"
published: 2026-11-07
description: "당기면 당길수록 도는 비행기의 끝. 실속 곡선, 받음각 리미터, G 리미터, 그리고 코너 속도."
image: /images/flight-3/07_turn_rate_corner.png
tags: ["Unreal Engine", "비행", "실속", "조종 법칙"]
category: 게임 물리
draft: false
---

> **게임 비행 이론 시리즈** — [1편 롤·피치·요](/posts/flight-theory-1/) · [2편 양력·항력·추력·중력](/posts/flight-theory-2/) · **3편 실속** · 4편 조종면과 토크, 안정성 (준비 중)

## 들어가며: 당기면 당길수록 도는 비행기

게임 개발자들은 완전히 멘탈이 나가버렸습니다.

2편에서 양력을 받음각으로 계산하자 비행기가 드디어 기수를 따라 돌기 시작했습니다. 식도 간단했죠. C_L = C_Lα × α, 직선 하나면 됐거든요. 그런데 막상 저속 구간을 테스트하려니, 이 직선에는 끝이 없다는 게 문제가 됐거든요. 받음각을 20도, 30도, 40도로 키우면 양력도 그대로 2배, 3배로 늘어났습니다.

실제 날개는 그렇게 움직이지 않습니다. 받음각이 어느 선을 넘으면 날개 윗면을 타고 흐르던 공기가 표면에서 떨어져 나가고, 양력이 급격히 무너집니다. 이것이 <strong>실속(Stall)</strong>입니다. 비행 게임에서 "너무 느리게 날면 위험하다"는 긴장감은 전부 여기서 나옵니다.

## 문제 상황: 자전거 속도로 떠 있는 전투기

2편의 예제 기체(9,000kg, 날개 28m²)를 그대로 가져왔죠. 속도를 40m/s(시속 144km)까지 줄였는데도, 기수를 38도 들자 **수평비행이 그대로 유지**됐죠. 예제 기체처럼 날개가 양력을 낼 수 있는 한계가 C_L 1.17 정도라면, 실제로는 66m/s 아래에서 떠 있을 수 없는 기체입니다.

선회도 마찬가지였죠. 100m/s에서 스틱을 끝까지 당겨 받음각 40도를 만들자 **6.5G**로 꺾였습니다. 같은 속도에서 실속을 반영하면 낼 수 있는 최대치는 2.3G입니다.

![실속이 없는 모델: 40m/s 수평비행과 속도별 최대 G](/images/flight-3/01_no_stall_problem.png)

결국 느린 비행기가 빠른 비행기보다 더 날카롭게 도는, 전투 게임에서 가장 치명적인 밸런스 구멍이 났습니다. 플레이어들은 스로틀을 줄이고 제자리에서 빙빙 도는 게 최강 전술이라는 걸 금방 알아낼 겁니다.

## 해결책 1: 직선 대신 꺾이는 곡선을 쓰자

그래서 똑똑한 개발자들이 기발한 생각을 했는데요. **양력 계수를 식으로 계산하지 말고, 풍동 실험에서 얻은 것 같은 곡선을 표처럼 찾아 쓰자**는 겁니다. 곡선은 세 구간으로 나뉩니다.

| 구간 | 받음각 (예제 기체) | 양력 | 항력 |
| --- | --- | --- | --- |
| 정상 비행 | 0 \~ 14도 | α에 비례, 14도에서 최대 1.17 | 작다 |
| 실속 직후 | 14 \~ 20도 | 1.17 → 0.75로 급감 | 급증 |
| 깊은 실속 | 20 \~ 90도 | 0을 향해 줄어듦 | 판자처럼 공기를 막음 |

![실속이 있는 양력·항력 곡선](/images/flight-3/02_stall_curves.png)

이 글의 곡선은 설명을 위해 단순화한 것이고, 실제 기체의 데이터는 아닙니다. 실속 각도와 최대 양력 계수는 날개 모양에 따라 달라집니다.

최대 양력 계수가 생기면 **실속 속도**가 자연스럽게 나옵니다. 양력이 무게를 들 수 있는 가장 느린 속도입니다.

$$
V_{stall} = \sqrt{\frac{2\,m g}{\rho\, S\, C_{L,max}}}
$$

예제 기체에 넣으면 √(2 × 88,290 ÷ (1.225 × 28 × 1.17)) ≈ **66m/s**입니다. 이제 40m/s로는 떠 있을 수 없고, 100m/s에서 낼 수 있는 선회도 2.3G가 한계가 됩니다.

언리얼에서는 이 곡선을 코드가 아니라 **`UCurveFloat` 에셋**으로 두는 게 좋습니다. 디자이너가 커브 에디터에서 점을 끌어 기체별 특성을 만들 수 있거든요.

```cpp
// FlightAeroData.h — 기체별 공력 데이터
UCLASS(BlueprintType)
class UFlightAeroData : public UDataAsset
{
    GENERATED_BODY()
public:
    // X: 받음각(도, -90~90), Y: C_L
    UPROPERTY(EditAnywhere, Category = "Aero")
    TObjectPtr<UCurveFloat> LiftCurve;

    // X: 받음각(도), Y: C_D (실속 후 항력 증가 포함)
    UPROPERTY(EditAnywhere, Category = "Aero")
    TObjectPtr<UCurveFloat> DragCurve;
};

// FlightPawn.cpp — ComputeForces 안에서
const float AoADeg = FMath::RadiansToDegrees(AoA);
const float CL = AeroData->LiftCurve->GetFloatValue(AoADeg);
const float CD = AeroData->DragCurve->GetFloatValue(AoADeg);
```

두 가지를 신경 쓰세요. 음의 받음각(배면 비행, 기수 내리기)도 곡선에 넣어야 하고, 곡선 보간은 선형이나 자동 탄젠트로 두어 최대값 근처에서 곡선이 튀어 오르지 않게 해야 합니다.

## 반전: 끝까지 당겼더니 오히려 덜 돈다

그런데 진짜 문제는 여기서부터였습니다. 1편에서 만든 조작은 "스틱을 당기면 초당 몇 도씩 기수를 돌린다"였거든요. 기수는 명령대로 돌지만, 속도 방향은 양력이 끌어주는 만큼만 따라갑니다. 그 차이가 곧 받음각이고, 받음각이 14도를 넘는 순간 양력은 무너집니다.

150m/s로 수평비행하다가 스틱을 끝까지(초당 20도) 6초 동안 당겼죠.

- 기수는 123도 돌았는데 **실제로 날아간 방향은 51도만** 바뀌었죠.
- 받음각은 1.2초 만에 실속각을 넘어 6초엔 72도까지 커졌죠.
- G는 5.0에서 0.3으로 무너졌고, 속도는 150m/s에서 69m/s로 실속 속도 코앞까지 빠졌죠.

![150m/s 풀 스틱 6초: 리미터 없음 vs 받음각 리미터 궤적](/images/flight-3/03_full_stick_pull.png)

왼쪽은 기수가 점점 속도 방향에서 벗어나 6초엔 거의 뒤로 누운 채 올라갑니다. 오른쪽은 기수와 경로가 12도 간격을 유지하며 깔끔하게 돕니다.

플레이어 입장에서는 더 돌려고 끝까지 당겼는데 비행기가 오히려 기수만 쳐들고 힘없이 미끄러진 겁니다. 물리는 맞는데, 게임으로는 "이유 없이 조작이 안 먹힌다"는 불만이 됩니다.

바로 그 순간 또 다른 개발자가 천재적인 아이디어를 냈습니다. 실제 현대 전투기의 플라이 바이 와이어(fly-by-wire)가 쓰는 방식인 <strong>받음각 리미터(AoA limiter)</strong>입니다. 스틱이 기수를 직접 돌리는 게 아니라, **"받음각을 얼마나 줄지"를 명령**하게 바꾸는 겁니다.

1. 스틱(0\~1)에 최대 받음각(12도, 실속각 14도보다 2도 여유)을 곱해 목표 받음각을 만듭니다.
2. 현재 받음각과의 차이만큼 기수를 돌립니다. 여기에 속도 방향이 도는 속도를 더해 목표를 놓치지 않게 합니다.
3. 풀 스틱을 당겨도 받음각은 12도에서 멈추고, 비행기는 실속 직전의 최대 양력으로 돕니다.

$$
\alpha_{cmd} = \text{Stick} \times \alpha_{max}, \qquad \dot{\theta} = \dot{\gamma} + K\,(\alpha_{cmd} - \alpha)
$$

θ는 기수 각도, γ는 속도 방향(비행 경로각)입니다. 같은 6초 풀 스틱을 다시 했더니, 받음각은 12도를 넘지 않았고 **실제 날아간 방향은 81도** 바뀌었습니다. 속도도 131m/s를 지켰습니다. 덜 당긴 게 더 많이 돈 겁니다.

![받음각과 G의 시간 변화](/images/flight-3/04_alpha_g_time.png)

## 또 골치거리: 고속에서는 17G로 꺾인다

하지만 또 골치거리가 생겼습니다. 받음각 12도는 속도와 상관없이 같은 값인데, 양력은 속도의 제곱에 비례하거든요. 300m/s에서 풀 스틱을 당기자 양력이 무게의 **17.6배**가 됐죠. 조종사는 기절하고 기체는 부서질 힘입니다. 게임적으로는 "빠르고 잘 도는" 비행기가 되어, 속도를 관리할 이유가 사라지죠.

![속도별 풀 스틱 G: 받음각 리미터만 vs G 리미터 추가](/images/flight-3/05_g_vs_speed.png)

바로 그 순간 두 한계를 합치는 설계가 자리 잡았습니다. **받음각 한계와 G 한계 중 더 작은 쪽을 쓰자**는 겁니다. 현재 속도에서 9G를 내는 받음각을 역산하고, 12도와 비교해 작은 값을 목표 상한으로 씁니다.

$$
\alpha_{limit} = \min\left(\alpha_{max},\ \frac{n_{max}\, m g}{q\, S\, C_{L\alpha}}\right)
$$

- **저속**에서는 9G를 내려면 받음각이 12도보다 커야 하므로, 받음각 한계가 걸립니다. 돌 수 있는 만큼만 돕니다.
- **고속**에서는 작은 받음각으로도 9G가 나므로, G 한계가 걸립니다. 300m/s에서 실제로 돌려보니 받음각 6.6도, **9.0G**에서 멈췄습니다.
- 두 한계가 만나는 속도가 있습니다. 예제 기체에서는 **약 215m/s**이고, 이 속도에서 가장 빨리 돕니다. 전투기 조종사들이 말하는 <strong>코너 속도(corner speed)</strong>입니다.

![받음각 + G 리미터 조종 법칙 흐름](/images/flight-3/06_control_law.png)

```cpp
// FlightPawn.h
UPROPERTY(EditAnywhere, Category = "Flight|Limiter") float AlphaMaxDeg      = 12.f;  // 실속각 - 여유
UPROPERTY(EditAnywhere, Category = "Flight|Limiter") float NMax             = 9.f;   // G 한계
UPROPERTY(EditAnywhere, Category = "Flight|Limiter") float AlphaGain        = 6.f;   // 1/s
UPROPERTY(EditAnywhere, Category = "Flight|Limiter") float MaxPitchRateDeg  = 40.f;

// FlightPawn.cpp
float AFlightPawn::ComputeAlphaLimitRad(float Q) const
{
    const float AlphaMax = FMath::DegreesToRadians(AlphaMaxDeg);
    const float Weight   = Mass * Gravity;
    // n = Q·S·CL / W  →  9G에 필요한 CL을 선형 구간으로 역산
    const float AlphaForG = NMax * Weight / FMath::Max(Q * WingArea * CL_Alpha, KINDA_SMALL_NUMBER);
    return FMath::Min(AlphaMax, AlphaForG);
}

// StepPhysics(고정 스텝) 안에서, ComputeForces로 Accel·AoA·LiftDir를 구한 뒤
const float AlphaCmd = PitchInput * ComputeAlphaLimitRad(Q);
const float GammaDot = FVector::DotProduct(Accel, LiftDir) / FMath::Max(Speed, 1.f); // 속도 방향이 도는 빠르기
float PitchRateDeg = FMath::RadiansToDegrees(GammaDot + AlphaGain * (AlphaCmd - AoA));
PitchRateDeg = FMath::Clamp(PitchRateDeg, -MaxPitchRateDeg, MaxPitchRateDeg);

// 1편의 방식: 로컬 축 기준으로 오른쪽에 곱하기 (FRotator 인자 순서는 Pitch, Yaw, Roll)
S.Rotation = S.Rotation * FRotator(PitchRateDeg * Dt, 0.f, 0.f).Quaternion();
S.Rotation.Normalize();
```

G 한계를 역산할 때 선형 구간 기울기(C_Lα)를 쓴 건, G 한계가 걸리는 고속에서는 받음각이 작아 항상 선형 구간 안에 있기 때문입니다. 곡선을 직접 역산해도 되지만, 실속 구간에서는 같은 C_L을 내는 받음각이 두 개라 역산이 모호해집니다.

## 결과물: 직접 돌려 봤습니다

모두 2편의 예제 기체에 이번 편의 실속 곡선을 넣어 돌렸습니다. 세로 평면 2D 모델이고 1/120초 고정 스텝입니다.

| 실험 | 리미터 없음 | 받음각 리미터 | 받음각 + G 리미터 |
| --- | --- | --- | --- |
| 150m/s, 풀 스틱 6초: 경로가 돈 각도 | 51도 (실속) | 81도 | 81도 |
| 150m/s, 풀 스틱 6초: 끝 속도 | 69m/s | 131m/s | 131m/s |
| 300m/s, 풀 스틱: 최대 G | — | 16.8G | 9.0G |

150m/s에서는 9G까지 가지 못하므로 G 리미터가 걸리지 않아, 두 리미터의 결과가 같습니다. 300m/s 행의 16.8G는 실제 시뮬레이션 값이고, 본문의 17.6G는 풀 스틱 순간의 이론값입니다. 당기는 동안 속도가 줄어 실제 최댓값이 조금 낮게 나왔습니다.

받음각 12도 리미터를 걸면 수평비행 최저 속도는 실속 속도 66m/s보다 조금 높은 72m/s가 됩니다. 실속에서 2도의 여유를 두는 대가입니다.

![속도별 최대 선회율과 코너 속도](/images/flight-3/07_turn_rate_corner.png)

이 그래프가 이번 편의 결과물입니다. 두 한계를 걸자 선회율이 215m/s에서 꼭짓점을 찍는 모양이 됐습니다. 플레이어는 이제 너무 느리면 안 돌고 너무 빠르면 크게 도니, 속도를 코너 속도 근처로 관리해야 합니다. 2편의 에너지 관리가 전투의 규칙으로 이어지는 지점입니다.

### 3단계 관점으로 다시 보기

- **주니어**: 커브의 X축은 도, 코드의 받음각은 라디안입니다. 변환을 빼먹으면 받음각 0.2(라디안)를 0.2도로 읽어 실속이 아예 안 일어납니다. `AeroData`나 커브가 비어 있을 때의 널 체크도 필수입니다.
- **미들**: 커브와 데이터 에셋은 `UPROPERTY`로 참조해 GC가 수거하지 않게 하고, 여러 기체가 공유하는 에셋이므로 런타임에 값을 바꾸지 마세요. 멀티플레이에서는 스틱 입력을 보내고 리미터 계산은 서버와 클라이언트가 같은 파라미터로 해야 예측이 어긋나지 않습니다.
- **시니어**: 리미터는 물리가 아니라 <strong>조종 법칙(control law)</strong>입니다. "입력 → 목표 각속도" 단계를 인터페이스로 분리해 두면, 리미터 없는 "전문가 모드"와 기본 모드를 갈아 끼울 수 있습니다. AlphaMax와 NMax를 기체별로 다르게 주면 코너 속도가 달라져 기체마다 유리한 교전 속도가 생깁니다. 받음각이 한계에 가까워질수록 카메라 떨림과 컨트롤러 진동을 주면 플레이어가 한계를 느낄 수 있습니다.

다음 편에서는 이번에도 코드로 직접 돌린 기수를, 실제 비행기처럼 **조종면이 만드는 토크와 안정성**으로 돌리는 법을 다룹니다. 손을 놓으면 기수가 왜 스스로 돌아오는지도 여기서 나옵니다.
