import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8080"


def req(method, path, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    if not body.get("ok"):
        raise SystemExit(json.dumps(body.get("error"), ensure_ascii=False, indent=2))
    return body["data"]


def compact(state):
    out = {
        "screen": state.get("screen"),
        "actions": state.get("available_actions") or [],
        "modal": state.get("modal"),
        "in_combat": state.get("in_combat"),
        "turn": state.get("turn"),
    }
    run = state.get("run") or {}
    if run:
        out["run"] = {
            k: run.get(k)
            for k in (
                "character",
                "floor",
                "act",
                "hp",
                "max_hp",
                "gold",
                "ascension",
                "relics",
                "deck_size",
                "potions",
            )
            if k in run
        }
    combat = state.get("combat") or {}
    if combat:
        player = combat.get("player") or {}
        out["combat"] = {
            "player_hp": player.get("current_hp"),
            "player_block": player.get("block"),
            "player_energy": player.get("energy"),
            "player_powers": player.get("powers"),
            "hand": [
                {
                    "index": c.get("index"),
                    "name": c.get("name"),
                    "cost": c.get("energy_cost"),
                    "playable": c.get("playable"),
                    "requires_target": c.get("requires_target"),
                    "valid_target_indices": c.get("valid_target_indices"),
                    "rules": c.get("resolved_rules_text"),
                }
                for c in (combat.get("hand") or [])
            ],
            "enemies": combat.get("enemies"),
            "end_turn_will_kill_player": combat.get("end_turn_will_kill_player"),
            "lethal_risks": combat.get("lethal_risks"),
        }
    for key in (
        "map",
        "selection",
        "character_select",
        "event",
        "chest",
        "rest",
        "reward",
        "shop",
        "game_over",
        "timeline",
    ):
        if state.get(key):
            out[key] = state[key]
    return out


def show_map(state):
    map_data = state.get("map") or {}
    nodes = map_data.get("nodes") or []
    rows = max((n.get("row") or 0 for n in nodes), default=0) + 1
    cols = max((n.get("col") or 0 for n in nodes), default=0) + 1
    if not nodes:
        print(json.dumps(compact(state), ensure_ascii=False, indent=2))
        return
    symbols = {
        "Monster": "M",
        "Elite": "E",
        "RestSite": "R",
        "Shop": "$",
        "Treasure": "T",
        "Unknown": "?",
        "Boss": "B",
        "Ancient": "A",
    }
    current = map_data.get("current_node") or {}
    available = {
        (n.get("row"), n.get("col"))
        for n in (map_data.get("available_nodes") or [])
    }
    grid = [[" "] * cols for _ in range(rows)]
    for node in nodes:
        row = node.get("row")
        col = node.get("col")
        if row is None or col is None:
            continue
        symbol = symbols.get(node.get("node_type"), "?")
        cell = symbol
        if node.get("is_current"):
            cell = "[" + symbol + "]"
        elif (row, col) in available:
            cell = "(" + symbol + ")"
        grid[row][col] = cell
    print("MAP", end="  ")
    print(" ".join(f"c{i}" for i in range(cols)))
    for row in range(rows):
        print(f"r{row:<2}", " ".join(grid[row]))
    print("current:", current)
    print("available_nodes:")
    for n in map_data.get("available_nodes") or []:
        print(
            f"  index={n.get('index')} ({n.get('row')},{n.get('col')}) {n.get('node_type')}"
        )


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: state | act <action> [--index N] [--target N]")
        return
    if args[0] == "state":
        data = req("GET", "/state")
        print(json.dumps(compact(data), ensure_ascii=False, indent=2))
        return
    if args[0] == "map":
        data = req("GET", "/state")
        show_map(data)
        return
    action = args[1]
    index = None
    target = None
    rest = args[2:]
    while rest:
        flag = rest.pop(0)
        if flag == "--index":
            index = int(rest.pop(0))
        elif flag == "--target":
            target = int(rest.pop(0))
    payload = {
        "action": action,
        "card_index": index if action in ("play_card",) else None,
        "option_index": index if action not in ("play_card",) else None,
        "target_index": target,
        "client_context": {"source": "codex", "tool_name": action},
    }
    data = req("POST", "/action", payload)
    result = {
        "action": data.get("action"),
        "status": data.get("status"),
        "message": data.get("message"),
    }
    if data.get("state"):
        result["state"] = compact(data["state"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
