import math
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class ASVCommandInterface(Node):
    def __init__(self):
        super().__init__("asv_command_interface")

        self.thruster_pub = self.create_publisher(
            Float64,
            "/asv/thruster_cmd",
            10
        )

        self.rudder_pub = self.create_publisher(
            Float64,
            "/asv/rudder_cmd",
            10
        )

        self.get_logger().info("ASV real-time command interface started")

    def publish_thruster(self, value):
        msg = Float64()
        msg.data = float(value)
        self.thruster_pub.publish(msg)
        self.get_logger().info(f"Published /asv/thruster_cmd = {value}")

    def publish_rudder_deg(self, deg):
        rad = math.radians(float(deg))
        msg = Float64()
        msg.data = rad
        self.rudder_pub.publish(msg)
        self.get_logger().info(
            f"Published /asv/rudder_cmd = {deg} deg = {rad:.3f} rad"
        )

    def neutral(self):
        self.publish_thruster(0.0)
        self.publish_rudder_deg(0.0)


def main(args=None):
    rclpy.init(args=args)
    node = ASVCommandInterface()

    print("""
================ ASV REAL-TIME COMMAND INTERFACE ================

Commands:
  f 4        -> forward thrust 4
  b -4       -> backward thrust -4
  r 25       -> rudder right 25 degrees
  l 35       -> rudder left 35 degrees
  s          -> stop thrust only
  n          -> neutral: stop thrust + center rudder
  q          -> quit

Example:
  f 4
  r 25
  l 35
  b -4
  n

=================================================================
""")

    try:
        while rclpy.ok():
            user_input = input("ASV command > ").strip().split()

            if not user_input:
                continue

            cmd = user_input[0].lower()

            if cmd == "q":
                break

            elif cmd == "f":
                node.publish_thruster(float(user_input[1]))

            elif cmd == "b":
                node.publish_thruster(float(user_input[1]))

            elif cmd == "r":
                node.publish_rudder_deg(abs(float(user_input[1])))

            elif cmd == "l":
                node.publish_rudder_deg(-abs(float(user_input[1])))

            elif cmd == "s":
                node.publish_thruster(0.0)

            elif cmd == "n":
                node.neutral()

            else:
                print("Unknown command")

            rclpy.spin_once(node, timeout_sec=0.01)

    except KeyboardInterrupt:
        pass

    node.neutral()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
