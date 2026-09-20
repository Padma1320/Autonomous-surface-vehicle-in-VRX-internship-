cmake_minimum_required(VERSION 3.10.2)
project(gz_waypoint_clicker)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt5 REQUIRED COMPONENTS Core Quick)
find_package(gz-cmake3 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-gui7 REQUIRED)
find_package(gz-sim7 REQUIRED)
find_package(gz-rendering7 REQUIRED)
find_package(gz-transport12 REQUIRED)
find_package(gz-msgs9 REQUIRED)

add_library(WaypointClicker SHARED
  src/WaypointClicker.cc
  WaypointClicker.qrc
)

target_link_libraries(WaypointClicker
  Qt5::Core
  Qt5::Quick
  gz-plugin2::register
  gz-gui7::gz-gui7
  gz-sim7::gz-sim7
  gz-rendering7::gz-rendering7
  gz-transport12::gz-transport12
  gz-msgs9::gz-msgs9
)

install(TARGETS WaypointClicker
  LIBRARY DESTINATION lib
)
