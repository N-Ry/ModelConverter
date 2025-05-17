# Lを抑える最小の2のべき乗を求める
def next_power_of_two(L):
    # 整数型に型変換
    L = int(L)

    if L <= 0:
        return 1  # 0や負数の場合、2^0 = 1 を返す
    return 1 << (L - 1).bit_length()

# 1辺の長さ L の正方形に長方形集合 rectangles が入りきるか
def can_pack(L, rectangles) -> bool:
    x = 0
    y = 0
    shelf_height = 0

    for w, h in rectangles:
        if w > L or h > L:
            return False  # 正方形に入らない

        if x + w <= L:
            x += w
            shelf_height = max(shelf_height, h)
        else:
            y += shelf_height
            if y + h > L:
                return False
            x = w
            shelf_height = h
            
    return True

# 与えられた長方形集合が入りきる最小の正方形サイズ
def min_square_size(rectangles):
    # 下限: 最大幅・高さのどちらか
    left = max(max(w for w, h in rectangles), max(h for w, h in rectangles))

    # 上限: 全面を縦か横に並べたとき（単純な合計）
    right = sum(max(w, h) for w, h in rectangles)

    while left < right:
        mid = (left + right) // 2
        if can_pack(mid, rectangles):
            right = mid
        else:
            left = mid + 1
    return left

# サイズLの正方形に長方形集合を配置
def place_rectangles(L, rectangles):
    # 元インデックスを保持して、高さ・幅の降順にソート
    indexed_rects = list(enumerate(rectangles))
    indexed_rects.sort(key=lambda r: (-r[1][1], -r[1][0]))

    x = 0
    y = 0
    shelf_height = 0
    placed_positions = {}

    for idx, (w, h) in indexed_rects:
        if x + w <= L:
            placed_positions[idx] = (x, y)
            x += w
            shelf_height = max(shelf_height, h)
        else:
            y += shelf_height
            if y + h > L:
                return None  # 入りきらない
            x = 0
            shelf_height = h
            placed_positions[idx] = (x, y)
            x += w

    # 出力を元インデックス順に復元
    result = [placed_positions[i] for i in range(len(rectangles))]
    return result