import evdev
import logging
import sys
import os
from controls.governor import ScalingGovernors
from controls.displays import DisplayInputs
from controls.fan import FAN_MODE, CPUFan

# LOGGING #######################
# Optional env var for setting log level.  Defaults to info
# CRITICAL, ERROR, WARNING, INFO, DEBUG
ASUS_MANAGER_LOGS_LEVEL = os.environ.get("ASUS_MANAGER_LOGS_LEVEL", logging.INFO)

logger = logging.getLogger()
logger.setLevel(ASUS_MANAGER_LOGS_LEVEL)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


config = {"UX582Z": {"asus-nb-wmi/input0"}}


keys = {
    157: {"name": "Fan"},  # 0x9d
    156: {"name": "Swap"},  # 0x9c
    106: {"name": "Disable Bottom Screen"},  # 0x6a
    133: {"name": "Disable Camera"},  # 0x85
    134: {"name": "My Asus"},  # 0x86
    107: {"name": "Disable Touchpad"},  # 0x6b  # handled by OS
    207: {"name": "A/C Connected"},
}


class AsusDuoPro:
    devices = {}

    def __init__(self):
        self.scaling_governor = ScalingGovernors()
        self.display_inputs = DisplayInputs()
        self.fan_control = CPUFan()

        self.display_inputs.get_devices()
        self.display_inputs.map_inputs()

    def scan(self):
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            self.devices[device.phys] = device

    def run(self, device_path):
        device = self.devices.get(device_path)
        if device is None:
            self.scan()
            device = self.devices.get(device_path)

        try:
            for event in device.read_loop():
                if event.code == 4 and event.type == 4:
                    logger.debug(evdev.categorize(event))
                    self.route_event(event.value)
        except KeyboardInterrupt:
            logger.warning("Keyboard Interrupt detected, stopping listener")

    def route_event(self, event_value):
        key_config = keys.get(event_value)
        if key_config is None:
            logger.warning(f"Unsupported key event value:{event_value}")
            return
        if event_value == 157:
            self.scaling_governor.set()
            if self.scaling_governor.mode == "powersave":
                self.fan_control.mode = FAN_MODE.THERMAL_CRUISE
            elif self.scaling_governor.mode == "performance":
                self.fan_control.mode = FAN_MODE.FULL
            else:
                self.fan_control.mode = FAN_MODE.DEFAULT
        else:
            logger.info(f"No function mapping for key:{key_config.get('name')}")


adp_daemon = AsusDuoPro()
adp_daemon.run("asus-nb-wmi/input0")
