import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8080"

USAGE = """usage:
  python sts2_helper.py state
  python sts2_helper.py map
  python sts2_helper.py act <action> [--index N] [--target N]"""

# Action names accepted by the mod's POST /action dispatch (plus names exposed by
# GameStateService). Bare invocation is kept for compatibility, so unknown bare
# words must be rejected locally instead of being sent as game actions.
KNOWN_ACTIONS = frozenset(
    {
        "abandon_run",
        "buy_card",
        "buy_potion",
        "buy_relic",
        "choose_bundle",
        "choose_capstone_option",
        "choose_event_option",
        "choose_map_node",
        "choose_rest_option",
        "choose_reward_card",
        "choose_timeline_epoch",
        "choose_treasure_relic",
        "claim_reward",
        "close_cards_view",
        "close_main_menu_submenu",
        "close_shop_inventory",
        "collect_rewards_and_proceed",
        "confirm_bundle",
        "confirm_modal",
        "confirm_selection",
        "confirm_timeline_overlay",
        "continue_run",
        "decrease_ascension",
        "discard_potion",
        "disconnect_multiplayer_lobby",
        "dismiss_modal",
        "embark",
        "end_turn",
        "host_multiplayer_lobby",
        "increase_ascension",
        "join_multiplayer_lobby",
        "open_character_select",
        "open_chest",
        "open_shop_inventory",
        "open_timeline",
        "play_card",
        "proceed",
        "ready_multiplayer_lobby",
        "remove_card_at_shop",
        "resolve_rewards",
        "return_to_main_menu",
        "run_console_command",
        "save_and_quit",
        "select_character",
        "select_deck_card",
        "skip_reward_cards",
        "unready",
        "use_potion",
    }
)


def usage_error(message):
    print(f"error: {message}", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    raise SystemExit(2)


def parse_index(flag, value):
    # The mod uses a missing (null) field for "no index/target"; negative values
    # are out of range (409 invalid_target / card_index is out of range), not sentinels.
    try:
        parsed = int(value)
    except ValueError:
        usage_error(f"{flag} expects an integer, got {value!r}")
    if parsed < 0:
        usage_error(f"{flag} expects a non-negative integer, got {value!r}")
    return parsed


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
        usage_error("missing command")
    if args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return
    if args[0] == "state":
        if len(args) > 1:
            usage_error(f"unexpected argument: {args[1]}")
        data = req("GET", "/state")
        print(json.dumps(compact(data), ensure_ascii=False, indent=2))
        return
    if args[0] == "map":
        if len(args) > 1:
            usage_error(f"unexpected argument: {args[1]}")
        data = req("GET", "/state")
        show_map(data)
        return
    if args[0] in ("act", "action"):
        if len(args) < 2 or args[1].startswith("-"):
            usage_error("missing action for 'act'")
        action = args[1]
        rest = args[2:]
    else:
        action = args[0]
        if action not in KNOWN_ACTIONS:
            usage_error(f"unknown command or action: {action!r}")
        rest = args[1:]
    index = None
    target = None
    while rest:
        flag = rest.pop(0)
        if flag in ("--index", "--target"):
            if not rest:
                usage_error(f"{flag} requires a value")
            value = parse_index(flag, rest.pop(0))
            if flag == "--index":
                index = value
            else:
                target = value
        elif flag in ("-h", "--help"):
            print(USAGE)
            return
        else:
            usage_error(f"unexpected argument: {flag}")
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
