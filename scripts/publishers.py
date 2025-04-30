#!/usr/bin/env python3
"""Publish data to ROS topic (ROS 2 Jazzy compatible)"""

import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

from mavros_msgs.msg import OverrideRCIn


class Pubs:
    """
    Class that controls publishing data to ROS topics.

    Attributes:
        data (dict): Dictionary containing all topic data and publishers
        node (Node): ROS 2 node instance
    """

    def __init__(self):
        self.node = Node('set_mav_data')
        self.data = {}
        self.topics = []  # List of (topic, msg_type, queue) tuples
        self.subscribe_topics()

    def get_data(self):
        return self.data

    def set_data(self, path, value=None, pub=None):
        """Add topic to dict and optionally publish data

        Args:
            path (str): Topic path
            value: Message data to publish
            pub: Publisher object to register
        """
        keys = path.strip('/').split('/')
        current = self.data
        for key in keys:
            current = current.setdefault(key, {})

        if pub is not None:
            current['pub'] = pub

        if value is not None and 'pub' in current:
            try:
                current['pub'].publish(value)
            except Exception as e:
                self.node.get_logger().error(f"Publish error on {path}: {e}")

    def subscribe_topic(self, topic, msg_type, queue_depth=10):
        qos = QoSProfile(depth=queue_depth)
        pub = self.node.create_publisher(msg_type, topic, qos)
        self.set_data(topic, pub=pub)

    def subscribe_topics(self):
        for topic, msg_type, queue_depth in self.topics:
            self.subscribe_topic(topic, msg_type, queue_depth)

    def shutdown(self):
        self.node.destroy_node()
        rclpy.shutdown()


def main():
    rclpy.init()
    pub = Pubs()

    # Register a publisher
    pub.subscribe_topic('/mavros/rc/override', OverrideRCIn)

    # Create dummy OverrideRCIn message
    def send_rc_override():
        msg = OverrideRCIn()
        msg.channels = [1201, 1200, 1200, 1200, 1200, 1200, 1200, 1205]
        pub.set_data('/mavros/rc/override', msg)

    try:
        while rclpy.ok():
            send_rc_override()
            time.sleep(1)
    except KeyboardInterrupt:
        pub.node.get_logger().info('Shutting down publisher...')
    finally:
        pub.shutdown()


if __name__ == '__main__':
    main()
