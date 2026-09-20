#!/usr/bin/env python3

import math
import subprocess
from collections import deque

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import Vector3


class GazeboPathTrail(Node):

    def __init__(self):
        super().__init__('gazebo_path_trail')

        self.path_sub = self.create_subscription(
            Path,
            '/asv/path',
            self.path_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Vector3,
            '/asv/imu_rpy',
            self.imu_callback,
            10
        )

        self.current_yaw_deg = 0.0

        self.last_x = None
        self.last_y = None
        self.count = 0

        # Spawn one road piece every 1 m
        self.min_distance = 1.0

        # Keep only latest 20 pieces
        self.max_pieces = 20
        self.spawned_names = deque()

        self.road_stl = (
            'file:///home/user/vrx_ws/src/vrx/vrx_gz/models/my_asv/meshes/Road_centered.STL'
        )

        self.get_logger().info(
            'Gazebo Road.STL trail started: rolling 20-piece trail'
        )

    def imu_callback(self, msg):
        self.current_yaw_deg = msg.z

    def path_callback(self, msg):

        if len(msg.poses) == 0:
            return

        pose = msg.poses[-1].pose

        x = pose.position.x
        y = pose.position.y

        if self.last_x is not None:
            dist = math.sqrt(
                (x - self.last_x) ** 2 +
                (y - self.last_y) ** 2
            )

            if dist < self.min_distance:
                return

        yaw_rad = math.radians(self.current_yaw_deg)

        self.spawn_road_piece(x, y, yaw_rad)

        self.last_x = x
        self.last_y = y

    def spawn_road_piece(self, x, y, yaw_rad):

        name = f'trail_road_{self.count}'
        self.count += 1

        req = (
            'sdf:"<sdf version=\'1.9\'>'
            f'<model name=\'{name}\'>'
            '<static>true</static>'
            f'<pose>{x} {y} 0.03 0 0 {yaw_rad}</pose>'
            '<link name=\'link\'>'
            '<visual name=\'visual\'>'
            '<geometry>'
            '<mesh>'
            f'<uri>{self.road_stl}</uri>'
            '<scale>0.08 0.08 0.08</scale>'
            '</mesh>'
            '</geometry>'
            '<material>'
            '<ambient>0.1 0.1 0.1 1</ambient>'
            '<diffuse>0.1 0.1 0.1 1</diffuse>'
            '<emissive>0.02 0.02 0.02 1</emissive>'
            '</material>'
            '</visual>'
            '</link>'
            '</model>'
            '</sdf>",'
            f'name:"{name}"'
        )

        cmd = [
            'gz', 'service',
            '-s', '/world/sydney_regatta/create',
            '--reqtype', 'gz.msgs.EntityFactory',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '5000',
            '--req', req
        ]

        subprocess.run(cmd)

        self.spawned_names.append(name)

        # Keep only latest 20 pieces
        if len(self.spawned_names) > self.max_pieces:
            old_name = self.spawned_names.popleft()
            self.delete_model(old_name)

        self.get_logger().info(
            f'Road trail spawned: {name}'
        )

    def delete_model(self, name):

        req = f'name: "{name}", type: MODEL'

        cmd = [
            'gz', 'service',
            '-s', '/world/sydney_regatta/remove',
            '--reqtype', 'gz.msgs.Entity',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '5000',
            '--req', req
        ]

        subprocess.run(cmd)

        self.get_logger().info(
            f'Removed old trail piece: {name}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = GazeboPathTrail()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
