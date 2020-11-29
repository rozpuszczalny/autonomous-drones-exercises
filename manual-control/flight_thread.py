#!/usr/bin/env python3

"""
This example shows how to use the manual controls plugin.

Note: Manual inputs are taken from a test set in this example to decrease complexity. Manual inputs
can be received from devices such as a joystick using third-party python extensions

Note: Taking off the drone is not necessary before enabling manual inputs. It is acceptable to send
positive throttle input to leave the ground. Takeoff is used in this example to decrease complexity
"""

import asyncio
import math
from mavsdk import System, geofence
from threading import Thread
from control_state import *

# Test set of manual inputs. Format: [roll, pitch, throttle, yaw]
manual_inputs = [
    [0, 0, 0.5, 0],  # no movement
    [-1, 0, 0.5, 0],  # minimum roll
    [1, 0, 0.5, 0],  # maximum roll
    [0, -1, 0.5, 0],  # minimum pitch
    [0, 1, 0.5, 0],  # maximum pitch
    [0, 0, 0.5, -1],  # minimum yaw
    [0, 0, 0.5, 1],  # maximum yaw
    [0, 0, 1, 0],  # max throttle
    [0, 0, 0, 0],  # minimum throttle
]


async def manual_controls():
    """Main function to connect to the drone and input manual controls"""
    # Connect to the Simulation
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone with UUID: {state.uuid}")
            break

    # Checking if Global Position Estimate is ok
    async for global_lock in drone.telemetry.health():
        if global_lock.is_global_position_ok:
            print("-- Global position state is ok")
            break

    # set the manual control input after arming
    await drone.manual_control.set_manual_control_input(
        float(0), float(0), float(0), float(0)
    )

    # Arming the drone
    print("-- Arming")
    await drone.action.arm()

    # set the manual control input after arming
    await drone.manual_control.set_manual_control_input(
        float(0), float(0), float(0.5), float(0)
    )

    # Takeoff the vehicle
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(15)

    # set the manual control input after arming
    await drone.manual_control.set_manual_control_input(
        float(0), float(0), float(0.5), float(0)
    )

    # start manual control
    print("-- Starting manual control")
    await drone.manual_control.start_position_control()

    while True:
        # get current state of roll axis (between -1 and 1)
        roll = get_roll()
        # get current state of pitch axis (between -1 and 1)
        pitch = get_pitch()
        # get current state of throttle axis (between -1 and 1, but between 0 and 1 is expected)
        throttle = get_throttle()
        # get current state of yaw axis (between -1 and 1)
        yaw = get_yaw()
        if flight_mode['requested'] != flight_mode['current']:
            if flight_mode['requested'] == FLIGHT_MODE_ALITIUDE:
                await drone.manual_control.start_altitude_control()
                flight_mode['current'] = FLIGHT_MODE_ALITIUDE
            else:
                await drone.manual_control.start_position_control()
                flight_mode['current'] = FLIGHT_MODE_POSITION

        if fence['current'] != fence['requested']:
            if fence['requested'] == None:
                await drone.geofence.upload_geofence([])
                fence['current'] = fence['requested']
            else:
                async for cp in drone.telemetry.home():
                    km_to_degree_lat = 111
                    km_to_degree_lon = 40075 * math.cos(cp.latitude_deg) / 360
                    diff_lat = (fence['requested'] / 1000) / km_to_degree_lat
                    diff_lon = (fence['requested'] / 1000) / km_to_degree_lon
                    lat_west = cp.latitude_deg - diff_lat
                    lon_south = cp.longitude_deg - diff_lon
                    lat_east = cp.latitude_deg + diff_lat
                    lon_north = cp.longitude_deg + diff_lon
                    polygon = geofence.Polygon([
                        geofence.Point(lat_west, lon_south),
                        geofence.Point(lat_west, lon_north),
                        geofence.Point(lat_east, lon_north),
                        geofence.Point(lat_east, lon_south)
                    ], geofence.Polygon.FenceType.INCLUSION)
                    await drone.geofence.upload_geofence([polygon])
                    fence['current'] = fence['requested']
                    break


        await drone.manual_control.set_manual_control_input(pitch, roll, throttle, yaw)

        await asyncio.sleep(0.1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(manual_controls())

def start_thread(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(manual_controls())

def start():
    loop = asyncio.get_event_loop()
    Thread(target=start_thread, args=(loop,), daemon=True).start()