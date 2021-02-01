import asyncio
import os
import sys
import signal
import time
from mavsdk import System, geofence

from utils.run_mavsdk_servers import run_mavsdk_servers
from utils.run_jmavsims import run_jmavsims

status = {}

interrupt = {'should': False}

def signal_handler(sig, frame):
    print('Stopping...')
    interrupt['should'] = True

    for task in asyncio.all_tasks(loop=loop):
        task.cancel()

signal.signal(signal.SIGINT, signal_handler)

PRINT_INTERVAL = 0.1

async def get_flight_mode_status(drone: System, droneName: str):
    async for flight_mode in drone.telemetry.flight_mode():
        if interrupt['should']:
            print('will interrupt')
            break
        status[droneName]['flight_mode'] = flight_mode

async def get_position_status(drone: System, droneName: str):
    async for position in drone.telemetry.position():
        if interrupt['should']:
            print('will interrupt')
            break
        status[droneName]['position'] = position
        status[droneName]['altitude'] = position.relative_altitude_m

async def get_battery_status(drone: System, droneName: str):
    async for battery in drone.telemetry.battery():
        if interrupt['should']:
            print('will interrupt')
            break
        status[droneName]['battery'] = battery

async def get_gps_info_status(drone: System, droneName: str):
    async for gps_info in drone.telemetry.gps_info():
        if interrupt['should']:
            print('will interrupt')
            break
        status[droneName]['gps_info'] = gps_info

async def print_status():
    while True:
        if interrupt['should']:
            print('will interrupt status')
            break
        os.system('clear')
        for droneName in status:
            droneStatus = status[droneName]
            print(f"Drone name '{droneName}'")
            if droneStatus.get('flight_mode'):
                print(f"Flight mode {droneStatus.get('flight_mode')}")
            else:
                print(f"Flight mode ___")
            if droneStatus.get('position'):
                print(f"position lat: {droneStatus.get('position').latitude_deg} lon: {droneStatus.get('position').longitude_deg}")
            else:
                print(f"position lat: ___ lon: ___")
            if droneStatus.get('battery'):
                print(f"battery V: {droneStatus.get('battery').voltage_v} remaining percent: {droneStatus.get('battery').remaining_percent}")
            else:
                print(f"battery V: ___ remaining percent: ___")
            if droneStatus.get('altitude'):
                print(f"altitude {droneStatus.get('altitude')}")
            else:
                print(f"altitude ___")
            if droneStatus.get('gps_info'):
                print(f"number of satellites {droneStatus.get('gps_info').num_satellites}")
            else:
                print(f"number of satellites ___")

        await asyncio.sleep(PRINT_INTERVAL)

async def start_drone(drone, droneName):
    status[droneName] = {}
    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone with UUID: {state.uuid}")
            break

    # Gather all tasks that 
    await asyncio.gather(
        get_flight_mode_status(drone, droneName),
        get_position_status(drone, droneName),
        get_battery_status(drone, droneName),
        get_gps_info_status(drone, droneName)
    )
    

async def manual_controls(no_instances):
    """Main function to connect to the drone"""
    # Connect to the Simulation
    the_tasks = []
    for i in range(0, no_instances):
        drone = System(mavsdk_server_address="localhost", port=50050+i)
        await drone.connect(system_address=f"udp://:{14540 + i}")
        the_tasks.append(start_drone(drone, f'Dron #{i+1}'))

    await asyncio.gather(
        print_status(),
        *the_tasks
    )

no_instances = 3

mav_servers = run_mavsdk_servers(no_instances)
jmavsims = run_jmavsims(no_instances)

loop = asyncio.get_event_loop()
task = manual_controls(no_instances)
try:
    loop.run_until_complete(task)
except asyncio.exceptions.CancelledError:
    pass

loop.close()

for sim in jmavsims:
    sim.terminate()

for mav in mav_servers:
    mav.terminate()

for sim in jmavsims:
    sim.wait()

for mav in mav_servers:
    mav.wait()
