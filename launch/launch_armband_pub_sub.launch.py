from ros2_mindrove.mindrove_configs import MINDROVE_ROS_NODE
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ros2_mindrove',
            executable='pub',
            name=MINDROVE_ROS_NODE,
            output='screen'
        ),
        Node(
            package='ros2_mindrove',
            executable='logger',
            name=MINDROVE_ROS_NODE,
            output='screen'
        )
    ])
