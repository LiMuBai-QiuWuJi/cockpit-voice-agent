import json
from domains import car_state_define, car_state


def setCarHvac(power: bool = None, temperature: int = None, fan_speed: int = None):
    if power is not None:
        car_state["hvac"]["power"] = power
    if temperature is not None:
        car_state["hvac"]["temperature"] = max(
            car_state_define.HVAC_TEMPERATURE_MIN,
            min(temperature, car_state_define.HVAC_TEMPERATURE_MAX),
        )
    if fan_speed is not None:
        car_state["hvac"]["fan_speed"] = max(
            car_state_define.HVAC_FAN_SPEED_MIN,
            min(fan_speed, car_state_define.HVAC_FAN_SPEED_MAX),
        )
    return {"status": "ok", "hvac": car_state["hvac"]}


def setCarWindow(position: str = None, open: bool = None):
    if position is None or open is None:
        return {"status": "error", "message": "position 和 open 不能为空"}
    target = position.lower()
    value = car_state_define.WINDOW_OPEN if open else car_state_define.WINDOW_CLOSE
    if target == "all":
        for key in car_state["window"]:
            car_state["window"][key] = value
    elif target in car_state["window"]:
        car_state["window"][target] = value
    else:
        return {"status": "error", "message": f"未知车窗位置：{position}"}
    return {"status": "ok", "window": car_state["window"]}


def call_cloud(user_input: str = "", car_state: dict = car_state):
    from main import cloud_handle

    payload = json.dumps(
        {"user_input": user_input, "car_state": car_state, "history_number": 0},
        ensure_ascii=False,
    )
    reply_json = cloud_handle(payload=payload)
    reply = json.loads(reply_json)
    print(f"\n助手：{reply.get('say', '')}")
    print(f"操作记录：{reply.get('actions', [])}")
    return reply


def main():
    print("实车模拟已启动")
    while True:
        user_input = input("\n 你(模拟语音输入) :").strip()
        if user_input:
            if user_input.lower() in ("exit", "quit"):
                break
            call_cloud(user_input)


if __name__ == "__main__":
    main()
