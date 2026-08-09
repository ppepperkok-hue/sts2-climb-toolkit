# STS2 AI Agent 模组操作手册

## 接口

- `GET /health`：模组健康检查
- `GET /state`：完整状态
- `GET /actions/available`：当前合法动作（比 /state 更新快，判断轮次以它为准）
- `POST /action`：执行动作，JSON：`{action, card_index, target_index, option_index, command, client_context}`

## 关键状态字段

- `screen`：MAIN_MENU / CHARACTER_SELECT / MAP / COMBAT / REWARD / CARD_SELECTION / EVENT / REST / SHOP / CHEST / MODAL / GAME_OVER
- `available_actions`：本回合合法动作名
- `combat.hand[]`：手牌（`index` 是打出用的索引；每打一张后索引会变）
- `combat.enemies[]`：敌人 `current_hp`、`intent`、`intents[].total_damage`、`powers`
- `end_turn_will_kill_player` / `lethal_risks[]`：结束回合是否会死
- `run.deck[]`：验证牌组（奖励收完核对数量）
- `reward.rewards[]` / `card_options`：奖励清单与三选一
- `agent_view.combat.exhaust_cards[]`：**消耗牌堆**（契约终结条件看这里）
- `event/rest/shop/chest` 的 `options[]`：选项及索引

## 常用动作

- 地图：`choose_map_node`（option_index）
- 战斗：`play_card`（card_index + target_index）、`end_turn`、`use_potion`（需要目标时带 target_index）、`discard_potion`
- 奖励：`claim_reward`、`choose_reward_card`、`collect_rewards_and_proceed`、`skip_reward_cards`
- 选牌/升级/移除：`select_deck_card`（deck_upgrade_select / deck_card_select 用）
- 事件：`choose_event_option`；休息：`choose_rest_option`；商店：`open_shop_inventory` / `buy_card` / `buy_relic` / `buy_potion` / `remove_card_at_shop` / `close_shop_inventory`
- 宝箱：`open_chest` → `choose_treasure_relic` → `proceed`
- 弹窗：`confirm_modal` / `dismiss_modal`
- 主菜单：`continue_run` / `abandon_run`（有确认弹窗）/ `open_character_select` / `open_timeline` / `save_and_quit`

## 操作纪律（踩坑总结）

1. **每打一张牌都重新读手牌索引**。索引随出牌变化，连续盲打必出错。
2. **只执行 `available_actions` 里的动作**；409 说明动作当前不可用，先读状态再重试。
3. **结束回合协议**：能量 0 且手牌无可打 → `end_turn` 一次 → sleep 0.5s → 读 `available_actions`；仍含 `end_turn` 且回合号没变 → 补发；回合号变了 → 立刻出牌，绝不再点 end_turn。
4. **SL 重开**：打错牌/局面崩了 → `save_and_quit` → 主菜单 → `continue_run`，战斗从本房间起点重来。
5. **卡牌奖励先列全再选**：读 `card_options` 的三张（名称/费用/效果），说明理由再 `choose_reward_card`；收完用 `run.deck` 核对。
6. **药水目标**：目标型药水（易伤药水等）不带 target 会 409；先读 `potions[].target_type`。
7. **状态滞后**：`/state` 可能滞后 1~10 秒；`/actions/available` 是实时轮次判断；sleep 控制在 0.5 秒内。
8. **回合开始手牌可能为空显示**：等 0.5 秒重读，别把「读不到手牌」当成空过。
9. **过牌后必须重读手牌**：剑柄打击/剑柄打击+/燃烧契约+/劫掠/耸肩无视等任何抽牌打出后，先读一遍新手牌（看摸到了什么），再决定后续动作。新摸到的可能是关键格挡、斩杀或过牌，别拿着旧手牌继续打；尤其是「先过牌再决定」的顺序，抽牌结果没看之前不要提前定死本回合计划。
10. **战斗数值纪律**：
    - 每回合先读**敌方状态栏**（力量/易伤/虚弱/荆棘/硬化外壳/接续/沙坑等）和**己方状态栏**（力量/敏捷/覆甲/虚弱/污染/狱火等），把加成、减伤、反伤和上限机制全部算进每张牌的预期伤害与格挡，再定出牌顺序。
    - 注意伤害上限类机制：硬化外壳（每回合最多 20 伤）、难杀（单次最多 9 伤）、荆棘（每段反伤）——大数字会骗人，先看机制再打。
    - **算牌堆**：不仅要数抽牌堆/弃牌堆/手牌各剩几张，还要**读两堆的内容**（`agent_view.combat.draw_cards` / `discard_cards`）：知道血墙、完美打击、破击等关键牌还在抽牌堆里还是已进弃牌堆——决定下一摸能不能摸到、头槌/燃烧契约能从弃牌堆捞什么、洗牌后大概率抽到什么；战斗专注锁抽牌后，本回合别再指望任何抽牌。
    - 每次出牌前后重读状态，把状态栏数值变化（力量增减、易伤层数、沙坑倒计时）纳入下一张牌的判断。
    - **低血量自伤牌标红**：血量 ≤5 时，放血/血墙/御血术/内核加速副作用等一切自伤牌都要先确认卡名再打出；连续出牌必须逐张重读，禁止凭索引连打。实测教训：1 血时把放血当剑柄打出，自伤 3 点直接死亡。
