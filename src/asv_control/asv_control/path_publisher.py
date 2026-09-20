#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Vector3, PoseStamped
from nav_msgs.msg import Path


class ASVPathPublisher(Node):

    def __init__(self):
        super().__init__('asv_path_publisher')

        self.path_pub = self.create_publisher(
            Path,
            '/asv/path',
            10
        )

        self.gps_sub = self.create_subscription(
            NavSatFix,
            '/asv/gps_data',
            self.gps_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Vector3,
            '/asv/imu_rpy',
            self.imu_callback,
            10
        )

        self.path = Path()
        self.path.header.frame_id = 'map'

        self.ref_lat = None
        self.ref_lon = None

        self.yaw_deg = 0.0

        # CG offset from model.sdf inertial pose:
        # <pose>-0.151 0.014 0.118 0 0 0</pose>
        # This shifts the path from GPS/base_link reference to ASV CG.
        self.cg_dx = -0.151
        self.cg_dy = 0.014

        self.get_logger().info(
            'ASV CG path publisher started: first GPS fix used as local origin'
        )

    def imu_callback(self, msg):
        # /asv/imu_rpy publishes yaw in degrees
        self.yaw_deg = msg.z

    def gps_callback(self, msg):

        if self.ref_lat is None:
            self.ref_lat = msg.latitude
            self.ref_lon = msg.longitude

            self.get_logger().info(
                f'Local GPS origin set: LAT={self.ref_lat:.8f}, '
                f'LON={self.ref_lon:.8f}'
            )

        # Convert latitude/longitude difference into local XY metres.
        # x = East-West displacement
        # y = North-South displacement
        meters_per_deg_lat = 110540.0
        meters_per_deg_lon = 111320.0 * math.cos(
            math.radians(self.ref_lat)
        )

        gps_x = (msg.longitude - self.ref_lon) * meters_per_deg_lon
        gps_y = (msg.latitude - self.ref_lat) * meters_per_deg_lat

        yaw_rad = math.radians(self.yaw_deg)

        # Rotate CG offset from body frame into map/world frame.
        # This makes the published path follow ASV CG, not GPS point.
        cg_x_world = (
            self.cg_dx * math.cos(yaw_rad)
            - self.cg_dy * math.sin(yaw_rad)
        )

        cg_y_world = (
            self.cg_dx * math.sin(yaw_rad)
            + self.cg_dy * math.cos(yaw_rad)
        )

        x = gps_x + cg_x_world
        y = gps_y + cg_y_world

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        pose.pose.orientation.w = 1.0

        self.path.header.stamp = self.get_clock().now().to_msg()
        self.path.poses.append(pose)

        self.path_pub.publish(self.path)

        self.get_logger().info(
            f'CG path point: x={x:.2f}, y={y:.2f}, '
            f'gps_x={gps_x:.2f}, gps_y={gps_y:.2f}, '
            f'yaw={self.yaw_deg:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ASVPathPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
