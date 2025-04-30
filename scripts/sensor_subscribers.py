#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import bluerov_ros2_playground.bluerov_ros2_playground.video_gstreamer as video_gstreamer

from sensor_msgs.msg import Imu, FluidPressure, BatteryState
from mavros_msgs.msg import CameraImageCaptured, CamIMUStamp, RCIn


class SensorSubscriber(Node):

    def __init__(self):
        super().__init__('sensor_subscriber')

        self.camera_reader = video_gstreamer.Video()

        self.create_subscription(
            CameraImageCaptured,
            '/mavros/camera/image_captured',
            self.camera_callback,
            10)

        self.create_subscription(
            Imu,
            '/mavros/imu/data',
            self.imu_callback,
            10)

        self.create_subscription(
            CamIMUStamp,
            '/mavros/cam_imu_sync/cam_imu_stamp',
            self.cam_imu_sync_callback,
            10)

        self.create_subscription(
            RCIn,
            '/mavros/rc/in',
            self.rc_callback,
            10)

        self.create_subscription(
            BatteryState,
            '/mavros/battery',
            self.battery_callback,
            10)

    def camera_callback(self, msg: CameraImageCaptured):
        self.get_logger().info(f"Camera image captured: seq={msg.header.stamp.sec}, file={msg.file_path}")

    def imu_callback(self, msg: Imu):
        self.get_logger().info(f"IMU orientation: {msg.orientation}")

    def cam_imu_sync_callback(self, msg: CamIMUStamp):
        self.get_logger().info(f"Cam-IMU sync: frame={msg.frame_stamp}, imu={msg.imu_stamp}")

    def rc_callback(self, msg: RCIn):
        self.get_logger().info(f"RC input channels: {msg.channels}")

    def battery_callback(self, msg: BatteryState):
        self.get_logger().info(f"Battery voltage: {msg.voltage} V")


def main(args=None):
    rclpy.init(args=args)
    node = SensorSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
