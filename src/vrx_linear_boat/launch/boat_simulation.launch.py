from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('vrx_linear_boat')
    urdf_path = os.path.join(pkg_dir, 'urdf', 'boat.urdf')
    
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # State publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_desc,
                'use_sim_time': False
            }]
        ),
        # GNC Logic Controller
        Node(
            package='vrx_linear_boat',
            executable='realtime_gnc_node',
            name='realtime_marine_gnc',
            output='screen'
        ),
        # Visualizer GUI (RViz2)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(pkg_dir, 'launch', 'config.rviz')],
            output='screen'
        )
    ])
