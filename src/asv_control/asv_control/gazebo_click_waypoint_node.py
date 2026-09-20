#!/usr/bin/env python3

import math
import subprocess

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, PointStamped
from nav_msgs.msg import Path


class GazeboClickWaypointNode(Node):
    def __init__(self):
        super().__init__("gazebo_click_waypoint_node")

        self.origin_lat = 12.96696941985891
        self.origin_lon = 80.29720408369546

        self.waypoints = []

        self.path_pub = self.create_publisher(Path, "/asv/waypoints", 10)

        # RViz clicked point topic
        # In RViz, use "Publish Point" tool and click on ocean/map.
        self.click_sub = self.create_subscription(
            PointStamped,
            "/clicked_point",
            self.clicked_point_callback,
            10
        )

        self.get_logger().info("Waypoint click node started.")
        self.get_logger().info("Click points in RViz using Publish Point tool.")
        self.get_logger().info("Publishing waypoints on /asv/waypoints")

    def xy_to_latlon(self, x, y):
        meters_per_deg_lat = 111320.0
        meters_per_deg_lon = 111320.0 * math.cos(math.radians(self.origin_lat))

        lat = self.origin_lat + (y / meters_per_deg_lat)
        lon = self.origin_lon + (x / meters_per_deg_lon)

        return lat, lon

    def clicked_point_callback(self, msg):
        x = msg.point.x
        y = msg.point.y
        z = 1.0

        lat, lon = self.xy_to_latlon(x, y)

        self.waypoints.append((x, y, lat, lon))

        wp_id = len(self.waypoints)

        self.get_logger().info(
            f"WP{wp_id}: x={x:.2f}, y={y:.2f}, lat={lat:.8f}, lon={lon:.8f}"
        )

        self.spawn_marker(wp_id, x, y, z)
        self.publish_path()

    def spawn_marker(self, wp_id, x, y, z):
        marker_name = f"gps_waypoint_{wp_id}"

        sdf = f"""
<sdf version='1.9'>
  <model name='{marker_name}'>
    <static>true</static>
    <pose>{x} {y} {z} 0 0 0</pose>

    <link name='link'>

      <visual name='pin_body'>
        <pose>0 0 1.0 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.35</radius>
            <length>2.0</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
          <emissive>1 0 0 1</emissive>
        </material>
      </visual>

      <visual name='pin_head'>
        <pose>0 0 2.2 0 0 0</pose>
        <geometry>
          <sphere>
            <radius>0.7</radius>
          </sphere>
        </geometry>
        <material>
          <ambient>1 1 0 1</ambient>
          <diffuse>1 1 0 1</diffuse>
          <emissive>1 1 0 1</emissive>
        </material>
      </visual>

    </link>
  </model>
</sdf>
"""

        cmd = [
            "gz", "service",
            "-s", "/world/sydney_regatta/create",
            "--reqtype", "gz.msgs.EntityFactory",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "10000",
            "--req", f'sdf:"{sdf}", name:"{marker_name}"'
        ]

        try:
            subprocess.run(cmd, check=True)
            self.get_logger().info(f"Spawned marker {marker_name}")
        except Exception as e:
            self.get_logger().error(f"Marker spawn failed: {e}")

    def publish_path(self):
        path = Path()
        path.header.frame_id = "map"
        path.header.stamp = self.get_clock().now().to_msg()

        for i, (x, y, lat, lon) in enumerate(self.waypoints):
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.header.stamp = self.get_clock().now().to_msg()

            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = 0.0

            pose.pose.orientation.w = 1.0

            path.poses.append(pose)

        self.path_pub.publish(path)


def main(args=None):
    rclpy.init(args=args)
    node = GazeboClickWaypointNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
