## ProjectB(Godot 4.7) scripts/game.gd 에서 발췌. 자동 조준 탐색 함수와 시야 캐시
## 격자: TS = 50 단위 칸, TN = 60 (맵 3000 x 3000), 매 프레임 update()에서 다시 채운다

## 플레이어 시야 캐시: 적마다 결과를 0.1~0.2초 기억한다 (벽 뒤에 적이 몰려 있을 때 매 프레임 전부 다시 검사하지 않도록)
func _sees(x: float, y: float, e: Dictionary, cache: bool) -> bool:
	if not cache:
		return los(x, y, e.x, e.y)
	if t < e.get("lvT", -1.0):
		return e.lv
	e.lv = los(x, y, e.x, e.y)
	e.lvT = t + 0.1 + randf() * 0.1
	return e.lv


func nearest(x: float, y: float, range: float, nests: bool, need_los := false, tr := false, cache := false):
	var b = null
	var bd = range
	var rec = null
	if tr:
		rec = {x = x, y = y, cells = [], blocked = [], rings = 0}
	var cx = int(clampf(x, 0, WORLD - 1) / TS)
	var cy = int(clampf(y, 0, WORLD - 1) / TS)
	var maxr = int(ceil((range + MAX_ER) / TS))
	for ring in maxr + 1:
		## 이 고리 칸에 있는 적까지의 최소 거리 하한
		if (ring - 1) * TS - MAX_ER > bd:
			break
		if rec != null:
			rec.rings = ring
		for j in range(cy - ring, cy + ring + 1):
			if j < 0 or j >= TN:
				continue
			var edge = j == cy - ring or j == cy + ring
			var k = cx - ring
			while k <= cx + ring:
				if k >= 0 and k < TN:
					if rec != null:
						rec.cells.append(Vector2i(k, j))
					for e in grid[j * TN + k]:
						if e.hp <= 0:
							continue
						var d: float = Vector2(e.x - x, e.y - y).length() - e.r
						if d < bd:
							if not need_los or _sees(x, y, e, cache):
								bd = d
								b = e
							elif rec != null:
								rec.blocked.append(e)
				k += 1 if edge else maxi(1, ring * 2)
	if nests:
		for o in map.objs:
			if is_dest(o) and not o.done:
				var d: float = Vector2(o.x - x, o.y - y).length() - o.r
				if d < bd:
					bd = d
					b = o
	if rec != null:
		rec.pick = b
		trace = rec
	return b


