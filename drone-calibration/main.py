import asyncio
import os
import sys
import signal
import math
from mavsdk import System, geofence

def signal_handler(sig, frame):
    print('Stopping...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def gyro_calibration(drone):
    try:
        print("-- Attempting to calibrate gyro...")
        async for progress in drone.calibration.calibrate_gyro():
            print(f"-- Gyro calibration {round(progress.progress * 100)}%...")
        print("-- Gyro calibration done!")
    except:
        print("-- Gyro calibration failed!")

async def accelerometer_calibration(drone):
    try:
        print("-- Attempting to calibrate accelerometer...")
        async for progress in drone.calibration.calibrate_accelerometer():
            if progress.has_status_text:
                print(f"-- Accelerometer calibration: {progress.status_text}")
            else:
                print(f"-- Accelerometer calibration {round(progress.progress * 100)}%...")
        print("-- Accelerometer calibration done!")
    except:
        print("-- Accelerometer calibration failed!")

async def level_horizon_calibration(drone):
    try:
        print("-- Attempting to calibrate level horizon...")
        async for progress in drone.calibration.calibrate_level_horizon():
            if progress.has_status_text:
                print(f"-- Level horizon calibration: {progress.status_text}")
            else:
                print(f"-- Level horizon calibration {round(progress.progress * 100)}%...")
        print("-- Level horizon calibration done!")
    except:
        print("-- Level horizon calibration failed!")

async def magnetometer_calibration(drone):
    try:
        print("-- Attempting to calibrate magnetometer...")
        async for progress in drone.calibration.calibrate_magnetometer():
            if progress.has_status_text:
                print(f"-- Magnetometer calibration: {progress.status_text}")
            else:
                print(f"-- Magnetometer calibration {round(progress.progress * 100)}%...")
        print("-- Magnetometer calibration done!")
    except Exception as e:
        print("-- Magnetometer calibration failed!")


async def manual_controls():
    """Main function to connect to the drone"""
    # Connect to the Simulation
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone with UUID: {state.uuid}")
            break

    await gyro_calibration(drone)
    await asyncio.sleep(1)
    await accelerometer_calibration(drone)
    await asyncio.sleep(1)
    await level_horizon_calibration(drone)
    await asyncio.sleep(1)
    await magnetometer_calibration(drone)


loop = asyncio.get_event_loop()
loop.run_until_complete(manual_controls())