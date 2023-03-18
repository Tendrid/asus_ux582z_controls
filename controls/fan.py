# https://www.kernel.org/doc/Documentation/hwmon/nct6775
# /sys/devices/platform/asus-nb-wmi/hwmon/hwmon4

"""
switch on = $ sudo echo 0 > /sys/devices/platform/asus-nb-wmi/hwmon/hwmon4/pwm1_enable
switch off = $ sudo echo 2 > /sys/devices/platform/asus-nb wmi/hwmon/hwmon4/pwm1_enable
"""

import os
import logging
from enum import Enum

logger = logging.getLogger()


class FAN_MODE(Enum):
    FULL = 0
    THERMAL_CRUISE = 2
    DEFAULT = 2


class CPUFan:
    FAN_PATH = "/sys/devices/platform/asus-nb-wmi/hwmon/hwmon4/pwm1_enable"

    def __init__(self):
        pass

    @property
    def mode(self):
        mode = -1
        with open(self.FAN_PATH) as fh:
            mode = int(fh.readline().strip())
        return mode

    @mode.setter
    def mode(self, fan_mode):
        if fan_mode not in FAN_MODE:
            # setting directly should raise
            raise ValueError(f"Invalid fan_mode selected: {fan_mode}")
        logger.info(f"Setting fan_mode to {fan_mode.name}")
        with open(self.FAN_PATH, "w") as fh:
            fh.write(str(fan_mode.value))
