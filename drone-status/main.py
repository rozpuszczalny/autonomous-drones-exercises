import asyncio
import os
import sys
import signal
from mavsdk import System, geofence

status = {
    'flight_mode': None,
    'position': None,
    'battery': None,
    'altitude': None,
    'gps_info': None,
}

def signal_handler(sig, frame):
    print('Stopping...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

PRINT_INTERVAL = 0.1

async def get_flight_mode_status(drone: System):
    async for flight_mode in drone.telemetry.flight_mode():
        status['flight_mode'] = flight_mode

async def get_position_status(drone: System):
    async for position in drone.telemetry.position():
        status['position'] = position
        status['altitude'] = position.relative_altitude_m

async def get_battery_status(drone: System):
    async for battery in drone.telemetry.battery():
        status['battery'] = battery

async def get_gps_info_status(drone: System):
    async for gps_info in drone.telemetry.gps_info():
        status['gps_info'] = gps_info

async def print_status():
    while True:
        os.system('clear')
        if status['flight_mode']:
            print(f"Flight mode {status['flight_mode']}")
        else:
            print(f"Flight mode ___")
        if status['position']:
            print(f"position lat: {status['position'].latitude_deg} lon: {status['position'].longitude_deg}")
        else:
            print(f"position lat: ___ lon: ___")
        if status['battery']:
            print(f"battery V: {status['battery'].voltage_v} remaining percent: {status['battery'].remaining_percent}")
        else:
            print(f"battery V: ___ remaining percent: ___")
        if status['altitude']:
            print(f"altitude {status['altitude']}")
        else:
            print(f"altitude ___")
        if status['gps_info']:
            print(f"number of satellites {status['gps_info'].num_satellites}")
        else:
            print(f"number of satellites ___")

        await asyncio.sleep(PRINT_INTERVAL)

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

    # Gather all tasks that 
    await asyncio.gather(
        get_flight_mode_status(drone),
        get_position_status(drone),
        get_battery_status(drone),
        get_gps_info_status(drone),
        print_status()
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(manual_controls())