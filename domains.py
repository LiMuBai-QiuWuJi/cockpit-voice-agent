class car_state_define:
    HVAC_TEMPERATURE_MAX = 30
    HVAC_TEMPERATURE_MIN = 16

    HVAC_FAN_SPEED_MAX = 8
    HVAC_FAN_SPEED_MIN = 1

    HVAC_MODE_AUTO = "auto"

    WINDOW_OPEN = 1      #窗户 开
    WINDOW_CLOSE = 0     #窗户 关


# 初始化状态
define = car_state_define
car_state = {
    "hvac": {
        "power": False,
        "temperature": 24,
        "fan_speed": 2,
        "mode": define.HVAC_MODE_AUTO
        },
    "window": {
        "front_left": define.WINDOW_CLOSE,
        "front_right": define.WINDOW_CLOSE,
        "rear_left": define.WINDOW_CLOSE,
        "rear_right": define.WINDOW_CLOSE
        },
}