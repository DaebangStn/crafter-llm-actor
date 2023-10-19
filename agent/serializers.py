from typing import Dict, List, Deque


def serializer_surrounding(_surrounding: Dict[str, list]) -> str:
    ignoring_items: List[str] = ['grass', 'player', 'path']
    position_explain = []

    for item, positions in _surrounding.items():
        if item in ignoring_items:
            continue
        if positions:
            positions_str = []
            for x, y in positions:
                if x == 0:
                    dir_y = "up" if y < 0 else "down"
                    positions_str.append(f"({abs(y)} {dir_y})".replace("1", "facing"))
                    continue
                if y == 0:
                    dir_x = "left" if x < 0 else "right"
                    positions_str.append(f"({abs(x)} {dir_x})".replace("1", "facing"))
                    continue

                dir_x = "left" if x < 0 else "right"
                dir_y = "up" if y < 0 else "down"
                positions_str.append(f"({abs(x)} {dir_x}, {abs(y)} {dir_y})")
            position_explain.append(f"{item} at positions: {', '.join(positions_str)}")
        else:
            pass
            # position_explain.append(f"{item} not found")

    return " - ".join(position_explain)


def serializer_surrounding_deque(_surrounding_deque: Deque[Dict[str, list]]) -> str:
    if len(_surrounding_deque) == 0:
        return "no information about surrounding"
    elif len(_surrounding_deque) == 1:
        explains = [
            'current surrounding:',
            serializer_surrounding(_surrounding_deque[0]),
        ]
        return "\n".join(explains)
    elif len(_surrounding_deque) == 2:
        explains = [
            'current surrounding:',
            serializer_surrounding(_surrounding_deque[-1]),
            'previous surrounding:',
            serializer_surrounding(_surrounding_deque[0]),
        ]
        return "\n".join(explains)
    else:
        raise ValueError("surrounding_deque must have length 0, 1, or 2")


def serializer_inventory(_inventory: Dict[str, int]) -> str:
    status_id = ['health', 'food', 'drink', 'energy']
    inventory_explain = []

    for item, count in _inventory.items():
        if item in status_id:
            inventory_explain.append(f"{item}: {count}/9")
        else:
            if count > 0:
                inventory_explain.append(f"{item}: {count}")
            else:
                pass
                # inventory_explain.append(f"{item} not found")

    return " - ".join(inventory_explain)


def serializer_inventory_deque(_inventory_deque: Deque[Dict[str, int]]) -> str:
    if len(_inventory_deque) == 0:
        return "no information about inventory"
    elif len(_inventory_deque) == 1:
        explains = [
            'current inventory:',
            serializer_inventory(_inventory_deque[0]),
        ]
        return "\n".join(explains)
    elif len(_inventory_deque) == 2:
        explains = [
            'current inventory:',
            serializer_inventory(_inventory_deque[-1]),
            'previous inventory:',
            serializer_inventory(_inventory_deque[0]),
        ]
        return "\n".join(explains)
    else:
        raise ValueError("inventory_deque must have length 0, 1, or 2")