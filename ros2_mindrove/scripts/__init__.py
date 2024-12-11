import sys
import os

sys.path.append("~/ros2_ws")

# Add the main project to the file path, since the ROS file structure goes
# |_ project
# |__ scripts
# |____ *.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
