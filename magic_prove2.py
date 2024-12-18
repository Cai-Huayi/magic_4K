import random

# 全局翻转计数字典
flip_count = {}

def flip_card(t, o):
    """
    翻转一张牌的朝向，并记录翻转次数。
    o为+1表示正面朝上，-1表示背面朝上
    翻转后o = -o
    """
    # 记录翻转次数
    if t not in flip_count:
        flip_count[t] = 0
    flip_count[t] += 1

    return (t, -o)

def print_deck(deck, title=""):
    if title:
        print(title)
    print(" ".join([f"{t}({'↑' if o==1 else '↓'})" for (t,o) in deck]))
    print()

def print_layout(layout_map, title=""):
    if title:
        print(title)

    if not layout_map:
        print("布局为空")
        return

    max_r = max(r for (r,c) in layout_map)
    max_c = max(c for (r,c) in layout_map)

    for r in range(max_r+1):
        row_str_list = []
        for c in range(max_c+1):
            stack = layout_map.get((r,c), [])
            if stack:
                stack_str = "|".join([f"{t}({'↑' if o==1 else '↓'})" for (t,o) in stack])
                row_str_list.append(f"({stack_str})[{len(stack)}]")
            else:
                row_str_list.append("Empty")
        print(" ".join(row_str_list))
    print()

def final_stack_to_linear(layout_map):
    if len(layout_map) == 1 and (0,0) in layout_map:
        final_stack = layout_map[(0,0)]
        # 从上到下显示牌：final_stack[-1]是顶部，final_stack[0]是底部
        final_stack_top_to_bottom = list(reversed(final_stack))

        print("最终一摞牌的线性展开(从上到下):")
        for (t,o) in final_stack_top_to_bottom:
            print(f"{t}({'↑' if o==1 else '↓'})")
    else:
        print("当前layout_map并非只有一个格子，无法线性展开为单摞牌。")

def create_initial_deck():
    # 12张任意牌背面朝下(o=-1)，4张K牌正面朝上(o=+1)并标序号
    random_cards = [(f"X{i+1}", -1) for i in range(12)]
    k_cards = [("K1", +1), ("K2", +1), ("K3", +1), ("K4", +1)]
    for k in k_cards:
        pos = random.randint(0, len(random_cards))
        random_cards.insert(pos, k)
    return random_cards

def interleave_flip(deck):
    new_deck = []
    for i in range(0, len(deck), 2):
        card1 = deck[i]       # (t,o)
        card2 = deck[i+1]
        # 第一张不变
        new_deck.append(card1)
        # 第二张翻转朝向 - 使用flip_card函数
        t2, o2 = card2
        new_deck.append(flip_card(t2, o2))
    return new_deck

def two_card_flip(deck):
    """
    正：逆序两张牌的顺序，但不改变朝向
    反：不改变两张牌的顺序，但翻转牌的朝向
    """
    new_deck = []
    for i in range(0, len(deck), 2):
        pair = deck[i:i+2]
        flip_to_positive = random.choice([True, False])
        
        if flip_to_positive:
            # 正：逆序，但朝向不变
            pair = list(reversed(pair))
        else:
            # 反：不逆序，但翻转朝向
            flipped_pair = []
            for (t,o) in pair:
                flipped_pair.append(flip_card(t, o))
            pair = flipped_pair

        new_deck.extend(pair)
    return new_deck

def s_shape_layout(deck, rows=4, cols=4):
    layout_map = {}
    index = 0
    for r in range(rows):
        row_cards = deck[index:index+cols]
        index += cols
        if r % 2 == 1:
            row_cards = list(reversed(row_cards))
        for c, card in enumerate(row_cards):
            layout_map[(r,c)] = [card]
    return layout_map

def normalize_layout(layout_map):
    if not layout_map:
        return layout_map
    min_r = min(r for (r,c) in layout_map)
    min_c = min(c for (r,c) in layout_map)
    adjusted_layout = {}
    for (r,c), stack in layout_map.items():
        adjusted_layout[(r - min_r, c - min_c)] = stack
    return adjusted_layout

def fold_from_direction(layout_map, direction):
    if not layout_map:
        return layout_map

    max_r = max(r for (r,c) in layout_map)
    max_c = max(c for (r,c) in layout_map)

    new_layout = {}

    if direction == 'N':
        # 将最上行r=0往下折叠到r=1
        for (r,c), stack in layout_map.items():
            if r == 0:
                flipped_stack = [flip_card(t,o) for (t,o) in reversed(stack)]
                target = layout_map.get((r+1,c), [])
                new_stack = target + flipped_stack
                new_layout[(r+1,c)] = new_stack
            else:
                if (r,c) not in new_layout:
                    new_layout[(r,c)] = stack
        new_layout = normalize_layout(new_layout)

    elif direction == 'S':
        # 将最下行r=max_r往上折叠
        for (r,c), stack in layout_map.items():
            if r == max_r:
                flipped_stack = [flip_card(t,o) for (t,o) in reversed(stack)]
                target = layout_map.get((r-1,c), [])
                new_stack = target + flipped_stack
                new_layout[(r-1,c)] = new_stack
            else:
                if (r,c) not in new_layout:
                    new_layout[(r,c)] = stack
        new_layout = normalize_layout(new_layout)

    elif direction == 'W':
        # 将最左列c=0往右折叠
        for (r,c), stack in layout_map.items():
            if c == 0:
                flipped_stack = [flip_card(t,o) for (t,o) in reversed(stack)]
                target = layout_map.get((r,c+1), [])
                new_stack = target + flipped_stack
                new_layout[(r,c+1)] = new_stack
            else:
                if (r,c) not in new_layout:
                    new_layout[(r,c)] = stack
        new_layout = normalize_layout(new_layout)

    elif direction == 'E':
        # 将最右列c=max_c往左折叠
        for (r,c), stack in layout_map.items():
            if c == max_c:
                flipped_stack = [flip_card(t,o) for (t,o) in reversed(stack)]
                target = layout_map.get((r,c-1), [])
                new_stack = target + flipped_stack
                new_layout[(r,c-1)] = new_stack
            else:
                if (r,c) not in new_layout:
                    new_layout[(r,c)] = stack
        new_layout = normalize_layout(new_layout)

    else:
        new_layout = layout_map

    return new_layout

if __name__ == "__main__":
    deck = create_initial_deck()
    print_deck(deck, "初始牌堆:")

    deck = interleave_flip(deck)
    print_deck(deck, "正反交错重组后的牌堆:")

    deck = deck[::-1]
    print_deck(deck, "整体逆序后的牌堆:")

    deck = two_card_flip(deck)
    print_deck(deck, "两张一组随机正反翻折后的牌堆:")

    layout_map = s_shape_layout(deck, rows=4, cols=4)
    print_layout(layout_map, "S形(Z字形)铺放结果:")

    for _ in range(8):
        direction= random.choice(["N","S","E","W"])
        layout_map = fold_from_direction(layout_map,direction)
        print_layout(layout_map, f"从{direction}方向折叠一次后的结果:")

    final_stack_to_linear(layout_map)

    # 输出翻转次数统计结果
    print("每张牌被翻转次数统计:")
    for card_name, count in flip_count.items():
        print(f"{card_name}: {count}次")
