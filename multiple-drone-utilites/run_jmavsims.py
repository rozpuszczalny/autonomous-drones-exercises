import subprocess
import os
import random

def run_jmavsims(no_instances, px4_cwd="../px4-firmware", starting_port=4560):
    mavs = []

    environment = os.environ.copy()
    environment["DISPLAY"] = ":0"
    environment["PX4_HOME_LAT"] = f"{53.134837 + (random.uniform(-0.001, 0.001))}"
    environment["PX4_HOME_LON"] = f"{18.032990 + (random.uniform(-0.001, 0.001))}"
    environment["PX4_HOME_ALT"] = "55"
    environment["HEADLESS"] = "1"

    subprocess.run(["./Tools/sitl_multiple_run.sh", f"{no_instances}"], cwd=px4_cwd, env=environment)

    for i in range(0, no_instances):
        port = starting_port + i

        env = environment.copy()
        env["PX4_HOME_LAT"] = f"{53.134837 + (random.uniform(-0.001, 0.001))}"
        env["PX4_HOME_LON"] = f"{18.032990 + (random.uniform(-0.001, 0.001))}"

        popen = subprocess.Popen(["./Tools/jmavsim_run.sh", "-l", "-p", f"{port}"], cwd=px4_cwd, env=env)
        mavs.append(popen)
    
    return mavs
