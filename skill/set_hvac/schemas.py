from domains import car_state_define
SET_HVAC_SCHEMAS = {
    "type":"function",
    "function":{
        "name":"set_hvac",
        "description":"设置空调温度，单位摄氏度。如果空调未开启，会自动先开启。",
        "parameters":{
            "type":"object",
            "properties":{
                "power":{
                    "type":"boolean",
                    "description":"是否打开空调,打开(True),关闭(False)"
                },
                "temperature":{
                    "type": "integer",
                    "description": "目标温度,范围见参数minimum与maximum",
                    "minimum": car_state_define.HVAC_TEMPERATURE_MIN,
                    "maximum": car_state_define.HVAC_TEMPERATURE_MAX,
                },
                "fan_speed":{
                    "type":"integer",
                    "description":"设置空调风速,范围见参数minimum与maximum",
                    "minimun": car_state_define.HVAC_FAN_SPEED_MIN,
                    "maximum": car_state_define.HVAC_FAN_SPEED_MAX
                }
            },
            "required": [],
        }
    }
}
# boolean