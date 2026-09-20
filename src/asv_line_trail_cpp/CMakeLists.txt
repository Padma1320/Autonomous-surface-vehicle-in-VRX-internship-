cmake_minimum_required(VERSION 3.8)
project(asv_line_trail_cpp)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)

find_package(gz-transport12 REQUIRED)
find_package(gz-msgs9 REQUIRED)

add_executable(asv_line_trail_cpp src/asv_line_trail_cpp.cpp)

ament_target_dependencies(
  asv_line_trail_cpp
  rclcpp
  nav_msgs
)

target_link_libraries(
  asv_line_trail_cpp
  gz-transport12::gz-transport12
  gz-msgs9::gz-msgs9
)

install(
  TARGETS asv_line_trail_cpp
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
