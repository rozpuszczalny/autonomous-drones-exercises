import math

def set_yaw(sequence: list, desired_yaw=0.0, previous_yaw=0.0):
    yaw_diff = desired_yaw - previous_yaw

    sequence.append(
        ((360.0/abs(yaw_diff)) * 15.0, 0.0, 0.0, 0.0, 36.0 if yaw_diff > 0 else -36.0)
    )

    return desired_yaw

SETTLE_DOWN_TIME = 2.0

# 1 / avg_sim_time
SIM_TIME_COMPENSATION = 1 / 0.95

def square(x: float=10.0, height_variation: float=10.0, side_duration: float=10.0, land_to_edge: float=5.0):
    """All sizes in meters"""
    land_to_point_edge = math.sqrt((x/2) ** 2 + land_to_edge ** 2)

    # 360 - angle, because we're going west, not east.
    land_to_point_angle = 360 - math.degrees(math.asin((x/2) / land_to_point_edge))

    sequence = []
    # Takeoff
    sequence.append((10.0, 0.0, 0.0, -5.0, 0.0))
    
    # Go to first point
    sequence.append({'yaw': land_to_point_angle, 'until_reached': 'yaw'})
    sequence.append((side_duration, land_to_point_edge/side_duration, 0.0, -height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Do square
    sequence.append({'yaw': 0.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    sequence.append({'yaw': 90.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, -height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))

    sequence.append({'yaw': 180.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))

    sequence.append({'yaw': 270.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, -height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Go to land
    sequence.append({'yaw': 45.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, ((x/2) * math.sqrt(2))/side_duration, 0.0, 0.0, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    # Do landing
    sequence.append((30.0, 0.0, 0.0, 5.0, 0.0))

    return sequence


def square2(x: float=10.0, height_variation: float=10.0, side_duration: float=10.0, land_to_edge: float=5.0):
    """All sizes in meters"""
    sequence = []
    # Takeoff
    sequence.append((10.0, 0.0, 0.0, -5.0, 0.0))
    
    # Go to first point
    sequence.append({'yaw': 0.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, land_to_edge/side_duration, 0.0, -height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Do square
    sequence.append({'yaw': 315.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    sequence.append({'yaw': 45.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, -height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))

    sequence.append({'yaw': 135.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))

    sequence.append({'yaw': 225.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, x/side_duration, 0.0, -height_variation/side_duration, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Go to land
    sequence.append({'yaw': 0.0, 'until_reached': 'yaw'})
    sequence.append((side_duration, (x/math.sqrt(2))/side_duration, 0.0, 0.0, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    # Do landing
    sequence.append((30.0, 0.0, 0.0, 5.0, 0.0))

    return sequence

def circle(r: float=10.0, circle_duration: float=60.0, land_to_edge: float=5.0):
    """All sizes in meters"""
    sequence = []
    # Takeoff
    sequence.append((15.0, 0.0, 0.0, -5.0, 0.0))
    
    # Go to first point
    sequence.append({'yaw': 0.0, 'until_reached': 'yaw'})
    sequence.append((10.0, land_to_edge/10.0, 0.0, 0.0, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Do circle
    sequence.append({'yaw': 270.0, 'until_reached': 'yaw'})
    sequence.append((circle_duration * SIM_TIME_COMPENSATION, (2 * math.pi * r) / circle_duration, 0.0, 0.0, math.degrees((2 * math.pi) / circle_duration)))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Go to land
    sequence.append({'yaw': 0.0, 'until_reached': 'yaw'})
    sequence.append((10.0, r / (2 * 10.0), 0.0, 0.0, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    # Do landing
    sequence.append((30.0, 0.0, 0.0, 5.0, 0.0))

    return sequence

def infinity(r: float=10.0, circle_duration: float=60.0, land_to_edge: float=5.0):
    """All sizes in meters"""
    sequence = []
    # Takeoff
    sequence.append((15.0, 0.0, 0.0, -5.0, 0.0))
    
    # Go to center
    sequence.append({'yaw': 0.0, 'until_reached': 'yaw'})
    sequence.append((10.0, (land_to_edge + r)/10.0, 0.0, 0.0, 0.0))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))
    
    # Do circle
    sequence.append((circle_duration * SIM_TIME_COMPENSATION, (2 * math.pi * r) / circle_duration, 0.0, 0.0, math.degrees((2 * math.pi) / circle_duration)))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))

    # Do second circle
    sequence.append((circle_duration * SIM_TIME_COMPENSATION, (2 * math.pi * r) / circle_duration, 0.0, 0.0, -math.degrees((2 * math.pi) / circle_duration)))
    sequence.append((SETTLE_DOWN_TIME, 0.0, 0.0, 0.0, 0.0))

    # Do landing
    sequence.append((30.0, 0.0, 0.0, 5.0, 0.0))

    return sequence
