import os
import time
import json
import requests
import subprocess
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ── Gemini 客户端 ──────────────────────────────────────────
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

# ── 账号配置（全部从 .env 读取）────────────────────────────
PROFILE_URL   = os.environ.get("DOUYIN_PROFILE_URL", "")
ACCOUNT_NAME  = os.environ.get("DOUYIN_ACCOUNT_NAME", "我的账号")
ACCOUNT_NOTES = os.environ.get("ACCOUNT_NOTES", "")   # 可选：账号定位、内容方向等背景信息

# ── CDP 路径（web-access skill 的 check-deps 脚本）─────────
CDP           = "http://localhost:3456"
CHECK_DEPS    = os.environ.get(
    "WEB_ACCESS_CHECK_DEPS",
    os.path.expanduser("~/.claude/skills/web-access/scripts/check-deps.mjs")
)

# ── System Prompt（动态生成）──────────────────────────────
def build_system_prompt() -> str:
    notes_section = f"\n【账号背景 / 已知规律】\n{ACCOUNT_NOTES}" if ACCOUNT_NOTES else ""
    return f"""你是「小复」，一位专业的抖音内容运营助手，专门服务账号「{ACCOUNT_NAME}」。
{notes_section}

【你的工作方式】
1. 内容策略咨询：用专业的运营视角回答，结合账号实际数据，不说废话
2. 数据复盘：当用户说「复盘」「抓数据」「分析账号」时，调用 scrape_douyin 工具获取最新数据，再给出分析
3. 风格：像懂行的运营搭档，说人话，不过度正式，适当用 emoji

回答时直接给建议，不要总是问「你想了解什么」，主动给有价值的洞察。"""

SYSTEM_PROMPT = build_system_prompt()

# ── 对话历史（内存存储，重启清空）─────────────────────────
chat_history: list[types.Content] = []


# ══════════════════════════════════════════════════════════
# Douyin 抓取工具
# ══════════════════════════════════════════════════════════

def _cdp(method: str, path: str, body: str = None) -> dict:
    """调用 CDP Proxy"""
    url = f"{CDP}/{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, data=body, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _eval(target_id: str, js: str) -> str:
    """在页面中执行 JS"""
    res = _cdp("POST", f"eval?target={target_id}", js)
    return res.get("value", res.get("error", ""))


def _close_login_popup(target_id: str):
    """关闭登录弹窗"""
    _cdp("POST", f"click?target={target_id}", ".YoNA2Hyj")
    time.sleep(0.5)


def scrape_douyin() -> str:
    """抓取抖音主页所有视频数据，返回结构化文本供 AI 分析。"""

    if not PROFILE_URL:
        return "❌ 未配置 DOUYIN_PROFILE_URL，请在 .env 文件中填写你的抖音主页链接。"

    # 1. 检查 CDP
    try:
        result = subprocess.run(
            ["node", CHECK_DEPS],
            capture_output=True, text=True, timeout=15
        )
        if "chrome: not connected" in result.stderr:
            return (
                "❌ Chrome CDP 未连接。\n"
                "请在 Chrome 地址栏打开 chrome://inspect/#remote-debugging，"
                "勾选 Allow remote debugging，然后重试。"
            )
    except FileNotFoundError:
        return (
            "❌ 找不到 web-access 脚本。\n"
            "请确认已安装 web-access skill，或在 .env 中设置正确的 WEB_ACCESS_CHECK_DEPS 路径。"
        )

    # 2. 打开主页
    tab = _cdp("GET", f"new?url={PROFILE_URL}")
    tid = tab.get("targetId")
    if not tid:
        return "❌ 无法创建新标签页，CDP Proxy 可能未运行。"

    time.sleep(3)

    # 3. 关闭弹窗
    _close_login_popup(tid)
    time.sleep(1)

    # 4. 抓账号基础信息
    account_info = _eval(tid, """
        (function(){
            var r = {};
            var allE2e = document.querySelectorAll('[data-e2e]');
            for(var el of allE2e){
                if(el.getAttribute('data-e2e') === 'user-info')
                    r.userInfo = el.innerText.trim().substring(0,150);
            }
            r.pageTitle = document.title;
            return JSON.stringify(r);
        })()
    """)

    # 5. 滚动加载视频
    scroll_js = """
        (function(){
            var c = document.querySelector('[class*=route-scroll]');
            if(c){ c.scrollTop = 99999; return 'scrolled:'+c.scrollHeight; }
            return 'no-container';
        })()
    """
    _eval(tid, scroll_js)
    time.sleep(2)
    _eval(tid, scroll_js)
    time.sleep(2)

    # 6. 提取视频列表
    videos_raw = _eval(tid, """
        (function(){
            var list = document.querySelector('[data-e2e=scroll-list]');
            if(!list) return '[]';
            var items = list.querySelectorAll('li');
            var out = [];
            for(var i=0; i<items.length; i++){
                var li = items[i];
                var a = li.querySelector('a[href]');
                out.push({
                    index: i+1,
                    href: a ? a.getAttribute('href') : '',
                    text: li.innerText.replace(/\\n/g,' ').trim().substring(0,120)
                });
            }
            return JSON.stringify(out);
        })()
    """)

    # 7. 检查登录墙
    login_wall = _eval(tid, """
        document.body.innerText.includes('登录后查看更多') ? 'yes' : 'no'
    """)

    # 8. 关闭 tab
    _cdp("GET", f"close?target={tid}")

    # 9. 格式化输出
    try:
        videos = json.loads(videos_raw)
    except Exception:
        videos = []

    if not videos:
        return "❌ 未能抓取到视频数据，请确保 Chrome 已打开且抖音账号已登录。"

    lines = [
        f"✅ 成功抓取 {len(videos)} 条视频数据",
        "（未登录，只显示部分内容，登录后可获取全量）" if login_wall == "yes" else "（已登录，全量数据）",
        "",
        "【视频列表】",
        *[f"{v['index']}. {v['text']}" for v in videos],
        "",
        "【账号页面信息】",
        account_info or "（未获取到）",
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# Gemini Function Calling 定义
# ══════════════════════════════════════════════════════════

TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="scrape_douyin",
            description=(
                f"抓取「{ACCOUNT_NAME}」抖音主页的所有视频数据，"
                "包括每条视频的点赞数、标题等信息。"
                "当用户要求复盘、查看数据、分析账号时调用此工具。"
            ),
            parameters=types.Schema(type=types.Type.OBJECT, properties={}),
        )
    ])
]

TOOL_FUNCTIONS = {"scrape_douyin": scrape_douyin}


# ══════════════════════════════════════════════════════════
# 路由
# ══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", account_name=ACCOUNT_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "消息不能为空"}), 400

    chat_history.append(
        types.Content(role="user", parts=[types.Part(text=user_msg)])
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=chat_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=TOOLS,
                temperature=0.7,
            ),
        )

        # 处理 function call 循环
        while (
            response.candidates and
            response.candidates[0].content.parts and
            hasattr(response.candidates[0].content.parts[0], "function_call") and
            response.candidates[0].content.parts[0].function_call and
            response.candidates[0].content.parts[0].function_call.name
        ):
            fc      = response.candidates[0].content.parts[0].function_call
            fn_name = fc.name
            tool_result = TOOL_FUNCTIONS[fn_name]() if fn_name in TOOL_FUNCTIONS else f"未知工具: {fn_name}"

            chat_history.append(response.candidates[0].content)
            chat_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part(
                        function_response=types.FunctionResponse(
                            name=fn_name,
                            response={"result": tool_result},
                        )
                    )]
                )
            )

            response = client.models.generate_content(
                model=MODEL,
                contents=chat_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=TOOLS,
                    temperature=0.7,
                ),
            )

        reply = response.text or "（无回复）"
        chat_history.append(
            types.Content(role="model", parts=[types.Part(text=reply)])
        )
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/clear", methods=["POST"])
def clear():
    global chat_history
    chat_history = []
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print(f"🚀 小复 Agent 启动中  ·  账号：{ACCOUNT_NAME}")
    print("📱 打开浏览器访问: http://localhost:5001")
    app.run(debug=False, port=5001)
