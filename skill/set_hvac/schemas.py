from domains import car_state_define

SET_HVAC_SCHEMAS = {
    "type": "function",
    "function": {
        "name": "set_hvac",
        "description": "设置空调状态，包括开关、温度、风速。",
        "parameters": {
            "type": "object",
            "properties": {
                "power": {
                    "type": "boolean",
                    "description": "是否打开空调，True 为打开，False 为关闭",
                },
                "temperature": {
                    "type": "integer",
                    "description": "目标温度，单位摄氏度，范围见 minimum 与 maximum",
                    "minimum": car_state_define.HVAC_TEMPERATURE_MIN,
                    "maximum": car_state_define.HVAC_TEMPERATURE_MAX,
                },
                "fan_speed": {
                    "type": "integer",
                    "description": "目标风速，范围见 minimum 与 maximum",
                    "minimum": car_state_define.HVAC_FAN_SPEED_MIN,
                    "maximum": car_state_define.HVAC_FAN_SPEED_MAX,
                },
            },
            "required": [],
        },
    },
}
