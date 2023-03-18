from subprocess import Popen, PIPE
from functools import reduce
import logging


logger = logging.getLogger()


TOP_PEN = "ELAN9008:00 04F3:4063 Stylus Pen (0)"
BOTTOM_PEN = "ELAN9009:00 04F3:4068 Stylus Pen (0)"
TOP_ERASER = "ELAN9008:00 04F3:4063 Stylus Eraser (0)"
BOTTOM_ERASER = "ELAN9009:00 04F3:4068 Stylus Eraser (0)"

TOP_INPUT = "ELAN9008:00 04F3:4063"
BOTTOM_INPUT = "ELAN9009:00 04F3:4068"
TOP_DISPLAY = "eDP-1-1"
BOTTOM_DISPLAY = "DP-1-1"

INPUT_MAP = (
    (TOP_INPUT, TOP_DISPLAY),
    (BOTTOM_INPUT, BOTTOM_DISPLAY),
    (TOP_PEN, TOP_DISPLAY),
    (BOTTOM_PEN, BOTTOM_DISPLAY),
    (TOP_ERASER, TOP_DISPLAY),
    (BOTTOM_ERASER, BOTTOM_DISPLAY),
)


class DisplayInputs:
    devices = {}

    def __init__(self):
        self.get_devices()

    def get_devices(self):
        with Popen(["xinput", "list"], stdout=PIPE) as proc:
            out = proc.stdout.read()

        clean_out = [
            b"\xe2\x8e\x9c   \xe2\x86\xb3 ",
            b"\xe2\x8e\xa3 ",
            b"    \xe2\x86\xb3 ",
            b"\xe2\x8e\xa1 ",
            b"id=",
        ]
        for line in reduce(lambda a, b: a.replace(b, b""), clean_out, out).split(b"\n"):
            if line:
                name, _id, _typ = [x.strip() for x in line.split(b"\t")]
                self.devices[name.decode("utf-8")] = {
                    "id": int(_id),
                    "type": _typ,
                }

    def map_inputs(self):
        for _map in INPUT_MAP:
            device_name, display_name = _map
            device = self.devices.get(device_name)
            if device:
                logger.info(f"Mapping {device_name} to display {display_name}")
                with Popen(
                    ["xinput", "map-to-output", str(device["id"]), display_name],
                    stdout=PIPE,
                ) as proc:
                    out = proc.stdout.read()
            else:
                logger.warning(f"Device not found, skipping: {device_name}")
