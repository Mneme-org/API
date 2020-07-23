import os
import sys
import time
import atexit
import subprocess

from mnemeapi import config

dir_name = os.path.dirname(__file__)
restart_file = os.path.join(dir_name, "mnemeapi", "mnemeapi.restart")
stop_file = os.path.join(dir_name, "mnemeapi", "mnemeapi.stop")


def start_api():
    if sys.platform.startswith("win"):
        uvicorn_path = os.popen("where uvicorn").read().rstrip("\n")
    else:
        uvicorn_path = os.popen("which uvicorn").read().rstrip("\n")

    script = [uvicorn_path, "mnemeapi:app", "--host", config.host, "--port", str(config.port), "--log-level", "info"]
    _api = subprocess.Popen(script, stdout=None, stderr=None, stdin=subprocess.DEVNULL)
    atexit.register(_api.terminate)
    return _api


def check_status():
    if os.path.exists(stop_file):
        try:
            os.remove(stop_file)
        except Exception:
            print("Unable to delete the stop file.")
        finally:
            print("mneme api stopped.")
            sys.exit(0)

    if os.path.exists(restart_file):
        try:
            os.remove(restart_file)
        except Exception:
            print("Unable to delete the restart file.")
        finally:
            print("mneme api is restarting..")
            api.kill()
            start_api()


if __name__ == "__main__":
    print("Starting the mneme api...")
    api = start_api()

    # Delete old stop and restart files
    try:
        os.remove(stop_file)
    except Exception:
        pass

    try:
        os.remove(restart_file)
    except Exception:
        pass

    while True:
        check_status()
        try:
            time.sleep(5)
        except Exception:
            sys.exit(0)
