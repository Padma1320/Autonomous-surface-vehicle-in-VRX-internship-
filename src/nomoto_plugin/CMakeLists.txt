cmake_minimum_required(VERSION 3.8)
project(nomoto_plugin)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(gz-sim7 REQUIRED)
find_package(gz-plugin2 REQUIRED)
find_package(gz-math7 REQUIRED)

include_directories(include)

add_library(NomotoPlugin SHARED
  src/NomotoPlugin.cc
)

ament_target_dependencies(NomotoPlugin
  rclcpp
  std_msgs
)

target_link_libraries(NomotoPlugin
  gz-sim7::gz-sim7
  gz-plugin2::gz-plugin2
  gz-math7::gz-math7
)

install(TARGETS NomotoPlugin
  LIBRARY DESTINATION lib
)

ament_package()
