#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float64
from geometry_msgs.msg import Pose
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity


class NomotoGzPoseSim(Node):
    def __init__(self):
        super().__init__("nomoto_gz_pose_sim")

        self.T = 2.5
        self.K = 0.15

        self.max_thrust = 30.0
        self.max_speed = 0.3

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.r = 0.0

        self.thrust_cmd = 0.0
        self.rudder_cmd_deg = 0.0

        self.dt = 0.02

        self.create_subscription(Float64, "/asv/thruster_cmd", self.thrust_callback, 10)
        self.create_subscription(Float64, "/asv/rudder_cmd", self.rudder_callback, 10)

        self.client = self.create_client(SetEntityPose, "/world/sydney_regatta/set_pose")

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for Gazebo set_pose service...")

        self.timer = self.create_timer(self.dt, self.update)

        self.get_logger().info("Nomoto Gazebo pose simulator started")

    def thrust_callback(self, msg):
        self.thrust_cmd = msg.data

    def rudder_callback(self, msg):
        self.rudder_cmd_deg = msg.data

    def update(self):
        delta = math.radians(self.rudder_cmd_deg)

        U = (self.thrust_cmd / self.max_thrust) * self.max_speed

        r_dot = (self.K * delta - self.r) / self.T
        self.r += r_dot * self.dt
        self.yaw += self.r * self.dt

        self.x += U * math.cos(self.yaw) * self.dt
        self.y += U * math.sin(self.yaw) * self.dt

        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        req = SetEntityPose.Request()
        req.entity = Entity()
        req.entity.name = "my_asv"
        req.entity.type = Entity.MODEL

        req.pose = Pose()
        req.pose.position.x = self.x
        req.pose.position.y = self.y
        req.pose.position.z = 0.5

        req.pose.orientation.x = 0.0
        req.pose.orientation.y = 0.0
        req.pose.orientation.z = qz
        req.pose.orientation.w = qw

        self.client.call_async(req)


def main(args=None):
    rclpy.init(args=args)
    node = NomotoGzPoseSim()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
