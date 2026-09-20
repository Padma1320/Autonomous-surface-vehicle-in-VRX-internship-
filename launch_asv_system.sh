#!/bin/bash

# =====================================================
# VRX ASV COMPLETE STARTUP
# =====================================================

cd ~/vrx_ws

# Kill old processes
pkill -9 gz
pkill -9 ruby
pkill -9 ign

pkill -f asv_gz_relay
pkill -f joy_node
pkill -f joystick_asv_control
pkill -f gps_publisher
pkill -f imu_rpy_publisher
pkill -f path_publisher
pkill -f gazebo_path_trail
pkill -f parameter_bridge
pkill -f image_bridge

sleep 2

# =====================================================
# Gazebo
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
export GZ_GUI_PLUGIN_PATH=/home/user/vrx_ws/install/gz_waypoint_clicker/lib:\$GZ_GUI_PLUGIN_PATH
export GZ_SIM_SYSTEM_PLUGIN_PATH=/home/user/vrx_ws/install/nomoto_plugin/lib:/home/user/vrx_ws/install/asv_dvl_plugin/lib:\$GZ_SIM_SYSTEM_PLUGIN_PATH
gz sim -v 4 sydney_regatta.sdf
exec bash
"

sleep 10

# =====================================================
# Spawn Boat
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
gz service -s /world/sydney_regatta/create \
--reqtype gz.msgs.EntityFactory \
--reptype gz.msgs.Boolean \
--timeout 10000 \
--req 'sdf_filename:\"/home/user/vrx_ws/src/vrx/vrx_gz/models/my_asv/model.sdf\",name:\"my_asv\",pose:{position:{x:0 y:0 z:0.5}}'
exec bash
"

sleep 2

# Relay
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control asv_gz_relay
exec bash
"

# Joy
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run joy joy_node
exec bash
"

# Joystick control
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control joystick_asv_control
exec bash
"

# GPS
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control gps_publisher
exec bash
"

# IMU
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control imu_rpy_publisher
exec bash
"

# Path
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control path_publisher
exec bash
"

# Trail
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control gazebo_path_trail
exec bash
"

# Waypoint Bridge
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run gz_waypoint_bridge gz_waypoint_bridge_node
exec bash
"


sleep 2

# GPS LOS Controller
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control adaptive_los_pid_follower
exec bash
"

# Keyboard Control
gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control keyboard_asv_control
exec bash
"


# DVL
gnome-terminal -- bash -c "
cd ~/vrx_ws
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash
ros2 run asv_control dvl_publisher
exec bash
"

# =====================================================
# LiDAR Bridge
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/my_asv/lidar@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan

exec bash
"


# =====================================================
# LiDAR Debug Node
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws

source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run asv_control lidar_debug_node

exec bash
"
# =====================================================
# Gazebo LiDAR Monitor
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws
python3 gazebo_lidar_monitor.py
exec bash
"



# =====================================================
# ZED2i Left/Right Image Bridge
# =====================================================

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run ros_gz_image image_bridge \
/my_asv/zed2i/left/image \
/my_asv/zed2i/right/image

exec bash
"

# =====================================================
# ZED2i CameraInfo Bridge
# =====================================================

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/my_asv/zed2i/left/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo \
/my_asv/zed2i/right/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo

exec bash
"

# =====================================================
# CameraInfo Fixer
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws/src/asv_control/asv_control

python3 zed2i_camera_info_fixer.py

exec bash
"

# =====================================================
# Stereo Disparity
# =====================================================

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run stereo_image_proc disparity_node \
--ros-args \
-p approximate_sync:=true \
-p queue_size:=100 \
-r left/image_rect:=/my_asv/zed2i/left/image \
-r right/image_rect:=/my_asv/zed2i/right/image \
-r left/camera_info:=/my_asv/zed2i/left/camera_info_fixed \
-r right/camera_info:=/my_asv/zed2i/right/camera_info_fixed

exec bash
"
# =====================================================
# Disparity Window Fixer
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws/src/asv_control/asv_control

python3 disparity_window_fixer.py

exec bash
"

# =====================================================
# Stereo Point Cloud
# =====================================================

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run stereo_image_proc point_cloud_node \
--ros-args \
-r /left/image_rect_color:=/my_asv/zed2i/left/image \
-r /left/camera_info:=/my_asv/zed2i/left/camera_info_fixed \
-r /right/camera_info:=/my_asv/zed2i/right/camera_info_fixed \
-r /disparity:=/disparity_fixed \
-r /points2:=/my_asv/zed2i/points2

exec bash
"

# =====================================================
# RViz Visualization
# =====================================================

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

rviz2 -d ~/vrx_ws/rviz/stereo.rviz

exec bash
"

# =====================================================
# ROS Topic Echo: GPS / IMU / DVL
# =====================================================

# =====================================================
# ROS Topic Echo: GPS / IMU / DVL
# =====================================================

# =====================================================
# Wait for sensor publishers
# =====================================================

sleep 8

# =====================================================
# ROS Topic Echo: GPS / IMU / DVL
# =====================================================

# =====================================================
# ROS Topic Echo: GPS / IMU / DVL
# waits until each topic exists before echoing
# =====================================================

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

until ros2 topic list | grep -q '^/asv/gps_data$'; do
  echo 'Waiting for /asv/gps_data...'
  sleep 1
done

ros2 topic echo /asv/gps_data
exec bash
"

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

until ros2 topic list | grep -q '^/asv/imu$'; do
  echo 'Waiting for /asv/imu...'
  sleep 1
done

ros2 topic echo /asv/imu
exec bash
"

gnome-terminal -- bash -c "
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

until ros2 topic list | grep -q '^/asv/dvl/velocity$'; do
  echo 'Waiting for /asv/dvl/velocity...'
  sleep 1
done

ros2 topic echo /asv/dvl/velocity
exec bash
"


# =====================================================
# EXTERNAL GUI GPS WAYPOINT BRIDGE
# /asv/waypoints_gps -> /asv/waypoints
# Spawns Gazebo waypoint markers and connectors
# =====================================================

gnome-terminal -- bash -c "
cd ~/vrx_ws
source /opt/ros/humble/setup.bash
source ~/vrx_ws/install/setup.bash

ros2 run gps_waypoint_gui_bridge gps_waypoint_gui_bridge_node

exec bash
"
