import asyncio
from mavsdk import System, geofence, telemetry, offboard
from datetime import datetime
import tasks
import math

YAW_SPEED = 36.0
YAW_TOLERANCE = 5

async def manual_controls(sequences):
    """Main function to connect to the drone"""
    # Connect to the Simulation
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone with UUID: {state.uuid}")
            break

    async for gps_info in drone.telemetry.gps_info():
        if gps_info.fix_type == telemetry.FixType.FIX_3D:
            print(f"-- Got 3D fix")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_attitude(offboard.Attitude(0.0, 0.0, 0.0, 0.0))

    try:
        print("-- Starting offboard mode")
        await drone.offboard.start()
    except offboard.OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
        {error._result.result}")

        print("-- Disarming")
        await drone.action.disarm()

        return

    sequence_began = datetime.now().timestamp()
    (seq_dur, north, east, down, yaw) = sequences.pop(0)
        
    await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(north, east, down, yaw))

    while True:
        if sequence_began + seq_dur < datetime.now().timestamp():
            print("-- Switching sequence...")
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
                            print(f"-- Yaw is: {deg}")
                            await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, -YAW_SPEED if anti_cw else YAW_SPEED))

                    continue
            else:
                (seq_dur, north, east, down, yaw) = command
                await drone.offboard.set_velocity_body(offboard.VelocityBodyYawspeed(north, east, down, yaw))

        await asyncio.sleep(0.1)

    print("-- Landing!")
    await drone.action.land()
    await asyncio.sleep(5.0)

    print("-- Disarming!")
    await drone.action.disarm()
    print("-- Done!")

    

loop = asyncio.get_event_loop()

loop.run_until_complete(manual_controls(
    # Uncomment one to run
    # tasks.square(x=30.0)
    tasks.square2(x=30.0)
    # tasks.infinity(circle_duration=30.0, r=10.0)
    # tasks.circle(circle_duration=30.0, r=10.0)
))
 