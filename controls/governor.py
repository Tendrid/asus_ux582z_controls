import os
import re
import logging

logger = logging.getLogger()


class ScalingGovernors:
    AVAILABLE_GOVERNORS_PATH = (
        "/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors"
    )
    CPU_PATH = "/sys/devices/system/cpu/"
    GOVERNOR_PATH = "cpufreq/scaling_governor"

    def __init__(self):
        self.governors = []
        self.cpus = []
        with open(self.AVAILABLE_GOVERNORS_PATH) as fh:
            self.governors = fh.readline().strip().split(" ")
        self.cpus = [x for x in os.listdir(self.CPU_PATH) if re.match("cpu\d+", x)]

    @property
    def mode(self):
        governor = "Unknown"
        with open(os.path.join(self.CPU_PATH, self.cpus[0], self.GOVERNOR_PATH)) as fh:
            governor = fh.readline().strip()
        return governor

    @mode.setter
    def mode(self, governor):
        if governor not in self.governors:
            # setting directly should raise
            raise ValueError(f"Invalid governor selected: {governor}")
        logger.info(f"Setting governor to {governor}")
        for cpu in self.cpus:
            with open(os.path.join(self.CPU_PATH, cpu, self.GOVERNOR_PATH), "w") as fh:
                fh.write(governor)

    def set(self, governor=None):
        if governor:
            try:
                index = self.governors.index(governor)
            except ValueError:
                # log a soft error, but dont break stride
                logger.error(f"Invalid governor selected: {governor}")
                return
        else:
            index = (self.governors.index(self.mode) + 1) % len(self.governors)
        self.mode = self.governors[index]
