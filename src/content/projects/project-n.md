---
title: "Project N"
summary: "중앙 깃발을 먼저 세우거나 최후의 1인이 되면 승리하는 Unity NGO 기반 2D 탑뷰 PvP"
start: "2026-08"
period: "2026.08.03 ~ 2026.08.10 (1주 집중 개발)"
status: 완료
team: "2인 (프로그래머 2, 기여도 약 70%)"
role: "로비·세션 / 인게임 구조·폴리싱 / 증강 / UI·사운드"
engine: "Unity"
stack: ["C#", "Netcode for GameObjects", "Unity Relay", "Unity Lobby", "WebGL"]
cover: https://i.ytimg.com/vi/6VDKwZcz3EU/hqdefault.jpg
video: https://youtu.be/6VDKwZcz3EU
links:
  - { label: "GitHub", url: "https://github.com/Cha-nu/ProjectN" }
order: 30
---

## 어떤 프로젝트인가

중앙 깃발을 먼저 세우거나 최후의 1인이 되면 승리하는 2D 탑뷰 멀티플레이 PvP입니다. PC와 WebGL에서 동작합니다. "멀티플레이에서 무엇을 서버가 결정해야 하는가"를 직접 나눠 보는 것이 학습 목표였습니다.

핵심 키워드: 서버 발급 좌석(slot) 단일 진실, Relay+Lobby 이원 구조, 상태 종료 경로 단일화

---
## 내가 맡은 것

| 영역 | 내 지분 | 내가 맡은 것 |
| --- | --- | --- |
| 로비·세션·매치메이킹 | 88% | 메인메뉴 ↔ 로비 연결, 방 생성 플로우·비밀번호 방, 세션 리스트·방 참여, Lobby 공개방 등록·목록 조회, Ready 판정 수정 |
| 인게임 (GameManager·Player) | 82% | 인게임 구조 개편, 맵 변경, 깃발 상태·카메라 줌, 리스폰·HUD 좌석 일원화, 깃발 스폰 위치 서버 결정 |
| 증강 | 주도 | 증강 드래프트 시스템·UI, bonusLives 기반 생명 추가 증강 재설계 |
| UI·사운드 | 100% | 메인메뉴(모바일/웹 레이아웃), 인게임 HUD, 나가기 다이얼로그, 설정창, 오디오 매니저 |
