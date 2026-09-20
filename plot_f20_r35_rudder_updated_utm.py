import os
import csv
import utm
import matplotlib.pyplot as plt

import rclpy
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


TEST_NAME = "f20_r35_rudder_updated"

BAG_PATH = os.path.expanduser(f"~/vrx_ws/bags/{TEST_NAME}")
OUT_CSV = os.path.expanduser(f"~/vrx_ws/bags/{TEST_NAME}/{TEST_NAME}_utm.csv")
OUT_PNG = os.path.expanduser(f"~/vrx_ws/bags/{TEST_NAME}/{TEST_NAME}_utm.png")

GPS_TOPIC = "/asv/gps_data"


def main():
    rclpy.init()

    reader = SequentialReader()
    reader.open(
        StorageOptions(uri=BAG_PATH, storage_id="sqlite3"),
        ConverterOptions(
            input_serialization_format="cdr",
            output_serialization_format="cdr"
        )
    )

    topic_types = reader.get_all_topics_and_types()
    type_map = {t.name: t.type for t in topic_types}

    gps_msg_type = get_message(type_map[GPS_TOPIC])

    rows = []
    e0 = None
    n0 = None

    while reader.has_next():
        topic, data, timestamp = reader.read_next()

        if topic == GPS_TOPIC:
            msg = deserialize_message(data, gps_msg_type)

            lat = float(msg.latitude)
            lon = float(msg.longitude)

            easting, northing, zone_num, zone_letter = utm.from_latlon(lat, lon)

            if e0 is None:
                e0 = easting
                n0 = northing

            x_m = easting - e0
            y_m = northing - n0

            rows.append([
                timestamp * 1e-9,
                lat,
                lon,
                x_m,
                y_m
            ])

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_sec", "latitude", "longitude", "x_m", "y_m"])
        writer.writerows(rows)

    x = [r[3] for r in rows]
    y = [r[4] for r in rows]

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, linewidth=2)
    plt.scatter(x[0], y[0], s=80, label="Start")
    plt.scatter(x[-1], y[-1], s=80, label="End")

    plt.xlabel("X displacement / UTM Easting (m)")
    plt.ylabel("Y displacement / UTM Northing (m)")
    plt.title("f20 r35 rudder updated")
    plt.grid(True)
    plt.axis("equal")
    plt.legend()

    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")

    print("CSV saved:", OUT_CSV)
    print("Plot saved:", OUT_PNG)

    plt.show()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
