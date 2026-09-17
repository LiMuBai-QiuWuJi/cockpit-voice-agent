import os
import json
from dotenv import load_dotenv

from call_llm import CallParameters, call_llm
from skill.set_hvac.schemas import SET_HVAC_SCHEMAS
from skill.set_window.schemas import SET_WINDOW_SCHEMAS
from skill.set_hvac.call_car import set_hvac
from skill.set_window.call_car import set_window

script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
print(f"加载'.env': {load_dotenv(env_path)}")

api_key = os.getenv("DEEPSEEK_OPENAI_API_KEY")
base_url = "https://api.deepseek.com"

TOOLS = [SET_HVAC_SCHEMAS, SET_WINDOW_SCHEMAS]
TOOL_MAP = {
    "set_hvac": set_hvac,
    "set_window": set_window,
}


def cloud_handle(payload: str = None) -> str:
    data = json.loads(payload)
    user_input = data.get("user_input", "")
    car_state = data.get("car_state", {})

    system_prompt = (
        "你是车载语音助手。根据用户指令调用工具控制车辆。\n"
        f"当前车辆状态：{json.dumps(car_state, ensure_ascii=False)}\n"
        "如果用户指令涉及多个操作，请一次性调用多个工具。"
        "调用完工具后，请用一句话告知用户执行结果。"
    )

    params = (
        CallParameters()
        .with_api_key(api_key)
        .with_base_url(base_url)
        .with_system_prompt(system_prompt)
        .with_user_input(user_input)
        .with_tools(TOOLS)
        .with_tool_map(TOOL_MAP)
    )

    return call_llm(params)
