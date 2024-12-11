"""Type definitions for Mindrove-related functions"""
import enum
from dataclasses import dataclass

from nptyping import NDArray, Float64
from typing import Tuple, Dict, Union, Optional

from mindrove.board_shim import (
    MindRoveInputParams, 
    BoardIds, 
    MindRovePresets, 
    IpProtocolTypes
)

class MindroveChannels(str, enum.Enum):
   """
   Enum for mindrove channels

   Represented as a string enum in order to utilize for getters.
   """
   EEG = "eeg"
   EXG = "exg"
   EMG = "emg"
   ECG = "ecg"
   EOG = "eog"
   EDA = "eda"
   PPG = "ppg"
   ACCEL = "accel"
   ROTATION = "rotation"
   ANALOG = "analog"
   GYRO = "gyro"
   OTHER = "other"
   TEMPERATURE = "temperature"
   RESISTANCE = "resistance"

MindroveSampleBuffer = Dict[MindroveChannels, Optional[NDArray[Float64]]]

@dataclass(frozen = True)
class MindroveInputParamsConstructor:
   """
   Mindrove input parameter constructor.

   This only exists because the `MindroveInputParams` class has no way
   to easily construct the fields, for whatever reason.
   """
   serial_port: str = ''
   mac_address: str = ''
   ip_address: str = ''
   ip_address_aux: str = ''
   ip_address_anc: str = ''
   ip_port: int = 0
   ip_port_aux: int = 0
   ip_port_anc: int = 0
   ip_protocol: IpProtocolTypes = IpProtocolTypes.NO_IP_PROTOCOL.value
   other_info: str = ''
   timeout: int = 0
   serial_number: str = ''
   file: str = ''
   file_aux: str = ''
   file_anc: str = ''
   master_board: BoardIds = BoardIds.NO_BOARD.value

   def as_mindrove(self) -> MindRoveInputParams:
      """
      Constructs a `MindroveInputParams` object with relevant 
      fields.

      Returns:
          MindRoveInputParams: Input parameters
      """
      params = MindRoveInputParams()
      for k,v in self.__dict__.items():
         params.__dict__[k] = v
         
      return params

@dataclass(frozen = True)
class MindroveHardwareDescription:
   """
   A hardware description for a given piece of Mindrove hardware.

   This contains all essential configuration fields:
   
   @param board_id: Board ID for hardware
   @param params: Input parameters for hardware
   @param preset: MindrovePresets object
   @param channels: Relevant channels to monitor for hardware
   """
   board_id: BoardIds
   params: MindroveInputParamsConstructor
   preset: MindRovePresets
   channels: Tuple[MindroveChannels, ...]
