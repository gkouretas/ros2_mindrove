#!/usr/bin/python3
import rclpy

from mindrove_typedefs import *
from mindrove_armband_publisher import MindroveArmbandRosPublisher
from mindrove.utils import LogLevels

from python_utils.ros2_utils.comms.node_manager import create_simple_node
from mindrove_configs import *

def main() -> None:
   rclpy.init()
   node = create_simple_node(MINDROVE_ROS_NODE)

   interface = MindroveArmbandRosPublisher(
      simulated = False,
      additional_channels = ("timestamp", "battery"),
      log_level = LogLevels.LEVEL_TRACE
   )

   interface.run(
      num_samples = 200, 
      nonblocking = True,
      lag_compensation = True
   )

   rclpy.spin(node)

if __name__ == "__main__":
   main()