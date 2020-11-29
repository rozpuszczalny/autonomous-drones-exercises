LEFT_UP_KEY = 'w'
LEFT_DOWN_KEY = 's'

LEFT_LEFT_KEY = 'a'
LEFT_RIGHT_KEY = 'd'

RIGHT_UP_KEY = 'Up'
RIGHT_DOWN_KEY = 'Down'

RIGHT_LEFT_KEY = 'Left'
RIGHT_RIGHT_KEY = 'Right'

MODE_1 = 'MODE_1'
MODE_2 = 'MODE_2'

FLIGHT_MODE_POSITION = 'POSITION'
FLIGHT_MODE_ALITIUDE = 'ALITIUDE'

control_state = {}

ALL_KEYS = (LEFT_UP_KEY, LEFT_DOWN_KEY, LEFT_LEFT_KEY, LEFT_RIGHT_KEY, RIGHT_UP_KEY, RIGHT_DOWN_KEY, RIGHT_LEFT_KEY, RIGHT_RIGHT_KEY)

for key in (LEFT_UP_KEY, LEFT_DOWN_KEY, LEFT_LEFT_KEY, LEFT_RIGHT_KEY, RIGHT_UP_KEY, RIGHT_DOWN_KEY, RIGHT_LEFT_KEY, RIGHT_RIGHT_KEY):
    control_state[key] = False

mode = {
    'current': MODE_2,
}

flight_mode = {
    'current': FLIGHT_MODE_POSITION,
    'requested': FLIGHT_MODE_POSITION
}

fence = {
    'current': None,
    'requested': None
}

def get_value(high_key, low_key, high_value=1.0, low_value=-1.0, neutral_value=0.0):
    if control_state[high_key] ^ control_state[low_key]:
        return float(high_value if control_state[high_key] else low_value)
    
    return float(neutral_value)

def get_left_y_value(high_value=1.0, low_value=-1.0, neutral_value=0.0):
    return get_value(LEFT_UP_KEY, LEFT_DOWN_KEY, high_value=high_value, low_value=low_value, neutral_value=neutral_value)

def get_left_x_value(high_value=1.0, low_value=-1.0, neutral_value=0.0):
    return get_value(LEFT_RIGHT_KEY, LEFT_LEFT_KEY, high_value=high_value, low_value=low_value, neutral_value=neutral_value)

def get_right_x_value(high_value=1.0, low_value=-1.0, neutral_value=0.0):
    return get_value(RIGHT_RIGHT_KEY, RIGHT_LEFT_KEY, high_value=high_value, low_value=low_value, neutral_value=neutral_value)

def get_right_y_value(high_value=1.0, low_value=-1.0, neutral_value=0.0):
    return get_value(RIGHT_UP_KEY, RIGHT_DOWN_KEY, high_value=high_value, low_value=low_value, neutral_value=neutral_value)


def get_pitch():
    return get_right_y_value() if mode['current'] is MODE_2 else get_left_y_value()

def get_roll():
    return get_right_x_value()

def get_throttle():
    return get_left_y_value(low_value=0.0, neutral_value=0.5) if mode['current'] is MODE_2 else get_right_y_value(low_value=0.0, neutral_value=0.5)

def get_yaw():
    return get_left_x_value()
