import random
from collections import Counter

# 麻將的所有牌
ALL_TILES = [f"{suit}{i}" for suit in ['m', 'p', 's'] for i in range(1, 10)] + [f"z{i}" for i in range(1, 8)]

# 將符號轉換為可讀文字
TILE_TRANSLATION = {
    'm': "萬",
    'p': "筒",
    's': "條",
    'z1': "東", 'z2': "南", 'z3': "西", 'z4': "北",
    'z5': "中", 'z6': "發", 'z7': "白"
}

def translate_tile(tile):
    """將牌轉換為可讀文字"""
    if tile in TILE_TRANSLATION:
        return TILE_TRANSLATION[tile]
    if tile[0] in TILE_TRANSLATION:
        return f"{tile[1]}{TILE_TRANSLATION[tile[0]]}"
    return tile

def translate_hand(hand):
    """將整副手牌轉換為可讀文字"""
    return [translate_tile(tile) for tile in hand]

def display_hand(hand):
    """顯示目前手牌"""
    hand.sort()
    readable_hand = translate_hand(hand)
    print("目前手牌: ", " ".join(readable_hand))

def random_draw(remaining_tiles):
    """隨機從牌堆抽一張牌"""
    if not remaining_tiles:
        return None
    return remaining_tiles.pop(random.randint(0, len(remaining_tiles) - 1))

def can_chi(hand, tile):
    """判斷是否可以吃"""
    if tile[-1] in 'z':  # 字牌不能吃
        return []
    suit = tile[0]
    num = int(tile[1])
    options = []
    for offset in [-2, -1, 1, 2]:
        chi_set = [f"{suit}{num + offset}", f"{suit}{num + offset + 1}", tile]
        if all(t in hand or t == tile for t in chi_set):
            options.append(sorted(chi_set))
    return options

def can_peng(hand, tile):
    """判斷是否可以碰"""
    return hand.count(tile) >= 2

def check_win(hand):
    """簡單胡牌判定 (七對子和基本組合)"""
    counter = Counter(hand)
    # 七對子判斷
    if all(count == 2 for count in counter.values()):
        return True, "七對子"
    
    # TODO: 完整的胡牌判斷邏輯
    return False, ""

def calculate_efficiency(hand):
    """計算手牌的進張數"""
    counter = Counter(hand)
    unique_tiles = set(hand)
    efficiency = 0
    
    for tile in unique_tiles:
        if tile[-1] in 'z':  # 字牌直接加分（簡化處理）
            efficiency += 1
        else:
            suit = tile[0]
            num = int(tile[1])
            neighbors = [f"{suit}{num - 1}", f"{suit}{num + 1}"]
            efficiency += sum(1 for n in neighbors if n in ALL_TILES and n not in hand)
    
    return efficiency

def suggest_action(hand, drawn_tile, chi_options, can_peng_flag):
    """根據當前情況推薦吃、碰或摸牌"""
    base_efficiency = calculate_efficiency(hand)
    recommendations = []
    
    if can_peng_flag:
        new_hand = hand + [drawn_tile] * 2
        new_efficiency = calculate_efficiency(new_hand)
        recommendations.append(("碰", new_efficiency))
    
    for chi_option in chi_options:
        new_hand = hand + [tile for tile in chi_option if tile != drawn_tile]
        new_efficiency = calculate_efficiency(new_hand)
        recommendations.append((f"吃 {chi_option}", new_efficiency))
    
    # 默認選擇保持原狀
    new_hand = hand + [drawn_tile]
    new_efficiency = calculate_efficiency(new_hand)
    recommendations.append(("保持原狀", new_efficiency))
    
    # 找到最高效率的選項
    best_action = max(recommendations, key=lambda x: x[1])
    return best_action

# 修改遊戲主邏輯加入完整牌局初始手牌

def main():
    # 初始化
    remaining_tiles = ALL_TILES * 4
    random.shuffle(remaining_tiles)

    # 起手摸 16 張牌
    hand = [random_draw(remaining_tiles) for _ in range(16)]

    # 模擬預設的玩家動作序列（替代 input）
    predefined_actions = iter(["保持原狀", "m1", "p9", "s3"])  # 預設的動作，包含打出的牌

    while True:
        display_hand(hand)

        # 隨機摸一張牌
        drawn_tile = random_draw(remaining_tiles)
        if not drawn_tile:
            print("牌堆已經沒有牌了！")
            break

        print(f"摸到了 {translate_tile(drawn_tile)}")
        
        # 判斷是否能吃或碰
        chi_options = can_chi(hand, drawn_tile)
        can_peng_flag = can_peng(hand, drawn_tile)

        if chi_options:
            readable_chi_options = [translate_hand(option) for option in chi_options]
            print(f"可以吃: {readable_chi_options}")
        if can_peng_flag:
            print("可以碰!")

        # 推薦策略
        best_action, efficiency = suggest_action(hand, drawn_tile, chi_options, can_peng_flag)
        print(f"推薦策略: {best_action} (效率: {efficiency})")

        # 加入摸到的牌
        if best_action == "保持原狀":
            hand.append(drawn_tile)
        elif "碰" in best_action:
            hand += [drawn_tile] * 2
        elif "吃" in best_action:
            chi_set = eval(best_action.split(" ")[1])  # 安全處理吃牌邏輯
            for tile in chi_set:
                if tile != drawn_tile:
                    hand.append(tile)

        # 胡牌判定
        is_win, win_type = check_win(hand)
        if is_win:
            print(f"胡牌！類型: {win_type}")
            break

        # 玩家選擇是否打出一張牌
        try:
            discard = next(predefined_actions)  # 使用預設動作
            print(f"選擇打出: {translate_tile(discard)}")
            if discard and discard in hand:
                hand.remove(discard)
                remaining_tiles.append(discard)
                random.shuffle(remaining_tiles)
        except StopIteration:
            print("沒有更多預設動作了！")
            break

if __name__ == "__main__":
    main()

