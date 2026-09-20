#!/usr/bin/env python3

import subprocess
import math
import time
import re


TOPIC = "/my_asv/lidar"


def get_lidar_once():
    try:
        out = subprocess.check_output(
            ["gz", "topic", "-e", "-t", TOPIC, "-n", "1"],
            text=True,
            timeout=3
        )
    except Exception:
        return None

    ranges = []
    angle_min = -3.14159
    angle_step = 0.008738776

    for line in out.splitlines():
        line = line.strip()

        if line.startswith("angle_min:"):
            angle_min = float(line.split(":")[1].strip())

        elif line.startswith("angle_step:"):
            angle_step = float(line.split(":")[1].strip())

        elif line.startswith("ranges:"):
            val = line.split(":")[1].strip()
            if val == "inf":
                ranges.append(float("inf"))
            else:
                try:
                    ranges.append(float(val))
                except:
                    pass

    return ranges, angle_min, angle_step


def sector_min(ranges, angle_min, angle_step, deg_min, deg_max):
    vals = []

    for i, r in enumerate(ranges):
        angle = angle_min + i * angle_step
        deg = math.degrees(angle)

        if deg_min <= deg <= deg_max:
            if math.isfinite(r):
                vals.append(r)

    return min(vals) if vals else float("inf")


while True:
    data = get_lidar_once()

    if data is None:
        print("LiDAR: no Gazebo data")
        time.sleep(1)
        continue

    ranges, angle_min, angle_step = data

    front = sector_min(ranges, angle_min, angle_step, -20, 20)
    left = sector_min(ranges, angle_min, angle_step, 20, 90)
    right = sector_min(ranges, angle_min, angle_step, -90, -20)

    obstacle = front < 5.0

    print(
        f"LiDAR | front={front:.2f} m | left={left:.2f} m | right={right:.2f} m | obstacle={obstacle}",
        flush=True
    )

    time.sleep(1)
