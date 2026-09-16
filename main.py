import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from skill.set_hvac.schemas import SET_HVAC_SCHEMAS
from skill.set_window.schemas import SET_WINDOW_SCHEMAS
from skill.set_hvac.call_car import set_hvac
from skill.set_window.call_car import set_window

script_dir = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(script_dir, ".env")
print(f"加载'.env': {load_dotenv(env_path)}")

api_key = os.getenv("DEEPSEEK_OPENAI_API_KEY")
base_url = "https://api.deepseek.com"
client = OpenAI(api_key=api_key, base_url=base_url)

TOOLS = [SET_HVAC_SCHEMAS, SET_WINDOW_SCHEMAS]
TOOL_MAP = {
    "set_hvac": set_hvac,
    "set_window": set_window,
}


class ChatSession:
    def __init__(self, content: str = ""):
        print("messages 已初始化并写入 system")
        self.messages = []
        self.add_system(content=content)

    def add_system(self, content: str = ""):
        print(f"add_system 被调用，并写入 {content}")
        self.messages.append({"role": "system", "content": content})

    def add_user(self, content: str = ""):
        print(f"add_user 被调用，并写入 {content}")
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str = "", msg_dict: dict = None):
        """content 和 msg_dict 选一个传入。若传入 msg_dict 则优先使用。"""
        if msg_dict is None:
            print(f"add_assistant 被调用，并写入 {content}")
            self.messages.append({"role": "assistant", "content": content})
        else:
            print(f"add_assistant 被调用，并写入 {msg_dict}")
            self.messages.append(msg_dict)

    def add_tools(self, tool_call_id: str = "", content: str = ""):
        print(f"add_tools 被调用，并写入 {tool_call_id}, {content}")
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })


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

    session = ChatSession(system_prompt)
    session.add_user(user_input)

    final_reply = ""
    actions = []

    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=session.messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            final_reply = msg.content or ""
            session.add_assistant(content=final_reply)
            break

        session.add_assistant(msg_dict=msg.model_dump())
        for tc in msg.tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"工具调用：{func_name}({args})")
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**args)
            else:
                result = {"status": "error", "message": f"未知工具：{func_name}"}
            actions.append({"tool": func_name, "args": args, "result": result})
            session.add_tools(
                tool_call_id=tc.id,
                content=json.dumps(result, ensure_ascii=False),
            )

    return json.dumps({"say": final_reply, "actions": actions}, ensure_ascii=False)
