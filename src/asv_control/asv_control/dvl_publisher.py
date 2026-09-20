#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import TwistStamped


class DVLSimPublisher(Node):

    def __init__(self):

        super().__init__(
            "dvl_publisher"
        )

        self.origin_lat = -33.724223

        self.origin_lon = 150.679736

        self.prev_x = None
        self.prev_y = None
        self.prev_time = None

        self.gps_sub = (
            self.create_subscription(
                NavSatFix,
                "/asv/gps_data",
                self.gps_callback,
                10
            )
        )

        self.dvl_pub = (
            self.create_publisher(
                TwistStamped,
                "/asv/dvl/velocity",
                10
            )
        )

        self.get_logger().info(
            "Simulated DVL publisher started"
        )

    def gps_to_xy(
        self,
        lat,
        lon
    ):

        meters_per_deg_lat = (
            111320.0
        )

        meters_per_deg_lon = (
            111320.0
            * math.cos(
                math.radians(
                    self.origin_lat
                )
            )
        )

        x = (
            lon
            - self.origin_lon
        ) * meters_per_deg_lon

        y = (
            lat
            - self.origin_lat
        ) * meters_per_deg_lat

        return x, y

    def gps_callback(
        self,
        msg
    ):

        x, y = self.gps_to_xy(
            msg.latitude,
            msg.longitude
        )

        now = (
            self.get_clock()
            .now()
        )

        if self.prev_x is None:

            self.prev_x = x
            self.prev_y = y
            self.prev_time = now

            return

        dt = (
            now
            - self.prev_time
        ).nanoseconds / 1e9

        if dt <= 0.0:
            return

        vx = (
            x
            - self.prev_x
        ) / dt

        vy = (
            y
            - self.prev_y
        ) / dt

        dvl_msg = TwistStamped()

        dvl_msg.header.stamp = (
            now.to_msg()
        )

        dvl_msg.header.frame_id = (
            "dvl_link"
        )

        dvl_msg.twist.linear.x = vx

        dvl_msg.twist.linear.y = vy

        dvl_msg.twist.linear.z = 0.0

        dvl_msg.twist.angular.x = 0.0

        dvl_msg.twist.angular.y = 0.0

        dvl_msg.twist.angular.z = 0.0

        self.dvl_pub.publish(
            dvl_msg
        )

        # Easy terminal log
        self.get_logger().info(
            f"DVL velocity: "
            f"vx={vx:.3f} m/s, "
            f"vy={vy:.3f} m/s"
        )

        self.prev_x = x

        self.prev_y = y

        self.prev_time = now


def main(args=None):

    rclpy.init(args=args)

    node = DVLSimPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
