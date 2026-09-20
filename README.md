# Autonomous Surface Vehicle Navigation in VRX

**ROS 2 · Gazebo / VRX · Marine Robotics · Autonomous Navigation · Sensor Integration · Reinforcement Learning**

**Engineering Internship · Seaconvoy Systems Engineering Pvt. Ltd. · 2026**

A ROS 2 and Gazebo-based autonomous surface vessel (ASV) simulation, navigation and control system developed during my engineering internship at **Seaconvoy Systems Engineering Pvt. Ltd.**

The project focused on configuring and validating the **Navis ASV** in the Virtual RobotX (VRX) simulation environment and progressively developing waypoint navigation, LOS guidance, vessel control, sensor integration, visualization and learning-based path-following capabilities.

This engineering work later provided the foundation for my separate research into recurrent reinforcement learning, multi-vessel collision avoidance and predictive safety filtering.

---

## Project Overview

The project was developed progressively from vessel integration and manual control toward autonomous navigation and learning-based control.

```text
Navis ASV Integration
        |
        v
ROS 2 ↔ Gazebo Interface
        |
        v
Manual Thruster / Rudder Control
        |
        v
GPS + IMU Integration
        |
        v
Waypoint Navigation
        |
        v
LOS Path Following
        |
        v
LiDAR + Stereo Perception
        |
        v
RViz2 Visualization
        |
        v
SAC / TD3 Path-Following Experiments
```

---

# Navis ASV in VRX

The project uses a custom **Navis autonomous surface vessel** integrated into the VRX `sydney_regatta` simulation environment.

The simulated vessel includes:

- thruster actuation
- rudder steering
- hydrodynamic behaviour
- GPS
- IMU
- LiDAR
- stereo camera
- DVL
- ROS 2 interfaces

This created a software platform for developing and evaluating autonomous marine navigation algorithms before physical-system validation.

---

# System Architecture

```text
                    Waypoint Selection
                           |
                           v
                    GPS Waypoints
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
                 Rudder / Thruster Commands
                           |
                           v
              +-------------------------+
              |       ROS 2 Layer       |
              +-------------------------+
                           |
                           v
              +-------------------------+
              |      Gazebo / VRX       |
              |        Navis ASV        |
              +-------------------------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          GPS / IMU      LiDAR       Stereo Camera
             |             |             |
             +-------------+-------------+
                           |
                           v
                         ROS 2
                           |
                           v
                         RViz2
```

---

# Interactive Waypoint Navigation

A custom waypoint workflow was used to create navigation targets directly inside the Gazebo environment.

<p align="center">
  <img src="IMG_0238.jpeg" width="850"
       alt="Navis ASV with Gazebo Waypoint Clicker">
</p>

<p align="center">
  <em>Navis ASV in the VRX environment with the Gazebo Waypoint Clicker activated for interactive waypoint selection.</em>
</p>

The waypoint interface allows navigation targets to be selected in the simulated environment and transferred into the ROS 2 navigation pipeline.

```text
Gazebo Waypoint Clicker
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
     ASV Control
```

---

# LOS Path Following

The autonomous navigation system uses **Line-of-Sight (LOS) guidance** to generate a desired heading from the vessel's position relative to the waypoint path.

<p align="center">
  <img src="IMG_0239.jpeg" width="850"
       alt="Navis ASV following a waypoint path in Gazebo">
</p>

<p align="center">
  <em>Navis ASV following the generated waypoint path in Gazebo/VRX.</em>
</p>

For consecutive waypoints, LOS guidance selects a target point ahead of the vessel rather than simply steering directly toward the next waypoint.

Conceptually:

```text
Waypoint A -------------------------------- Waypoint B
                          *
                      LOS Target
                         /
                        /
                       /
                    Navis ASV
```

A look-ahead distance is used to obtain smoother path-following behaviour.

---

## Cross-Track Error

Navigation performance is evaluated using **Cross-Track Error (CTE)**.

CTE measures the lateral displacement of the vessel from the desired path:

```text
Desired Path
------------------------------------------------
                         |
                         | CTE
                         |
                       Vessel
```

Tracking CTE allows path-following performance to be evaluated quantitatively rather than only through visual inspection.

---

# Heading & Vessel Control

The desired heading generated by LOS guidance is compared with the current vessel heading estimated from the IMU.

```text
Desired Heading --------+
                        |
                        v
                  Heading Error
                        ^
                        |
Current Heading --------+
                        |
                        v
                 Heading Control
                        |
                        v
                  Rudder Command
                        |
                        v
                     Navis ASV
```

The control system interfaces with:

- rudder commands
- thruster commands
- vessel heading
- waypoint information
- vessel position

through ROS 2.

---

# Vessel Dynamics

Simplified vessel behaviour is represented using a first-order **Nomoto yaw model**:

```text
T · dr/dt + r = K · δ
```

where:

- `T` — vessel response time constant
- `K` — steering gain
- `r` — yaw rate
- `δ` — rudder command

The repository includes components for experimenting with Nomoto-based yaw dynamics alongside the Gazebo vessel simulation.

Hydrodynamic parameters were also configured to obtain usable surge, sway and yaw behaviour for navigation and control experiments.

---

# Sensor Integration

The Navis ASV simulation integrates multiple sensors used for navigation, perception and system evaluation.

| Sensor | Application |
|---|---|
| **GPS / NavSat** | Vessel position and waypoint navigation |
| **IMU** | Orientation, yaw and heading estimation |
| **LiDAR** | Range sensing and obstacle perception |
| **ZED2i Stereo Camera** | Stereo imagery and 3D perception |
| **DVL** | Vessel velocity information |

---

## GPS

GPS/NavSat data provides vessel-position information to the navigation pipeline.

```text
Gazebo NavSat
      |
      v
Gazebo Transport
      |
      v
ROS 2 Interface
      |
      v
Vessel Position
      |
      v
Waypoint Navigation
```

---

## IMU

The simulated IMU provides vessel orientation information.

Quaternion orientation is processed to obtain yaw/heading for navigation and control.

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
LOS + Heading Control
```

---

## LiDAR

A simulated LiDAR provides range measurements for obstacle perception.

The Gazebo LiDAR data is bridged into ROS 2 and represented using:

```text
sensor_msgs/msg/LaserScan
```

The repository also includes LiDAR monitoring and debugging utilities.

```text
Gazebo LiDAR
     |
     v
Gazebo Transport
     |
     v
ROS–Gazebo Bridge
     |
     v
LaserScan
     |
     v
ROS 2 Processing
```

---

# Stereo Vision & 3D Point Cloud

A simulated **ZED2i stereo camera** was integrated into the Navis ASV sensor stack.

The stereo pipeline provides:

- left-camera image
- right-camera image
- camera calibration information
- stereo disparity
- reconstructed 3D point cloud

```text
       ZED2i Stereo Camera
               |
        +------+------+
        |             |
        v             v
   Left Image     Right Image
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
             RViz2
```

### RViz2 Visualization

<p align="center">
  <img src="IMG_0240.jpeg" width="900"
       alt="RViz stereo-camera and PointCloud2 visualization">
</p>

<p align="center">
  <em>RViz2 visualization of stereo-camera images together with the reconstructed 3D PointCloud2 output.</em>
</p>

This visualization was used to verify that the simulated stereo sensing pipeline was successfully connected through ROS 2.

---

# DVL Integration

A simulated **Doppler Velocity Log (DVL)** interface was also included for vessel-velocity information.

The repository contains:

- Gazebo DVL plugin
- ROS 2 DVL publisher
- velocity-topic monitoring

This extends the simulated sensing stack beyond position and orientation measurements.

---

# ROS 2 / Gazebo Integration

Control algorithms operate as ROS 2 nodes while vessel physics and sensor simulation run in Gazebo.

```text
ROS 2 Navigation / Controller
             |
      +------+------+
      |             |
      v             v
   Thruster        Rudder
   Command         Command
      |             |
      +------+------+
             |
             v
       Gazebo Relay
             |
             v
         Navis ASV
```

This separation allows guidance, sensing and control algorithms to be developed independently from the underlying simulator.

---

# Teleoperation & Functional Validation

Manual vessel control was implemented before autonomous navigation to verify the control interfaces and vessel response.

## Keyboard Control

The repository includes:

```text
keyboard_asv_control
```

for direct thruster and rudder control.

## Joystick Control

A Logitech game controller was also integrated through ROS 2.

```text
joy_node
    |
    v
joystick_asv_control
    |
    +--------------+
    |              |
    v              v
Thruster         Rudder
Command          Command
```

Teleoperation was useful for validating:

- ROS 2 command transmission
- thruster behaviour
- rudder response
- vessel steering
- simulation integration

before autonomous guidance was introduced.

---

# Reinforcement Learning Path Following

The internship project was extended from classical LOS-based navigation to **learning-based continuous control**.

Two off-policy reinforcement-learning algorithms were investigated:

### Soft Actor-Critic — SAC

and

### Twin Delayed Deep Deterministic Policy Gradient — TD3

The repository contains trained policy checkpoints:

```text
rl_models/
├── sac_asv_waypoint.zip
└── td3_asv_waypoint.zip
```

The RL environment used simplified Nomoto vessel dynamics and continuous rudder control for waypoint/path-following experiments.

Both algorithms were trained for **900,000 timesteps** in the experimental study.

---

## SAC vs TD3 Evaluation

The trained policies were evaluated across **10 path geometries**, including:

- straight path
- moderate turns
- sharp turns
- U-turn
- triangle
- oval
- semicircle
- smooth curve
- mixed-curvature paths
- sharp zigzag

The evaluation considered:

1. nominal path following
2. current disturbance
3. current + sensor noise

This allowed the learned controllers to be tested beyond a single trajectory.

---

## Nominal Path-Following Results

Both trained controllers successfully completed all ten nominal test paths.

| Metric | SAC | TD3 |
|---|---:|---:|
| Successful paths | **10 / 10** | **10 / 10** |
| Mean CTE | **0.245 m** | **0.455 m** |

In the reported nominal evaluation, SAC achieved lower mean cross-track error and required less average rudder activity than TD3.

The comparison was used to study the trade-off between path-tracking accuracy, steering activity and robustness rather than relying on a single success metric.

---

## Robustness Evaluation

The RL evaluation also introduced environmental and sensing disturbances.

The test framework examined controller behaviour under:

- current disturbance
- sensor noise
- varying path curvature
- sharp heading changes
- demanding zigzag trajectories

The **sharp-zigzag geometry** was among the most demanding test cases because of its rapid changes in desired heading.

These experiments provided the transition from basic waypoint following toward more robust autonomous navigation research.

---

# Main ROS 2 Nodes

The `asv_control` package contains nodes covering navigation, sensing, control, visualization and debugging.

Key executables include:

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

> `adaptive_los_pid_follower` is retained here because it is the executable name used in the source code. The guidance method is referred to throughout this documentation as **LOS guidance**.

---

# ROS 2 / Gazebo Packages

The workspace contains several custom packages supporting the simulated ASV platform.

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

Main ROS 2 package containing navigation, control and sensor-processing nodes.

### `asv_dvl_plugin`

Gazebo plugin supporting simulated DVL measurements.

### `gps_waypoint_gui_bridge`

Interface for transferring waypoint information into the ROS 2 navigation pipeline.

### `gz_waypoint_bridge`

Bridge between Gazebo waypoint interaction and ROS 2.

### `gz_waypoint_clicker`

Gazebo GUI component supporting interactive waypoint selection.

### `nomoto_plugin`

Gazebo plugin supporting simplified Nomoto vessel dynamics.

### Path / Trail Components

Additional packages provide path and trajectory visualization during simulation.

---

# Repository Structure

```text
Autonomous-surface-vehicle-in-VRX-internship-/
│
├── src/
│   ├── asv_control/
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
├── IMG_0238.jpeg
├── IMG_0239.jpeg
├── IMG_0240.jpeg
│
├── bag_to_csv_plot.py
├── gazebo_lidar_monitor.py
├── gazebo_stereo_monitor.py
├── launch_asv_system.sh
├── lidar_bridge.yaml
├── my_asv_world.sdf
├── sensor_sync_log.csv
└── README.md
```

---

# Running the Project

The repository contains the development launcher:

```bash
./launch_asv_system.sh
```

The launcher was used to coordinate the main simulation, vessel and ROS 2 components.

> **Note:** This launcher originates from the internship development environment and may contain machine-specific paths. These paths should be updated when reproducing the project on another system.

---

## Build

The project follows a ROS 2 workspace structure and can be built using `colcon`.

```bash
source /opt/ros/humble/setup.bash

colcon build --symlink-install

source install/setup.bash
```

The corresponding VRX installation and required simulation assets must also be available.

---

## Example Nodes

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

### GPS

```bash
ros2 run asv_control gps_publisher
```

### IMU

```bash
ros2 run asv_control imu_rpy_publisher
```

### Path Visualization

```bash
ros2 run asv_control path_publisher
```

### LOS Waypoint Follower

```bash
ros2 run asv_control adaptive_los_pid_follower
```

### DVL

```bash
ros2 run asv_control dvl_publisher
```

### LiDAR Debugging

```bash
ros2 run asv_control lidar_debug_node
```

---

# Technologies & Skills

## Robotics & Simulation

- ROS 2 Humble
- Gazebo Sim
- Virtual RobotX (VRX)
- RViz2
- SDF
- ROS–Gazebo interfaces
- Custom Gazebo plugins
- Autonomous Surface Vehicles

## Programming & Development

- Python
- C++
- `rclpy`
- NumPy
- Linux / Ubuntu 22.04
- Bash / ROS 2 CLI
- Git / GitHub
- `colcon`

## Navigation & Control

- Waypoint navigation
- Line-of-Sight guidance
- Cross-Track Error
- Desired-heading generation
- Heading control
- Rudder control
- Thruster control
- Nomoto first-order dynamics
- Hydrodynamic modelling

## Sensors & Perception

- LiDAR
- Stereo Camera
- GPS / NavSat
- IMU
- DVL
- LaserScan
- PointCloud2
- Stereo disparity
- Sensor synchronization
- Sensor logging

## Reinforcement Learning

- Stable-Baselines3
- Gymnasium
- Soft Actor-Critic (SAC)
- Twin Delayed DDPG (TD3)
- Continuous control
- Observation/action design
- Reward design
- Policy training
- Policy checkpointing
- Multi-scenario evaluation

## Evaluation & Visualization

- CSV logging
- Matplotlib
- RViz2
- Gazebo visualization
- CTE analysis
- Path visualization
- Disturbance testing
- Sensor-noise testing
- Quantitative policy comparison

---

# Internship Scope

This repository represents the **engineering development and learning-based navigation work carried out around the Navis ASV simulation platform during the internship**.

The internship work included:

```text
ASV Simulation Integration
        ↓
ROS 2 / Gazebo Communication
        ↓
Manual Vessel Control
        ↓
GPS + IMU Navigation
        ↓
Waypoint Interface
        ↓
LOS Path Following
        ↓
LiDAR + Stereo Perception
        ↓
RViz2 Visualization
        ↓
SAC / TD3 Path-Following Experiments
```

The project established the simulation and autonomy foundation that was subsequently extended into a separate research project.

---

# Subsequent Research

Following the internship-stage work, the autonomous-navigation research was extended toward:

- recurrent PPO
- recurrent steering and speed policies
- variable-speed navigation
- dynamic obstacle avoidance
- multi-vessel encounters
- joint residual reinforcement learning
- CPA / TCPA reasoning
- COLREG-inspired scenarios
- predictive safety filtering
- progress-aware safe-action selection
- robustness evaluation
- component-ablation studies

This later research is maintained separately:

### [ASV Collision Avoidance — Research Repository](https://github.com/Padma1320/ASV-Collision-Avoidance)

**Research status: Under Review — IEEE ICRA 2027 · Extended work in progress**

Keeping the two repositories separate distinguishes the original **internship engineering platform and SAC/TD3 experimentation** from the subsequent **research contribution**.

---

# Project Context

This work was developed during an engineering internship at **Seaconvoy Systems Engineering Pvt. Ltd.**

The internship involved configuring and validating an existing Seaconvoy-developed ASV model in Gazebo, establishing the simulation and ROS 2 framework, and developing autonomous navigation, sensing, control and reinforcement-learning experiments around the simulated Navis ASV platform.

---

