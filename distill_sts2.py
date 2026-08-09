import json
import os
import re

BASE = r"D:\Steam\steamapps\common\Slay the Spire 2\STS2AIAgent_extracted\mcp_server\data\eng"
OUT = r"C:\Users\Administrator\.codex\skills\sts2-climber\references"


def clean(text):
    if not text:
        return ""
    text = re.sub(r"\[/?[a-zA-Z0-9_\- ]+\]", "", text)
    text = re.sub(r"res://\S+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def load(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else data.get("data", data)


def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(name, len(content.splitlines()), "lines")


cards = load("cards.json")
cards_by_color = {}
for c in cards:
    cards_by_color.setdefault(c.get("color", "?"), []).append(c)

for color in sorted(cards_by_color):
    label = color.capitalize()
    lines = [f"# {label} Cards", ""]
    for c in sorted(cards_by_color[color], key=lambda x: (x.get("rarity", ""), x.get("name", ""))):
        cost = c.get("cost")
        cost_txt = "X" if c.get("is_x_cost") else str(cost) if cost is not None else "?"
        parts = [f"- **{c.get('name')}** ({cost_txt}费, {c.get('type')}, {c.get('rarity')})"]
        extra = []
        if c.get("damage") is not None:
            extra.append(f"伤害{c['damage']}")
        if c.get("block") is not None:
            extra.append(f"格挡{c['block']}")
        if c.get("hit_count") is not None:
            extra.append(f"打{c['hit_count']}下")
        if c.get("cards_draw") is not None:
            extra.append(f"抽{c['cards_draw']}")
        if extra:
            parts[0] = parts[0][:-1] + f", {'/'.join(extra)})"
        desc = clean(c.get("description"))
        if desc:
            parts.append(desc)
        lines.append(": ".join(parts))
    write(f"cards-{color}.md", "\n".join(lines) + "\n")

monsters = load("monsters.json")
lines = ["# Monsters", ""]
for m in sorted(monsters, key=lambda x: x.get("name", "")):
    hp = f"{m.get('min_hp')}-{m.get('max_hp')}"
    moves = ", ".join(mv.get("name", "?") for mv in m.get("moves", [])[:6])
    lines.append(f"- **{m.get('name')}** ({m.get('type')}, HP {hp}): {moves}")
write("monsters.md", "\n".join(lines) + "\n")

relics = load("relics.json")
lines = ["# Relics", ""]
for r in sorted(relics, key=lambda x: (x.get("rarity", ""), x.get("name", ""))):
    lines.append(f"- **{r.get('name')}** ({r.get('rarity')}, {r.get('pool')}): {clean(r.get('description'))}")
write("relics.md", "\n".join(lines) + "\n")

potions = load("potions.json")
lines = ["# Potions", ""]
for p in sorted(potions, key=lambda x: x.get("name", "")):
    lines.append(f"- **{p.get('name')}** ({p.get('rarity')}, {p.get('pool')}): {clean(p.get('description'))}")
write("potions.md", "\n".join(lines) + "\n")

events = load("events.json")
lines = ["# Events", ""]
for e in sorted(events, key=lambda x: x.get("name", "")):
    desc = clean(e.get("description"))[:180]
    lines.append(f"- **{e.get('name')}** ({e.get('act')}): {desc}")
write("events.md", "\n".join(lines) + "\n")

encounters = load("encounters.json")
lines = ["# Encounters", ""]
for e in sorted(encounters, key=lambda x: ((x.get("act") or ""), (x.get("name") or ""))):
    mobs = ", ".join(m.get("name", "?") for m in e.get("monsters", []))
    lines.append(f"- **{e.get('name')}** ({e.get('act')}, {e.get('room_type')}): {mobs}")
write("encounters.md", "\n".join(lines) + "\n")

characters = load("characters.json")
lines = ["# Characters", "", "| 角色 | HP | 金币 | 能量 | 球位 | 起始牌组 |", "|---|---|---|---|---|---|"]
for c in sorted(characters, key=lambda x: x.get("name", "")):
    deck = ", ".join(c.get("starting_deck", []))
    lines.append(f"| {c.get('name')} | {c.get('starting_hp')} | {c.get('starting_gold')} | {c.get('max_energy')} | {c.get('orb_slots')} | {deck} |")
write("characters.md", "\n".join(lines) + "\n")

acts = load("acts.json")
lines = ["# Acts", "", "| Act | 房间数 | Boss | 古神 |", "|---|---|---|---|"]
for a in sorted(acts, key=lambda x: x.get("name", "")):
    lines.append(f"| {a.get('name')} | {a.get('num_rooms')} | {', '.join(a.get('bosses', []))} | {', '.join(a.get('ancients', []))} |")
write("acts.md", "\n".join(lines) + "\n")

keywords = load("keywords.json")
lines = ["# Keywords", ""]
for k in sorted(keywords, key=lambda x: x.get("name", "")):
    lines.append(f"- **{k.get('name')}**: {clean(k.get('description'))}")
write("keywords.md", "\n".join(lines) + "\n")
