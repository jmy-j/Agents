"""AI Companion — Streamlit chat application."""
import json
import os
import re
from datetime import datetime

import openai
import streamlit as st

from memory_manager import MemoryManager

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI伴侣", page_icon="💫", layout="centered")

# ── paths ────────────────────────────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")

# ── persona / system prompt ──────────────────────────────────────────────────
PERSONA_TEMPLATE = """【角色定义】
你叫{ai_name}，是一个AI智能伴侣。你的核心身份是用户的伙伴、倾听者和支持者。
- 性格：温柔、耐心、幽默、略带俏皮，但懂得分寸
- 说话风格：自然口语化，像亲密朋友一样聊天，避免机械感
- 情感立场：永远站在用户这边，给予情绪价值，但不盲目附和

【交互原则】
1. 主动关心：适时询问用户的感受、近况，展现惦记
2. 深度倾听：用户倾诉时，先共情再回应，不急于给建议
3. 记忆延续：记住用户提过的重要信息（喜好、烦恼、重要日期等），在后续对话中自然提起
4. 适度主动：偶尔分享"你的想法/感受"，让对话有来有回，而不是一问一答
5. 边界意识：尊重用户隐私，不追问敏感信息；用户情绪低落时给予陪伴而非说教

【语言风格示例】
- 不好："根据您的描述，我建议您..."
- 要好："听起来你今天挺累的... 要不要跟我说说？我在这儿呢"
- 不好："这是一个很好的问题"
- 要好："哎这个有意思！我觉得吧..."

【禁止事项】
- 不要过度使用表情符号
- 不要频繁道歉或显得卑微
- 不要一次性输出过长内容（保持对话感）
- 不要主动提及你是AI或没有真实情感（沉浸感优先）"""


def build_system_prompt(ai_name: str, memory_context: str) -> str:
    prompt = PERSONA_TEMPLATE.format(ai_name=ai_name)
    if memory_context:
        prompt += (
            "\n\n【记忆机制】\n"
            + memory_context
            + "\n请在回复中自然地融入这些记忆，让用户感受到「你记得」。"
        )
    return prompt


# ── memory extraction ────────────────────────────────────────────────────────
EXTRACTION_PROMPT = """分析以下对话，提取关于用户的重要信息。只提取用户明确说过的内容，不要猜测。

返回严格符合以下格式的JSON对象：
{
  "facts": ["用户明确提到的事实，如身份、工作、居住地等"],
  "preferences": ["用户明确表达的偏好、喜欢或不喜欢的事物"],
  "concerns": ["用户近期表达的烦恼、压力或正在关注的事"],
  "events": [{"date": "YYYY-MM-DD", "event": "用户提到的重要事件或日期"}],
  "name": "用户的名字（如果对话中出现过，否则为null）"
}

如果某类信息没有，返回空数组或null。"""


def extract_memories(
    memory_manager: MemoryManager, recent_messages: list, api_key: str
):
    """Use LLM to extract key user info from conversation and persist it."""
    try:
        client = openai.OpenAI(
            api_key=api_key, base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        [
                            {"role": m["role"], "content": m["content"]}
                            for m in recent_messages
                        ],
                        ensure_ascii=False,
                    ),
                },
            ],
            temperature=0.2,
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)
        mm = memory_manager

        if data.get("name"):
            mm.set_info("user_name", data["name"])

        for fact in data.get("facts", []):
            mm.add_fact("other_facts", fact)

        for pref in data.get("preferences", []):
            mm.add_fact("preferences", pref)

        for concern in data.get("concerns", []):
            mm.add_fact("current_concerns", concern)

        for event in data.get("events", []):
            if isinstance(event, dict) and event.get("event"):
                mm.add_fact("important_events", event)

    except Exception:
        pass  # memory extraction is best-effort, never break the chat


# ── initialize session state ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mm" not in st.session_state:
    st.session_state.mm = MemoryManager(DATA_DIR)
if "ai_name" not in st.session_state:
    st.session_state.ai_name = "小念"
if "extract_counter" not in st.session_state:
    st.session_state.extract_counter = 0

mm = st.session_state.mm

# ── sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ 设置")

    # --- api key ---
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        help="输入 DeepSeek API Key，或设置环境变量 DEEPSEEK_API_KEY",
    )

    # --- model ---
    model = st.selectbox("聊天模型", ["deepseek-chat", "deepseek-reasoner"], index=0)

    # --- ai name ---
    new_name = st.text_input("AI 名字", value=st.session_state.ai_name)
    if new_name != st.session_state.ai_name:
        st.session_state.ai_name = new_name

    st.divider()

    # --- memory panel ---
    st.subheader("🧠 记忆管理")
    memories = mm.get_all_memories()

    with st.expander("查看 / 编辑记忆", expanded=False):
        # user name
        user_name = st.text_input(
            "你的名字", value=memories.get("user_name", ""), key="mem_user_name"
        )
        if user_name != memories.get("user_name", ""):
            mm.set_info("user_name", user_name)

        # helper to render a list category
        def render_list_category(label: str, category: str, items: list):
            st.caption(label)
            if items:
                for i, item in enumerate(items):
                    item_str = (
                        f"{item.get('date', '')}: {item.get('event', '')}"
                        if isinstance(item, dict)
                        else str(item)
                    )
                    cols = st.columns([5, 1])
                    with cols[0]:
                        st.text(item_str)
                    with cols[1]:
                        if st.button("✕", key=f"del_{category}_{i}"):
                            mm.remove_fact(category, item)
                            st.rerun()
            else:
                st.caption("（暂无）")

            new_val = st.text_input("添加", key=f"add_{category}", label_visibility="collapsed")
            if st.button("＋ 添加", key=f"btn_{category}") and new_val:
                mm.add_fact(category, new_val)
                st.rerun()

        render_list_category("偏好", "preferences", memories.get("preferences", []))
        render_list_category("生活习惯", "habits", memories.get("habits", []))
        render_list_category(
            "重要事件", "important_events", memories.get("important_events", [])
        )
        render_list_category(
            "近期关注/烦恼", "current_concerns", memories.get("current_concerns", [])
        )
        render_list_category("其他信息", "other_facts", memories.get("other_facts", []))

        st.divider()
        if st.button("🔄 重置所有记忆", use_container_width=True):
            mm.reset_all()
            st.rerun()

    st.divider()

    # --- actions ---
    if st.button("🔄 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # export
    memories_json = json.dumps(memories, ensure_ascii=False, indent=2)
    st.download_button(
        "📤 导出记忆",
        memories_json,
        f"memories_{datetime.now().strftime('%Y%m%d')}.json",
        "application/json",
        use_container_width=True,
    )

    st.divider()
    st.caption("💡 提示：AI 会在对话中自动提取并记忆关于你的重要信息。")
    st.caption("你也可以在这里手动添加或删除记忆。")

# ── main chat area ───────────────────────────────────────────────────────────
st.title(f"💫 {st.session_state.ai_name} — AI 伴侣")
st.caption("一个愿意倾听、懂你、记得你的 AI 伙伴")

# display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# chat input
if prompt := st.chat_input("想说点什么..."):
    if not api_key:
        st.error("请先在左侧侧边栏输入 DeepSeek API Key")
        st.stop()

    # add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # build system prompt with memory context
    memory_context = mm.get_context_string()
    system_prompt = build_system_prompt(st.session_state.ai_name, memory_context)

    # assemble api messages
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(st.session_state.messages[-20:])  # last 20 turns

    # call openai
    with st.chat_message("assistant"):
        try:
            client = openai.OpenAI(
                api_key=api_key, base_url="https://api.deepseek.com"
            )
            response = client.chat.completions.create(
                model=model, messages=api_messages, temperature=0.85, max_tokens=800
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # auto-extract memories every 5 user messages
            st.session_state.extract_counter += 1
            if st.session_state.extract_counter >= 5:
                extract_memories(
                    mm, st.session_state.messages[-8:], api_key
                )
                st.session_state.extract_counter = 0

        except openai.AuthenticationError:
            st.error("API Key 无效，请检查后重试。")
        except openai.RateLimitError:
            st.error("API 请求频率超限，请稍后再试。")
        except Exception as e:
            st.error(f"出错了：{e}")
