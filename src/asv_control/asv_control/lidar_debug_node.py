#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan


class LidarDebugNode(Node):
    def __init__(self):
        super().__init__("lidar_debug_node")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.sub = self.create_subscription(
            LaserScan,
            "/my_asv/lidar",
            self.lidar_callback,
            qos
        )

        self.get_logger().info("LiDAR debug node started. Waiting for /my_asv/lidar...")

    def sector_min(self, msg, deg_min, deg_max):
        vals = []

        for i, r in enumerate(msg.ranges):
            angle = msg.angle_min + i * msg.angle_increment
            deg = math.degrees(angle)

            if deg_min <= deg <= deg_max:
                if math.isfinite(r) and msg.range_min <= r <= msg.range_max:
                    vals.append(r)

        return min(vals) if vals else float("inf")

    def lidar_callback(self, msg):
        front = self.sector_min(msg, -20, 20)
        left = self.sector_min(msg, 20, 90)
        right = self.sector_min(msg, -90, -20)

        obstacle = front < 5.0

        self.get_logger().info(
            f"LiDAR | front={front:.2f} m | left={left:.2f} m | right={right:.2f} m | obstacle={obstacle}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = LidarDebugNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
