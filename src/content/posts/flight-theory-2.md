---
title: "게임 비행 이론 2편: 양력·항력·추력·중력"
published: 2026-11-07
description: "레일 위를 미끄러지던 비행기에 무게를 주는 법. 네 가지 힘, 받음각 기반 양력, 그리고 고정 타임스텝."
image: /images/flight-2/02_four_forces.png
tags: ["Unreal Engine", "비행", "물리", "고정 타임스텝"]
category: 게임 물리
draft: false
---

> **게임 비행 이론 시리즈** — [1편 롤·피치·요](/posts/flight-theory-1/) · **2편 양력·항력·추력·중력** · [3편 실속](/posts/flight-theory-3/) · 4편 조종면과 토크, 안정성 (준비 중)

## 들어가며: 레일 위를 달리는 비행기

게임 개발자들은 완전히 멘탈이 나가버렸습니다.

1편에서 회전은 쿼터니언으로 깔끔하게 정리했습니다. 이제 비행기를 앞으로 날리기만 하면 되는데요. 가장 쉬운 방법은 "기수가 향한 방향으로 일정한 속도로 이동"이었습니다. 코드 한 줄이면 되고, 조작한 대로 정확히 날아가니 테스트할 때도 문제가 없어 보였거든요. 그런데 막상 플레이테스트를 하려니, 비행기가 하늘을 나는 게 아니라 보이지 않는 레일 위를 미끄러지는 느낌이 나거든요.

```cpp
// ❌ 레일 방식: 속도 = 기수 방향 × 고정 속력
const FVector Velocity = GetActorForwardVector() * Speed;
AddActorWorldOffset(Velocity * DeltaTime);
```

## 문제 상황: 하늘로 올라가도 지치지 않는 비행기

250m/s로 날다가 기수를 수직으로 세워 30초를 버텼죠. 레일 방식 비행기는 30초 뒤에도 **속도 250m/s 그대로, 고도 +7,500m**였죠. 중력을 거슬러 올라가는데 에너지를 하나도 안 쓴 겁니다.

![250m/s 수직 상승 30초: 레일 방식과 네 가지 힘 비교](/images/flight-2/01_rail_vs_physics_climb.png)

엔진 출력을 0으로 내려도 마찬가지였죠. 속도는 `Speed` 변수가 정하니까요. 급선회를 해도 속도 방향이 기수를 즉시 따라가서, 관성도 미끄러짐도 없었죠.

결국 이 방식에는 비행 게임의 재미가 되는 것들이 통째로 빠져 있습니다. **고도와 속도를 맞바꾸는 에너지 관리**, 선회할 때 밀려나는 느낌, 엔진을 줄였을 때의 긴장감입니다.

## 해결책 1: 속도를 정하지 말고 힘을 주자

그래서 똑똑한 개발자들이 기발한 생각을 했는데요. **속도를 직접 정하지 말고, 비행기에 걸리는 힘만 계산하자**는 겁니다. 속도는 그 힘이 만들어 낸 결과가 되고요. 비행기에는 딱 네 가지 힘이 걸립니다.

| 힘 | 방향 | 크기 | 만드는 것 |
| --- | --- | --- | --- |
| 추력 (Thrust) | 기수 방향 | 스로틀 × 최대 추력 | 엔진 |
| 항력 (Drag) | 속도 반대 | ½ρv² · S · C_D | 공기 저항 |
| 양력 (Lift) | 속도에 수직 | ½ρv² · S · C_L | 날개 |
| 중력 (Weight) | 아래 | m · g | 지구 |

![비행기에 걸리는 네 가지 힘](/images/flight-2/02_four_forces.png)

추력만 기수를 따르고, 양력과 항력은 속도를 기준으로 방향이 정해진다는 점이 핵심입니다. 기수와 속도 사이의 각도 α는 반전에서 다시 나옵니다.

항력과 양력에 공통으로 붙은 ½ρv²는 <strong>동압(dynamic pressure)</strong>입니다. 속도가 2배면 양력도 항력도 4배가 됩니다. ρ는 공기 밀도, S는 날개 면적, C_L과 C_D는 날개 모양이 정하는 계수입니다.

네 힘을 더하고 질량으로 나누면 가속도가 나오고, 가속도를 쌓으면 속도가, 속도를 쌓으면 위치가 나옵니다.

$$
\vec{a} = \frac{\vec{T} + \vec{L} + \vec{D} + m\vec{g}}{m}, \qquad \vec{v} \mathrel{+}= \vec{a}\,\Delta t, \qquad \vec{p} \mathrel{+}= \vec{v}\,\Delta t
$$

처음 구현은 보통 이렇게 생깁니다. 양력은 "날개가 위로 밀어주는 힘"이니 기체의 위 방향으로, 계수는 수평 비행이 되는 값으로 고정해 둡니다.

```cpp
// 해결책 1: 네 가지 힘 + F=ma (양력 계수는 고정)
const float  Speed = Velocity.Size();
const FVector VelDir = Velocity.GetSafeNormal();
const float  Q = 0.5f * AirDensity * Speed * Speed;        // 동압

const FVector Thrust = GetActorForwardVector() * Throttle * MaxThrust;
const FVector Lift   = GetActorUpVector() * Q * WingArea * CL_Fixed;   // ← 여기가 다음 문제
const FVector Drag   = -VelDir * Q * WingArea * CD;
const FVector Weight = FVector(0, 0, -Mass * Gravity);

const FVector Accel = (Thrust + Lift + Drag + Weight) / Mass;
Velocity += Accel * DeltaTime;
AddActorWorldOffset(Velocity * 100.f * DeltaTime);   // m → UE 단위(cm)
```

이 글의 예제 기체는 질량 9,000kg, 날개 면적 28m², 최대 추력 60kN인 가상의 전투기입니다. 공기 밀도는 해수면 값(1.225kg/m³)으로 고정했습니다. 언리얼의 길이 단위는 cm라서, 물리 계산은 m로 하고 위치에 반영할 때만 100을 곱했습니다.

이제 수직 상승을 하면 중력과 항력이 속도를 깎고, 엔진을 끄면 속도가 줄어듭니다. 드디어 비행기가 무게를 갖게 됐죠.

## 반전: 기수를 들어도 올라가지 않는다

그런데 진짜 문제는 여기서부터였습니다. 양력 계수를 고정해 두면 양력은 **오직 속도에만** 따라 변하거든요. 조종사가 스틱을 어떻게 움직이든 양력은 그대로입니다.

두 가지 실험을 했습니다. 예제 기체의 고정 계수는 200m/s에서 수평 비행이 되는 값(C_L = 0.129)입니다.

- **200m/s에서 기수를 10도 들었더니**, 8초 뒤 고도가 오히려 7m 낮아졌습니다. 기수만 들리고 비행기는 수평으로 미끄러졌죠.
- **기수를 수평으로 둔 채 280m/s로 속도만 올렸더니**, 양력이 무게의 1.96배가 됐습니다. 기수는 수평인데 비행기가 엘리베이터처럼 8초에 299m를 솟구쳤죠.

바로 그 순간 또 다른 개발자가 천재적인 아이디어를 냈습니다. 실제 날개처럼, 양력 계수를 <strong>받음각(Angle of Attack, AoA)</strong>으로 계산하자는 겁니다.

받음각은 **기수가 가리키는 방향과 실제로 날아가는 방향(속도) 사이의 각도**입니다. 날개가 공기를 비스듬히 받을수록 양력이 커집니다. 실속 전까지는 거의 비례합니다.

![받음각이 양력을 만든다, C_L은 α에 비례](/images/flight-2/03_angle_of_attack.png)

$$
C_L = C_{L\alpha} \cdot \alpha, \qquad C_D = C_{D0} + k \cdot C_L^2
$$

예제 기체의 C_Lα는 4.8/rad(약 0.084/도)입니다. 두 가지가 함께 바뀝니다.

1. **양력 방향**은 기체의 위가 아니라 **속도에 수직**입니다. 양력은 속도의 크기는 바꾸지 않고 방향만 휘게 됩니다.
2. <strong>항력에 유도항력(k·C_L²)</strong>이 붙습니다. 양력을 많이 만들수록 항력도 커져서, 급선회를 하면 속도가 빠집니다.

```cpp
// ✅ 받음각 기반 양력
const FVector Forward = GetActorForwardVector();
const FVector Right   = GetActorRightVector();
const FVector Up      = GetActorUpVector();

// 기체 대칭면(전방-위)에 투영한 속도와 기수 사이의 각 (기수가 위면 +)
const FVector VelInPlane = FVector::VectorPlaneProject(Velocity, Right);
const float   AoA = FMath::Atan2(-FVector::DotProduct(VelInPlane, Up),
                                  FVector::DotProduct(VelInPlane, Forward));

const float CL = CL_Alpha * AoA;                 // 실속은 3편에서
const float CD = CD0 + InducedK * CL * CL;

// 양력 방향: 속도에 수직, 기체 대칭면 안
const FVector LiftDir = FVector::CrossProduct(VelDir, Right).GetSafeNormal();
const FVector Lift    = LiftDir * Q * WingArea * CL;
const FVector Drag    = -VelDir * Q * WingArea * CD;
```

같은 실험을 다시 돌렸습니다. 기수를 10도 들면 받음각이 생기고 양력이 커져서, 궤적이 기수를 따라 휘며 8초에 **231m**를 올라갔습니다. 280m/s에서 기수를 수평으로 두면, 필요한 받음각을 스스로 찾으려고 29m 살짝 가라앉을 뿐 거의 수평을 유지했습니다. "속도가 빠르면 작은 받음각으로도 충분하다"는 실제 비행기의 성질이 저절로 나타난 겁니다.

![고정 계수 양력과 받음각 양력의 궤적 비교](/images/flight-2/04_fixed_vs_aoa.png)

위는 기수를 들었을 때, 아래는 속도만 올렸을 때입니다. 빨간 선(고정 계수)은 두 경우 모두 기수와 궤적이 따로 놉니다.

어느 방향으로 돌지 직접 코드로 정하지 않았는데, 양력이 받음각에 반응하니 속도가 기수를 따라갑니다. 실제 비행기도 이렇게 돕니다.

## 또 골치거리: 30fps 플레이어와 144fps 플레이어의 비행기가 다르다

하지만 또 골치거리가 생겼습니다. 힘을 쌓는 코드가 `Tick`의 `DeltaTime`을 그대로 쓰거든요. 한 프레임 사이에도 비행기의 방향과 속도는 계속 바뀌는데, 코드는 프레임 처음의 힘이 프레임 내내 일정하다고 가정합니다. 그래서 **프레임이 길수록 오차가 커집니다.**

같은 조작(받음각 8도 유지, 약 5G 루프)을 60초 동안 서로 다른 프레임레이트로 돌려 봤습니다. 30fps 플레이어와 144fps 플레이어의 비행기는 60초 뒤 **198m** 떨어진 곳에 있었죠. 멀티플레이에서는 서버와 클라이언트의 예측이 어긋나고, 리플레이는 다시 재생할 때마다 다른 데 착륙합니다. 레벨 디자이너가 "이 협곡은 루프로 빠져나갈 수 있다"고 맞춘 수치도 다른 PC에서는 맞지 않게 됩니다.

![프레임레이트별 루프 60초 오차](/images/flight-2/05_framerate_error.png)

바로 그 순간 이 문제를 정리한 방법이 널리 퍼졌습니다. Glenn Fiedler의 글 "Fix Your Timestep!"으로 유명해진 **고정 타임스텝**입니다. 생각은 단순합니다. **화면은 얼마나 빨리 그리든, 물리는 항상 같은 간격(예: 1/120초)으로만 계산한다.**

1. 매 프레임 `DeltaTime`을 통(Accumulator)에 모읍니다.
2. 통에 1/120초가 차 있는 만큼 물리 스텝을 돌립니다. 30fps면 프레임당 4번, 144fps면 프레임에 따라 0번 또는 1번입니다.
3. 통에 남은 자투리 시간만큼 직전 상태와 현재 상태를 보간해서 화면에 그립니다. 이 단계가 없으면 144fps에서도 비행기가 120Hz로 뚝뚝 끊겨 보입니다.

![고정 타임스텝 타임라인](/images/flight-2/06_fixed_timestep.png)

```cpp
// FlightPawn.h
struct FFlightState { FVector Position; FVector Velocity; FQuat Rotation; };  // m, m/s

static constexpr float PhysicsStep      = 1.f / 120.f;
static constexpr int32 MaxStepsPerFrame = 8;     // 한 프레임이 길어져도 무한히 따라잡지 않게
float        Accumulator = 0.f;
FFlightState PrevState, CurrState;

// FlightPawn.cpp
void AFlightPawn::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    Accumulator += FMath::Min(DeltaTime, PhysicsStep * MaxStepsPerFrame);
    while (Accumulator >= PhysicsStep)
    {
        PrevState = CurrState;
        StepPhysics(CurrState, PhysicsStep);     // 항상 같은 dt
        Accumulator -= PhysicsStep;
    }

    // 화면용 보간: 물리 상태는 건드리지 않는다
    const float Alpha = Accumulator / PhysicsStep;
    const FVector Pos = FMath::Lerp(PrevState.Position, CurrState.Position, Alpha);
    const FQuat   Rot = FQuat::Slerp(PrevState.Rotation, CurrState.Rotation, Alpha);
    SetActorLocationAndRotation(Pos * 100.0, Rot);   // m → cm
}

void AFlightPawn::StepPhysics(FFlightState& S, float Dt) const
{
    const FVector Accel = ComputeForces(S) / Mass;   // 추력·양력·항력·중력
    S.Velocity += Accel * Dt;          // 속도 먼저
    S.Position += S.Velocity * Dt;     // 갱신된 속도로 위치 (반암시적 오일러)
}
```

같은 루프를 1/120초 고정 스텝으로 다시 돌렸더니, 30fps·60fps·144fps는 물론 8\~33ms로 프레임 시간이 들쭉날쭉한 경우까지 60초 뒤 위치가 **소수점 자리까지 완전히 같았습니다.** 플레이어 사이의 차이가 198m에서 0m가 된 겁니다.

하나 오해하기 쉬운 점이 있습니다. 고정 스텝이 더 **정확해지는** 건 아닙니다. 1/120초 스텝의 오차는 60초 뒤 정밀 해석해와 60m 차이로, 144fps 가변 스텝(50m)보다 조금 큽니다. 대신 **모두가 같은 오차를 갖습니다.** 게임에서는 정확한 것보다 항상 같은 게 더 중요합니다. 더 정확해야 하면 스텝을 줄이면 됩니다.

## 결과물: 직접 돌려 봤습니다

아래 실험은 모두 이 글의 예제 기체로 돌렸습니다. 세로 평면만 다루는 2D 점질량 모델이고, Python(numpy)으로 1/120초 고정 스텝을 썼습니다.

**실험 1. 250m/s로 수직 상승 30초 (추력 최대)**

| 모델 | 30초 뒤 속도 | 30초 뒤 고도 |
| --- | --- | --- |
| 레일 방식 | 250m/s | +7,500m |
| 네 가지 힘 | 114m/s | +5,313m |

추력(60kN)이 무게(약 88kN)보다 작아서, 수직으로 서면 속도를 고도로 바꾸며 올라갑니다. 엔진을 끄고 기수를 3도로 고정하면 속도가 1분에 200m/s에서 124m/s로 줄었습니다.

![수직 상승과 엔진 끈 활공의 속도 변화](/images/flight-2/07_results_speed.png)

**실험 2. 고정 계수 양력 vs 받음각 양력 (8초)**

| 조작 | 고정 계수 | 받음각 기반 |
| --- | --- | --- |
| 200m/s, 기수 10도 들기 | 고도 −7m (안 올라감) | 고도 +231m |
| 280m/s, 기수 수평 유지 | 고도 +299m (혼자 솟음) | 고도 −29m (거의 수평) |

**실험 3. 프레임레이트별 루프 60초**

정밀 해석해(RK4, 1/4000초)와의 거리 오차를 쟀습니다. 프레임마다 `DeltaTime`을 쓰면 30fps 플레이어의 오차는 248m, 144fps 플레이어는 50m로 서로 다릅니다. 고정 스텝을 쓰면 모두 60.5m로 똑같습니다.

다음 편에서는 이번에 "실속은 다음에"라고 미뤄둔 것, 즉 **받음각이 너무 커지면 양력이 무너지는 실속**을 다룹니다.
