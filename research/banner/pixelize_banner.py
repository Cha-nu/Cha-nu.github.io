"""AI가 만든 픽셀 아트 배너를 진짜 픽셀 격자(저해상도 PNG)로 되돌린다.

AI 이미지는 픽셀 한 칸이 가로 약 6.5px, 세로 약 6.1px로 정수가 아니고 칸 크기도 들쭉날쭉하다.
브라우저가 이 그림을 화면 폭에 맞춰 다시 줄이면 칸 크기가 더 어긋나서 구름 테두리가 자글거린다.
그래서 격자 간격을 찾아 칸마다 대표색 하나(중앙값)를 뽑아 저해상도 그림을 만들고,
사이트에서는 CSS image-rendering: pixelated로 키워서 보여 준다.

사용법:
    python research/banner/pixelize_banner.py <원본.png> public/assets/banner/desktop.png
"""

import sys

import numpy as np
from PIL import Image


def find_grid(edge_strength: np.ndarray, length: int) -> tuple[float, float]:
    """칸 경계에서 밝기 변화가 가장 크게 모이는 (간격, 시작 위치)를 찾는다."""
    best = (-1.0, 0.0, 0.0)
    for period in np.arange(4.0, 12.0, 0.01):
        for phase in np.arange(0.0, period, 0.25):
            idx = np.round(np.arange(phase, length - 1, period)).astype(int)
            idx = idx[idx < len(edge_strength)]
            score = edge_strength[idx].mean()
            if score > best[0]:
                best = (score, period, phase)
    return best[1], best[2]


def cells(period: float, phase: float, length: int) -> list[tuple[int, int]]:
    edges = np.arange(phase + 1 - period, length, period)
    cut = sorted({min(length, max(0, int(round(v)))) for v in edges} | {length})
    return [(a, b) for a, b in zip(cut[:-1], cut[1:]) if b - a >= 2]


def main(src_path: str, out_path: str) -> None:
    img = np.asarray(Image.open(src_path).convert("RGB")).astype(float)
    h, w, _ = img.shape
    gray = img.mean(axis=2)

    px, phx = find_grid(np.abs(np.diff(gray, axis=1)).sum(axis=0), w)
    py, phy = find_grid(np.abs(np.diff(gray, axis=0)).sum(axis=1), h)
    print(f"격자 간격: 가로 {px:.2f}px, 세로 {py:.2f}px")

    cx, cy = cells(px, phx, w), cells(py, phy, h)
    out = np.zeros((len(cy), len(cx), 3), np.uint8)
    for j, (y0, y1) in enumerate(cy):
        for i, (x0, x1) in enumerate(cx):
            # 칸 테두리 1px은 이웃 칸과 섞여 있어서 뺀다.
            m = 1 if min(y1 - y0, x1 - x0) > 3 else 0
            block = img[y0 + m : y1 - m, x0 + m : x1 - m].reshape(-1, 3)
            out[j, i] = np.median(block, axis=0)

    Image.fromarray(out).save(out_path, optimize=True)
    print(f"{out_path}: {out.shape[1]}x{out.shape[0]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
