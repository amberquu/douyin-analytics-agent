# 🎬 Douyin Analytics Agent

**[English](#-english) | [中文](#-中文)**

---

## 🇬🇧 English

A conversational AI agent for Douyin (Chinese TikTok) content creators — chat with it to get account retrospectives, video performance breakdowns, and content strategy advice, powered by Google Gemini.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini_API-Flash-orange?style=flat&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

### ✨ Features

- **Conversational interface** — web-based chat UI, ask anything about your content strategy
- **Live data scraping** — connects to your logged-in Chrome browser via CDP to pull real-time video stats (likes, comments, shares, saves) directly from your Douyin profile
- **Retrospective analysis** — auto-generates structured reports: top/bottom performers, tag effectiveness, engagement ratios, posting patterns
- **Personalised advice** — the agent knows your account context and gives specific, actionable recommendations (not generic tips)
- **Function calling** — Gemini decides when to trigger data scraping vs. answer from context, no manual switching needed

### 🖥️ Demo

```
You:   帮我复盘一下最近的数据

Agent: 正在抓取你的抖音主页数据...
       ✅ 成功抓取 30 条视频

       📊 账号概览
       粉丝：2,365 | 总获赞：30.2万 | 赞粉比：127:1

       🔥 TOP 内容
       1. 「打版现场」— 3.5万赞 · 分享率 9.1%
       2. 「想念变成空气」— 3.2万赞 · 收藏率 6.7%

       💡 偶像追星类内容平均是情感类的 6x，
          下次可以尝试「偶像 + 情感共鸣」混合切入...
```

### 🚀 Quick Start

**Prerequisites**
- Python 3.10+
- Google Chrome (with remote debugging enabled)
- [web-access Claude Code skill](https://github.com/eze-is/web-access) installed (for CDP proxy)
- A Gemini API key → [get one here](https://aistudio.google.com/app/apikey)

**Installation**

```bash
git clone https://github.com/amberquu/douyin-analytics-agent
cd douyin-analytics-agent
pip install -r requirements.txt
cp .env.example .env   # then fill in your values
```

**Enable Chrome Remote Debugging**

Open `chrome://inspect/#devices` in Chrome and check **"Allow remote debugging"**, then log in to Douyin.

**Run**

```bash
python app.py
# Open http://localhost:5001
```

### ⚙️ Configuration (`.env`)

```env
GEMINI_API_KEY=your_key_here
DOUYIN_PROFILE_URL=https://www.douyin.com/user/your_uid
DOUYIN_ACCOUNT_NAME=Your Account Name
ACCOUNT_NOTES=Content direction, follower count, known patterns...  # optional
```

### 💬 Usage

| What you type | What the agent does |
|--------------|---------------------|
| `帮我复盘` / `分析数据` | Scrapes profile → full retrospective report |
| `最近发什么内容好？` | Content strategy advice |
| `我的账号有什么问题？` | Account health diagnosis |
| `#xxx 标签效果怎么样？` | Tag-level performance analysis |

### 🏗️ Architecture

```
Browser (localhost:5001)
    ↓
Flask Backend
    ├── Gemini API — conversation + function calling
    └── scrape_douyin() tool
              ↓
         CDP Proxy (:3456) ← web-access skill
              ↓
         Chrome (your logged-in Douyin session)
              ↓
         Structured data → Gemini → Analysis report
```

### 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python · Flask |
| AI | Google Gemini API · Function Calling |
| Scraping | Chrome DevTools Protocol (CDP) |
| Frontend | Vanilla JS · marked.js |

### ⚠️ Notes

- Scraping runs inside your own Chrome — no credentials sent anywhere
- `.env` is gitignored — API key and account info stay local
- Avoid running too frequently to prevent rate limiting

---

## 🇨🇳 中文

一个面向抖音创作者的对话式 AI 助手，接入你的抖音账号后，用聊天的方式就能拿到账号数据复盘报告和内容策略建议，底层由 Google Gemini 驱动。

### ✨ 功能亮点

- **网页对话界面** — 浏览器里直接聊，随时问内容策略问题
- **实时数据抓取** — 通过 CDP 连接你登录中的 Chrome，直接从抖音主页拉取视频数据（点赞、评论、收藏、分享）
- **自动复盘报告** — 生成结构化分析：爆款/低效内容对比、标签效果、互动率分析、发布规律
- **个性化建议** — Agent 了解你的账号定位，给的是针对你的具体建议，不是泛泛而谈
- **Function Calling** — Gemini 自动判断什么时候去抓数据、什么时候直接回答，不需要手动切换

### 🚀 快速开始

**环境要求**
- Python 3.10+
- Google Chrome（需开启远程调试）
- 安装 [web-access Claude Code skill](https://github.com/eze-is/web-access)（提供 CDP Proxy）
- Gemini API Key → [点此获取](https://aistudio.google.com/app/apikey)

**安装**

```bash
git clone https://github.com/amberquu/douyin-analytics-agent
cd douyin-analytics-agent
pip install -r requirements.txt
cp .env.example .env   # 然后填入你的配置
```

**开启 Chrome 远程调试**

在 Chrome 地址栏打开 `chrome://inspect/#devices`，勾选 **Allow remote debugging**，并在 Chrome 中登录抖音。

**启动**

```bash
python app.py
# 打开浏览器访问 http://localhost:5001
```

### ⚙️ 配置说明（`.env`）

```env
GEMINI_API_KEY=你的Key
DOUYIN_PROFILE_URL=https://www.douyin.com/user/你的UID
DOUYIN_ACCOUNT_NAME=账号名称
ACCOUNT_NOTES=内容方向、粉丝数量、已知规律等（可选）
```

> 如何找 `DOUYIN_PROFILE_URL`：在 Chrome 里打开你的抖音主页，复制地址栏链接即可。

### 💬 使用方式

| 你说什么 | Agent 会做什么 |
|---------|--------------|
| `帮我复盘` / `分析数据` | 抓取主页数据 → 生成完整复盘报告 |
| `最近发什么内容好？` | 根据账号情况给内容策略建议 |
| `我的账号有什么问题？` | 账号健康度诊断 |
| `#xxx 标签效果怎么样？` | 标签维度数据分析 |

### ⚠️ 注意事项

- 数据抓取在你自己的 Chrome 里进行，不会向外部发送任何账号凭证
- `.env` 文件在 `.gitignore` 里，API Key 和账号信息只存在于本地
- 不要过于频繁地调用，避免触发平台限流

### 📄 License

MIT
