---
title: "Project: ARK"
summary: "파라곤 적 3종이 4초마다 밀려오는 웨이브를 막아내는 UE5.4 C++ TPS 서바이벌"
start: "2025-11"
period: "2025.11 ~ 2026.01 (약 2개월)"
status: 완료
team: "2인 (기여도 90%)"
role: "PlayerCharacter · NavMesh AI · Game Flow"
engine: "Unreal Engine 5.4"
stack: ["C++", "AnimNotify", "NavMesh", "Niagara"]
cover: https://i.ytimg.com/vi/ANB4t7hArCU/hqdefault.jpg
video: https://www.youtube.com/watch?v=ANB4t7hArCU
links:
  - { label: "GitHub", url: "https://github.com/Cha-nu/Project-Ark" }
order: 50
---

## 어떤 프로젝트인가

어두운 Sci-Fi 도시에서 파라곤 적 3종(근접 Crunch · 중거리 Wraith · 포격 Howitzer)이 4초마다 밀려오는 웨이브를 사격·저격·유탄으로 막아내는 TPS 서바이벌입니다. 투사체, 히트스캔, 범위 데미지, 근접 판정을 한 게임에 전부 구현해 보는 것이 목표였습니다.

핵심 키워드: 히트스캔 전환(터널링 해결), 적 AI 산개 로직, 판정 방식별 데미지 파이프라인

---
## 내가 맡은 것

- 평상시 걷기와 `Shift` 달리기를 구분한 TPS 이동
- 기본 Bullet, Q 범위 공격, E 관통 사격의 서로 다른 전투 감각
- 공격 모션의 실제 타격 프레임과 판정을 연결하는 `AnimNotify`
- 근접·중거리·원거리 적의 역할별 추적과 공격
- Q/E 쿨다운 아이콘, 크로스헤어 반동, Niagara 타격 피드백
- 적 스폰, 처치 수 집계, 전원 처치 후 클리어 레벨 전환
