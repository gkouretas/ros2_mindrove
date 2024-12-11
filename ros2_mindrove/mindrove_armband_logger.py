#!/usr/bin/python3
from __future__ import annotations

from mindrove_configs import *
from idl_definitions.msg import MindroveArmBandEightChannelMsg

from python_utils.ros2_utils.comms.message_csv_logger import ROSMessageCSVLogger
from python_utils.ros2_utils.comms.node_manager import get_node

class ROSMindroveCSVLogger(ROSMessageCSVLogger):
    def __init__(self, log_name: str = MindroveArmBandEightChannelMsg.__name__, **kwargs):
        super().__init__(
            node = get_node(MINDROVE_ROS_NODE), 
            msg_type = MindroveArmBandEightChannelMsg, 
            topic = MINDROVE_ROS_TOPIC_NAME, 
            log_name = log_name, 
            **kwargs
        )

        self._last_frame: int = -1

    def callback(self, data: MindroveArmBandEightChannelMsg):
        """
        Callback for ROS bioplux .csv logger.

        Check for skipped frames prior to logging data.
        """
        if self._last_frame + 1 != data.frame: 
            self._node.get_logger().warning(f"{MINDROVE_ROS_TOPIC_NAME} sub: frame skip. {self._last_frame} -> {data.frame}")
        
        self._last_frame = data.frame

        return super().callback(data)