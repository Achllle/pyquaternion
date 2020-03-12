cmake_minimum_required(VERSION 3.0.2)
project(pyquaternion)

find_package(catkin REQUIRED)

catkin_package()

catkin_python_setup()

if (CATKIN_ENABLE_TESTING)
  catkin_add_nosetests(tests/test_quaternion.py)
endif()
