---
title: "[ArcRaiders: Wasp] 이동 시 벽을 뚫고 이동하는 현상"
published: 2026-11-07
description: "RootComponent로 쓴 USceneComponent(DefaultSceneRoot)에는 충돌 볼륨이 없어, 속도와 무관하게 드론이 벽을 그대로 통과했다."
category: 트러블슈팅
project: arc-wasp
tags: ["Unreal Engine", "충돌", "FloatingPawnMovement"]
draft: false
---

<iframe src="https://www.youtube-nocookie.com/embed/DIb6gzrK8xk" title="드론 벽 통과" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 증상

드론 Pawn에 콜리전 컴포넌트를 추가했는데도, 충돌을 일으키는 다른 에셋들과 달리 드론만 벽을 그대로 통과하는 문제가 발생했습니다. 처음에는 콜리전 프리셋(BlockAll)과 채널 설정 문제로 의심해 프리셋을 다시 맞추고 맵 에셋의 콜리전까지 수정해봤지만 해결되지 않았고, 검색 끝에 원인을 찾았습니다.

## 원인

`DefaultSceneRoot`(`USceneComponent`)를 RootComponent로 두고 `FloatingPawnMovement`를 쓰면, 이동과 충돌 계산은 모두 RootComponent를 기준으로 이루어집니다. 그런데 `USceneComponent`는 위치·회전 정보만 가질 뿐 물리적인 부피(Collision)가 없기 때문에, 엔진 입장에서는 "부피가 0인 물체"로 계산되어 모든 에셋을 그대로 통과하게 됩니다. 즉 이 문제는 이동 속도와 무관하게, 애초에 Root에 충돌 볼륨 자체가 없어서 발생한 문제였습니다.

```text
// 문제 구조 — Root가 USceneComponent라 충돌 볼륨이 없음
DefaultSceneRoot (USceneComponent)   // RootComponent, 위치 정보만 있고 물리 부피 없음
 ├─ StaticMesh
 └─ FloatingPawnMovement             // RootComponent 기준으로 이동·충돌 계산 → 통과
```

## 해결

예전에 참고했던 캐릭터 블루프린트 구조를 다시 찾아보니 다음과 같이 구성돼 있었습니다.

```text
[Root] CapsuleComponent (Capsule)
 ├── ArrowComponent (Arrow)
 ├── Mesh (SkeletalMesh)
 └── SpringArmComponent (SpringArm)
      └── CameraComponent (Camera)
```

`ACharacter`가 `CapsuleComponent`를 Root로 쓰는 이유는, 이동 계산에 쓰이는 콜리전(Capsule)과 전투 판정에 쓰이는 콜리전(Skeletal Mesh)을 분리해서 관리하기 위해서였습니다. 지상 캐릭터는 캐릭터 무브먼트의 이동 계산에 유리해 캡슐을 주로 쓰지만, 하늘을 나는 드론은 캡슐 형태가 기체 크기와 맞지 않아 대신 `SphereComponent`를 Root로 선택했습니다. `ArrowComponent`는 콜리전과 무관하게, 에디터에서 정면(X축) 방향을 시각적으로 확인하기 위한 용도로만 붙였습니다.

```cpp
ADronePawn::ADronePawn()
{
    // 1. 루트는 단순한 구체 (이동 및 환경 충돌용)
    CollisionComponent = CreateDefaultSubobject<USphereComponent>(TEXT("SphereComp"));
    RootComponent = CollisionComponent;
    CollisionComponent->SetSphereRadius(20.f);

    // 2. 드론 메쉬
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisualMesh"));
    MeshComponent->SetupAttachment(RootComponent);

    // 3. 에로우 컴포넌트 — 정면(X축) 확인용
    ArrowComponent = CreateDefaultSubobject<UArrowComponent>(TEXT("ForwardArrow"));
    ArrowComponent->SetupAttachment(RootComponent);

    // 4. Floating Movement
    MovementComponent = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("FloatingMove"));
}
```

| 항목 | 문제 구조 | 해결 구조 |
| --- | --- | --- |
| Root 컴포넌트 | DefaultSceneRoot (USceneComponent) | SphereComponent |
| 충돌 볼륨 | 없음 → 모든 에셋 통과 | 있음 → 정상 충돌 |
| 이동 계산 기준 | 위치 정보만 있는 Root | 실제 충돌 볼륨을 가진 Root |
| 참고 구조 | - | ACharacter: Capsule(이동용) + SkeletalMesh(전투용) 분리 |

<iframe src="https://www.youtube-nocookie.com/embed/9oeAZyGuwOw" title="드론 충돌 수정 결과" loading="lazy" style="width:100%;aspect-ratio:16/9;border:0;border-radius:12px" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 결과

구조를 바꿔 다시 플레이해보니 드론이 벽과 정상적으로 충돌했고, 벽에 부딪히면 드론을 파괴하도록 설계한 의도대로 동작했습니다. 이 문제는 드론 Pawn만이 아니라 `FloatingPawnMovement`나 커스텀 이동 컴포넌트를 쓰는 플레이어 Pawn에도 동일하게 해당되는 구조적인 문제였습니다. 앞으로 Pawn을 구현할 때는 RootComponent에 반드시 실제 충돌 볼륨을 가진 컴포넌트를 사용하는 구조를 기본으로 가져가기로 했습니다.
