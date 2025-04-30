# bluerov_ros_driver

## Overview
The `bluerov_ros2_driver` is a ROS2 package designed for simulation and control of the BlueROV underwater robot. It includes functionalities for  processing sensor data and sending joystick commands.

## Dependencies

You'll need to install mavros:

```bash
sudo apt install ros-jazzy-mavros
```
Then install GeographicLib datasets by downloading and running the install_geographiclib_datasets.sh script:

```bash
wget https://raw.githubusercontent.com/mavlink/mavros/ros2/mavros/scripts/install_geographiclib_datasets.sh

chmod +x install_geographiclib_datasets.sh

sudo ./install_geographiclib_datasets.sh

```

## Installation
To install `bluerov_ros2_playground`, clone this repository into your ROS2 workspace and compile it using the ROS2 build tools.

```bash
cd ~/ros2_ws/src
git clone https://github.com/olayasturias/bluerov_ros2_driver.git
cd ~/ros2_ws
colcon build --packages-select bluerov_ros2_driver
```

## Launch
After installation, you can launch the simulation and control nodes using the provided launch files:
```
ros2 launch bluerov_ros2_driver mavros_launch.py
```