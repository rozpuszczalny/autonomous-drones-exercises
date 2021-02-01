import subprocess

def run_mavsdk_servers(no_instances, starting_port=50050, starting_drone_port=14540):
    mavs = []

    for i in range(0, no_instances):
        port = starting_port + i
        drone_port = starting_drone_port + i

        popen = subprocess.Popen(["mavsdk_server", "-p", f"{port}", f"udp://:{drone_port}"], restore_signals=False, start_new_session=True)
        mavs.append(popen)
    
    return mavs
