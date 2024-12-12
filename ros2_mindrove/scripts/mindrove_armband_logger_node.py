#!/usr/bin/python3
"""
Script for executing a logger node for the Mindrove armband
"""
import rclpy

# Project based / ROS imports
from ros2_mindrove.mindrove_configs import *
from ros2_mindrove.mindrove_armband_logger import ROSMindroveCSVLogger
from python_utils.ros2_utils.comms.node_manager import create_simple_node

def main() -> None:
    rclpy.init()
    node = create_simple_node(MINDROVE_ROS_NODE)

    ROSMindroveCSVLogger()
    rclpy.spin(node)

if __name__ == "__main__":
    main()