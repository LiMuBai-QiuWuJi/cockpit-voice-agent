from domains import car_state_define

SET_WINDOW_SCHEMAS = {
    "type": "function",
    "function": {
        "name": "set_window",
        "description": "控制车辆指定车窗的开关。",
        "parameters": {
            "type": "object",
            "properties": {
                "position": {
                    "type": "string",
                    "enum": ["front_left", "front_right", "rear_left", "rear_right", "all"],
                    "description": "车窗位置，all 表示全部车窗",
                },
                "open": {
                    "type": "boolean",
                    "description": "True 为打开车窗，False 为关闭车窗",
                },
            },
            "required": ["position", "open"],
        },
    },
}
