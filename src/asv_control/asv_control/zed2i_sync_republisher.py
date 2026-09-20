#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, CameraInfo


class Zed2iSyncRepublisher(Node):
    def __init__(self):
        super().__init__('zed2i_sync_republisher')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.baseline = 0.12  # 12 cm stereo baseline

        self.left_img = None
        self.right_img = None
        self.left_info = None
        self.right_info = None

        self.create_subscription(
            Image,
            '/my_asv/zed2i/left/image',
            self.left_img_cb,
            qos
        )

        self.create_subscription(
            Image,
            '/my_asv/zed2i/right/image',
            self.right_img_cb,
            qos
        )

        self.create_subscription(
            CameraInfo,
            '/my_asv/zed2i/left/camera_info',
            self.left_info_cb,
            qos
        )

        self.create_subscription(
            CameraInfo,
            '/my_asv/zed2i/right/camera_info',
            self.right_info_cb,
            qos
        )

        self.left_img_pub = self.create_publisher(
            Image,
            '/my_asv/zed2i_sync/left/image_rect',
            qos
        )

        self.right_img_pub = self.create_publisher(
            Image,
            '/my_asv/zed2i_sync/right/image_rect',
            qos
        )

        self.left_info_pub = self.create_publisher(
            CameraInfo,
            '/my_asv/zed2i_sync/left/camera_info',
            qos
        )

        self.right_info_pub = self.create_publisher(
            CameraInfo,
            '/my_asv/zed2i_sync/right/camera_info',
            qos
        )

        self.timer = self.create_timer(0.2, self.publish_synced)  # 5 Hz

    def left_img_cb(self, msg):
        self.left_img = msg

    def right_img_cb(self, msg):
        self.right_img = msg

    def left_info_cb(self, msg):
        self.left_info = msg

    def right_info_cb(self, msg):
        self.right_info = msg

    def publish_synced(self):
        if None in [self.left_img, self.right_img, self.left_info, self.right_info]:
            missing = []

            if self.left_img is None:
                missing.append("LEFT IMAGE")

            if self.right_img is None:
                missing.append("RIGHT IMAGE")

            if self.left_info is None:
                missing.append("LEFT INFO")

            if self.right_info is None:
                missing.append("RIGHT INFO")

            self.get_logger().warn("Missing: " + ", ".join(missing))
            return

        stamp = self.get_clock().now().to_msg()

        left_img = self.left_img
        right_img = self.right_img
        left_info = self.left_info
        right_info = self.right_info

        left_img.header.stamp = stamp
        right_img.header.stamp = stamp
        left_info.header.stamp = stamp
        right_info.header.stamp = stamp

        left_img.header.frame_id = 'zed2i_left_camera'
        right_img.header.frame_id = 'zed2i_right_camera'
        left_info.header.frame_id = 'zed2i_left_camera'
        right_info.header.frame_id = 'zed2i_right_camera'

        left_info.p[3] = 0.0
        fx = right_info.k[0]
        right_info.p[3] = -fx * self.baseline

        self.left_img_pub.publish(left_img)
        self.right_img_pub.publish(right_img)
        self.left_info_pub.publish(left_info)
        self.right_info_pub.publish(right_info)

        self.get_logger().info('Published synced stereo pair')


def main(args=None):
    rclpy.init(args=args)
    node = Zed2iSyncRepublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
