""""
UBX
Forked from the Comm module of SD-Node, written c. 2017
Later mods from HeadingSensor, c. 2021
Takes a serial UBX input, parses and extracts heading information
Optionally, forwards to a UDP address:port
Tested with Python >=3.6

By: JOR
    v0.1    22SEP21     First draft
    v0.2    06JAN21     Rework for ZED-9R
"""

import serial
import sys

# Utilities used by all UBX tools
import ubx.Sensors
from ubx.utilities import ubx_crc, log_file_name, mc_sender, ip_validator, udp_sender
from ubx.UBXParser import UBXParser

# Get all the settings for this programme
import settings.sensors as settings
this_programme = settings.UBXHEADINGSENSOR['PROG']
MCAST_GRP = settings.UBXHEADINGSENSOR["MCAST_GROUP"]
MCAST_PORT = settings.UBXHEADINGSENSOR["MCAST_PORT"]
SERIAL_DEVICE = settings.UBXHEADINGSENSOR["SERIAL_DEVICE"]
#MY_IPv4_ADDRESS = settings.UBXHEADINGSENSOR["MY_IPv4_ADDRESS"]
#ip_validator(MY_IPv4_ADDRESS)

# Get the NMEA sentence class
from nmea.hdt import hdt
myHDT = hdt()

# Instantiate an object to parse UBX
myUBX = UBXParser()

# Get a logfile name for UBX
ubx_log_file = './logfiles/' + log_file_name('.ubx')

print(f'***** {this_programme} *****')
print(f'Accepts UBX from serial port {SERIAL_DEVICE}')
print('1. Extracts information and logs raw UBX')
print(f'2. Outputs to a multicast address {MCAST_GRP}:{MCAST_PORT} for other applications to use.')
print(f'Logging as {ubx_log_file}')

# Main Loop
try:
    print("press [ctrl][c] at any time to exit...")

    with serial.Serial("/dev/ttyAMA4") as Serial_Port1:
        Serial_Port1.baudrate = 115200
        Serial_Port1.bytesize = serial.EIGHTBITS
        Serial_Port1.parity = serial.PARITY_NONE
        Serial_Port1.stopbits = serial.STOPBITS_ONE
        Serial_Port1.timeout = None

        Serial_Port1.flushInput()

        # Find the serial number of the UBlox device, send the query, it will be the first sentence back
        ubx_sec_uniqid_query = b'\xB5\x62\x27\x03\x00\x00\x2A\xA5'
        Serial_Port1.write(ubx_sec_uniqid_query)

        # Continuous loop until [ctrl][c]
        while True:
            # Read the first byte, if no byte, loop
            byte1 = Serial_Port1.read(1)
            if len(byte1) <1:
                break
            # Check for UBX header = xB5 and X62, Unicode = µb
            if byte1 == b"\xb5":
                byte2 = Serial_Port1.read(1)
                if len(byte2) < 1:
                    break
                if byte2 == b"\x62":
                    # Get the UBX class
                    byte3 = Serial_Port1.read(1)
                    # Get the UBX message
                    byte4 = Serial_Port1.read(1)
                    # Get the UBX payload length
                    byte5and6 = Serial_Port1.read(2)
                    # Calculate the length of the payload
                    length_of_payload = int.from_bytes(byte5and6, "little", signed=False)
                    # Read the buffer for the payload length
                    ubx_payload = Serial_Port1.read(length_of_payload)
                    # Last two bytes are 2*CRC, save them for later use
                    ubx_crc_a = Serial_Port1.read(1)
                    ubx_crc_b = Serial_Port1.read(1)
                    # Calculate CRC using CLASS + MESSAGE + LENGTH + PAYLOAD
                    payload_for_crc = byte3 + byte4 + byte5and6 + ubx_payload
                    # If the CRC is good, proceed
                    if ubx_crc(payload_for_crc,ubx_crc_a, ubx_crc_b):
                        # Log the ubx bytes
                        payload_for_save = byte1 + byte2 + payload_for_crc + ubx_crc_a + ubx_crc_b
                        with open (ubx_log_file, 'ab') as file:
                            file.write(payload_for_save)
                    # Process the ubx bytes
                        # Reset the new data flags
                        myUBX.new_heading = 0
                        myUBX.new_position = 0
                        # Parse
                        myUBX.ubx_parser(byte3, byte4, ubx_payload)
                        # Now see if there are new values
                        if myUBX.new_heading:
                            # Get the heading as a float and round to two places
                            heading = round(myUBX.heading, 4)
                            # Convert heading from float to string
                            heading_string = str(heading)
                            # Create a NMEA sentence
                            nmea_full_hdt = myHDT.create(heading_string)
                            print(nmea_full_hdt)
                            # Processed the old heading, reset the flag
                            myUBX.new_heading = 0
                            # Send the heading to a multicast address
                            # mc_sender(MY_IPv4_ADDRESS, MCAST_GRP, MCAST_PORT, nmea_full_hdt.encode())
                            udp_sender(MCAST_GRP, MCAST_PORT, nmea_full_hdt.encode())
                    else:
                        print('Bad CRC')
            else:
                print(f"What is {byte1}")

except serial.SerialException as err:
    print("Serial port error: {0}".format(err))
except OSError as err:
    print("OS error: {0}".format(err))
except ValueError as err:
    print("Value Error error: {0}".format(err))
except KeyboardInterrupt:
    print("\n" + "Caught keyboard interrupt, exiting")
    exit(0)
except:
    print("Unexpected error in UBX Sensor:", sys.exc_info()[0])
finally:
    print("Exiting Main Thread")
    exit(0)

