#!/usr/bin/env python3

import re
import subprocess

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus


class GPSPublisher(Node):

    def __init__(self):
        super().__init__("gps_publisher")

        self.pub = self.create_publisher(
            NavSatFix,
            "/asv/gps_data",
            10
        )

        self.timer = self.create_timer(
            0.2,
            self.read_gz_gps
        )

        self.get_logger().info(
            "Gazebo GPS to ROS2 NavSatFix publisher started"
        )

    def read_gz_gps(self):

        result = subprocess.run(
            [
                "timeout",
                "1",
                "gz",
                "topic",
                "-e",
                "-t",
                "/my_asv/gps"
            ],
            capture_output=True,
            text=True
        )

        text = result.stdout

        lat = self.get_value(
            text,
            "latitude_deg"
        )

        lon = self.get_value(
            text,
            "longitude_deg"
        )

        alt = self.get_value(
            text,
            "altitude"
        )

        if None in [lat, lon, alt]:
            return

        msg = NavSatFix()

        msg.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )

        msg.header.frame_id = "gps_link"

        msg.status.status = (
            NavSatStatus.STATUS_FIX
        )

        msg.status.service = (
            NavSatStatus.SERVICE_GPS
        )

        msg.latitude = lat
        msg.longitude = lon
        msg.altitude = alt

        msg.position_covariance = [
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0
        ]

        msg.position_covariance_type = (
            NavSatFix.COVARIANCE_TYPE_UNKNOWN
        )

        self.pub.publish(msg)

        # Easy terminal log
        self.get_logger().info(
            f"LAT={lat:.8f}, "
            f"LON={lon:.8f}, "
            f"ALT={alt:.2f}"
        )

    def get_value(
        self,
        text,
        key
    ):

        pattern = (
            key
            + r":\s*([-+eE0-9\.]+)"
        )

        match = re.search(
            pattern,
            text
        )

        if match:
            return float(
                match.group(1)
            )

        return None


def main(args=None):

    rclpy.init(args=args)

    node = GPSPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
