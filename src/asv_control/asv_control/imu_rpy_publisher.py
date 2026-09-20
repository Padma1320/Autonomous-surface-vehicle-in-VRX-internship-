#!/usr/bin/env python3

import math
import re
import subprocess

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3


class IMUPublisher(Node):

    def __init__(self):

        super().__init__("imu_rpy_publisher")

        self.imu_pub = self.create_publisher(
            Imu,
            "/asv/imu",
            10
        )

        self.rpy_pub = self.create_publisher(
            Vector3,
            "/asv/imu_rpy",
            10
        )

        self.prev_roll = None
        self.prev_pitch = None
        self.prev_yaw = None
        self.prev_time = None

        self.timer = self.create_timer(
            0.2,
            self.read_gz_imu
        )

        self.get_logger().info(
            "Gazebo IMU publisher started"
        )

    def read_gz_imu(self):

        result = subprocess.run(
            [
                "timeout",
                "1",
                "gz",
                "topic",
                "-e",
                "-t",
                "/my_asv/imu"
            ],
            capture_output=True,
            text=True
        )

        text = result.stdout

        qx = self.get_block_value(
            text,
            "orientation",
            "x"
        )

        qy = self.get_block_value(
            text,
            "orientation",
            "y"
        )

        qz = self.get_block_value(
            text,
            "orientation",
            "z"
        )

        qw = self.get_block_value(
            text,
            "orientation",
            "w"
        )

        if None in [qx, qy, qz, qw]:
            return

        now = self.get_clock().now()

        roll, pitch, yaw = self.quat_to_rpy(
            qx,
            qy,
            qz,
            qw
        )

        angular_x = 0.0
        angular_y = 0.0
        angular_z = 0.0

        if self.prev_time is not None:

            dt = (
                now - self.prev_time
            ).nanoseconds / 1e9

            if dt > 0.0:

                angular_x = self.wrap_angle(
                    roll - self.prev_roll
                ) / dt

                angular_y = self.wrap_angle(
                    pitch - self.prev_pitch
                ) / dt

                angular_z = self.wrap_angle(
                    yaw - self.prev_yaw
                ) / dt

        imu_msg = Imu()

        imu_msg.header.stamp = now.to_msg()
        imu_msg.header.frame_id = "imu_link"

        imu_msg.orientation.x = qx
        imu_msg.orientation.y = qy
        imu_msg.orientation.z = qz
        imu_msg.orientation.w = qw

        imu_msg.angular_velocity.x = angular_x
        imu_msg.angular_velocity.y = angular_y
        imu_msg.angular_velocity.z = angular_z

        imu_msg.linear_acceleration.x = 0.0
        imu_msg.linear_acceleration.y = 0.0
        imu_msg.linear_acceleration.z = 0.0

        # Orientation available, covariance unknown
        imu_msg.orientation_covariance = [
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0
        ]

        # Angular velocity available, covariance unknown
        imu_msg.angular_velocity_covariance = [
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0
        ]

        # Linear acceleration is NOT available
        imu_msg.linear_acceleration_covariance[0] = -1.0

        self.imu_pub.publish(imu_msg)

        rpy_msg = Vector3()

        rpy_msg.x = math.degrees(roll)
        rpy_msg.y = math.degrees(pitch)
        rpy_msg.z = math.degrees(yaw)

        self.rpy_pub.publish(rpy_msg)

        self.get_logger().info(
            f"ROLL={rpy_msg.x:.2f}, "
            f"PITCH={rpy_msg.y:.2f}, "
            f"YAW={rpy_msg.z:.2f}, "
            f"YAW_RATE={angular_z:.4f} rad/s"
        )

        self.prev_roll = roll
        self.prev_pitch = pitch
        self.prev_yaw = yaw
        self.prev_time = now

    def get_block_value(
        self,
        text,
        block,
        key
    ):

        pattern = (
            block
            + r"\s*\{[^}]*"
            + key
            + r":\s*([-+eE0-9\.]+)"
        )

        match = re.search(
            pattern,
            text
        )

        if match:
            return float(match.group(1))

        return None

    def quat_to_rpy(
        self,
        x,
        y,
        z,
        w
    ):

        roll = math.atan2(
            2.0 * (w * x + y * z),
            1.0 - 2.0 * (x * x + y * y)
        )

        sinp = 2.0 * (w * y - z * x)

        pitch = math.asin(
            max(-1.0, min(1.0, sinp))
        )

        yaw = math.atan2(
            2.0 * (w * z + x * y),
            1.0 - 2.0 * (y * y + z * z)
        )

        return roll, pitch, yaw

    def wrap_angle(self, angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )


def main(args=None):

    rclpy.init(args=args)

    node = IMUPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
