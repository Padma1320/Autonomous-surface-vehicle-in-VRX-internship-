#!/usr/bin/env python3

import math
import numpy as np

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64

from stable_baselines3 import SAC, TD3


class RLWaypointFollower(Node):

    def __init__(self):
        super().__init__('rl_waypoint_follower')

        self.thruster_pub = self.create_publisher(Float64, '/asv/thruster_cmd', 10)
        self.rudder_pub = self.create_publisher(Float64, '/asv/rudder_cmd', 10)

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

        self.waypoint_sub = self.create_subscription(
            Path,
            '/asv/waypoints_gps',
            self.waypoint_callback,
            10
        )

        # Same GPS origin as your old controller
        self.origin_lat = -33.724223
        self.origin_lon = 150.679736

        self.x = 0.0
        self.y = 0.0
        self.yaw_deg = 0.0
        self.gps_received = False

        self.waypoints = []
        self.current_segment = 0
        self.last_waypoint_count = 0
        self.prev_distance_to_wp = None

        self.max_rudder = 0.61
        self.max_thrust = 20.0
        self.constant_thrust = 14.0
        self.arrival_radius = 5.0

        # Choose model here: "sac" or "td3"
        self.model_type = "sac"

        if self.model_type == "sac":
            self.model = SAC.load("/home/user/vrx_ws/rl_models/sac_asv_waypoint.zip")
            self.get_logger().info("Loaded SAC model")
        else:
            self.model = TD3.load("/home/user/vrx_ws/rl_models/td3_asv_waypoint.zip")
            self.get_logger().info("Loaded TD3 model")

        self.get_logger().info("RL Waypoint Follower Started")
        self.get_logger().info("State = [x, y, psi, e]")
        self.get_logger().info("Action = rudder only")
        self.get_logger().info("Thrust = constant 14 N")

    def gps_to_local_xy(self, lat, lon):
        meters_per_deg_lat = 111320.0
        meters_per_deg_lon = 111320.0 * math.cos(math.radians(self.origin_lat))

        x = (lon - self.origin_lon) * meters_per_deg_lon
        y = (lat - self.origin_lat) * meters_per_deg_lat

        return x, y

    def gps_callback(self, msg):
        self.x, self.y = self.gps_to_local_xy(msg.latitude, msg.longitude)
        self.gps_received = True
        self.control_loop()

    def imu_callback(self, msg):
        self.yaw_deg = msg.z

    def waypoint_callback(self, msg):
        gps_waypoints = []

        for pose in msg.poses:
            lat = pose.pose.position.x
            lon = pose.pose.position.y

            x, y = self.gps_to_local_xy(lat, lon)
            gps_waypoints.append((x, y))

        if len(gps_waypoints) == 0:
            return

        self.waypoints = gps_waypoints

        if len(self.waypoints) != self.last_waypoint_count:
            self.get_logger().info(f"Received {len(self.waypoints)} mouse-click waypoints")

            if len(self.waypoints) >= 2:
                self.current_segment = self.find_nearest_segment()

            self.last_waypoint_count = len(self.waypoints)

    def normalize_angle_deg(self, angle):
        while angle > 180.0:
            angle -= 360.0
        while angle < -180.0:
            angle += 360.0
        return angle

    def find_nearest_segment(self):
        if len(self.waypoints) < 2:
            return 0

        best_segment = 0
        best_distance = float('inf')

        for i in range(len(self.waypoints) - 1):
            dist = self.distance_to_segment(
                self.x,
                self.y,
                self.waypoints[i],
                self.waypoints[i + 1]
            )

            if dist < best_distance:
                best_distance = dist
                best_segment = i

        return best_segment

    def distance_to_segment(self, px, py, wp1, wp2):
        x1, y1 = wp1
        x2, y2 = wp2

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0.0 and dy == 0.0:
            return math.hypot(px - x1, py - y1)

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.hypot(px - closest_x, py - closest_y)

    def los_cte(self, wp1, wp2):
        x1, y1 = wp1
        x2, y2 = wp2

        dx = x2 - x1
        dy = y2 - y1

        path_angle = math.atan2(dy, dx)

        bx = self.x - x1
        by = self.y - y1

        # e = CTE
        e = -bx * math.sin(path_angle) + by * math.cos(path_angle)

        return e

    def control_loop(self):
        if not self.gps_received:
            self.publish_cmd(0.0, 0.0)
            return

        if len(self.waypoints) < 2:
            self.publish_cmd(0.0, 0.0)
            return

        if self.current_segment >= len(self.waypoints) - 1:
            self.publish_cmd(0.0, 0.0)
            self.get_logger().info("RL mission completed")
            return

        wp1 = self.waypoints[self.current_segment]
        wp2 = self.waypoints[self.current_segment + 1]

        distance_to_wp2 = math.hypot(wp2[0] - self.x, wp2[1] - self.y)

        if (
            distance_to_wp2 < self.arrival_radius or
            (
                self.prev_distance_to_wp is not None and
                distance_to_wp2 > self.prev_distance_to_wp and
                self.prev_distance_to_wp < 10.0
            )
        ):
            self.get_logger().info(
                f"Reached/passed waypoint {self.current_segment + 1} | "
                f"Distance={distance_to_wp2:.2f}"
            )
            self.current_segment += 1
            self.prev_distance_to_wp = None
            return

        self.prev_distance_to_wp = distance_to_wp2

        e = self.los_cte(wp1, wp2)

        # Convert yaw from degrees to radians because RL was trained in radians
        psi_rad = math.radians(self.yaw_deg)

        obs = np.array(
            [self.x, self.y, psi_rad, e],
            dtype=np.float32
        )

        action, _ = self.model.predict(obs, deterministic=True)

        rudder = float(action[0])
        rudder = max(min(rudder, self.max_rudder), -self.max_rudder)

        thrust = self.constant_thrust
        thrust = max(min(thrust, self.max_thrust), -self.max_thrust)

        self.publish_cmd(thrust, rudder)

        self.get_logger().info(
            f"RL | Pos=({self.x:.2f},{self.y:.2f}) "
            f"WP={self.current_segment}->{self.current_segment + 1} "
            f"Dist={distance_to_wp2:.2f} CTE={e:.2f} "
            f"Yaw={self.yaw_deg:.2f} "
            f"Thrust={thrust:.2f} Rudder={rudder:.3f}"
        )

    def publish_cmd(self, thrust, rudder):
        t = Float64()
        r = Float64()

        t.data = thrust
        r.data = rudder

        self.thruster_pub.publish(t)
        self.rudder_pub.publish(r)


def main(args=None):
    rclpy.init(args=args)
    node = RLWaypointFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
