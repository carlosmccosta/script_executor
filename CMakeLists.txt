cmake_minimum_required(VERSION 3.0.2)
project(script_executor)

set(${PROJECT_NAME}_CATKIN_COMPONENTS
    rospy
    std_msgs
)

find_package(catkin REQUIRED COMPONENTS ${${PROJECT_NAME}_CATKIN_COMPONENTS})

catkin_python_setup()

catkin_package(
  CATKIN_DEPENDS ${${PROJECT_NAME}_CATKIN_COMPONENTS}
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
