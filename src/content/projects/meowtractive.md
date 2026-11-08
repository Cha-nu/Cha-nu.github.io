---
title: "MeowTractive (묘력만점)"
summary: "고양이가 되어 행인을 매료시켜 팬을 모으는 UE5.8 기반 4인 경쟁 파티게임"
start: "2026-06"
period: "2026.06 ~ 2026.07 (2개월)"
status: 완료
team: "5인 팀 (기여도 40%)"
role: "Steam 온라인 시스템 · 고양이 GAS · CommonUI 프레임워크"
engine: "Unreal Engine 5.8"
stack: ["C++", "GAS", "Online Subsystem Steam", "Seamless Travel", "CommonUI"]
cover: https://i.ytimg.com/vi/DhKlnQbQFTU/hqdefault.jpg
video: https://youtu.be/DhKlnQbQFTU
links:
  - { label: "GitHub", url: "https://github.com/NBcampUnrealTrack/8th-Team9-CH4-Project" }
order: 20
---

## 어떤 프로젝트인가

고양이가 되어 도시의 행인 NPC를 매료해 팬으로 만들고, 3분 안에 가장 많은 팬을 확보하면 승리하는 4인 경쟁 파티게임입니다. Steam 리슨 서버 멀티플레이로 동작합니다. 같은 스킬이 대상에 따라 "매료" 또는 "공격"으로 갈라지는 이중 판정이 핵심 요구사항이었습니다.

핵심 키워드: Steam 세션/리슨 서버 수명주기, GAS 매료·전투 파이프라인, CommonUI 3레이어 Activation Stack

---
## 내가 맡은 것

- Steam Online Subsystem + 리슨 서버 기반 세션 생성·매칭·초대 처리
- Seamless Travel 기반 로비 → 매치 전환과 PostLogin 핸드셰이크로 재접속·재입장 처리
- 고양이 캐릭터 GAS 스킬 시스템 (클래스 1개 + TMap 데이터 분리 구조)
- 같은 스킬이 대상에 따라 매료 또는 공격으로 갈리는 이중 판정 파이프라인
- 하이브리드 쿨다운(GA+GE)과 충전형 대시, CC·매료도 등 상태 관리
- CommonUI 3레이어 Activation Stack으로 HUD·메뉴 입력/포커스 관리
