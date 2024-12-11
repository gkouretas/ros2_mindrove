import os
import glob
from setuptools import find_packages, setup

package_name = 'ros2_mindrove'

setup(
    name=package_name,
    version='0.0.0',
    # packages=find_packages(exclude=['test']),
    packages = [package_name, f"{package_name}/scripts", f"{package_name}/python_utils/ros2_utils/comms"],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*.launch.py'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gkouretas',
    maintainer_email='gkouretas@scu.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pub = ros2_mindrove.scripts.mindrove_armband_publisher_node:main',
            'pub_sim = ros2_mindrove.scripts.mindrove_simulated_armband_publisher_node:main',
            'logger = ros2_mindrove.scripts.mindrove_armband_logger_node:main'
        ],
    },

)

