# CCBot

通过 Telegram 远程控制运行在 tmux 里的 Claude Code 或 Codex 会话。

https://github.com/user-attachments/assets/15ffb38e-5eb9-4720-93b9-412e4961dc93

## 它是什么

CCBot 本质上是 tmux 之上的一个 Telegram 控制层。

- Claude Code 或 Codex 进程继续跑在 tmux 窗口里
- 你通过 Telegram 看输出、发消息、下命令
- 随时可以用 `tmux attach` 回到终端

每个 Telegram 话题对应一个 tmux 窗口，以及一个 Claude Code 或 Codex 会话。

## 功能

- 一个话题对应一个会话
- 实时回复和状态更新
- 可以从 Telegram 恢复旧会话
- 支持语音转文字
- 支持交互式按钮
- 支持消息历史和截图
- 同时支持 Claude Code 和 Codex

## 前置要求

- `tmux`
- `claude` 或 `codex`
- 一个通过 [@BotFather](https://t.me/BotFather) 创建的 Telegram Bot

## 安装

### 从 GitHub 安装

```bash
uv tool install git+https://github.com/six-ddc/ccmux.git
```

或者：

```bash
pipx install git+https://github.com/six-ddc/ccmux.git
```

### 从源码安装

```bash
git clone https://github.com/six-ddc/ccmux.git
cd ccmux
uv sync
```

## 基本配置

创建 `~/.ccbot/.env`：

```ini
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_USERS=your_telegram_user_id
```

常用可选项：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `CCBOT_RUNTIME` | `claude` | 新窗口默认启动 `claude` 还是 `codex` |
| `CLAUDE_COMMAND` | `claude` | Claude Code 命令 |
| `CODEX_COMMAND` | `codex --no-alt-screen` | Codex 命令 |
| `TMUX_SESSION_NAME` | `ccbot` | tmux 会话名 |
| `OPENAI_API_KEY` | _(空)_ | 只在语音转文字时需要 |

如果你是在没有交互终端的 VPS 上运行，Claude Code 命令可以考虑设置得更少交互一些，例如：

```bash
CLAUDE_COMMAND=IS_SANDBOX=1 claude --dangerously-skip-permissions
```

## 安装 Hook

执行：

```bash
ccbot hook --install
```

如果你想显式把 Claude Code 和 Codex 两边的 hook 都装上：

```bash
ccbot hook --install --run all
```

Codex 在 `v0.114.0` 里仍然把 hooks 当实验特性。如果你是在 CCBot 之外手动启动 Codex，请自己加上：

```bash
codex -c features.codex_hooks=true
```

## 启动 Bot

```bash
ccbot
```

如果你是从源码运行：

```bash
uv run ccbot
```

如果你只想让这一次进程使用 Codex：

```bash
ccbot --run codex
```

`ccbot --run claude|codex` 只影响当前这次启动，不会改写 `.env`。

## 日常使用

1. 在 Telegram 群里创建一个新话题
2. 在这个话题里发送任意消息
3. 选择项目目录
4. 选择恢复旧会话或新开会话
5. 之后继续在这个话题里聊天

文字和语音都会转发到绑定的 Claude Code 或 Codex 会话。关闭话题时，
对应的 tmux 窗口也会一起关闭。

## 常用命令

| 命令 | 说明 |
| --- | --- |
| `/start` | 显示欢迎消息 |
| `/history` | 查看当前话题的消息历史 |
| `/screenshot` | 截图当前终端 |
| `/esc` | 发送 Escape 中断当前会话 |

大多数其他 `/...` 命令也会直接转发给当前话题对应的 Claude Code 或 Codex，
例如 `/clear`、`/compact`、`/cost`、`/review`。

## 手动使用 tmux

如果你想自己先开窗口：

```bash
tmux attach -t ccbot
tmux new-window -n myproject -c ~/Code/myproject
claude
```

如果你用的是 Codex：

```bash
tmux attach -t ccbot
tmux new-window -n myproject -c ~/Code/myproject
codex --no-alt-screen --enable codex_hooks
```
