#!/usr/bin/env python3

import csv
import os

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import TwistStamped

from message_filters import Subscriber, ApproximateTimeSynchronizer


class SensorSyncLogger(Node):

    def __init__(self):
        super().__init__("sensor_sync_logger")

        self.output_file = os.path.expanduser(
            "~/vrx_ws/sensor_sync_log.csv"
        )

        self.gps_sub = Subscriber(
            self,
            NavSatFix,
            "/asv/gps_data"
        )

        self.imu_sub = Subscriber(
            self,
            Imu,
            "/asv/imu"
        )

        self.dvl_sub = Subscriber(
            self,
            TwistStamped,
            "/asv/dvl/velocity"
        )

        self.sync = ApproximateTimeSynchronizer(
            [
                self.gps_sub,
                self.imu_sub,
                self.dvl_sub
            ],
            queue_size=30,
            slop=0.25
        )

        self.sync.registerCallback(
            self.synced_callback
        )

        self.csv_file = open(
            self.output_file,
            "w",
            newline=""
        )

        self.writer = csv.writer(
            self.csv_file
        )

        self.writer.writerow([
            "stamp_sec",
            "stamp_nanosec",

            "gps_latitude",
            "gps_longitude",
            "gps_altitude",

            "imu_orientation_x",
            "imu_orientation_y",
            "imu_orientation_z",
            "imu_orientation_w",

            "imu_angular_velocity_x",
            "imu_angular_velocity_y",
            "imu_angular_velocity_z",

            "imu_linear_acceleration_x",
            "imu_linear_acceleration_y",
            "imu_linear_acceleration_z",

            "dvl_linear_x",
            "dvl_linear_y",
            "dvl_linear_z",

            "dvl_angular_x",
            "dvl_angular_y",
            "dvl_angular_z"
        ])

        self.get_logger().info(
            f"Sensor sync logger started: {self.output_file}"
        )

    def synced_callback(
        self,
        gps_msg,
        imu_msg,
        dvl_msg
    ):
        stamp = gps_msg.header.stamp

        row = [
            stamp.sec,
            stamp.nanosec,

            gps_msg.latitude,
            gps_msg.longitude,
            gps_msg.altitude,

            imu_msg.orientation.x,
            imu_msg.orientation.y,
            imu_msg.orientation.z,
            imu_msg.orientation.w,

            imu_msg.angular_velocity.x,
            imu_msg.angular_velocity.y,
            imu_msg.angular_velocity.z,

            imu_msg.linear_acceleration.x,
            imu_msg.linear_acceleration.y,
            imu_msg.linear_acceleration.z,

            dvl_msg.twist.linear.x,
            dvl_msg.twist.linear.y,
            dvl_msg.twist.linear.z,

            dvl_msg.twist.angular.x,
            dvl_msg.twist.angular.y,
            dvl_msg.twist.angular.z
        ]

        self.writer.writerow(row)
        self.csv_file.flush()

        self.get_logger().info(
            f"SYNC t={stamp.sec}.{stamp.nanosec}: "
            f"lat={gps_msg.latitude:.8f}, "
            f"lon={gps_msg.longitude:.8f}, "
            f"yaw_qz={imu_msg.orientation.z:.3f}, "
            f"dvl_vx={dvl_msg.twist.linear.x:.3f}, "
            f"dvl_vy={dvl_msg.twist.linear.y:.3f}"
        )

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = SensorSyncLogger()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
