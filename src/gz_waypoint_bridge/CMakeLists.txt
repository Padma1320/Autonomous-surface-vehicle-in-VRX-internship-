cmake_minimum_required(VERSION 3.8)
project(gz_waypoint_bridge)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(gz-transport12 REQUIRED)
find_package(gz-msgs9 REQUIRED)
add_executable(gz_waypoint_bridge_node src/gz_waypoint_bridge_node.cpp)

ament_target_dependencies(
  gz_waypoint_bridge_node
  rclcpp
  nav_msgs
  geometry_msgs
  sensor_msgs
)

target_link_libraries(gz_waypoint_bridge_node
  gz-transport12::gz-transport12
  gz-msgs9::gz-msgs9
  Geographic
)

install(TARGETS
  gz_waypoint_bridge_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
