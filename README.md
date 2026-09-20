# Autonomous Surface Vehicle in VRX

An autonomous surface vessel (ASV) simulation and control system developed using **ROS 2 Humble, Gazebo Sim and the Virtual RobotX (VRX) environment**.

The project was developed during an internship to explore autonomous marine navigation, waypoint guidance, vessel control, sensor integration, stereo perception, vessel dynamics modelling and reinforcement-learning-based navigation.

The system uses a custom **Navis ASV** integrated into the VRX `sydney_regatta` simulation environment.

---

## Project Overview

The project integrates a simulated autonomous surface vessel with ROS 2 for sensing, navigation, guidance, control and visualization.

The development includes:

- Custom Navis ASV integration in VRX
- ROS 2–Gazebo communication
- GPS-based waypoint navigation
- IMU-based vessel heading estimation
- Line-of-Sight (LOS) guidance
- Heading-error-based vessel control
- Thruster and rudder control
- Nomoto yaw-dynamics modelling
- LiDAR integration
- ZED2i stereo-camera simulation
- Stereo disparity processing
- 3D point-cloud generation
- DVL velocity sensing
- Keyboard teleoperation
- Joystick teleoperation
- Gazebo waypoint visualization
- RViz visualization
- Sensor logging and monitoring
- Reinforcement-learning experiments using SAC and TD3

---

## System Architecture

```text
                         GPS Waypoints
                              |
                              v
                     Waypoint Interface
                              |
                              v
                      LOS Guidance
                              |
                    Desired Heading
                              |
                              v
             +-------------------------------+
             |     Heading Control           |
             |                               |
             | Desired Heading               |
             |        -                      |
             | Current Heading from IMU      |
             +---------------+---------------+
                             |
                       Rudder Command
                             |
                             v
+------------------------------------------------------------+
|                    ROS 2 Control Layer                     |
|                                                            |
|       Thruster Command                  Rudder Command      |
+---------------------------+--------------------------------+
                            |
                            v
+------------------------------------------------------------+
|                       Gazebo / VRX                         |
|                                                            |
|                       Navis ASV                            |
+---------------------------+--------------------------------+
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
    GPS / IMU             LiDAR             ZED2i Stereo
       |                    |                    |
       |                    |              Left / Right
       |                    |                 Images
       |                    |                    |
       |                    |               Disparity
       |                    |                    |
       |                    |               PointCloud2
       |                    |                    |
       +--------------------+--------------------+
                            |
                            v
                          ROS 2
                            |
                            v
                          RViz
```

---

# Navigation and Guidance

## Waypoint Navigation

The vessel follows a sequence of waypoints provided through the ROS 2 waypoint interface.

Waypoint-related components in the project provide communication between the graphical waypoint interface, ROS 2 navigation system and Gazebo visualization.

The navigation pipeline can be represented as:

```text
GPS Waypoint
     |
     v
Waypoint Bridge
     |
     v
/asv/waypoints
     |
     v
LOS Guidance
     |
     v
Desired Heading
     |
     v
Heading Controller
     |
     v
Rudder Command
```

Waypoint markers and connecting paths can also be displayed in the Gazebo environment.

---

## Line-of-Sight (LOS) Guidance

Line-of-Sight guidance is used to determine the heading required for the vessel to follow the path between successive waypoints.

The guidance algorithm considers the vessel position relative to the desired path and generates a **desired heading**.

Conceptually:

```text
Previous Waypoint
        |
        | Desired Path
        |
        +-----------------------> Next Waypoint
                  \
                   \
                    \ LOS Target
                     \
                      ASV
```

The difference between the desired path and vessel position can be represented using the **Cross-Track Error (CTE)**.

The LOS algorithm generates the desired vessel heading required to reduce this deviation and continue toward the waypoint.

---

## Cross-Track Error

Cross-Track Error represents the lateral deviation of the vessel from the desired path between waypoints.

```text
Waypoint A ------------------------------- Waypoint B
                       |
                       |  Cross-Track Error
                       |
                       |
                      ASV
```

A smaller CTE indicates that the vessel is following the desired path more closely.

---

# Heading Control

The desired heading generated by the LOS guidance system is compared with the vessel's measured heading.

```text
Desired Heading
       |
       |      Current Heading
       |             |
       v             v
      +---------------+
      | Heading Error |
      +-------+-------+
              |
              v
          Controller
              |
              v
        Rudder Command
              |
              v
             ASV
```

The controller generates steering commands that are transmitted to the simulated vessel.

---

# Nomoto Vessel Dynamics

The project includes a **Nomoto vessel model** for simplified modelling of ship yaw dynamics.

A first-order Nomoto model can represent the relationship between rudder input and vessel yaw response as:

```text
T * dr/dt + r = K * δ
```

where:

- `T` = vessel response time constant
- `K` = steering gain
- `r` = yaw rate
- `δ` = rudder angle

The Nomoto model provides a simplified way of studying vessel steering behaviour without requiring a complete high-order hydrodynamic model.

The repository contains both ROS/Python-based Nomoto simulation components and a Gazebo Nomoto plugin used during vessel-dynamics experimentation.

---

# Sensor Integration

The Navis ASV simulation integrates multiple sensors for navigation and perception.

---

## GPS

The simulated GPS/NavSat sensor provides vessel position information.

The GPS pipeline is conceptually:

```text
Gazebo NavSat Sensor
        |
        v
Gazebo Transport
        |
        v
ROS 2 GPS Publisher / Bridge
        |
        v
GPS Position
        |
        v
Waypoint Navigation
```

GPS information is used by the navigation system to determine the vessel's position relative to the desired waypoint path.

---

## IMU

The simulated IMU provides vessel orientation information.

The orientation is processed to obtain the vessel heading required by the guidance and control system.

```text
Gazebo IMU
     |
     v
ROS 2
     |
     v
Orientation
     |
     v
Yaw / Heading
     |
     v
Heading Controller
```

---

## LiDAR

A simulated LiDAR sensor is integrated with the ASV.

Gazebo LiDAR messages are bridged into ROS 2 using `ros_gz_bridge`.

The ROS 2 representation uses:

```text
sensor_msgs/msg/LaserScan
```

The project also contains a LiDAR debugging node and a Gazebo LiDAR monitoring utility.

The LiDAR pipeline is:

```text
Gazebo LiDAR
     |
     v
Gazebo Transport
     |
     v
ros_gz_bridge
     |
     v
ROS 2 LaserScan
     |
     v
Monitoring / Processing
```

---

## ZED2i Stereo Camera

A simulated ZED2i stereo-camera configuration is integrated into the vessel.

The system provides:

- Left camera image
- Right camera image
- Left camera calibration information
- Right camera calibration information
- Stereo disparity
- 3D point cloud

The stereo pipeline is:

```text
       ZED2i Stereo Camera
              |
       +------+------+
       |             |
       v             v
 Left Image      Right Image
       |             |
       +------+------+
              |
              v
       stereo_image_proc
              |
              v
          Disparity
              |
              v
        PointCloud2
              |
              v
             RViz
```

ROS 2 `stereo_image_proc` is used for stereo disparity and point-cloud processing.

Camera-information and disparity-fixing utilities are also included to support the simulated stereo pipeline.

---

## DVL

The repository contains a simulated **Doppler Velocity Log (DVL)** interface for vessel velocity information.

The project includes:

- A Gazebo DVL plugin
- ROS 2 DVL publisher
- Velocity topic monitoring

The DVL data is exposed through the ROS 2 sensing pipeline for vessel-motion analysis.

---

# Teleoperation

The ASV can also be controlled manually.

## Keyboard Control

The `keyboard_asv_control` ROS 2 node provides keyboard-based control of:

- Thruster command
- Rudder command

This was used during initial vessel integration and control testing.

## Joystick Control

Joystick teleoperation is provided through:

```text
joy_node
      |
      v
joystick_asv_control
      |
      +------------------+
      |                  |
      v                  v
Thruster Command    Rudder Command
```

This provides direct manual control of the simulated ASV.

---

# Gazebo / ROS 2 Interface

The project contains an ASV Gazebo relay node that connects ROS 2 control commands with the simulated vessel.

The basic command flow is:

```text
ROS 2 Controller
       |
       +---------------------+
       |                     |
       v                     v
Thruster Command        Rudder Command
       |                     |
       +----------+----------+
                  |
                  v
             Gazebo Relay
                  |
                  v
              Navis ASV
```

---

# Visualization

## Gazebo

Gazebo provides the primary simulation environment and is used for:

- Vessel simulation
- Sensor simulation
- Waypoint visualization
- Path visualization
- Vessel dynamics
- Environmental interaction

The project uses the VRX:

```text
sydney_regatta.sdf
```

simulation world.

---

## RViz2

RViz2 is used to visualize ROS 2 sensor outputs.

The repository contains an RViz configuration for the stereo-perception pipeline.

Visualized data can include:

- Stereo-camera information
- Point clouds
- Sensor topics
- Navigation information

---

# Reinforcement Learning Experiments

In addition to conventional waypoint guidance and vessel control, the internship workspace contains reinforcement-learning experiments for ASV waypoint navigation.

The repository contains trained models for:

### Soft Actor-Critic (SAC)

```text
rl_models/sac_asv_waypoint.zip
```

### Twin Delayed Deep Deterministic Policy Gradient (TD3)

```text
rl_models/td3_asv_waypoint.zip
```

These models were investigated as learning-based alternatives for ASV navigation/control.

The reinforcement-learning work in this repository represents the experimentation performed during the original internship project.

More advanced subsequent research involving recurrent PPO, dynamic-obstacle interaction, COLREGS reasoning and predictive safety filtering is outside the scope of this repository.

---

# ROS 2 Nodes

The `asv_control` package contains ROS 2 executables for several parts of the system.

```text
keyboard_asv_control
joystick_asv_control
asv_gz_relay
imu_rpy_publisher
gps_publisher
path_publisher
gazebo_path_trail
gazebo_click_waypoint_node
adaptive_los_pid_follower
dvl_publisher
nomoto_gz_pose_sim
lidar_debug_node
sensor_sync_logger
```

These nodes cover vessel control, navigation, sensing, simulation and debugging functionality.

---

# Custom ROS 2 / Gazebo Components

The source workspace contains several custom packages.

```text
src/
├── asv_control/
├── asv_dvl_plugin/
├── asv_line_trail_cpp/
├── asv_trail_plugin/
├── gps_waypoint_gui_bridge/
├── gz_waypoint_bridge/
├── gz_waypoint_clicker/
├── my_asv_controller/
├── navis_model/
├── nomoto_plugin/
└── vrx_linear_boat/
```

### `asv_control`

Main Python ROS 2 package containing navigation, control and sensor-processing nodes.

### `asv_dvl_plugin`

Gazebo plugin developed for simulated DVL functionality.

### `gps_waypoint_gui_bridge`

ROS 2 bridge for transferring GPS waypoint information to the ASV navigation system and supporting waypoint visualization.

### `gz_waypoint_bridge`

Interface between Gazebo waypoint interaction and ROS 2.

### `gz_waypoint_clicker`

Gazebo GUI component for interactive waypoint input.

### `nomoto_plugin`

Gazebo plugin for simplified Nomoto vessel dynamics.

### Path / Trail Components

Additional components provide vessel trajectory and path visualization during simulation.

---

# Repository Structure

```text
Autonomous-surface-vehicle-in-VRX-internship/
│
├── src/
│   │
│   ├── asv_control/
│   │   └── asv_control/
│   │       ├── adaptive_los_pid_follower.py
│   │       ├── asv_gz_relay.py
│   │       ├── controller.py
│   │       ├── disparity_window_fixer.py
│   │       ├── dvl_publisher.py
│   │       ├── gazebo_click_waypoint_node.py
│   │       ├── gazebo_path_trail.py
│   │       ├── gps_publisher.py
│   │       ├── imu_rpy_publisher.py
│   │       ├── joystick_asv_control.py
│   │       ├── keyboard_asv_control.py
│   │       ├── lidar_debug_node.py
│   │       ├── nomoto_gz_pose_sim.py
│   │       ├── path_publisher.py
│   │       ├── rl_waypoint_follower.py
│   │       ├── sensor_sync_logger.py
│   │       ├── zed2i_camera_info_fixer.py
│   │       └── zed2i_sync_republisher.py
│   │
│   ├── asv_dvl_plugin/
│   ├── asv_line_trail_cpp/
│   ├── asv_trail_plugin/
│   ├── gps_waypoint_gui_bridge/
│   ├── gz_waypoint_bridge/
│   ├── gz_waypoint_clicker/
│   ├── my_asv_controller/
│   ├── navis_model/
│   ├── nomoto_plugin/
│   └── vrx_linear_boat/
│
├── rl_models/
│   ├── sac_asv_waypoint.zip
│   └── td3_asv_waypoint.zip
│
├── rviz/
│   └── stereo.rviz
│
├── bag_to_csv_plot.py
├── gazebo_lidar_monitor.py
├── gazebo_stereo_monitor.py
├── launch_asv_system.sh
├── lidar_bridge.yaml
├── my_asv_world.sdf
├── sensor_sync_log.csv
└── plotting utilities
```

---

# Main Startup Script

The repository contains:

```bash
launch_asv_system.sh
```

The development launcher was used to start the integrated simulation components, including:

```text
VRX / Gazebo
      |
      v
Spawn Navis ASV
      |
      +-----------------------------+
      |                             |
      v                             v
ROS 2 Control                  Sensor Pipeline
      |                             |
      v                    +--------+---------+
Gazebo Relay                |        |        |
      |                    GPS      IMU     LiDAR
      v                                      |
Joystick / Keyboard                          |
      |                                      |
      v                                  LaserScan
Waypoint Bridge                              |
      |                                      |
      v                                      |
LOS Controller                         ZED2i Stereo
      |                                      |
      v                                  Disparity
Rudder / Thruster                            |
                                             v
                                        PointCloud2
                                             |
                                             v
                                            RViz
```

> **Note:** `launch_asv_system.sh` is the development launcher from the original internship workspace and contains machine/workspace-specific paths. These paths may need to be updated for another installation.

---

# Build

This repository follows the standard ROS 2 workspace structure and can be built using `colcon`.

After installing the required dependencies and VRX environment:

```bash
cd ~/vrx_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

# Running Individual Nodes

Examples:

### Gazebo Relay

```bash
ros2 run asv_control asv_gz_relay
```

### Keyboard Control

```bash
ros2 run asv_control keyboard_asv_control
```

### Joystick Control

```bash
ros2 run joy joy_node
ros2 run asv_control joystick_asv_control
```

### GPS Publisher

```bash
ros2 run asv_control gps_publisher
```

### IMU Publisher

```bash
ros2 run asv_control imu_rpy_publisher
```

### Path Publisher

```bash
ros2 run asv_control path_publisher
```

### LOS Waypoint Follower

```bash
ros2 run asv_control adaptive_los_pid_follower
```

### DVL Publisher

```bash
ros2 run asv_control dvl_publisher
```

### LiDAR Debug Node

```bash
ros2 run asv_control lidar_debug_node
```

---

# Main Technologies and Skills

### Robotics

- Autonomous Surface Vehicles
- Marine Robotics
- Autonomous Navigation
- Waypoint Navigation
- Line-of-Sight Guidance
- Cross-Track Error
- Heading Control
- Vessel Dynamics
- Nomoto Modelling

### ROS 2

- ROS 2 Humble
- ROS 2 Nodes
- Publishers and Subscribers
- ROS 2 Topics
- ROS-Gazebo Communication
- Custom ROS 2 Packages
- Sensor Message Processing

### Simulation

- Gazebo Sim
- Virtual RobotX (VRX)
- SDF
- Custom Vessel Models
- Gazebo Plugins
- Simulated Sensors

### Perception and Sensors

- GPS / NavSat
- IMU
- LiDAR
- LaserScan
- Stereo Vision
- Stereo Disparity
- PointCloud2
- DVL

### Programming

- Python
- C++
- Bash
- NumPy

### Reinforcement Learning

- Soft Actor-Critic (SAC)
- Twin Delayed DDPG (TD3)
- Continuous-Control Experimentation

### Development Tools

- Ubuntu Linux
- RViz2
- Git
- GitHub
- ROS 2 CLI
- Colcon

---

# Large Assets and Upstream VRX

The complete upstream VRX source tree is intentionally not duplicated in this repository.

Large simulation mesh assets are also excluded from normal Git tracking to keep the repository within standard GitHub file-size limits.

For example, the original Navis vessel STL used during development is not stored directly in this repository.

To reproduce the complete simulation, the corresponding VRX environment and required vessel mesh assets must be installed separately.

---

# Development Environment

The original project was developed using:

```text
Operating System : Ubuntu 22.04
ROS              : ROS 2 Humble
Simulator        : Gazebo Sim / VRX
Primary Language : Python
Plugins          : C++
Build System     : colcon / ament
Visualization    : RViz2
Version Control  : Git / GitHub
```

---

# Project Scope

This repository represents the **original autonomous surface vessel internship project**.

Its primary scope is:

```text
ASV Simulation
      +
ROS 2 Integration
      +
Sensor Integration
      +
Waypoint Navigation
      +
LOS Guidance
      +
Vessel Control
      +
Nomoto Dynamics
      +
Stereo / LiDAR Perception
      +
SAC / TD3 Experimentation
```

Later research extensions involving recurrent PPO, dynamic obstacle avoidance, COLREGS-aware navigation and predictive safety filtering are intentionally kept outside the scope of this repository.

---

