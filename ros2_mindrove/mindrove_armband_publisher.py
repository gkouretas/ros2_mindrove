from typing import Tuple
from mindrove_interface import MindroveInterface

from mindrove.utils import LogLevels

from mindrove_typedefs import *
from mindrove_configs import *

from idl_definitions.msg import MindroveArmBandEightChannelMsg
from geometry_msgs.msg import Vector3
from python_utils.ros2_utils.comms.node_manager import get_node

# Hardware definition for real arm band
MindroveArmBand = MindroveHardwareDescription(
   board_id = BoardIds.MINDROVE_WIFI_BOARD, 
   params = MindroveInputParamsConstructor( # see https://docs.mindrove.com/SupportedBoards.html#streaming-board
      ip_address = "192.168.4.1",
      ip_port = 4210,
      timeout = 10
   ),
   preset = MindRovePresets.DEFAULT_PRESET, 
   channels = (
      MindroveChannels.EMG,
      MindroveChannels.ACCEL,
      MindroveChannels.GYRO # TODO: are there more available for the armband?
   )
)

# Hardware definition for simulated arm band
SimulatedArmBand = MindroveHardwareDescription(
   board_id = BoardIds.SYNTHETIC_BOARD,
   params = MindroveInputParamsConstructor(),
   preset = MindRovePresets.DEFAULT_PRESET,
   channels = MindroveArmBand.channels
)

class MindroveArmbandRosPublisher(MindroveInterface):
    def __init__(self, simulated: bool = False, additional_channels: Tuple[str, ...] = ..., log_level: LogLevels = LogLevels.LEVEL_OFF) -> None:
        super().__init__(SimulatedArmBand if simulated else MindroveArmBand, additional_channels, log_level, samples_per_interval = 2)
        self.mindrove_publisher = get_node(MINDROVE_ROS_NODE).create_publisher(MindroveArmBandEightChannelMsg, MINDROVE_ROS_TOPIC_NAME, 0)
        self._ctrl_ts: float = 0.0

    def data_callback(self, timestamp: float, data: MindroveSampleBuffer) -> None:
         """
         Publish arm band message packet

         Args:
            timestamp (float): Timestamp taken when data was received
            data (MindroveSampleBuffer): Data buffer from Mindrove
         """
         msg = MindroveArmBandEightChannelMsg() 
         msg.frame = self._num
         msg.world_timestamp = timestamp
         msg.source_timestamp = data["timestamp"].flatten().tolist()
         msg.battery_percentage = data["battery"].flatten().tolist()

         _emg = data[MindroveChannels.EMG].flatten().tolist()

         # Get number of EMG samples we were able to extract from the buffer
         msg.num_emg_samples = len(_emg) // 8

         # Control timestamp, to be used for signal processing / frequency analysis
         # NOTE: maybe remove this from publishing if performance is poor? This can be computed offline easily...
         msg.control_timestamp = [self._ctrl_ts + (x * (self._sampling_rate)) for x in range(msg.num_emg_samples)]
         self._ctrl_ts += (self._sampling_rate * msg.num_emg_samples)

         msg.c1 = _emg[:msg.num_emg_samples]
         msg.c2 = _emg[msg.num_emg_samples:int(2*msg.num_emg_samples)]
         msg.c3 = _emg[int(2*msg.num_emg_samples):int(3*msg.num_emg_samples)]
         msg.c4 = _emg[int(3*msg.num_emg_samples):int(4*msg.num_emg_samples)]
         msg.c5 = _emg[int(4*msg.num_emg_samples):int(5*msg.num_emg_samples)]
         msg.c6 = _emg[int(5*msg.num_emg_samples):int(6*msg.num_emg_samples)]
         msg.c7 = _emg[int(6*msg.num_emg_samples):int(7*msg.num_emg_samples)]
         msg.c8 = _emg[int(7*msg.num_emg_samples):int(8*msg.num_emg_samples)]
         
         msg.accel = []
         msg.gyro = []

         # Get the number of IMU samples we were able to extract from the buffer
         # Divide by 3 b/c 1 sample = length 3 (x,y,z)
         # TODO: control timestamp for IMU???
         msg.num_imu_samples = data[MindroveChannels.ACCEL].size // 3 
         for accel, gyro in zip(data[MindroveChannels.ACCEL].T, data[MindroveChannels.GYRO].T):
            msg.accel.append(Vector3(x = accel[0], y = accel[1], z = accel[2]))
            msg.gyro.append(Vector3(x = gyro[0], y = gyro[1], z = gyro[2]))

         self.mindrove_publisher.publish(msg)