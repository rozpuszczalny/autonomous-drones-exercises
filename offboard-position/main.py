import asyncio
from mavsdk import System, geofence, telemetry, offboard
from datetime import datetime

# (duration in s, north, east, down, yaw)
# Values gathered via trial-and-error method
sequences_square = [
    # Takeoff
    (10.0, 0.0, 0.0, -10.0, 0.0),
    # Draw square
    (10.0, 10.0, 0.0, -10.0, 0.0),
    (10.0, 10.0, 10.0, -10.0, 90.0),
    (10.0, 0.0, 10.0, -10.0, 180.0),
    (10.0, 0.0, 0.0, -10.0, 270.0),
    # Land
    (30.0, 0.0, 0.0, 0.0, 0.0),
]

# (duration in s, north, east, down, yaw)
# Values gathered via trial-and-error method
sequences_triangle = [
    # Takeoff
    (10.0, 0.0, 0.0, -10.0, 0.0),
    # Draw triangle
    (10.0, 10.0, 0.0, -10.0, 0.0),
    # a = 10; h = a*sqrt(3) / 2 ~= 8.66025404
    (10.0, 5.0, 8.66025404, -10.0, 120.0),
    (10.0, 0.0, 0.0, -10.0, 240.0),
    # Land
    (30.0, 0.0, 0.0, 0.0, 0.0),
]

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
        
    await drone.offboard.set_position_ned(offboard.PositionNedYaw(north, east, down, yaw))

    while True:
        if sequence_began + seq_dur < datetime.now().timestamp():
            print("-- Switching sequence...")
            if len(sequences) == 0:
                break
            sequence_began = datetime.now().timestamp()
            (seq_dur, north, east, down, yaw) = sequences.pop(0)
        
            await drone.offboard.set_position_ned(offboard.PositionNedYaw(north, east, down, yaw))

        await asyncio.sleep(0.1)

    print("-- Landing!")
    await drone.action.land()
    await asyncio.sleep(5.0)

    print("-- Disarming!")
    await drone.action.disarm()
    print("-- Done!")

    

loop = asyncio.get_event_loop()
# Uncomment to draw square/triangle
# loop.run_until_complete(manual_controls(sequences_square))
loop.run_until_complete(manual_controls(sequences_triangle))