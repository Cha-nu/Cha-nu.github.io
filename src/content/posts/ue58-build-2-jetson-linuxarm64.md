---
title: "UE 5.8 플랫폼 빌드 2편: Jetson Orin NX용 LinuxArm64 빌드하기"
published: 2026-11-10
description: "언리얼 엔진 5.8.4 프로젝트를 Windows에서 v26 크로스컴파일 툴체인으로 LinuxArm64 패키징하고, JetPack 6.0의 Jetson Orin NX 16GB에서 실행한 과정을 정리합니다."
category: 언리얼 엔진
tags: ["Unreal Engine", "Linux", "Jetson", "ARM64", "패키징"]
project: augmented-alkagi
draft: false
---

> **UE 5.8 플랫폼 빌드** — [1편: 언리얼에서 안드로이드 빌드하기](/posts/ue58-build-1-android/) · **2편: Jetson Orin NX용 LinuxArm64 빌드하기**

> 이 글은 언리얼 엔진 5.8.4(런처 설치판), Windows 11, Jetson Orin NX 16GB(J4012, JetPack 6.0, Ubuntu 22.04) 기준입니다. 툴체인 버전은 엔진마다 다르니 사용하는 엔진 버전의 `Engine/Config/Linux/Linux_SDK.json`에서 확인하세요.

<!-- TODO(작성자): 결과 절(표)과 빠진 화면(04, 05, 06, 09, 10번)은 Jetson에서 직접 실행한 뒤 채웁니다. 그때까지 주석으로 숨겨 둡니다. -->

---
## 들어가며

1편에서 증강 알까기(ProjectA)를 안드로이드로 패키징했습니다. 이번에는 같은 프로젝트를 NVIDIA Jetson Orin NX에서 돌려 봅니다. Jetson은 ARM64(aarch64) CPU를 쓰는 리눅스 보드라서, 언리얼에서는 **LinuxArm64** 플랫폼으로 빌드해야 합니다.

Jetson에서 엔진을 직접 빌드할 수도 있지만, 메모리 16GB로는 시간이 오래 걸리고 메모리가 부족할 위험이 큽니다. 그래서 Windows에서 크로스컴파일(Cross-Compile)로 패키징하고 결과물만 Jetson에 복사하는 방법을 썼습니다.

---
## 런처에서 리눅스 타깃 플랫폼을 설치합니다

1편의 안드로이드와 같은 방법입니다. Epic Games 런처의 **라이브러리 → 엔진 카드의 실행 옆 화살표 → 옵션 → 타깃 플랫폼**에서 **리눅스**를 체크하고 **적용**을 누릅니다.

![Unreal Engine 5.8.4 설치 옵션에서 리눅스(18.541GB)를 체크한 화면. 다운로드 크기 5.479GB, 필요한 저장 공간 48.048GB로 표시된다](/images/ue58-build-2-jetson-linuxarm64/01_launcher_linux.png)

목록에 적힌 크기는 18.541GB이지만, 제 PC에서 실제로 표시된 다운로드 크기는 5.479GB였습니다. 엔진 전체에 필요한 저장 공간은 48.048GB로 늘어납니다.


---
## 툴체인이 없으면 Linux 플랫폼이 꺼져 있습니다

런처에서 리눅스 타깃 플랫폼을 설치하면 에디터의 **Platforms → SDK Management**에 LinuxArm64가 새로 나타납니다. 하지만 Linux와 LinuxArm64 모두 경고 아이콘이고, 설치된 SDK가 `--`로 표시됩니다.

![SDK Management에서 Linux와 LinuxArm64가 경고 아이콘으로 표시되고, 허용 버전 v26_clang-20.1.8-rockylinux8에 설치 버전이 비어 있는 화면](/images/ue58-build-2-jetson-linuxarm64/02_sdk_management_before.png)

런처의 리눅스 항목은 Linux(x86_64)와 LinuxArm64용 엔진 파일을 함께 설치합니다. 실제로 엔진 폴더에 `Engine/Binaries/LinuxArm64`가 생겼습니다. 하지만 이 파일을 쓸 컴파일러는 들어 있지 않습니다. 이때의 UBT 로그도 둘 다 빌드할 수 없는 상태입니다.

```text
Unable to find valid SDK(s) for Linux:
  Found Sdk Version, Required=v26_clang-20.1.8-rockylinux8.
        Registering build platform: Linux - buildable: False
        Registering build platform: LinuxArm64 - buildable: False
```

5.8이 요구하는 버전은 `Engine/Config/Linux/Linux_SDK.json`에 적혀 있습니다.

```json
{
	"MainVersion" : "v26_clang-20.1.8-rockylinux8",
	"MinVersion" : "v26_clang-20.1.8-rockylinux8",
	"MaxVersion" : "v26_clang-20.1.8-rockylinux8"
}
```

Min과 Max가 같습니다. 즉 **정확히 이 버전만** 받습니다. [Epic 공식 문서](https://dev.epicgames.com/documentation/unreal-engine/linux-development-requirements-for-unreal-engine)에도 5.7\~5.8의 컴파일러는 clang 20.1.8로 적혀 있습니다.

---
## v26 크로스컴파일 툴체인을 설치합니다

1. [공식 문서](https://dev.epicgames.com/documentation/unreal-engine/linux-development-requirements-for-unreal-engine)의 Version History 표에서 5.7\~5.8 줄의 **Cross-Compile Toolchain** 열에 있는 `v26 clang-20.1.8-based` 링크로 설치 파일(.exe)을 받습니다.

   ![Epic 공식 문서 Version History 표. 5.7\~5.8 줄의 Cross-Compile Toolchain 열에 v26 clang-20.1.8-based 링크가 있다](/images/ue58-build-2-jetson-linuxarm64/03_toolchain_download.png)

   오른쪽의 **Native Toolchain** 열은 리눅스 PC에서 직접 빌드할 때 쓰는 것입니다. Windows에서 Jetson용으로 빌드하려면 **Cross-Compile** 열을 받아야 합니다.

2. 설치 파일을 실행합니다. 기본 경로는 `C:\UnrealToolchains\v26_clang-20.1.8-rockylinux8`입니다.
3. 설치가 끝나면 시스템 환경변수 `LINUX_MULTIARCH_ROOT`가 설치 경로로 등록됐는지 확인합니다.

```bat
echo %LINUX_MULTIARCH_ROOT%
:: C:\UnrealToolchains\v26_clang-20.1.8-rockylinux8\
```

<!-- TODO: 화면을 받으면 되살립니다
![툴체인 설치 화면](/images/ue58-build-2-jetson-linuxarm64/04_toolchain_installer.png)

![LINUX_MULTIARCH_ROOT 환경변수 확인 화면](/images/ue58-build-2-jetson-linuxarm64/05_env_var.png)
-->

이 툴체인 하나에 x86_64용과 aarch64용 컴파일러가 함께 들어 있습니다. 따라서 Linux와 LinuxArm64를 따로 설치할 필요가 없습니다. 환경변수가 바뀌었으니 에디터와 런처를 다시 켭니다.

다시 켠 뒤 `Saved/Logs/AutoSDKInfo.txt`에서 아래 줄이 보이면 준비가 끝난 것입니다.

<!-- TODO: 툴체인 설치 후 실제 로그로 교체 -->

```text
Registering build platform: LinuxArm64 - buildable: True
```

<!-- TODO: 화면을 받으면 되살립니다
![툴체인 설치 후 SDK Management에서 LinuxArm64의 설치 버전이 v26_clang-20.1.8-rockylinux8로 표시된 화면](/images/ue58-build-2-jetson-linuxarm64/06_sdk_management_after.png)
-->

---
## LinuxArm64로 패키징합니다

툴체인이 잡히면 <strong>Platforms → Package Project</strong>의 LinuxArm64에서 경고 아이콘이 사라집니다.

![Platforms → Package Project 메뉴. Linux와 LinuxArm64의 경고 아이콘이 리눅스 아이콘으로 바뀌었고, LinuxArm64가 선택돼 있다](/images/ue58-build-2-jetson-linuxarm64/07_package_project_linuxarm64.png)

Android, IOS, Mac, TVOS는 여전히 경고 아이콘이지만 Linux와 LinuxArm64는 리눅스 아이콘으로 바뀌었습니다. LinuxArm64에 마우스를 올리면 텍스처 압축 방식(Flavor)을 고르는 메뉴가 나옵니다.

![Package Project 메뉴에서 LinuxArm64를 펼치면 DXT, ASTC, ETC2, Multi 네 가지 Flavor가 보이고, 빌드 구성은 Shipping이 선택된 화면](/images/ue58-build-2-jetson-linuxarm64/08_flavor_selection.png)

| Flavor | 텍스처 압축 | 주로 쓰는 GPU |
| --- | --- | --- |
| DXT | BC(DXT) | 데스크톱 GPU (NVIDIA, AMD 등) |
| ASTC | ASTC | 모바일 GPU (Mali 등) |
| ETC2 | ETC2 | 오래된 모바일 GPU |
| Multi | 여러 형식을 함께 넣음 | 대상 GPU를 모를 때 (용량이 커짐) |

Jetson Orin NX의 GPU는 데스크톱 RTX 30 시리즈와 같은 NVIDIA Ampere 아키텍처입니다. 그래서 데스크톱 리눅스와 같은 <strong>LinuxArm64 (DXT)</strong>를 골랐습니다. CPU가 ARM이라고 해서 모바일용 ASTC를 고를 필요는 없습니다. 실제로 GPU가 BC 압축을 지원하는지는 Jetson에서 `vulkaninfo`로 확인합니다.

<!-- TODO: Jetson의 vulkaninfo 결과(textureCompressionBC)로 확인 후 기록 -->

```bash
vulkaninfo | grep -i textureCompression
# textureCompressionBC = true 이면 DXT Flavor를 그대로 쓸 수 있습니다.
```

빌드 구성은 **Development**로 했습니다. Shipping은 콘솔 명령이 꺼져 있어서 `stat fps`로 성능을 잴 수 없기 때문입니다.

<!-- TODO: 패키징 시간, 결과 폴더 크기, 막힌 점(있다면)을 실제 값으로 기록 -->

결과물 폴더에는 `ProjectA.sh` 실행 스크립트와 `ProjectA/Binaries/LinuxArm64/` 아래 실행 파일, 그리고 쿠킹된 콘텐츠가 들어 있습니다.

<!-- TODO: 화면을 받으면 되살립니다
![패키징 결과 폴더](/images/ue58-build-2-jetson-linuxarm64/09_package_output.png)
-->

---
## Jetson으로 옮기고 실행합니다

### Jetson 준비

JetPack 6.0의 NVIDIA 드라이버는 Vulkan을 지원합니다. 언리얼 리눅스 빌드는 Vulkan으로 그리므로 먼저 Vulkan이 GPU를 잡는지 확인합니다.

```bash
sudo apt install -y vulkan-tools
vulkaninfo --summary | grep -E "deviceName|apiVersion|driverVersion"
```

성능을 재려면 전원 모드를 최대로 올리고 클럭을 고정합니다.

```bash
sudo nvpmodel -q          # 현재 전원 모드 확인
sudo nvpmodel -m 0        # 최대 성능 모드
sudo jetson_clocks
```

### 복사와 실행

결과물은 용량이 크므로 외장 1TB SSD에 둡니다.

```bash
# Windows(PowerShell)에서
scp -r "<패키징 폴더>\LinuxArm64" <user>@<jetson-ip>:/mnt/ssd/ProjectA

# Jetson에서
cd /mnt/ssd/ProjectA
chmod +x ProjectA.sh ProjectA/Binaries/LinuxArm64/*
./ProjectA.sh -log
```

<!-- TODO: 화면을 받으면 되살립니다
![Jetson에서 증강 알까기가 실행된 화면](/images/ue58-build-2-jetson-linuxarm64/10_jetson_running.png)
-->

<!-- TODO(작성자): Jetson에서 직접 잰 값이 나오면 되살립니다. (0장 2번)
---
## 결과

| 항목 | 값 |
| --- | --- |
| 전원 모드 | (nvpmodel 결과) |
| 해상도 | |
| 평균 FPS (`stat fps`) | |
| 메모리 사용량 (`tegrastats`) | |
-->

---
## 마치며

안드로이드와 마찬가지로, LinuxArm64 빌드도 엔진의 SDK json에 적힌 버전을 그대로 맞추는 일이 핵심이었습니다. 툴체인 하나와 환경변수 하나로 Windows에서 Jetson용 실행 파일까지 만들 수 있습니다.
