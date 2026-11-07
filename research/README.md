# research

글에 나오는 수치와 그래프를 만든 스크립트를 보관하는 곳입니다. 글의 숫자는 여기 있는 코드로 다시 낼 수 있어야 합니다.

- 폴더 이름은 글의 시리즈 키 또는 글 파일 이름과 같게 합니다. (예: `flight-theory/part2`)
- 실험 스크립트(`exp*.py`, `sim.py` 등)가 먼저, 그림 스크립트(`g*.py`, `f*.py`)가 나중입니다. 그림 스크립트는 실험이 남긴 `.npy`, `.json`을 읽습니다.
- 결과 그림은 `fig/`에 생기며, 글에 쓸 그림만 `public/images/<글>/`로 복사합니다. `fig/`, `*.npy`는 저장소에 올리지 않습니다.

```bash
pip install numpy matplotlib pillow
cd research/flight-theory/part2
mkdir -p fig
python3 expA.py && python3 expB.py && python3 expC.py && python3 expC2.py
python3 g1.py && python3 g23.py && python3 g4.py && python3 g567.py
```

그림의 한글 글꼴은 Noto Sans CJK KR을 씁니다. 없으면 설치하거나 `plt.rcParams["font.family"]`를 바꿔 주세요.
