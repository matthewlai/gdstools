# gdstools
Scripts to interact with GW Instek GDS 1000B oscilloscopes.

## Pre-requisites
* Python 3
* Pillow (`pip3 install Image`)
* PySerial (`pip3 install pyserial`)

### capture_screen.py
Captures a screenshot of the current display.
Requires an oscilloscope that supports the ":DISPlay:OUTPut?" command (tested on GDS-1104B).

`capture_screen.py OUTPUT_FILE --port SERIAL_PORT --width SCREEN_WIDTH --height SCREEN_HEIGHT`

Example:
`capture_screen.py screenshot.png --port /dev/ttyACM0 --width 800 --height 480`
