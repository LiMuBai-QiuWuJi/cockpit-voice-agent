from realCarSimulation import setCarHvac


def set_hvac(power: bool = None, temperature: int = None, fan_speed: int = None):
    return setCarHvac(power=power, temperature=temperature, fan_speed=fan_speed)
