import os
import json
from openai import OpenAI
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(script_dir,".env")
print(f"加载'.env': {load_dotenv(env_path)}")

api_key = os.getenv("DEEPSEEK_OPENAI_API_KEY")
base_url="https://api.deepseek.com"
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

class ChatSession:
    def __init__(self, content:str=""):
        print("mseeages 已初始化并写入system")
        self.messages = []
        self.add_system(content=content)

    def add_system(self, content:str=""):
        print(f"add_system 被调用，并写入{content}")
        self.messages.append({"role":"system","content":content})

    def add_user(self, content:str=""):
        print(f"add_user 被调用，并写入{content}")
        self.messages.append({"role":"user","content":content})

    def add_assistant(self, content:str="",msg_dict:dict={}):
        """content 和 msg_dict 选一个传入。若都传入则默认添加非空的msg_dict"""
        if len(msg_dict)==0:
            print(f"add_assistant 被调用，并写入{content}")
            self.messages.append({"role":"assistant","content":content})
        else:
            print(f"add_assistant 被调用，并写入{msg_dict}")
            self.messages.append(msg_dict)

    def add_tools(self, tool_call_id:str="", content:str=""):
        print(f"add_tools 被调用，并写入{tool_call_id} , {content}")
        self.messages.append({
            "role":"tool",
            "tool_call_id":tool_call_id,
            "content":content
        })

def call_llm(model:str="",user_input:str=""):

    response = client.chat.completions.create(
        model=model,
        messages=
    )

def main():
    print("车载语音中台已启动")
    session = ChatSession(
        "你是车载语音助手。根据用户指令调用工具控制车辆。\n"
        f"当前车辆状态：{json.dumps(car_state, ensure_ascii=False)}\n"
        "如果用户指令涉及多个操作，请一次性调用多个工具。"
        )
    
    while True:
        user_input = input("\n 你：").strip()
        if user_input!=None and len(user_input)>0:
            if user_input.lower in ("exit","quit"):
                break
            if user_input.lower == "showall":
                print(f"{session.messages}")
                continue
            call_llm()


if __name__ == "__main__":
    main()

