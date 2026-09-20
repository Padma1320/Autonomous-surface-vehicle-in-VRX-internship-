#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64


class JoystickASVControl(Node):

    def __init__(self):
        super().__init__('joystick_asv_control')

        self.thruster_pub = self.create_publisher(
            Float64,
            '/asv/thruster_cmd',
            10
        )

        self.rudder_pub = self.create_publisher(
            Float64,
            '/asv/rudder_cmd',
            10
        )

        self.joy_sub = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )

        self.max_thrust = 30
        self.max_rudder = math.radians(35)
        self.deadzone = 0.02
        
        self.current_speed = 0.0
        self.speed_step = 0.25
        
        self.prev_a = 0
        self.prev_b = 0
        self.prev_y = 0

        self.get_logger().info('Joystick ASV control started')
        self.get_logger().info('Right stick up/down -> thrust')
        self.get_logger().info('Right stick left/right -> rudder')

    def apply_deadzone(self, value):
        if abs(value) < self.deadzone:
            return 0.0
        return value

    def joy_callback(self, msg):

        if len(msg.axes) < 5:
            return
        if len(msg.buttons) < 4:
            return

        # Logitech F310 X mode button mapping
        a_button = msg.buttons[0]
        b_button = msg.buttons[1]
        y_button = msg.buttons[3]

        # A button: increase available speed
        if a_button == 1 and self.prev_a == 0:
            self.current_speed = min(
                self.current_speed + self.speed_step,
                self.max_thrust
            )

        # B button: decrease available speed
        if b_button == 1 and self.prev_b == 0:
            self.current_speed = max(
                self.current_speed - self.speed_step,
                0.0
            )

        # Y button: stop
        if y_button == 1 and self.prev_y == 0:
            self.current_speed = 0.0

        self.prev_a = a_button
        self.prev_b = b_button
        self.prev_y = y_button

        thrust_axis = self.apply_deadzone(msg.axes[4])
        rudder_axis = self.apply_deadzone(msg.axes[3])

        thrust = -thrust_axis * self.max_thrust
        rudder = -rudder_axis * self.max_rudder

        thrust_msg = Float64()
        rudder_msg = Float64()

        thrust_msg.data = thrust
        rudder_msg.data = rudder

        self.thruster_pub.publish(thrust_msg)
        self.rudder_pub.publish(rudder_msg)

        self.get_logger().info(
            f'Thrust: {thrust:.2f}, Rudder: {rudder:.2f},Speed: {self.current_speed:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = JoystickASVControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
