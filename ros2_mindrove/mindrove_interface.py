"""Mindrove interface module"""
import threading
import time, timeit

from mindrove.board_shim import BoardShim
from mindrove.utils import LogLevels

from mindrove_typedefs import *
from mindrove_processing import *

from typing import List, Dict, Tuple, Union

class MindroveInterface(BoardShim):
   def __init__(
      self, 
      desc: MindroveHardwareDescription, 
      additional_channels: Tuple[str, ...] = ("timestamp",),
      log_level: LogLevels = LogLevels.LEVEL_OFF,
      samples_per_interval: int = 1
   ) -> None:
      """
      MindroveInterface, built on top of `BoardShim`

      Args:
          desc (MindroveHardwareDescription): Hardware description of interface
          log_level (LogLevels, optional): Log level to use. Defaults to LogLevels.LEVEL_OFF.
      """
      super().__init__(desc.board_id, desc.params.as_mindrove())
      self.set_log_level(log_level)
      self.prepare_session()

      self._desc = desc
      self._sampling_interval = 1.0 / self.get_sampling_rate(self._desc.board_id, self._desc.preset)
      self._sampling_rate = self._sampling_interval / samples_per_interval

      self._scaling_factors = get_scaling_factors()

      self._buf_size: int
      self._num: int = 0
      
      self._channel_map: Dict[str, Union[int, List[int]]] = {
         k: [] for k in self._desc.channels
      }
      
      self._init_channel_map(additional_channels)

   def start_stream(self, num_samples: int, streamer_params: str = None) -> None:
      # Overloaded from BoardShim.start_stream
      self._buf_size = num_samples
      return super().start_stream(num_samples, streamer_params)  

   def get_data_buffer(self) -> Tuple[float, MindroveSampleBuffer]:
      """
      Get most recent data buffer

      Returns:
         Dict[MindroveChannels, Float64]: Dictionary contianing relevant channels and their polled values.
      """
      def get_factor(key) -> float:
         """Local getter for Mindrove channel scaling factors"""
         if key in self._scaling_factors.keys(): 
            return self._scaling_factors[key]
         else: 
            return 1.0

      t = time.time()
      data = self.get_board_data(self._buf_size, self._desc.preset)
      return t, {k: (data[channel] * get_factor(k)) if data[channel].size != 0 else None for k, channel in self._channel_map.items()}

   def run(self, num_samples: int, streamer_params: str = None, nonblocking: bool = True, lag_compensation: bool = False):
      """
      Cyclically query Mindrove device for data

      Args:
          num_samples (int): Number of data points to store in circular buffer.
          streamer_params (str, optional): Parameter for Mindrove streaming. Defaults to None.
          nonblocking (bool, optional): Configures if a thread will be dispatched, or if a blocking loop 
          will be entered. Defaults to True.
      """
      self.start_stream(num_samples, streamer_params)
      if nonblocking: 
         threading.Thread(target = self._cyclic_sample, args = (lag_compensation,), daemon = True).start()
      else: 
         self._cyclic_sample(lag_compensation)

   def _cyclic_sample(self, lag_compensation: bool = True):
      """      
      Cyclic sampling of Mindrove data. Will query the data at the sampling rate configured by the sensor.


      Args:
          lag_compensation (bool, optional): Will apply lag compensation by reducing the dynamic delays based 
          upon the estimated latency. Defaults to True.
      """
      self._num = 0
      avg_lag = 0.0
      callback = self.get_data_buffer

      while True:
         t0 = timeit.default_timer()
         t, sample = callback()
         if self._sample_is_empty(sample):
            # Ignore empty sample
            continue
         else:
            if (self._num == 0):
               self.log_message(LogLevels.LEVEL_INFO, "Received first sample")
               
            self.data_callback(t, sample)
            self._num += 1

            # Compute the average drift we are experiencing from the expected sampling rate
            if lag_compensation:
               avg_lag = (avg_lag * (self._num-1) + (t - sample["timestamp"][-1])) / self._num

            # Compute delay time
            # Offset by the computed lag
            delay_s = max(0.0, self._sampling_interval - (timeit.default_timer() - t0) - avg_lag)
            time.sleep(delay_s)

   def data_callback(self, timestamp: float, data: MindroveSampleBuffer) -> None:
      """
      Abstract method for a data callback

      Args:
          timestamp (float): Timestamp [sec] where data is received
          data (MindroveSampleBuffer): Mindrove sample buffer
      """
      raise NotImplementedError

   def _init_channel_map(self, additional_channels: Tuple[str, ...]) -> None:
      """
      Acquire the channel indexes for the given hardware's sensor(s).
      """
      for channel in self._desc.channels:
         func_name = f"get_{channel}_channels"
         self._channel_map[channel] = getattr(BoardShim, func_name)(self._desc.board_id, self._desc.preset)

      for channel in additional_channels:
         func_name = f"get_{channel}_channel"
         self._channel_map[channel] = getattr(BoardShim, func_name)(self._desc.board_id, self._desc.preset)

   def _sample_is_empty(self, sample: MindroveSampleBuffer):
      for v in sample.values():
         if v is None: return True

      return False