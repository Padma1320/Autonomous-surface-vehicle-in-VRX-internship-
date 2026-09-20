#!/usr/bin/env python3

import subprocess
import time
import re


RGB_TOPIC = "/my_asv/stereo/image"
DEPTH_TOPIC = "/my_asv/stereo/depth_image"


def get_image_info(topic):
    try:
        out = subprocess.check_output(
            ["gz", "topic", "-e", "-t", topic, "-n", "1"],
            text=True,
            timeout=3,
            errors="ignore"
        )
    except Exception:
        return None

    width = None
    height = None
    pixel_format = None

    for line in out.splitlines():
        line = line.strip()

        if line.startswith("width:"):
            width = line.split(":")[1].strip()

        elif line.startswith("height:"):
            height = line.split(":")[1].strip()

        elif line.startswith("pixel_format_type:"):
            pixel_format = line.split(":")[1].strip()

    return width, height, pixel_format


while True:
    rgb = get_image_info(RGB_TOPIC)
    depth = get_image_info(DEPTH_TOPIC)

    if rgb:
        print(
            f"Stereo RGB | width={rgb[0]} | height={rgb[1]} | format={rgb[2]}",
            flush=True
        )
    else:
        print("Stereo RGB | no Gazebo data", flush=True)

    if depth:
        print(
            f"Stereo Depth | width={depth[0]} | height={depth[1]} | format={depth[2]}",
            flush=True
        )
    else:
        print("Stereo Depth | no Gazebo data", flush=True)

    print("----------------------------------", flush=True)
    time.sleep(1)
