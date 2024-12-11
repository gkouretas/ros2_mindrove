#!/usr/bin/python3
from mindrove_typedefs import *
from mindrove_armband_publisher import MindroveArmbandRosPublisher
from mindrove.utils import LogLevels

def main() -> None:
   interface = MindroveArmbandRosPublisher(
      simulated = True,
      additional_channels = ("timestamp", "battery"),
      log_level = LogLevels.LEVEL_TRACE
   )

   interface.run(
      num_samples = 200, 
      nonblocking = False,
      lag_compensation = True
   )

if __name__ == "__main__":
   main()