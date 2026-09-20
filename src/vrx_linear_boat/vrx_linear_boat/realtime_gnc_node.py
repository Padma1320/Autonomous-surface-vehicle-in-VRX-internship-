import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TransformStamped
from sensor_msgs.msg import Imu
import tf2_ros
import numpy as np
import math

class RealTimeMarineGnc(Node):
    def __init__(self):
        super().__init__('realtime_marine_gnc')
        
        # Rigid Structural Parameters
        self.Ixx = 0.525
        self.Iyy = 2.77
        self.Izz = 2.77
        self.mass = 10.0 
        
        # 12-State Vector: [x, y, z, roll, pitch, yaw, u, v, w, p, q, r]
        self.state = np.zeros(12)
        
        # Real-Time Target Memory Registers
        self.target_x = 0.0
        self.target_y = 0.0
        self.active_mission = False
        
        # Tuned PID Constants for Rapid Real-Time Response
        self.kp_surge = 5.0
        self.ki_surge = 0.02
        self.kd_surge = 1.2
        self.surge_integral = 0.0
        self.prev_surge_err = 0.0
        
        self.kp_yaw = 10.0
        self.ki_yaw = 0.05
        self.kd_yaw = 2.5
        self.yaw_integral = 0.0
        self.prev_yaw_err = 0.0

        self.forces = np.zeros(3)
        self.torques = np.zeros(3)
        
        # Communication Interfaces
        self.target_sub = self.create_subscription(PoseStamped, '/vrx/waypoint', self.target_listener_callback, 10)
        self.imu_sub = self.create_subscription(Imu, '/imu/data', self.imu_listener_callback, 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        
        # Execution Timer (100Hz Loop)
        self.dt = 0.01
        self.timer = self.create_timer(self.dt, self.realtime_control_loop)
        self.get_logger().info("Real-Time Marine GNC Node Online. Awaiting target...")

    def target_listener_callback(self, msg):
        self.target_x = msg.pose.position.x
        self.target_y = msg.pose.position.y
        self.active_mission = True
        self.get_logger().info(f"Target Updated -> X: {self.target_x}, Y: {self.target_y}")

    def imu_listener_callback(self, msg):
        # Update velocities directly from structural IMU feedback indexes
        self.state[9]  = msg.angular_velocity.x  # p
        self.state[10] = msg.angular_velocity.y  # q
        self.state[11] = msg.angular_velocity.z  # r

    def realtime_control_loop(self):
        if not self.active_mission:
            self.forces = np.zeros(3)
            self.torques = np.zeros(3)
            self.solve_linear_physics_matrix()
            return

        # 1. Guidance (Line-of-Sight Calculations)
        curr_x = self.state[0]
        curr_y = self.state[1]
        curr_yaw = self.state[5]
        
        dx = self.target_x - curr_x
        dy = self.target_y - curr_y
        distance_error = math.sqrt(dx**2 + dy**2)
        
        target_angle = math.atan2(dy, dx)
        heading_error = target_angle - curr_yaw
        heading_error = math.atan2(math.sin(heading_error), math.cos(heading_error))

        # 2. Control Laws (Decoupled PID)
        if distance_error < 0.3:
            self.surge_integral = 0.0
            surge_force = 0.0
            self.active_mission = False 
            self.get_logger().info("Target Reached.")
        else:
            self.surge_integral += distance_error * self.dt
            surge_deriv = (distance_error - self.prev_surge_err) / self.dt
            surge_force = (self.kp_surge * distance_error) + (self.ki_surge * self.surge_integral) + (self.kd_surge * surge_deriv)
            self.prev_surge_err = distance_error

        self.yaw_integral += heading_error * self.dt
        yaw_deriv = (heading_error - self.prev_yaw_err) / self.dt
        yaw_moment = (self.kp_yaw * heading_error) + (self.ki_yaw * self.yaw_integral) + (self.kd_yaw * yaw_deriv)
        self.prev_yaw_err = heading_error

        # 3. Thrust Allocation Mapping
        self.forces[0] = surge_force * math.cos(curr_yaw) 
        self.forces[1] = surge_force * math.sin(curr_yaw) 
        self.torques[2] = yaw_moment                      

        self.solve_linear_physics_matrix()

    def solve_linear_physics_matrix(self):
        # 6-DOF Linearized dynamics calculations
        ax = self.forces[0] / self.mass
        ay = self.forces[1] / self.mass
        az = self.forces[2] / self.mass
        
        al_roll  = self.torques[0] / self.Ixx
        al_pitch = self.torques[1] / self.Iyy
        al_yaw   = self.torques[2] / self.Izz
        
        # Integrate linear velocities
        self.state[6] += ax * self.dt  
        self.state[7] += ay * self.dt  
        self.state[8] += az * self.dt  
        
        # Integrate angular velocities
        self.state[9]  += al_roll * self.dt  
        self.state[10] += al_pitch * self.dt 
        self.state[11] += al_yaw * self.dt   
        
        # Integrate absolute position metrics
        self.state[0] += self.state[6] * self.dt 
        self.state[1] += self.state[7] * self.dt 
        self.state[2] += self.state[8] * self.dt 
        
        # Integrate absolute orientation rotation metrics
        self.state[3] += self.state[9] * self.dt  
        self.state[4] += self.state[10] * self.dt 
        self.state[5] += self.state[11] * self.dt 
        
        self.broadcast_realtime_transform()

    def broadcast_realtime_transform(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = self.state[0]
        t.transform.translation.y = self.state[1]
        t.transform.translation.z = self.state[2]
        
        r, p, y = self.state[3], self.state[4], self.state[5]
        cy, sy = math.cos(y * 0.5), math.sin(y * 0.5)
        cp, sp = math.cos(p * 0.5), math.sin(p * 0.5)
        cr, sr = math.cos(r * 0.5), math.sin(r * 0.5)
        
        t.transform.rotation.w = cr * cp * cy + sr * sp * sy
        t.transform.rotation.x = sr * cp * cy - cr * sp * sy
        t.transform.rotation.y = cr * sp * cy + sr * cp * sy
        t.transform.rotation.z = cr * cp * sy - sr * sp * cy
        
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = RealTimeMarineGnc()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
