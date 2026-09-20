cmake_minimum_required(VERSION 3.8)
project(asv_dvl_plugin)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(gz-sim7 REQUIRED)
find_package(gz-plugin2 REQUIRED)
find_package(gz-transport12 REQUIRED)
find_package(gz-msgs9 REQUIRED)

add_library(ASVDVLPlugin SHARED
  src/ASVDVLPlugin.cc
)

target_link_libraries(ASVDVLPlugin
  gz-sim7::gz-sim7
  gz-plugin2::gz-plugin2
  gz-transport12::gz-transport12
  gz-msgs9::gz-msgs9
)

install(
  TARGETS ASVDVLPlugin
  LIBRARY DESTINATION lib
)

ament_package()
