import os
import csv
import matplotlib.pyplot as plt
import utm

import rclpy
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


BAG_PATH = os.path.expanduser("~/vrx_ws/bags/f20_r35_test")
CSV_PATH = os.path.expanduser("~/vrx_ws/bags/f20_r35_test/gps_utm_xy.csv")
PLOT_PATH = os.path.expanduser("~/vrx_ws/bags/f20_r35_test/gps_utm_xy_plot.png")


def main():
    rclpy.init()

    storage_options = StorageOptions(
        uri=BAG_PATH,
        storage_id="sqlite3"
    )

    converter_options = ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )

    reader = SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    gps_topic = "/asv/gps_data"

    if gps_topic not in type_map:
        print("ERROR: /asv/gps_data not found in bag")
        print("Available topics:", list(type_map.keys()))
        return

    gps_msg_type = get_message(type_map[gps_topic])

    rows = []

    e0 = None
    n0 = None
    zone_num = None
    zone_letter = None

    while reader.has_next():
        topic, data, timestamp = reader.read_next()

        if topic == gps_topic:
            msg = deserialize_message(data, gps_msg_type)

            lat = float(msg.latitude)
            lon = float(msg.longitude)

            easting, northing, z_num, z_letter = utm.from_latlon(lat, lon)

            if e0 is None:
                e0 = easting
                n0 = northing
                zone_num = z_num
                zone_letter = z_letter

            x_m = easting - e0
            y_m = northing - n0

            rows.append({
                "time_sec": timestamp * 1e-9,
                "latitude": lat,
                "longitude": lon,
                "utm_easting_m": easting,
                "utm_northing_m": northing,
                "x_m": x_m,
                "y_m": y_m,
                "utm_zone": f"{zone_num}{zone_letter}"
            })

    if len(rows) == 0:
        print("No GPS data found.")
        rclpy.shutdown()
        return

    with open(CSV_PATH, "w", newline="") as csvfile:
        fieldnames = [
            "time_sec",
            "latitude",
            "longitude",
            "utm_easting_m",
            "utm_northing_m",
            "x_m",
            "y_m",
            "utm_zone"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("CSV saved to:", CSV_PATH)
    print("UTM zone:", f"{zone_num}{zone_letter}")

    x_vals = [row["x_m"] for row in rows]
    y_vals = [row["y_m"] for row in rows]

    plt.figure(figsize=(8, 6))
    plt.plot(x_vals, y_vals, linewidth=2, marker="o", markersize=3)

    plt.scatter(x_vals[0], y_vals[0], s=80, label="Start")
    plt.scatter(x_vals[-1], y_vals[-1], s=80, label="End")

    plt.xlabel("X displacement / UTM Easting (m)")
    plt.ylabel("Y displacement / UTM Northing (m)")
    plt.title("ASV trajectory at f 20 and r 35")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()

    plt.savefig(PLOT_PATH, dpi=300, bbox_inches="tight")
    print("Plot saved to:", PLOT_PATH)

    plt.show()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
