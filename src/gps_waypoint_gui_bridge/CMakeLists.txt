cmake_minimum_required(VERSION 3.8)
project(gps_waypoint_gui_bridge)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(gps_waypoint_gui_bridge_node
  src/gps_waypoint_gui_bridge_node.cpp
)

ament_target_dependencies(gps_waypoint_gui_bridge_node
  rclcpp
  nav_msgs
  geometry_msgs
)

install(TARGETS
  gps_waypoint_gui_bridge_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
