import asyncio
import os
import sys
import signal
import time
from mavsdk import System, geofence, telemetry, offboard
from datetime import datetime
import tasks
import math

from utils.run_mavsdk_servers import run_mavsdk_servers
from utils.run_jmavsims import run_jmavsims


YAW_SPEED = 36.0
YAW_TOLERANCE = 5

status = {}

async def start_drone(drone, droneName, sequences):
    status[droneName] = {}
    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- |{droneName}| Connected to drone with UUID: {state.uuid}")
            break

    async for gps_info in drone.telemetry.gps_info():
        if gps_info.fix_type == telemetry.FixType.FIX_3D:
            print(f"-- |{droneName}| Got 3D fix")
            break

    print(f"-- |{droneName}| Arming")
    await drone.action.arm()

    print(f"-- |{droneName}| Setting initial setpoint")
    await drone.offboard.set_attitude(offboard.Attitude(0.0, 0.0, 0.0, 0.0))

    try:
        print(f"-- |{droneName}| Starting offboard mode")
        await drone.offboard.start()
    except offboard.OffboardError as error:
        print(f"-- |{droneName}| Starting offboard mode failed with error code: \
        {error._result.result}")

        print(f"-- |{droneName}| Disarming")
        await drone.action.disarm()

        return

    sequence_began = datetime.now().timestamp()
    (seq_dur, north, east, down, yaw) = sequences.pop(0)
        
    await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(north, east, down, yaw))

    while True:
        if sequence_began + seq_dur < datetime.now().timestamp():
            print(f"-- |{droneName}| Switching sequence...")
            if len(sequences) == 0:
                break
            sequence_began = datetime.now().timestamp()
            command = sequences.pop(0)
            if isinstance(command, dict):
                seq_dur = 0.0
                if command['until_reached'] == 'yaw':
                    await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, YAW_SPEED))
                    tele: telemetry.Telemetry = drone.telemetry
                    
                    last_update = datetime.now().timestamp()
                    anti_cw = None
                    async for info in tele.attitude_euler():
                        deg = info.yaw_deg if info.yaw_deg >= 0.0 else 360 + info.yaw_deg
                        if anti_cw is None:
                            anti_cw = command['yaw'] - deg > 180.0

                        if abs(min(deg - command['yaw'], command['yaw'] - deg)) < YAW_TOLERANCE:
                            break

                        if datetime.now().timestamp() - last_update > 0.1:
                            await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, -YAW_SPEED if anti_cw else YAW_SPEED))

                    continue
            else:
                (seq_dur, north, east, down, yaw) = command
                await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(north, east, down, yaw))

        await asyncio.sleep(0.1)
    

async def manual_controls(no_instances):
    """Main function to connect to the drone"""
    # Connect to the Simulation
    the_tasks = []
    for i in range(0, no_instances):
        drone = System(mavsdk_server_address="localhost", port=50050+i)
        await drone.connect(system_address=f"udp://:{14540 + i}")
        the_tasks.append(start_drone(
            drone,
            f'Dron #{i+1}',
            # task to do
            # Uncomment one to run
            # tasks.square(x=30.0)
            # tasks.square2(x=30.0)
            tasks.infinity(circle_duration=30.0, r=10.0)
            # tasks.circle(circle_duration=30.0, r=10.0)
        ))

    await asyncio.gather(
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

print("Done! Now terminating...")

loop.close()

os.kill(os.getpid(), signal.SIGINT)

for sim in jmavsims:
    sim.send_signal(signal.SIGINT)

for mav in mav_servers:
    mav.send_signal(signal.SIGINT)

for sim in jmavsims:
    sim.terminate()

for mav in mav_servers:
    mav.terminate()

for sim in jmavsims:
    sim.wait()

for mav in mav_servers:
    mav.wait()

# For some reason it doesn't work here.
# One may try to clean it up with killall java; killall mavsdk_server
# but it might kill other, non-drone correlated java processes
