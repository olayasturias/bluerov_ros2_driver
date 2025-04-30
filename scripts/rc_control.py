#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import time
import cv2


import publishers as pubs
import subscribers as subs

from geometry_msgs.msg import TwistStamped
from mavros_msgs.srv import CommandBool
from sensor_msgs.msg import JointState, Joy, BatteryState
from mavros_msgs.msg import OverrideRCIn, RCIn, RCOut


class Code:

    def __init__(self):
        self.node = rclpy.create_node('bluerov_rc_node')

        # Arm the vehicle
        self.arm_service = self.node.create_client(CommandBool, '/mavros/cmd/arming')
        while not self.arm_service.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info('Waiting for /mavros/cmd/arming service...')
        self.arm(True)

        # Initialize publishers and subscribers
        self.pub = pubs.Pubs()
        self.sub = subs.Subs()

        self.pub.subscribe_topic('/mavros/rc/override', OverrideRCIn)
        self.pub.subscribe_topic('/mavros/setpoint_velocity/cmd_vel', TwistStamped)
        self.pub.subscribe_topic('/BlueRov2/body_command', JointState)

        self.sub.subscribe_topic('/joy', Joy)
        self.sub.subscribe_topic('/mavros/battery', BatteryState)
        self.sub.subscribe_topic('/mavros/rc/in', RCIn)
        self.sub.subscribe_topic('/mavros/rc/out', RCOut)

        # Register shutdown hook
        self.node.get_logger().info('Registering shutdown callback')

    def arm(self, arm=True):
        """ Arm or disarm the vehicle """
        req = CommandBool.Request()
        req.value = arm

        future = self.arm_service.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)

        if future.result() is not None:
            self.node.get_logger().info(f'Vehicle {"armed" if arm else "disarmed"}: success={future.result().success}')
        else:
            self.node.get_logger().error(f'Failed to call arm service: {future.exception()}')

    @staticmethod
    def pwm_to_thrust(pwm):
        return (-3.04338931856672e-13 * pwm ** 5
                + 2.27813523978448e-9 * pwm ** 4
                - 6.73710647138884e-6 * pwm ** 3
                + 0.00983670053385902 * pwm ** 2
                - 7.08023833982539 * pwm
                + 2003.55692021905)

    def run(self):
        rate = self.node.create_rate(10)  # 10 Hz
        try:
            while rclpy.ok():
                rclpy.spin_once(self.node, timeout_sec=0.1)

                try:
                    voltage = self.sub.get_data()['mavros']['battery']['voltage']
                    rc_in = self.sub.get_data()['mavros']['rc']['in']['channels']
                    rc_out = self.sub.get_data()['mavros']['rc']['out']['channels']

                    self.node.get_logger().info(f'Battery voltage: {voltage}')
                    self.node.get_logger().info(f'RC In: {rc_in}')
                    self.node.get_logger().info(f'RC Out: {rc_out}')
                except Exception as error:
                    self.node.get_logger().warn(f'Get data error: {error}')

                try:
                    joy = self.sub.get_data()['joy']['axes']
                    override = [int(val * 400 + 1500) for val in joy]
                    override += [0] * (8 - len(override))  # pad to 8 channels
                    self.pub.set_data('/mavros/rc/override', override)
                except Exception as error:
                    self.node.get_logger().warn(f'Joy error: {error}')

                try:
                    rc = self.sub.get_data()['mavros']['rc']['out']['channels']
                    joint = JointState()
                    joint.name = [f"thr{i + 1}" for i in range(5)]
                    joint.position = [self.pwm_to_thrust(pwm) for pwm in rc]
                    self.pub.set_data('/BlueRov2/body_command', joint)
                except Exception as error:
                    self.node.get_logger().warn(f'RC error: {error}')

                rate.sleep()

        except KeyboardInterrupt:
            self.node.get_logger().info("Keyboard interrupt detected. Shutting down...")

    def disarm(self):
        self.node.get_logger().info("Disarming vehicle...")
        self.arm(False)


def main(args=None):
    rclpy.init(args=args)
    code = Code()
    try:
        code.run()
    except KeyboardInterrupt:
        code.node.get_logger().info("Shutting down via KeyboardInterrupt")
    finally:
        code.disarm()
        code.node.destroy_node()

if __name__ == '__main__':
    main()