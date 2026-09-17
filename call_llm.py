import json
from dataclasses import dataclass,field
from typing import Any, Callable
from openai import OpenAI


@dataclass
class CallParameters:
    api_key: str = ""
    base_url: str = ""

    system_prompt: str = ""
    user_input: str = ""

    model:str = ""
    max_tokens:int = 4096
    temperature:float = 0.4
    timeout:float = 3
    stream: bool = False
    tools: list[dict] = field(default_factory=list)
    tool_choice: str = "auto"

    tool_map: dict[str, Callable] = field(default_factory=dict)
    context_mode: str = "none"      
    """  none | recent | unlimited  \n无 | 最近 | 无限"""
    context_window: int = 0
    """  recent 模式时保留最近 N 轮  """


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


def call_llm(parameters: CallParameters) -> json:
    from openai.types.chat import ChatCompletion

    client = OpenAI(api_key=parameters.api_key, base_url=parameters.base_url)

    session = ChatSession(parameters.system_prompt)
    session.add_user(parameters.user_input)

    final_reply = ""
    actions = []

    while True:
        response:ChatCompletion = client.chat.completions.create(
            model=parameters.model,
            messages=session.messages,
            max_tokens=parameters.max_tokens,
            temperature=parameters.temperature,
            timeout=parameters.timeout,
            stream=parameters.stream,
            tools=parameters.tools,
            tool_choice=parameters.tool_choice
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
            if func_name in parameters.tool_map:
                result = parameters.tool_map[func_name](**args)
            else:
                result = {"status": "error", "message": f"未知工具：{func_name}"}
            actions.append({"tool": func_name, "args": args, "result": result})
            session.add_tools(
                tool_call_id=tc.id,
                content=json.dumps(result, ensure_ascii=False),
            )

    return json.dumps({"say": final_reply, "actions": actions}, ensure_ascii=False)
