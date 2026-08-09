# STS2 Climb Toolkit

与《杀戮尖塔 2》（Slay the Spire 2）的本地 mod「STS2 AI Agent」（`http://127.0.0.1:8080`）配合使用的爬塔辅助工具集，服务于 Codex 的 AI 爬塔工作流。

## 内容

- `sts2_helper.py` — STS2 AI Agent 本地 HTTP API 的轻量 Python 客户端（`GET /state`、`POST /action`），并带状态压缩视图。
- `sts2_walk.py` — 递归遍历 `/state` 返回结构，用于探查消耗牌堆等字段。
- `distill_sts2.py` — 从游戏解包数据（卡牌 / 敌人 / 遗物 / 药水等 JSON）蒸馏成 Markdown 知识库，输出到 Codex 的 `sts2-climber` skill 的 `references/` 目录。
- `GameStateService.cs` — 基于 STS2 AI Agent mod 提取研究的状态服务源码（C# / Godot），用于理解游戏内部状态结构。
- `sky_probe.mjs` / `work/cua-*.mjs` — 对 Codex 桌面版内置 CUA / Chrome 自动化能力的探测脚本（依赖本地内部路径，仅本机研究用）。
- `sts2_*.png` — 爬塔过程中的屏幕截图样本（已由 `.gitignore` 排除，不入库）。
- `skills/sts2-climber/` — Codex 的 `sts2-climber` skill 完整拷贝：爬塔知识库（卡牌 / 敌人 / 遗物 / 事件 / 路线与选卡策略）与实战操作手册，含历次爬塔复盘教训。
- `tools/sts2-ai-agent/STS2AIAgent.zip` — 「STS2 AI Agent」mod 的分发包（作者 CharTyr），新机器恢复时直接使用。

## 用法

```bash
# 请求当前游戏状态（需先启动游戏并加载 STS2 AI Agent mod）
python sts2_helper.py state

# 遍历状态结构中的消耗相关字段
python sts2_walk.py

# 从解包数据生成知识库（需先解包游戏数据，路径见脚本头部）
python distill_sts2.py
```

## 新机器恢复（开箱即用）

1. 安装游戏与 mod：把 `tools/sts2-ai-agent/STS2AIAgent.zip` 解压到游戏的 `Mods/` 目录（如 `D:\steam\steamapps\common\Slay the Spire 2\Mods\`），启动游戏后确认本地 HTTP 服务在 `http://127.0.0.1:8080`。
2. 安装 skill：把 `skills/sts2-climber/` 整个目录复制到 `C:\Users\Administrator\.codex\skills\sts2-climber`（或 `$CODEX_HOME/skills/`）。
3. 运行脚本：见上方用法；`sts2_helper.py` 仅依赖 Python 标准库。

## 说明

- 本仓库是个人爬塔工作流的工具与研究笔记，部分脚本依赖本机绝对路径与本地 mod 环境，不保证开箱即用。
- `GameStateService.cs` 与 `sky_probe.mjs` 涉及 mod 与桌面客户端内部实现，仅供研究，请遵守相关软件的许可与使用条款。
- `STS2AIAgent.zip` 版权归原作者 CharTyr 所有，本仓库仅作个人备份与恢复用途；如需分发请遵循原作者的许可条款。
- 本仓库只收录与《杀戮尖塔 2》爬塔相关的内容；人格配置、记忆库等个人资产不在本仓库内，请另行备份。
