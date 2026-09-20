import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64 , String , Float32


class ASVGazeboRelay(Node):
    def __init__(self):
        super().__init__("asv_gz_relay")

        self.create_subscription(
            Float64,
            "/asv/thruster_cmd",
            self.thruster_callback,
            10
        )

        self.create_subscription(
            Float64,
            "/asv/rudder_cmd",
            self.rudder_callback,
            10
        )

        self.get_logger().info("ASV Gazebo relay started")
        self.get_logger().info("Listening to /asv/thruster_cmd and /asv/rudder_cmd")

    def send_gz_double(self, topic, value):
        subprocess.run(
            [
                "gz", "topic",
                "-t", topic,
                "-m", "gz.msgs.Double",
                "-p", f"data: {float(value)}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def thruster_callback(self, msg):
        self.send_gz_double(
            "/model/my_asv/joint/thruster_joint/cmd_thrust",
            msg.data
        )
        self.get_logger().info(f"Sent Gazebo thrust = {msg.data}")

    def rudder_callback(self, msg):
        self.send_gz_double(
            "/model/my_asv/joint/rudder_joint/0/cmd_pos",
            msg.data
        )
        self.get_logger().info(f"Sent Gazebo rudder = {msg.data:.3f} rad")


def main(args=None):
    rclpy.init(args=args)
    node = ASVGazeboRelay()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
