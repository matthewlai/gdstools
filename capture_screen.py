#!/usr/bin/env python3

#  This file is part of gdstools.
#
#  Copyright 2018 Matthew Lai
#
#  gdstools is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  gdstools is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with gdstools.  If not, see <https://www.gnu.org/licenses/>.

from argparse import ArgumentParser
from PIL import Image

import array
import serial
import sys

def ParseArgs():
  parser = ArgumentParser()
  parser.add_argument("-p", "--port", dest="port", type=str,
                      help="Serial port of the DSO", default="/dev/ttyACM0")
  parser.add_argument("--width", dest="width", type=int,
                      help="Horizontal resolution of the DSO", default=800)
  parser.add_argument("--height", dest="height", type=int,
                      help="Vertical resolution of the DSO", default=480)
  parser.add_argument("output", metavar="<output file>", type=str,
                      help="Output filename")
  return parser.parse_args()

def ReadBlockData(dso):
  header_len_block = dso.read(2)
  length_length = int(header_len_block.decode()[1])
  length_block = dso.read(length_length)
  data_length = int(length_block.decode())
  return array.array('H', dso.read(data_length))

def DecodeRLE(data):
  decoded_data = array.array('H')
  for i in range(0, len(data), 2):
    count = data[i]
    colour = data[i+1]
    for j in range(0, count):
      decoded_data.append(colour)
  return decoded_data
  
def ToRGB888(data):
  converted_data = array.array('B')
  for x in data:
    converted_data.append((x >> 8) & 0xf8)
    converted_data.append((x >> 3) & 0xfc)
    converted_data.append((x << 3) & 0xf8)
  return converted_data

def main():
  args = ParseArgs()

  with serial.Serial(args.port, timeout=10) as dso:
    # See if this is actually a DSO
    dso.write(b'*IDN?\n')
    idn = dso.readline()
    
    if idn.decode()[0:2] != "GW":
      sys.exit("Not a GW Instek oscilloscope? Exiting.")

    print("GW Oscilloscope found: " + idn.decode().rstrip())

    dso.write(b':DISPlay:OUTPut?\n')
    image_data = ReadBlockData(dso)
    decoded_data = DecodeRLE(image_data)
    decoded_data_len = len(decoded_data)

    expected_data_len = args.width * args.height
    if expected_data_len != decoded_data_len:
      exit("Screen size mismatch! Expecting: {}x{}={}, received: {}".format(
            args.width, args.height, expected_data_len, decoded_data_len))

    image = Image.frombytes(mode="RGB", size=(args.width, args.height),
                            data=ToRGB888(decoded_data).tobytes())
    image.save(args.output)

    print("Image saved to " + args.output)

main()
