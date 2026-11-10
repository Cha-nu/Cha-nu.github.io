# project-b-nearest

[ProjectB] 자동 조준 탐색(nearest) 개발일지의 수치를 낸 코드와 기록입니다.

- `nearest.gd`: 게임 코드에서 발췌한 탐색 함수 (격자 고리 탐색, 시야 검사, 시야 캐시)
- `bench.gd`: 측정 코드 (게임의 자동 점검에서 발췌)
- `autotest_runs.log`: 같은 측정을 3번 돌린 원본 출력

## 실행

ProjectB(Godot 4.7.2) 폴더에서 아래 명령으로 자동 점검을 돌리면 `AUTOTEST nearest`, `AUTOTEST lab ...` 줄이 출력됩니다.

```bash
godot --path . -- --autotest
```

## 조건

- Windows 11 데스크톱, Godot 4.7.2 (Mobile 렌더러), GDScript, 창 모드 실행
- 시간은 `Time.get_ticks_usec()`로 잰 1회 탐색 평균(µs). 정확도 비교는 무작위 400지점 x 사거리 230/290/600
- 밀집·벽 뒤 측정은 적 150명을 얼려(`frz`) 위치를 고정하고, 질의 200번 동안 게임 시간을 1/30초씩 진행
- 모바일 기기에서는 재지 않았습니다
