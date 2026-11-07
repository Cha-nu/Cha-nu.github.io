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

## 내가 맡은 것

- Steam Online Subsystem + 리슨 서버 기반 세션 생성·매칭·초대 처리
- Seamless Travel 기반 로비 → 매치 전환과 PostLogin 핸드셰이크로 재접속·재입장 처리
- 고양이 캐릭터 GAS 스킬 시스템 (클래스 1개 + TMap 데이터 분리 구조)
- 같은 스킬이 대상에 따라 매료 또는 공격으로 갈리는 이중 판정 파이프라인
- 하이브리드 쿨다운(GA+GE)과 충전형 대시, CC·매료도 등 상태 관리
- CommonUI 3레이어 Activation Stack으로 HUD·메뉴 입력/포커스 관리

## 핵심 기능

| 기능 | 요약 |
| --- | --- |
| Steam 온라인 아키텍처 | 리슨 서버 + Steam OSS로 인프라 없이 방 목록·재접속·초대 처리. Widget → GameInstance → SessionSubsystem 3층으로 흐름과 I/O 분리 |
| 로비 → 매치 상태머신 & Seamless Travel | PostLogin/HandleSeamlessTravelPlayer 핸드셰이크로 로딩 동기화, PlayerIndex를 매료도·타게팅의 키로 사용 |
| 로비 고양이 선택 | 데이터는 정상 복제하되 표현(머티리얼)만 숨겨 매치 입장 전까지 선택을 비공개로 유지 |
| 전투 파이프라인 & 매료 시스템 | 데미지는 메타 어트리뷰트, CC는 태그/어트리뷰트, 행인의 매료도는 GAS 밖 전용 컴포넌트(FastArray)로 관리 |
| 고양이 스킬 시스템 | 캐릭터 클래스는 하나, 스킬 구성은 TMap 데이터로 분리해 새 고양이 추가를 데이터 한 줄로 |
| 쿨다운 하이브리드 & 충전형 대시 | 쿨다운 수치는 GA, 태그는 스킬별 GE에 두고, 대시는 어트리뷰트 + Cost GE + ASC 타이머로 3회 충전 |
| CommonUI 3레이어 Activation Stack | 위젯이 입력 모드·포커스를 스스로 선언하고 활성화 스택이 적용·복원을 대신 |
