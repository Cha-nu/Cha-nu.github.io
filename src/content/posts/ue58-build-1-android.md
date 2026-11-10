---
title: "UE 5.8 플랫폼 빌드 1편: Android Studio만 설치하고 언리얼에서 안드로이드 빌드하기"
published: 2026-11-10
description: "언리얼 엔진 5.8.4에서는 Android Studio를 설치해 첫 실행만 끝내면, 나머지 SDK·NDK·에뮬레이터는 에디터의 SDK Management가 엔진에 맞는 버전으로 설치합니다. 그 과정과 APK 패키징까지 정리합니다."
category: 언리얼 엔진
tags: ["Unreal Engine", "Android", "패키징", "모바일"]
project: augmented-alkagi
image: /images/ue58-build-1-android/03_sdk_management.png
draft: false
---

> **UE 5.8 플랫폼 빌드** — **1편: Android Studio만 설치하고 언리얼에서 안드로이드 빌드하기** · 2편: Windows에서 크로스컴파일해 Jetson Orin NX에서 실행하기 (준비 중)

> 이 글은 언리얼 엔진 5.8.4(CL 58902052, 런처 설치판)와 Windows 11 기준입니다. SDK 버전은 엔진마다 다르니 사용하는 엔진 버전의 `Engine/Config/Android/Android_SDK.json`에서 확인하세요.

---
## 들어가며

증강 알까기(ProjectA)를 안드로이드에서 돌려 보려고 APK를 뽑았습니다. 언리얼 안드로이드 빌드라고 하면 SDK·NDK 버전을 하나하나 맞추고 환경변수를 잡는 작업부터 떠올리기 쉽습니다.

실제로 제가 직접 한 일은 **Android Studio를 설치하고 첫 실행을 끝낸 것**뿐이었습니다. 엔진이 원하는 버전의 SDK·NDK와 에뮬레이터는 언리얼 에디터가 설치했습니다. 이 글에서는 그 과정을 PC에 남은 설치 시각과 엔진 코드로 확인하고, 패키징까지 정리합니다.

---
## 엔진이 원하는 버전은 json에 적혀 있습니다

언리얼은 버전마다 지원하는 Android SDK·NDK가 정해져 있습니다. 5.8에서는 `Engine/Config/Android/Android_SDK.json`에 들어 있습니다.

```json
{
	"MainVersion": "r27c",
	"MinVersion": "r27c",
	"MaxVersion": "r29",
	"platforms": "android-36",
	"build-tools": "36.0.0",
	"cmake": "3.22.1",
	"ndk": "27.2.12479018"
}
```

| 항목 | 5.8.4가 요구하는 값 |
| --- | --- |
| SDK Platform | `android-36` |
| Build-Tools | `36.0.0` |
| CMake | `3.22.1` |
| NDK | `27.2.12479018`(r27c), 허용 범위 r27c\~r29 |

이 값을 직접 맞출 필요는 없습니다. 뒤에서 보듯 에디터가 이 json을 읽어서 그대로 설치하기 때문입니다. 다만 어떤 버전이 깔려야 하는지 알고 있으면 문제가 생겼을 때 원인을 찾기 쉽습니다.

---
## Android Studio를 설치하고 첫 실행을 끝냅니다

Android Studio를 설치하고 실행하면 첫 실행 마법사가 기본 SDK를 받습니다. SDK 경로는 기본값인 `C:\Users\<사용자>\AppData\Local\Android\Sdk`를 썼습니다.

제 PC의 SDK 폴더를 보면, 마법사가 1분 남짓한 사이에 아래 패키지를 받았습니다.

| 설치 시각 | 패키지 |
| --- | --- |
| 12:08 | Android Emulator |
| 12:09 | Platform `android-37.0`, 시스템 이미지·소스 `android-37.0`, Build-Tools `36.0.0`, Platform-Tools |

마법사는 그 시점의 최신 플랫폼을 받습니다. 그래서 엔진이 쓰는 36이 아니라 37(Android 17)이 먼저 깔렸습니다. 아래 화면에서 API 37.0이 체크돼 있는 이유입니다.

![Android Studio Settings의 Android SDK, SDK Platforms 탭. 첫 실행 때 받은 Android 17.0 API 37.0이 체크돼 있고, Android 16.0 API 36.0은 Partially installed로 보인다](/images/ue58-build-1-android/01_sdk_platforms.png)

37이 깔려 있어도 빌드에는 영향이 없습니다. 패키징할 때 엔진이 만든 gradle 설정을 보면 `COMPILE_SDK_VERSION=36`, `TARGET_SDK_VERSION=36`으로 json 값을 그대로 썼습니다.

SDK Tools 탭은 건드리지 않아도 됩니다. 오히려 주의할 점이 하나 있습니다.

![SDK Tools 탭. Build-Tools, NDK, CMake 옆에 37.0.0, 30.0.16248370, 4.1.2로 올리라는 Update Available이 표시돼 있다](/images/ue58-build-1-android/02_sdk_tools.png)

Android Studio는 Build-Tools 37.0.0, NDK 30.0.16248370, CMake 4.1.2로 올리라고 `Update Available`을 띄웁니다. NDK 30은 엔진 허용 범위(r27c\~r29)를 벗어나므로, 언리얼용 SDK라면 이 업데이트는 따라가지 않습니다.

---
## 나머지는 언리얼 에디터가 설치합니다

에디터에서 <strong>Platforms → SDK Management → Android</strong>를 열고 SDK 설치를 누릅니다. 설치가 끝나면 아래 화면처럼 허용 범위(r27c\~r29)와 설치된 버전(r27c)이 표시되고, 메뉴는 `Force Reinstall Sdk`로 바뀝니다.

![Platforms → SDK Management → Android 메뉴에서 허용 범위 r27c\~r29, 설치 버전 r27c로 인식된 화면](/images/ue58-build-1-android/03_sdk_management.png)

같은 메뉴에서 iOS·Linux·Mac·TVOS는 경고 아이콘으로 표시됩니다. 해당 플랫폼의 SDK를 찾지 못했다는 뜻입니다. 2편에서 Linux를 이 상태에서 켜 봅니다.

### 버튼 하나가 하는 일

이 메뉴는 Turnkey라는 엔진 도구를 실행합니다. 안드로이드용 코드는 `Engine/Source/Programs/AutomationTool/Android/AndroidPlatform.Automation.cs`에 있고, 순서는 아래와 같습니다.

1. `sdkmanager`가 없으면 Command-line Tools부터 설치합니다.
2. `Engine/Extras/Android/SetupAndroid.bat`을 실행합니다. 이때 `Android_SDK.json`의 platforms, build-tools, cmake, ndk 값을 인자로 넘깁니다.
3. 설치가 끝나면 `AndroidEmulator.json`을 읽어 `SetupAndroidEmulator.bat`으로 에뮬레이터를 만듭니다.

제 PC의 설치 시각도 이 순서와 맞습니다.

| 설치 시각 | 패키지 | 설치한 단계 |
| --- | --- | --- |
| 14:32 | Command-line Tools (latest) | 1 |
| 14:34 | Platform `android-36`, NDK `27.2.12479018` | 2 (`SetupAndroid.bat`) |
| 14:35 | 시스템 이미지 `android-36` (x86_64, Play Store) | 3 (`SetupAndroidEmulator.bat`) |

`SetupAndroid.bat`은 패키지 설치와 함께 `ANDROID_HOME`, `JAVA_HOME`(Android Studio의 `jbr`), `NDKROOT`를 사용자 환경변수로 등록합니다. 그래서 프로젝트 설정의 SDK·NDK·Java 경로 칸은 비워 둬도 됩니다.

에뮬레이터 설정은 `Engine/Config/Android/AndroidEmulator.json`에 있습니다.

```json
{
	"AvdDevice": "pixel_6",
	"DeviceApiVersion": "36",
	"DeviceDataSize": "48G",
	"DeviceRamSize": "6144"
}
```

`SetupAndroid.bat`을 탐색기에서 직접 실행할 때는 주의할 점이 있습니다. 인자 없이 실행하면 build-tools 기본값으로 36.0.0이 아닌 36.1.0을 받습니다. 에디터 메뉴를 쓰면 json 값을 넘기므로 이 문제가 없습니다.

---
## 에디터에서 바로 기기·에뮬레이터로 실행합니다

SDK가 잡히면 패키징 전에도 에디터에서 바로 실행해 볼 수 있습니다. <strong>Platforms → Quick Launch Current Level</strong>에서 연결된 기기나 에뮬레이터를 고르면, 쿠킹과 설치와 실행을 한 번에 합니다. 실기기는 개발자 옵션에서 USB 디버깅을 켜 둡니다.

---
## 프로젝트 설정에서 안드로이드를 켭니다

**Project Settings → Platforms → Android**에서 설정합니다. 제가 바꾼 값은 아래와 같고, 프로젝트의 `Config/Android/AndroidEngine.ini`에 저장됩니다.

```ini
[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]
Orientation=SensorLandscape
bBuildForArm64=True
bSupportsVulkan=True
bSupportsVulkanSM5=False

[/Script/Engine.RendererSettings]
r.Mobile.ShadingPath=0
r.DynamicGlobalIlluminationMethod=0
r.ReflectionMethod=0
r.Shadow.Virtual.Enable=0
```

- `Configure Now` 버튼으로 프로젝트용 안드로이드 빌드 파일을 만듭니다. (`Build/Android` 폴더가 생깁니다.)
- `bBuildForArm64`만 켜서 arm64 기기만 지원합니다.
- 렌더러는 Vulkan 모바일로 맞추고, SM5와 Lumen·가상 섀도 맵은 끕니다.

---
## 패키징합니다

<strong>Platforms → Package Project → Android (ASTC)</strong>를 고릅니다. 빌드 구성은 Shipping으로 했습니다.

결과물은 두 곳에 생깁니다.

| 위치 | 파일 | 크기 |
| --- | --- | --- |
| `Binaries/Android` | `ProjectA-Android-Shipping-arm64.apk` | 85MB |
| `Saved/StagedBuilds` | `Android_ASTC.obb` (콘텐츠) | 570MB |

APK에는 실행 파일과 자바 코드가, OBB에는 쿠킹된 콘텐츠가 들어갑니다. 같은 폴더의 `Install_ProjectA-Android-Shipping-arm64.bat`을 실행하면 `adb`로 APK와 OBB를 기기에 함께 설치합니다.

---
## 자주 막히는 곳

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| SDK 설치가 sdkmanager를 못 찾는다며 멈춥니다 | Android Studio를 설치만 하고 첫 실행을 하지 않아 SDK 경로가 없습니다 | Android Studio를 실행해 첫 실행 마법사를 끝냅니다 |
| 설치는 끝났는데 Android가 경고 아이콘으로 남습니다 | 환경변수가 새로 등록됐지만 에디터와 런처가 예전 값을 들고 있습니다 | 런처까지 완전히 껐다가 다시 켭니다 |
| NDK 버전 경고 | Android Studio의 Update Available을 따라 NDK 30이 깔렸습니다 | `Force Reinstall Sdk`로 json 버전을 다시 설치합니다 |

---
## 복습 질문

답을 먼저 떠올린 다음 눌러서 확인해 보세요.

<details>
<summary>1. Android Studio에서 직접 해야 하는 일은 무엇인가요.</summary>

설치하고 첫 실행 마법사를 끝내는 것입니다. 그러면 SDK 폴더와 기본 패키지가 생깁니다. 엔진이 원하는 `android-36`, NDK `27.2.12479018`, Command-line Tools, 에뮬레이터 이미지는 에디터의 SDK Management가 설치합니다.

</details>

<details>
<summary>2. Android Studio가 API 37을 받았는데 엔진이 36으로 빌드하는 이유는 무엇인가요.</summary>

첫 실행 마법사는 그 시점의 최신 플랫폼을 받고, 엔진은 `Android_SDK.json`에 적힌 `android-36`을 쓰기 때문입니다. 실제 gradle 설정도 `COMPILE_SDK_VERSION=36`, `TARGET_SDK_VERSION=36`이었습니다.

</details>

<details>
<summary>3. SetupAndroid.bat을 직접 실행하는 것과 에디터 메뉴로 설치하는 것은 무엇이 다른가요.</summary>

에디터 메뉴는 `Android_SDK.json`의 버전을 인자로 넘기고, 끝난 뒤 에뮬레이터까지 만듭니다. bat을 인자 없이 직접 실행하면 build-tools 기본값 36.1.0을 받고 에뮬레이터도 만들지 않습니다.

</details>

---
## 마치며

언리얼 5.8의 안드로이드 빌드 준비는 생각보다 단순했습니다. Android Studio를 설치해 첫 실행만 끝내면, 나머지는 에디터의 SDK Management가 json에 적힌 버전 그대로 설치합니다. 제가 할 일은 Android Studio의 업데이트 알림을 따라가지 않는 것 정도였습니다.

다음 편에서는 같은 프로젝트를 Windows에서 크로스컴파일해 <strong>Jetson Orin NX(ARM64 리눅스)</strong>에서 실행해 봅니다.
