#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from stereo_msgs.msg import DisparityImage


class DisparityWindowFixer(Node):
    def __init__(self):
        super().__init__('disparity_window_fixer')

        self.sub = self.create_subscription(
            DisparityImage,
            '/disparity',
            self.cb,
            qos_profile_sensor_data
        )

        self.pub = self.create_publisher(
            DisparityImage,
            '/disparity_fixed',
            qos_profile_sensor_data
        )

    def cb(self, msg):
        # Fix invalid unsigned-underflow valid_window from stereo_image_proc
        msg.valid_window.x_offset = 70
        msg.valid_window.y_offset = 7
        msg.valid_window.width = msg.image.width - msg.valid_window.x_offset
        msg.valid_window.height = msg.image.height - msg.valid_window.y_offset

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DisparityWindowFixer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
