#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64 ,String, Float32


class AdaptiveLOSPIDFollower(Node):

    def __init__(self):
        super().__init__('adaptive_los_pid_follower')

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

        self.origin_lat = -33.724223
        self.origin_lon = 150.679736

        self.x = 0.0
        self.y = 0.0
        self.yaw_deg = 0.0
        self.yaw_rate = 0.0
        self.gps_received = False

        self.waypoints = []
        self.last_waypoint_count = 0
        self.current_segment = 0
        self.prev_distance_to_wp = None
        # LOS + PD controller
        self.kp = 0.004
        self.kd = 0.025
       
        self.prev_time = self.get_clock().now()

        # Command limits
        self.max_rudder = 0.61
        self.max_thrust = 20.0

        # Fixed waypoint acceptance radius
        self.arrival_radius = 5.0

        self.get_logger().info('LOS + PD Follower Started')
        self.get_logger().info(
            'Subscribing to /asv/gps_data, /asv/imu_rpy, /asv/waypoints_gps'
        )

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
        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds / 1e9

        new_yaw = msg.z

        if dt > 0.0:
            yaw_diff = self.normalize_angle(new_yaw - self.yaw_deg)
            self.yaw_rate = yaw_diff / dt

        self.yaw_deg = new_yaw
        self.prev_time = now

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
            self.get_logger().info(f'Received {len(self.waypoints)} GPS waypoints')

            if len(self.waypoints) >= 2:
                self.current_segment = self.find_nearest_segment()

            self.last_waypoint_count = len(self.waypoints)

    def normalize_angle(self, angle):
        while angle > 180.0:
            angle -= 360.0
        while angle < -180.0:
            angle += 360.0
        return angle

    def segment_length(self, wp1, wp2):
        return math.hypot(wp2[0] - wp1[0], wp2[1] - wp1[1])

    def lookahead_distance(self, wp1, wp2):
        length = self.segment_length(wp1, wp2)
        lookahead = 4# 0.25 * length
        return max(4.0, min(25.0, lookahead))

    def los_guidance(self, wp1, wp2, lookahead):
        x1, y1 = wp1
        x2, y2 = wp2

        dx = x2 - x1
        dy = y2 - y1

        # Path angle gamma
        path_angle = math.atan2(dy, dx)

        bx = self.x - x1
        by = self.y - y1

        # Cross-track error Ye
        cross_track = -bx * math.sin(path_angle) + by * math.cos(path_angle)

        # LOS correction atan(-Ye / Delta)
        correction = math.atan2(-cross_track, lookahead)

        # Desired heading psi_d
        desired_heading = path_angle + correction

        return math.degrees(desired_heading), cross_track

    def pd_heading_control(self, heading_error):
       rudder = -self.kp * heading_error + self.kd * self.yaw_rate
       rudder = max(min(rudder, self.max_rudder), -self.max_rudder)
       return rudder
    def adaptive_thrust(self, heading_error):
       abs_error = abs(heading_error)

       if abs_error > 35.0:
          return 0.7

       if abs_error > 15.0:
          return 1.0

       return self.max_thrust

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

    def control_loop(self):
        if not self.gps_received:
            self.publish_cmd(0.0, 0.0)
            return

        if len(self.waypoints) < 2:
            self.publish_cmd(0.0, 0.0)
            return

        if self.current_segment >= len(self.waypoints) - 1:
            self.publish_cmd(0.0, 0.0)
            self.get_logger().info('LOS + PD mission completed')
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
              f'Reached/passed waypoint {self.current_segment + 1} | '
              f'Distance={distance_to_wp2:.2f} Radius={self.arrival_radius:.2f}'
    )
           self.current_segment += 1
           self.prev_distance_to_wp = None
           return
        self.prev_distance_to_wp = distance_to_wp2
        lookahead = self.lookahead_distance(wp1, wp2)

        desired_heading, cross_track = self.los_guidance(wp1, wp2, lookahead)

        heading_error = self.normalize_angle(desired_heading - self.yaw_deg)
        rudder = self.pd_heading_control(heading_error)
        
        desired_thrust = 14.0

        thrust = max(
        min(desired_thrust, self.max_thrust),
        -self.max_thrust
)
       
        self.publish_cmd(thrust, rudder)

        self.get_logger().info(
            f'LOS_PD | Pos=({self.x:.2f},{self.y:.2f}) '
            f'WP={self.current_segment}->{self.current_segment + 1} '
            f'Dist={distance_to_wp2:.2f} CTE={cross_track:.2f} '
            f'Lookahead={lookahead:.2f} Radius={self.arrival_radius:.2f} '
            f'Yaw={self.yaw_deg:.2f} Desired={desired_heading:.2f} '
            f'Err={heading_error:.2f} YawRate={self.yaw_rate:.2f} '
            f'Thrust={thrust:.2f} Rudder={rudder:.2f}'
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
    node = AdaptiveLOSPIDFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
