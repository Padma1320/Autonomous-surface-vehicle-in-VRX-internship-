# Autonomous Surface Vehicle Navigation in VRX

**ROS 2 · Gazebo / VRX · Guidance, Navigation & Control (GNC) · Marine Robotics · Sensor Integration · Reinforcement Learning**

**Engineering Internship · Seaconvoy Systems Engineering Pvt. Ltd. · 2026**

A ROS 2 and Gazebo-based autonomous surface vessel (ASV) simulation, navigation and control system developed during my engineering internship at **Seaconvoy Systems Engineering Pvt. Ltd.**

The project focused on configuring and validating the **Navis ASV** in the Virtual RobotX (VRX) simulation environment and progressively developing **Guidance, Navigation & Control (GNC)** capabilities including waypoint navigation, Line-of-Sight guidance, heading control, sensor integration, visualization, joystick-based vessel control and reinforcement-learning-based path following.

This engineering work later provided the simulation and autonomy foundation for my separate research into recurrent reinforcement learning, multi-vessel collision avoidance and predictive safety filtering.

---

## Project Overview

The project was developed progressively from vessel integration and manual control toward autonomous navigation, perception and learning-based control.

```text
Navis ASV Integration
        |
        v
ROS 2 ↔ Gazebo Interface
        |
        v
Keyboard + Joystick Control
        |
        v
GPS + IMU Navigation
        |
        v
Interactive Waypoint Selection
        |
        v
LOS Guidance
        |
        v
Heading / Rudder Control
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

The simulated platform includes:

- thruster actuation
- rudder steering
- hydrodynamic behaviour
- GPS / NavSat
- IMU
- LiDAR
- ZED2i stereo camera
- DVL
- ROS 2 interfaces
- interactive waypoint selection
- keyboard and joystick control

The simulation platform enabled navigation, sensing and control algorithms to be developed and evaluated in software before later physical-system validation stages.

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

# Guidance, Navigation & Control (GNC)

The project implements a complete simulation-level **Guidance, Navigation & Control (GNC)** workflow.

### Guidance

- waypoint-based path definition
- Line-of-Sight (LOS) guidance
- look-ahead target generation
- desired-heading generation

### Navigation

- GPS / NavSat position
- IMU orientation
- yaw / heading estimation
- waypoint tracking
- Cross-Track Error (CTE) evaluation

### Control

- heading-error control
- rudder commands
- thruster commands
- keyboard interface
- joystick interface
- autonomous waypoint following
- Nomoto-based vessel-dynamics experimentation

The overall GNC loop can be represented as:

```text
        GPS / IMU
            |
            v
     Vessel State
            |
            v
      LOS Guidance
            |
            v
     Desired Heading
            |
            v
      Heading Error
            |
            v
    Steering Control
            |
            v
   Rudder / Thruster
            |
            v
        Navis ASV
            |
            +------------------+
                               |
                               v
                         Sensor Feedback
                               |
                               +----> next control cycle
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

The waypoint interface allows navigation targets selected in the simulated environment to enter the ROS 2 navigation pipeline.

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

CTE represents the lateral displacement of the vessel from the desired path:

```text
Desired Path
------------------------------------------------
                         |
                         | CTE
                         |
                       Vessel
```

Tracking CTE allows path-following performance to be evaluated quantitatively rather than relying only on visual inspection.

---

# Heading & Vessel Control

The desired heading generated by LOS guidance is compared with the vessel heading obtained from the IMU.

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
- vessel position
- waypoint information

through ROS 2.

---

# Keyboard & Joystick Interface Control

Manual vessel control was implemented before autonomous navigation to validate the ROS 2–Gazebo command interface and vessel response.

## Keyboard Control

The repository includes:

```text
keyboard_asv_control
```

for direct thruster and rudder commands.

This was used during initial vessel integration and functional testing.

---

## Joystick Interface & Teleoperation

A **Logitech game controller** was integrated into the ROS 2 control pipeline for manual ASV operation.

```text
Logitech Joystick
       |
       v
    joy_node
       |
       v
joystick_asv_control
       |
   +---+---+
   |       |
   v       v
Thruster  Rudder
Command   Command
   |       |
   +---+---+
       |
       v
    Navis ASV
```

The joystick interface was used to test:

- manual vessel manoeuvring
- thruster response
- rudder response
- ROS 2 command transmission
- steering behaviour
- vessel dynamics
- transition from manual to autonomous control

This provided a practical control interface for validating the simulated ASV before autonomous GNC algorithms were introduced.

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

The Navis ASV simulation integrates multiple sensors supporting navigation, perception and system evaluation.

| Sensor | Application |
|---|---|
| **GPS / NavSat** | Vessel position and waypoint navigation |
| **IMU** | Orientation, yaw and heading estimation |
| **LiDAR** | Range sensing and obstacle perception |
| **ZED2i Stereo Camera** | Stereo imagery and 3D perception |
| **DVL** | Vessel velocity information |

---

## GPS / NavSat

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
GNC Pipeline
```

---

## LiDAR

A simulated LiDAR provides range measurements for obstacle perception.

Gazebo LiDAR data is bridged into ROS 2 and represented using:

```text
sensor_msgs/msg/LaserScan
```

The repository also contains LiDAR monitoring and debugging utilities.

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

## RViz2 Visualization

<p align="center">
  <img src="IMG_0240.jpeg" width="900"
       alt="RViz stereo-camera and PointCloud2 visualization">
</p>

<p align="center">
  <em>RViz2 visualization of stereo-camera images together with the reconstructed 3D PointCloud2 output.</em>
</p>

RViz2 was used to inspect the simulated sensor pipeline and verify the ROS 2 perception outputs.

---

# DVL Integration

A simulated **Doppler Velocity Log (DVL)** interface was included for vessel-velocity information.

The repository contains:

- Gazebo DVL plugin
- ROS 2 DVL publisher
- velocity-topic monitoring

This extends the simulated sensing stack beyond position and orientation measurements.

---

# ROS 2 / Gazebo Integration

Guidance and control algorithms operate as ROS 2 nodes while vessel physics and sensor simulation run in Gazebo.

```text
ROS 2 GNC / Controller
          |
     +----+----+
     |         |
     v         v
 Thruster    Rudder
 Command     Command
     |         |
     +----+----+
          |
          v
     Gazebo Relay
          |
          v
      Navis ASV
          |
          v
   Simulated Sensors
          |
          v
        ROS 2
```

This architecture allows guidance, sensing and control components to be developed independently from the underlying simulator.

---

# Reinforcement Learning Path Following

The internship project was extended from classical LOS-based navigation to **learning-based continuous-control experiments**.

Two off-policy reinforcement-learning algorithms were investigated:

### Soft Actor-Critic (SAC)

and

### Twin Delayed Deep Deterministic Policy Gradient (TD3)

The repository contains trained policy checkpoints:

```text
rl_models/
├── sac_asv_waypoint.zip
└── td3_asv_waypoint.zip
```

The RL environment uses simplified Nomoto vessel dynamics and continuous rudder control for waypoint/path-following experiments.

Both policies were trained for **900,000 timesteps** in the experimental study.

---

# SAC vs TD3 Evaluation

The trained SAC and TD3 policies were evaluated across **10 path geometries**, including straight, curved, turning, U-turn, triangular, oval, semicircular and sharp-zigzag trajectories.

The evaluation considered three operating regimes:

1. **No disturbance**
2. **Current disturbance**
3. **Current + sensor noise**

The experiments evaluate more than successful completion by examining:

- trajectory tracking
- Cross-Track Error (CTE)
- rudder behaviour
- path geometry
- disturbance response
- sensor-noise robustness

---

## Semicircle Evaluation

<p align="center">
  <img src="sac-td3-semicircle.jpeg" width="950"
       alt="SAC and TD3 semicircle path-following evaluation">
</p>

<p align="center">
  <em>SAC vs TD3 semicircle evaluation showing trajectory tracking, rudder command, cross-track error and disturbance traces.</em>
</p>

The semicircle experiment tests continuous curved-path tracking and provides a useful comparison of the two learned controllers over sustained curvature.

The figure combines:

- desired path and waypoints
- SAC trajectory
- TD3 trajectory
- rudder commands
- absolute CTE
- disturbance traces

---

## Sharp-Zigzag Evaluation

<p align="center">
  <img src="sac-td3-sharp-zigzag.jpeg" width="950"
       alt="SAC and TD3 sharp-zigzag path-following evaluation">
</p>

<p align="center">
  <em>SAC vs TD3 sharp-zigzag evaluation showing trajectory tracking, steering activity, cross-track error and environmental disturbances.</em>
</p>

The sharp-zigzag trajectory represents a more demanding path-following condition because the desired heading changes rapidly and repeatedly.

It provides a useful stress test for:

- steering response
- tracking accuracy
- controller recovery
- rudder activity
- disturbance robustness

---

# SAC vs TD3 Results

In the nominal no-disturbance evaluation, both trained controllers successfully completed all ten test paths.

| Metric | SAC | TD3 |
|---|---:|---:|
| Successful paths | **10 / 10** | **10 / 10** |
| Mean CTE | **0.245 m** | **0.455 m** |

The evaluation showed that SAC achieved lower mean cross-track error in the nominal ten-path comparison.

The broader experiments also evaluated the policies under environmental current and sensor-noise conditions to examine robustness beyond nominal path following.

The purpose of the comparison was not only to determine whether the vessel reached the goal, but also to study:

- path-tracking accuracy
- steering behaviour
- control effort
- robustness
- sensitivity to path geometry

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
├── sac-td3-semicircle.jpeg
├── sac-td3-sharp-zigzag.jpeg
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

> **Note:** The launcher originates from the internship development environment and may contain machine-specific paths. These should be updated when reproducing the project on another system.

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

## Guidance, Navigation & Control (GNC)

- Waypoint navigation
- Line-of-Sight (LOS) guidance
- Cross-Track Error (CTE)
- Desired-heading generation
- Heading-error control
- Rudder control
- Thruster control
- Joystick interface & teleoperation
- Keyboard control
- Nomoto first-order vessel dynamics
- Hydrodynamic modelling
- Path-following evaluation

## Sensors & Perception

- GPS / NavSat
- IMU
- LiDAR
- LaserScan
- ZED2i stereo camera
- Stereo disparity
- PointCloud2
- DVL
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
- Multi-path evaluation
- Disturbance testing
- Sensor-noise testing

## ROS 2 Development

- `rclpy`
- ROS 2 nodes
- Publishers / subscribers
- Topics
- Sensor messages
- ROS–Gazebo bridges
- Custom ROS 2 packages
- ROS 2 CLI
- `colcon`

## Programming & Development

- Python
- C++
- NumPy
- Bash
- Linux / Ubuntu 22.04
- Git
- GitHub

## Evaluation & Visualization

- CSV logging
- Matplotlib
- RViz2
- Gazebo visualization
- CTE analysis
- Rudder-command analysis
- Path visualization
- Quantitative policy comparison
- Multi-scenario testing

---

# Internship Scope

This repository represents the **engineering development and reinforcement-learning path-following work carried out around the Navis ASV simulation platform during the internship**.

```text
Navis ASV / VRX Integration
            |
            v
ROS 2 ↔ Gazebo Communication
            |
            v
Keyboard + Joystick Control
            |
            v
GPS + IMU Navigation
            |
            v
Waypoint Interface
            |
            v
Guidance, Navigation & Control
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
SAC / TD3 Path Following
```

The project established the simulation, sensing and GNC foundation that was subsequently extended into a separate collision-avoidance research project.

---

# Subsequent Research

Following the internship-stage work, the autonomous-navigation framework was extended toward:

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

Keeping the repositories separate distinguishes the original **internship engineering, GNC and SAC/TD3 experimentation** from the subsequent **research contribution**.

---

# Project Context

This work was developed during an engineering internship at **Seaconvoy Systems Engineering Pvt. Ltd.**

The internship involved configuring and validating an existing Seaconvoy-developed ASV model in Gazebo, establishing the simulation and ROS 2 framework, and developing navigation, sensing, control and reinforcement-learning experiments around the simulated Navis ASV platform.

---

# Author

**Padma Muthu Lakshmanan**  
B.Tech — Instrumentation & Control Engineering  
National Institute of Technology, Tiruchirappalli

[GitHub](https://github.com/Padma1320)
