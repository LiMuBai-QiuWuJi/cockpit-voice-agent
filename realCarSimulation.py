from domains import car_state_define,car_state

def getCarState() -> car_state:
    return car_state

def setCarHvac(power:bool=None, tempreature:int=None, fan_speed:int=None):
    if power != None:
        car_state["hvac"]["power"] = power
    if tempreature != None:
        car_state["hvac"]["temperature"] = tempreature
    if fan_speed != None:
        car_state["hvac"]["fan_speed"] = fan_speed

def setCarWindow():
    print



