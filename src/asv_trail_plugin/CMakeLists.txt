cmake_minimum_required(VERSION 3.8)
project(asv_trail_plugin)

find_package(ament_cmake REQUIRED)
find_package(gz-sim7 REQUIRED)
find_package(gz-plugin2 REQUIRED)
find_package(gz-transport12 REQUIRED)
find_package(gz-msgs9 REQUIRED)

add_library(asv_trail_plugin SHARED
  src/asv_trail_plugin.cc
)

target_link_libraries(asv_trail_plugin
  gz-sim7::gz-sim7
  gz-plugin2::gz-plugin2
  gz-transport12::gz-transport12
  gz-msgs9::gz-msgs9
)

install(
  TARGETS asv_trail_plugin
  LIBRARY DESTINATION lib
)

ament_package()
