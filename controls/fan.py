# https://askubuntu.com/questions/42494/how-can-i-change-the-nvidia-gpu-fan-speed
# https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks#Overclocking_and_cooling

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
    FAN_PATH = "/sys/devices/platform/asus-nb-wmi/hwmon/"  # hwmon6/pwm1_enable"
    PWM_NAME = "pwm1_enable"
    __fan = None

    def __init__(self):
        for hwmon in os.listdir(self.FAN_PATH):
            if os.path.isfile(os.path.join(self.FAN_PATH, hwmon, self.PWM_NAME)):
                if self.__fan and self.__fan != hwmon:
                    logger.critical(f"MULTIPLE FANS DETECTED: {self.__fan} {hwmon}")
                self.__fan = hwmon
                if not self.__fan:
                    logger.critical(f"NO FANS DETECTED")
                else:
                    logger.info(f"Setting fan to {self.__fan}")
        self.mode = FAN_MODE.DEFAULT

    @property
    def hwmon(self):
        return os.path.join(self.FAN_PATH, self.__fan, self.PWM_NAME)

    @property
    def mode(self):
        mode = -1
        with open(self.hwmon) as fh:
            mode = int(fh.readline().strip())
        return mode

    @mode.setter
    def mode(self, fan_mode):
        if fan_mode not in FAN_MODE:
            # setting directly should raise
            raise ValueError(f"Invalid fan_mode selected: {fan_mode}")
        logger.info(f"Setting fan_mode to {fan_mode.name}")
        with open(self.hwmon, "w") as fh:
            fh.write(str(fan_mode.value))
