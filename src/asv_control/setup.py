from setuptools import setup, find_packages

package_name = 'asv_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='ASV control package for VRX Gazebo',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'keyboard_asv_control = asv_control.keyboard_asv_control:main',
            'joystick_asv_control = asv_control.joystick_asv_control:main',
            'asv_gz_relay = asv_control.asv_gz_relay:main',
            'imu_rpy_publisher = asv_control.imu_rpy_publisher:main',
            'gps_publisher = asv_control.gps_publisher:main',
            'path_publisher = asv_control.path_publisher:main',
            'gazebo_path_trail = asv_control.gazebo_path_trail:main',
            'gazebo_click_waypoint_node = asv_control.gazebo_click_waypoint_node:main',
            'adaptive_los_pid_follower = asv_control.adaptive_los_pid_follower:main',
            'dvl_publisher = asv_control.dvl_publisher:main',
            'nomoto_gz_pose_sim = asv_control.nomoto_gz_pose_sim:main',
            'lidar_debug_node = asv_control.lidar_debug_node:main',
            'sensor_sync_logger = asv_control.sensor_sync_logger:main',
           ],
    },
)
