## ProjectB scripts/main.gd 의 자동 점검(--autotest)에서 발췌. 결과는 autotest_runs.log

## 1) 무작위 400지점 정확도·속도 비교 (적 300명)
## nearest(): 격자 고리 탐색이 전수 탐색과 같은 답을 내는지, 속도 비교
	var brute = func(x, y, r):
		var bb = null
		var bdd = r
		for e in game.en:
			if e.hp > 0:
				var dd = Vector2(e.x - x, e.y - y).length() - e.r
				if dd < bdd:
					bdd = dd
					bb = e
		return bb
	while game.en.size() < 300:
		game.spawn("ru", randf_range(100, 2900), randf_range(100, 2900))
	game.update(1.0 / 30.0)
	var pts = []
	for i in 400:
		var c = game.en[randi() % game.en.size()] if randf() < 0.7 and game.en.size() > 0 else {x = randf() * 3000, y = randf() * 3000}
		pts.append(Vector2(c.x + randf_range(-200, 200), c.y + randf_range(-200, 200)))
	var mism = 0
	for q in pts:
		for r in [230.0, 290.0, 600.0]:
			if not is_same(game.nearest(q.x, q.y, r, false), brute.call(q.x, q.y, r)):
				mism += 1
	var u0 = Time.get_ticks_usec()
	for q in pts:
		game.nearest(q.x, q.y, 290.0, false)
	var u1 = Time.get_ticks_usec()
	for q in pts:
		brute.call(q.x, q.y, 290.0)
	var u2 = Time.get_ticks_usec()
	var blocked = 0
	for q in pts:
		var a1 = game.nearest(q.x, q.y, 290.0, false)
		var a2 = game.nearest(q.x, q.y, 290.0, false, true)
		if a1 != null and not is_same(a1, a2):
			blocked += 1
	print("AUTOTEST nearest en=%d mismatch=%d grid_us=%d brute_us=%d los_skipped=%d/%d" % [game.en.size(), mism, (u1 - u0) / pts.size(), (u2 - u1) / pts.size(), blocked, pts.size()])

## 2) 벽 뒤 적 / 밀집 / 벽 뒤 밀집
## ---------- nearest() 탐색 실험: 벽 뒤 적, 밀집, 벽 뒤 밀집 ----------
## 프레임마다 한 번 부르는 상황을 흉내 낸다 (게임 시간 t를 1/30초씩 진행)
func _bench(x: float, y: float, r: float, los_on: bool, n := 200, cache := false) -> Array:
	game.los_n = 0
	for e in game.en:
		e.erase("lvT")
	var u0 = Time.get_ticks_usec()
	for i in n:
		game.t += 1.0 / 30.0
		game.nearest(x, y, r, false, los_on, false, cache)
	var us = float(Time.get_ticks_usec() - u0) / n
	return [us, float(game.los_n) / n]


func _brute_us(x: float, y: float, r: float, n := 200) -> float:
	var u0 = Time.get_ticks_usec()
	for i in n:
		var bd = r
		for e in game.en:
			if e.hp > 0:
				var d = Vector2(e.x - x, e.y - y).length() - e.r
				if d < bd:
					bd = d
	return float(Time.get_ticks_usec() - u0) / n


func _clear_enemies() -> void:
	for e in game.en:
		if is_instance_valid(e.node):
			e.node.queue_free()
	game.en.clear()
	game.rcall = null


func _freeze_all() -> void:
	for e in game.en:
		e.frz = 999.0
		e.st = "alert"
		e.alT = 0.0
		e.aw = 1.0
		e.px = e.x
		e.py = e.y


func _search_lab() -> void:
	if game.pause == "lvl":
		lvl_ov.visible = false
		game.choose_upgrade({heal = true})
	game.p.inv = 0.0
	game.p.hp = game.p.maxhp
	game.p.xp = -99999
	game.comms = null
	## 촬영용: 사격을 멈추고(재장전 상태 유지) 화면 글자를 지운다
	game.p.reload = 9999.0
	hud.banner_t = 0.0
	hud.banner_lb.modulate.a = 0.0
	game.fl.clear()
	## 높이 16 이상, 한 변 60~140인 건물 하나를 고른다
	var wall = null
	for cell in game.map.rg:
		for k in cell:
			var far_aa = true
			for o in game.map.objs:
				if Vector2(o.x - k.x, o.y - k.y).length() < game.AAR + 250:
					far_aa = false
			if far_aa and k.has("hw") and k.h >= 16 and k.hw > 30 and k.hh > 30 and k.hw < 70 and k.x > 500 and k.x < 2500 and k.y > 500 and k.y < 2500:
				wall = k
				break
		if wall != null:
			break
	if wall == null:
		print("AUTOTEST lab no wall")
		return
	var px = wall.x - wall.hw - 45.0
	var py = wall.y
	game.p.x = px
	game.p.y = py
	var r: float = game.p.w.range
	## 1) 벽 뒤 가까운 적 4 + 트인 곳의 먼 적 3
	_clear_enemies()
	for i in 4:
		game.spawn("ru", wall.x + wall.hw + 25 + i * 12, wall.y - 30 + i * 20)
	for i in 3:
		game.spawn("rf", px - 60 + i * 30, py + 200 + i * 15)
	_freeze_all()
	game.dbg_trace = true
	for i in 3:
		game.update(1.0 / 30.0)
	var near_raw = game.nearest(px, py, r, false, false)
	var near_los = game.nearest(px, py, r, false, true)
	game.nearest(px, py, r, false, true, true)
	print("AUTOTEST lab wall: no_los_pick=%s los_pick=%s" % [near_raw.type if near_raw else "-", near_los.type if near_los else "-"])
	await get_tree().create_timer(0.4).timeout
	await _shot("trace_wall")
	## 2) 밀집: 플레이어 앞 160 지점에 반경 90 안 150명
	_clear_enemies()
	game.p.x = px - 400
	game.p.y = py
	var cx = game.p.x - 160
	var cy = game.p.y
	for i in 150:
		var a = randf() * TAU
		var d = sqrt(randf()) * 90
		game.spawn("ru", cx + cos(a) * d, cy + sin(a) * d)
	_freeze_all()
	for i in 3:
		game.update(1.0 / 30.0)
	var g1 = _bench(game.p.x, game.p.y, r, false)
	var g2 = _bench(game.p.x, game.p.y, r, true)
	var bf = _brute_us(game.p.x, game.p.y, r)
	game.nearest(game.p.x, game.p.y, r, false, true, true)
	print("AUTOTEST lab crowd: en=%d grid_us=%.1f grid_los_us=%.1f los_calls=%.1f brute_us=%.1f rings=%d cells=%d" % [game.en.size(), g1[0], g2[0], g2[1], bf, game.trace.rings, game.trace.cells.size()])
	await get_tree().create_timer(0.4).timeout
	await _shot("trace_crowd")
	## 3) 최악: 벽 바로 뒤에 150명 (모두 플레이어보다 가깝지만 시야가 막힘)
	_clear_enemies()
	game.p.x = px
	game.p.y = py
	for i in 150:
		game.spawn("ru", wall.x + wall.hw + 15 + randf() * 70, wall.y - wall.hh + randf() * wall.hh * 2)
	_freeze_all()
	for i in 3:
		game.update(1.0 / 30.0)
	var w1 = _bench(px, py, r, false)
	var w2 = _bench(px, py, r, true)
	var w3 = _bench(px, py, r, true, 200, true)
	var wb = _brute_us(px, py, r)
	game.nearest(px, py, r, false, true, true)
	print("AUTOTEST lab behind_wall: en=%d grid_us=%.1f grid_los_us=%.1f los_calls=%.1f cached_us=%.1f cached_los_calls=%.1f brute_us=%.1f rings=%d cells=%d pick=%s" % [game.en.size(), w1[0], w2[0], w2[1], w3[0], w3[1], wb, game.trace.rings, game.trace.cells.size(), game.trace.pick != null])
	await get_tree().create_timer(0.4).timeout
	await _shot("trace_worst")
	game.dbg_trace = false
