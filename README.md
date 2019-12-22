# terminator
Create menu from setup files, make changes to terminator configuration file and open 4 windows in terminal:
* 2 upper windows - connection to hosts with configured port forwarding
* 2 buttom windows - console connection to devices

### Prerequisites
* python3
* pexpect

## Deployment
1.Install requirements:
```
pip3 install -r requirements.txt (Python 3)
```
2. Create xml file, described your setup.
3. Call launch.py file:
```
.../python3 launch.py
```

## Posible Defects
1. Not stable console connection with minicom version lower than 2.6. If script doesn't connect you to device, terminal window will be active and you can login manually
2. After connecting to console auto-completion doesn't work for first command. Workaround - resize window or repeate command.

## Limitation
Script work only on Unix family platform. Let me know if it you need support for Windows
