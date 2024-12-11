"""
Utility functions for processing Mindrove signals
"""
from mindrove_typedefs import *

def get_scaling_factors() -> Dict[MindroveChannels, float]:
   """
   Get relevant scaling factors to convert from ADC -> real units.

   Currently included:
   - EMG: uV
   - ACCEL: m/s^2
   - GYRO: dps

   Args:
       interface (BoardShim): BoardShim interface

   Returns:
       Dict[MindroveChannels, float]: Dictionary that can be keyed with
       a Mindrove channel enum / string identifier.
   """
   # Expected format is: x.y.z
   # version = tuple((int(x) for x in interface.get_version().split(".")))

   # NOTE: these are the scaling factors, pre-5.0.0
   # Return these if relevant, no easy way to check the version w/ this...   
   # return {
   #    MindroveChannels.EMG: 0.045,
   #    MindroveChannels.ACCEL: 0.061035e-3 * 9.81,
   #    MindroveChannels.GYRO: 0.01526
   # }
   
   return {
      MindroveChannels.EMG: 1.0,       # [uV]
      MindroveChannels.ACCEL: 9.81,    # [g] -> [m/s^2] 
      MindroveChannels.GYRO: 1.0       # [dps]
   }