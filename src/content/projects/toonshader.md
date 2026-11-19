---
title: "Toon Shader"
summary: "언리얼 엔진 5.8에서 애니메이션풍 캐릭터에 그림자를 받는 셀 셰이딩, 얼굴 SDF 그림자, 눈, 외곽선을 구현한 셰이더 학습 프로젝트"
start: "2026-11"
period: "2026.11 ~"
status: 진행 중
team: "개인 (AI 어시스턴트 활용)"
role: "툰 셰이더 설계와 머티리얼 구현, 캐릭터 조작 구성"
engine: "Unreal Engine 5.8"
stack: ["Material", "Post Process", "Blueprint", "Enhanced Input", "Blender"]
cover: /images/toon-shading-2/00_cover.png
video: https://www.youtube.com/watch?v=O5YsP1ajFg8
order: 90
draft: false
---

> **팬메이드·학습 목적 고지** — 이 프로젝트에 쓴 캐릭터 모델, 텍스처, 게임 화면의 저작권은 명조: 워더링 웨이브(Wuthering Waves)의 개발사 Kuro Games에 있습니다. 셰이더 공부를 위한 비상업적 팬메이드 작업이며, 모델과 텍스처 파일은 배포하지 않습니다.

## 어떤 프로젝트인가

애니메이션풍 캐릭터 셰이더를 공부하려고 시작한 프로젝트입니다. 처음에는 유튜브 강의([Unreal Engine 5 - Toon Shader Tutorial](https://youtu.be/GAkxpwy9xtg))를 보고 Half-Lambert와 SmoothStep으로 3톤 셀 셰이딩과 림라이트를 만들었습니다. 그런데 캐릭터에 다른 물체의 그림자가 지지 않고, 눈이 탁하고, 원작보다 밝게 뜨는 문제가 있었습니다.

그래서 몸은 엔진 조명을 받게 하고 후처리에서 명암을 단계로 자르는 구조로 바꿨습니다. 얼굴은 SDF 텍스처로, 눈은 시차와 광택막으로 따로 처리했습니다. 마지막으로 캐릭터를 직접 움직이며 볼 수 있게 입력, 카메라, 애니메이션 블루프린트를 붙였습니다.

## 내가 맡은 것

- 셀 셰이딩: 첫 번째 셰이더(`MM_ToonShader`)와 외곽선(`M_ToonOutline`)을 직접 만들었습니다.
- 머티리얼 구현: `MM_ToonLit`, `MM_ToonFace`, `MM_ToonEye`는 AI의 노드 안내와 검토를 받아 직접 구성했습니다.
- 후처리: `PP_Toon`을 AI의 조언을 받아 직접 구성했습니다. AI의 확인 작업 중 편집이 날아가 AI에게 재구현을 맡겼고, 그 결과를 Named Reroute로 정리하고 그림자 색을 조정했습니다.
- 캐릭터 조작: 입력, 카메라, 애니메이션 블루프린트는 AI가 구현했고, 동작을 확인하며 수정을 요청했습니다.

## 기술적으로 어려웠던 점

- [툰 셰이딩 1편: 셀 셰이딩의 원리](/posts/toon-shading-1/): 셰이더 안에서 명암을 계산하면 그림자를 받지 못하는 이유와, 후처리로 옮긴 구조를 정리했습니다.
- [툰 셰이딩 2편: 언리얼 머티리얼 구현](/posts/toon-shading-2/): 머티리얼별 노드 구성과 막힌 점을 정리했습니다.

## 돌아보며

명암 단계는 후처리로, 얼굴과 눈은 Unlit으로 나누면서 그림자를 받는 툰 캐릭터를 만들 수 있었습니다. 치마와 스카프의 흔들림은 Kawaii Physics를 한 번 넣었다가 어색해서 뺐습니다. 다음에는 Kawaii Physics 설정을 다시 다듬어 천 흔들림을 개선해 오겠습니다.
