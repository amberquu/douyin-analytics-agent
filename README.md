# 🎬 Douyin Analytics Agent

A conversational AI agent for Douyin (Chinese TikTok) content creators — chat with it to get account retrospectives, video performance breakdowns, and content strategy advice, powered by Google Gemini.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini_API-Flash-orange?style=flat&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## ✨ Features

- **Conversational interface** — web-based chat UI, ask anything about your content strategy
- **Live data scraping** — connects to your logged-in Chrome browser via CDP to pull real-time video stats (likes, comments, shares, saves) directly from your Douyin profile
- **Retrospective analysis** — auto-generates structured reports: top/bottom performers, tag effectiveness, engagement ratios, posting patterns
- **Personalised advice** — the agent knows your account context and gives specific, actionable recommendations (not generic tips)
- **Function calling** — Gemini decides when to trigger data scraping vs. answer from context, no manual switching needed

---

## 🖥️ Demo

```
You:   帮我复盘一下最近的数据

Agent: 正在抓取你的抖音主页数据...
       ✅ 成功抓取 30 条视频

       📊 账号概览
       ─────────────────────────────
       粉丝：2,365 | 总获赞：30.2万 | 赞粉比：127:1

       🔥 TOP 内容（近期）
       1. 「打版现场」— 3.5万赞 · 分享率 9.1%
       2. 「想念变成空气」— 3.2万赞 · 收藏率 6.7%

       💡 建议：偶像追星类内容平均是情感类的 6x，
          下次可以尝试「偶像 + 情感共鸣」混合切入...
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Chrome (with remote debugging enabled)
- [web-access Claude Code skill](https://github.com/eze-is/web-access) installed (for CDP proxy)
- A Gemini API key → [get one here](https://aistudio.google.com/app/apikey)

### Installation

```bash
git clone https://github.com/amberquu/douyin-analytics-agent
cd douyin-analytics-agent
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` with your own values:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here
DOUYIN_PROFILE_URL=https://www.douyin.com/user/your_uid_here
DOUYIN_ACCOUNT_NAME=Your Account Name

# Optional — give the agent context about your content direction
ACCOUNT_NOTES=Content direction: lifestyle vlog, main tags #xxx, 5k followers, 200k total likes
```

To find your `DOUYIN_PROFILE_URL`: open your Douyin profile in Chrome and copy the full URL from the address bar.

### Enable Chrome Remote Debugging

In Chrome's address bar, open:
```
chrome://inspect/#devices
```
Check **"Allow remote debugging for this browser instance"** and log in to Douyin.

### Run

```bash
python app.py
```

Open **http://localhost:5001** in your browser.

---

## 💬 Usage

| What you type | What the agent does |
|--------------|---------------------|
| `帮我复盘` / `分析数据` | Scrapes your profile → generates full retrospective report |
| `最近发什么内容好？` | Gives content strategy advice based on your account context |
| `我的账号有什么问题？` | Account health diagnosis |
| `#xxx 标签效果怎么样？` | Tag-level performance breakdown |
| Any free-form question | Conversational strategy advice |

---

## 🏗️ Architecture

```
Browser (localhost:5001)
    │
    ▼
Flask Backend (app.py)
    │  ├── Gemini API (gemini-flash) — conversation + function calling
    │  └── scrape_douyin() tool
    │           │
    │           ▼
    │      CDP Proxy (:3456)  ←── web-access skill
    │           │
    │           ▼
    │      Chrome (logged-in, your Douyin session)
    │           │
    │           ▼
    │      douyin.com/user/your_profile
    ▼
Structured data → Gemini → Analysis report
```

---

## 📁 Project Structure

```
douyin-analytics-agent/
├── app.py              # Flask app + Gemini function calling
├── templates/
│   └── index.html      # Chat UI
├── requirements.txt
├── .env.example        # Config template
└── .gitignore
```

---

## ⚠️ Notes

- Data scraping runs inside **your own Chrome session** — no credentials are sent anywhere
- The agent only reads public-facing page data (same as what you see when logged in)
- Avoid running too frequently to prevent platform rate limiting
- `.env` is gitignored — your API key and account info stay local

---

## 🛠️ Tech Stack

- **Backend**: Python · Flask
- **AI**: Google Gemini API (`google-genai`) with function calling
- **Scraping**: Chrome DevTools Protocol (CDP) via [web-access](https://github.com/eze-is/web-access)
- **Frontend**: Vanilla HTML/CSS/JS · marked.js

---

## License

MIT
