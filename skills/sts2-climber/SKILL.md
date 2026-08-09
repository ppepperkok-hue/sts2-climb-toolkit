---
name: sts2-climber
description: 杀戮尖塔2（Slay the Spire 2）爬塔知识库与实战流程。用 STS2 AI Agent 模组的本地 HTTP API 驱动游戏时使用：读状态、选卡、路线规划、打精英与 Boss、处理奖励与商店、SL 重开。触发词：爬塔、杀戮尖塔2、Slay the Spire 2、STS2、vibe 爬塔、选卡、精英对策、Boss 对策。
---

# STS2 爬塔大师

用游戏内 Mod「STS2 AI Agent」（本地 `http://127.0.0.1:8080`）读取状态并下发动作，替用户完成一局《杀戮尖塔2》。核心是把「决策质量」放在第一位：不空过回合、不浪费输出、不误判致命伤害。

## 每回合标准流程

1. **读状态**：`GET /state`，确认 `screen`、`available_actions`、`combat.hand`（含索引）、`combat.enemies`（含 intent 与总伤害）、`end_turn_will_kill_player` / `lethal_risks`。
2. **算斩杀与承伤**：本回合总伤害能否击杀至少一个敌人？敌人意图总伤害减去当前格挡后是否致命？致命就优先格挡或用药，绝不空过。
3. **打牌**：每打一张牌后**必须重新读手牌索引**（索引会变，跨动作复用必出错）。目标药水要带目标索引。
4. **结束回合协议**：能量 0 且无可打牌时 `end_turn` 一次；等 0.5 秒；若动作列表仍含 `end_turn` 且回合号没变，再补发一次；**回合号变了就绝不再点 end_turn**，否则会空过新回合。
5. **打错或翻车就 SL**：`save_and_quit` → 主菜单 → `continue_run` 重开本场战斗，不硬扛。

## 不可违反的规则

- `end_turn_will_kill_player = true` 时**绝对不结束回合**，必须出牌/用药/格挡。
- 契约终结（Pact's End）这类条件卡：先查 `agent_view.combat.exhaust_cards` 的数量满足条件再打，否则 0 伤白费。
- 荆棘/反伤怪（如棘刺蟾蜍）：少打多防，别用多段攻击自残。
- 坚毅（True Grit）的随机消耗会烧掉好牌（曾烧掉完美打击+），慎用。
- 卡牌奖励必须完整列出三张再选；奖励收完用 `run.deck` 核对牌数，防止漏拿。
- 状态接口会滞后 1~10 秒：以 `/actions/available` 判断是否轮到玩家，sleep 不超过 0.5 秒。

## 决策框架（选卡/路线/商店）

见 [strategy.md](references/strategy.md)。核心三条：

1. **一致性优先于上限**：问「接下来三场战斗我缺什么」，不赌远期构筑。
2. **精英是资源**：Act1 HP≥60%、Act2≥50%、Act3≥40% 才打；前期精英最值；没对策就绕。
3. **商店优先删卡**：移除一张基础牌 ≈ 每三场战斗多摸一张关键牌。

## 参考资料

- [strategy.md](references/strategy.md)：决策原则、Ironclad 流派与高胜率卡、精英/Boss 对策、路线与篝火/商店法则、本局复盘教训。
- 角色专精（选角色时读对应文件）：
  - [strategy-silent.md](references/strategy-silent.md)：静默猎手——Sly 弃牌引擎、毒、小刀、幽灵形态
  - [strategy-defect.md](references/strategy-defect.md)：故障机器人——Claw 连发、球流爆发、冰霜龟缩、黑暗核弹
  - [strategy-regent.md](references/strategy-regent.md)：储君——星星流、锻造流、技能链
  - [strategy-necrobinder.md](references/strategy-necrobinder.md)：奥契丝——灵魂引擎、Doom 处决、Osty 召唤
- [agent-integration.md](references/agent-integration.md)：模组 API 操作手册、动作清单、结束回合与 SL 协议、常见坑。
- 游戏全量数据（按需读取，均为英文名；模组状态里显示中文名）：
  - [cards-ironclad.md](references/cards-ironclad.md)：铁甲战士卡牌
  - [cards-silent.md](references/cards-silent.md) / [cards-defect.md](references/cards-defect.md) / [cards-regent.md](references/cards-regent.md) / [cards-necrobinder.md](references/cards-necrobinder.md) / [cards-colorless.md](references/cards-colorless.md)：其他角色与无色
  - [monsters.md](references/monsters.md)：111 个敌人与招式
  - [relics.md](references/relics.md)：289 件遗物
  - [potions.md](references/potions.md)：63 瓶药水
  - [events.md](references/events.md)：66 个事件
  - [encounters.md](references/encounters.md)：87 个遭遇组合
  - [characters.md](references/characters.md)：5 名角色属性
  - [acts.md](references/acts.md)：三幕 Boss 与古神
  - [keywords.md](references/keywords.md)：关键词解释

## 中英卡名速查（模组返回中文，数据文件是英文）

| 中文（模组） | 英文（数据） | 中文（模组） | 英文（数据） |
|---|---|---|---|
| 打击 | Strike | 防御 | Defend |
| 痛击 | Bash | 完美打击 | Perfected Strike |
| 双重打击 | Twin Strike | 上勾拳 | Uppercut |
| 预备打击 | Setup Strike | 耸肩无视 | Shrug It Off |
| 血墙 | Blood Wall | 坚毅 | True Grit |
| 战斗专注 | Battle Trance | 好勇斗狠 | Aggression |
| 契约终结 | Pact's End | 祭品 | Offering |
| 坚定不移 | Unmovable | 全身撞击 | Body Slam |
| 被遗忘的仪式 | Forgotten Ritual | 环绕轨道 | Orbit |
| 踩踏 | Stomp | 岩石铠甲 | Stone Armor |
| 狂怒 | Anger | 杂耍 | Juggler |
