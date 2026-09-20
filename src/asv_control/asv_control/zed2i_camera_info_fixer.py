#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CameraInfo


class Zed2iCameraInfoFixer(Node):
    def __init__(self):
        super().__init__('zed2i_camera_info_fixer')

        self.baseline = 0.12  # left/right separation = 12 cm

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.left_pub = self.create_publisher(
            CameraInfo,
            '/my_asv/zed2i/left/camera_info_fixed',
            qos
        )

        self.right_pub = self.create_publisher(
            CameraInfo,
            '/my_asv/zed2i/right/camera_info_fixed',
            qos
        )

        self.create_subscription(
            CameraInfo,
            '/my_asv/zed2i/left/camera_info',
            self.left_callback,
            10
        )

        self.create_subscription(
            CameraInfo,
            '/my_asv/zed2i/right/camera_info',
            self.right_callback,
            10
        )

    def left_callback(self, msg):
        fixed = msg
        fixed.p[3] = 0.0
        self.left_pub.publish(fixed)

    def right_callback(self, msg):
        fixed = msg
        fx = fixed.k[0]
        fixed.p[3] = -fx * self.baseline
        self.right_pub.publish(fixed)


def main(args=None):
    rclpy.init(args=args)
    node = Zed2iCameraInfoFixer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
