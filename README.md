# NvidiaGPUFanCurve
Python tools for changing fan curve for multiple NVIDIA gpus. Tested with python 3.6 on Ubuntu 16.04.

Work in progress
- indicator.py runs nvidiafancontrol and adds a menu item with stats
- nvidiafancontrol.py can be run independently and prints stuff to console
- nvidia_fancontrol.py (should be called config.py) is the configuration can set curves for each gpu and interval(seconds)
