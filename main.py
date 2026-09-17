import os
import json
import re
from dotenv import load_dotenv

from call_llm import CallParameters, call_llm
from skill.set_hvac.schemas import SET_HVAC_SCHEMAS
from skill.set_window.schemas import SET_WINDOW_SCHEMAS
from skill.set_hvac.call_car import set_hvac
from skill.set_window.call_car import set_window

script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
print(f"加载'.env': {load_dotenv(env_path)}")

# True=联网调用 DeepSeek，False=离线模式（本地规则匹配）
USE_ONLINE_LLM: bool = True

api_key = os.getenv("DEEPSEEK_OPENAI_API_KEY")
base_url = "https://api.deepseek.com"

TOOLS = [SET_HVAC_SCHEMAS, SET_WINDOW_SCHEMAS]
TOOL_MAP = {
    "set_hvac": set_hvac,
    "set_window": set_window,
}

WINDOW_KEYWORDS = {
    "主驾": "front_left", "驾驶员": "front_left", "左前": "front_left",
    "副驾": "front_right", "右前": "front_right",
    "左后": "rear_left", "后排左": "rear_left",
    "右后": "rear_right", "后排右": "rear_right",
}


def _offline_handle(user_input: str) -> tuple[str, list]:
    """离线模式：不调用 LLM，用简单规则匹配执行车控工具。
    返回 (回复文本, 动作列表)。"""
    text = user_input
    actions = []

    # 温度
    temp_match = re.search(r"(\d{1,2})\s*度", text)
    if temp_match:
        temp = int(temp_match.group(1))
        actions.append({"tool": "set_hvac", "args": {"temperature": temp},
                        "result": set_hvac(temperature=temp)})

    # 空调开关：先匹配明确短语，再兜底动词
    open_ac_phrases = ("开空调", "打开空调", "开启空调", "空调打开", "把空调打开")
    close_ac_phrases = ("关空调", "关闭空调", "空调关", "把空调关了", "空调关一下", "把空调关掉")
    is_open_ac = any(p in text for p in open_ac_phrases)
    is_close_ac = any(p in text for p in close_ac_phrases)

    if not is_open_ac and not is_close_ac and "空调" in text:
        has_open = any(v in text for v in ("打开", "开启", "开"))
        has_close = any(v in text for v in ("关闭", "关上", "关掉", "关"))
        if has_close and not has_open:
            is_close_ac = True
        elif has_open and not has_close:
            is_open_ac = True

    if is_open_ac:
        actions.append({"tool": "set_hvac", "args": {"power": True},
                        "result": set_hvac(power=True)})
    elif is_close_ac:
        actions.append({"tool": "set_hvac", "args": {"power": False},
                        "result": set_hvac(power=False)})
    elif temp_match and not is_close_ac:
        # 调温度时未明确关空调，默认打开
        actions.insert(0, {"tool": "set_hvac", "args": {"power": True},
                           "result": set_hvac(power=True)})

    # 车窗位置
    if "所有" in text or "全部" in text:
        position = "all"
    else:
        position = None
        for keyword, key in WINDOW_KEYWORDS.items():
            if keyword in text:
                position = key
                break

    # 车窗开关：更口语化
    if position:
        open_w_phrases = ("打开", "开", "升起", "摇上")
        close_w_phrases = ("关闭", "关上", "关掉", "关", "降下", "摇下")
        is_open_w = any(p in text for p in open_w_phrases) and not any(p in text for p in close_w_phrases)
        is_close_w = any(p in text for p in close_w_phrases) and not any(p in text for p in open_w_phrases)

        if not is_open_w and not is_close_w:
            # 只说位置没给动词，默认打开
            is_open_w = True

        if is_open_w:
            actions.append({"tool": "set_window", "args": {"position": position, "open": True},
                            "result": set_window(position=position, open=True)})
        elif is_close_w:
            actions.append({"tool": "set_window", "args": {"position": position, "open": False},
                            "result": set_window(position=position, open=False)})

    if actions:
        say = f"已执行：{', '.join(a['tool'] for a in actions)}"
    else:
        say = "未识别到本地支持的车控指令。"

    return say, actions


def cloud_handle(payload: str = None) -> str:
    data = json.loads(payload)
    user_input = data.get("user_input", "")
    car_state = data.get("car_state", {})

    # 优先走离线规则库，命中则直接返回
    offline_say, offline_actions = _offline_handle(user_input)
    if offline_actions:
        return json.dumps({"say": offline_say, "actions": offline_actions}, ensure_ascii=False)

    # 离线模式且本地未命中：提示切在线
    if not USE_ONLINE_LLM:
        return json.dumps(
            {"say": "离线模式仅支持基础车控指令（空调/车窗），请切换到在线模式使用自然语言。", "actions": []},
            ensure_ascii=False,
        )

    # 在线模式且本地未命中：走 LLM
    system_prompt = (
        "你是车载语音助手。根据用户指令调用工具控制车辆。\n"
        f"当前车辆状态：{json.dumps(car_state, ensure_ascii=False)}\n"
        "如果用户指令涉及多个操作，请一次性调用多个工具。"
        "调用完工具后，请用一句话告知用户执行结果。"
    )

    params = CallParameters(
        api_key=api_key,
        base_url=base_url,
        model="deepseek-flash",
        system_prompt=system_prompt,
        user_input=user_input,
        tools=TOOLS,
        tool_choice="auto",
        tool_map=TOOL_MAP,
        stream=False,
        context_mode="recent",
        context_window=2,
    )
    return call_llm(params)
