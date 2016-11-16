#!/usr/bin/env python
'''
Monitor listen packets from Elcon/TCCH. Tested on TCCH-120-15 (1800W), under Python 2.7.12.
Should work on all Elcon/TCCH chargers with the non-CAN firmware.
Non-CAN firmware chargers allow selection of cell count by pushing a hidden button at power-up.
Based on work by user Coulomb @ http://www.diyelectriccar.com
'''

import struct
import binascii
from sys import exit 

# Test data
#
wire_data =             b'\xFF\xFE\xF0\x4A\x02\x0D\x14\x14\x00\x00\x01\x41\x64\x3A\x16\x41' 
wire_data = wire_data + b'\x4A\x70\xF0\x00\x00\x00\x00\x43\x21\x5E\x20\x40\x2D\x18\x11\x00'
wire_data = wire_data + b'\x00\x00\x00\x43\x21\x72\xE6\xFF\x0A\x41\x70\x00\x00\x00\x00\x00'
wire_data = wire_data + b'\x00\x43\xB0\xA2\x0C\x43\x4A\x19\x9A\x40\x2E\x2C\xCE\x40\x2E\x2C'
wire_data = wire_data + b'\xCE\x00\x00\x00\x00\x3D\x61\xF2\x59\x00\x01\x02\x01\x01\x5F'

# Packet structure format specifier. See: https://docs.python.org/2/library/struct.html
#
struct_format = '> '						# big-endian
struct_format = struct_format + 'H '		# WORD,  Start characters (0xFFFE)
struct_format = struct_format + 'B '        # BYTE,  Type (Listen: 0xF0, Master: 0xC5)
struct_format = struct_format + 'B '        # BYTE,  Length (excluding: Start characters, Type, Length and Check sum (5 bytes))
struct_format = struct_format + 'B '        # BYTE,  EEPROM
struct_format = struct_format + 'B '        # BYTE,  HW Ver
struct_format = struct_format + 'B '        # BYTE,  SW Ver
struct_format = struct_format + 'B '        # BYTE,  Curve Ver
struct_format = struct_format + 'H '		# WORD,  Error
struct_format = struct_format + 'B '        # BYTE,  Input voltage flag
struct_format = struct_format + 'f '        # FLOAT, Internal temp
struct_format = struct_format + 'f '        # FLOAT, Internal temp start
struct_format = struct_format + 'f '        # FLOAT, External temp
struct_format = struct_format + 'f '        # FLOAT, DC Voltage
struct_format = struct_format + 'f '        # FLOAT, DC Current
struct_format = struct_format + 'f '        # FLOAT, DC Current Wave
struct_format = struct_format + 'f '        # FLOAT, Battery Voltage
struct_format = struct_format + 'B '        # BYTE,  Input voltage
struct_format = struct_format + 'B '        # BYTE,  Battry over temp flag
struct_format = struct_format + 'f '        # FLOAT, Battery temp         
struct_format = struct_format + 'f '        # FLOAT, Voltage temp compens 
struct_format = struct_format + 'f '        # FLOAT, PFC Voltage  
struct_format = struct_format + 'f '        # FLOAT, DC Voltage set       
struct_format = struct_format + 'f '        # FLOAT, DC Current set       
struct_format = struct_format + 'f '        # FLOAT, Battery Current set   
struct_format = struct_format + 'f '        # FLOAT, DVDT 15min           
struct_format = struct_format + 'f '        # FLOAT, AH total delivered   
struct_format = struct_format + 'H '		# WORD,  Time charging minutes
struct_format = struct_format + 'B '        # BYTE,  Charge state flag
struct_format = struct_format + 'B '        # BYTE,  Relay flag          
struct_format = struct_format + 'B '        # BYTE,  Serial error count 
struct_format = struct_format + 'B '        # BYTE,  Check sum

# Unpack the packet using the format specifier
#
unpacked = struct.unpack(struct_format, wire_data)

# Validate the listen packet.
#
if (unpacked[0] != 0xFFFE):
    print "Incorrect start characters: 0x" + format(unpacked[0],  '04x').upper()
    exit(1)

if (unpacked[1] != 0xF0):
    print "Incorrect type: 0x" + format(unpacked[1],  '02x').upper()
    exit(2)

if (unpacked[2] != 74):
    print "Incorrect length: " + format(unpacked[2])
    exit(3)
    
# Packet check-sum calculation: XOR all bytes in packet, exluding Start characters and Check sum.
#
stripped = wire_data[2:78]
checksum = reduce(lambda x,y:x^y, map(ord, stripped))
if (unpacked[30] != checksum):
    print "Incorrect checksum. Calculated: 0x" + format(checksum, '02x').upper() + "  Read: 0x" + format(unpacked[30], '02x').upper()
    exit(4)

print "Dumping Listen Packet -"
print "  Packet start:          0x" + format(unpacked[0],  '04x').upper()
print "  Packet type:           0x" + format(unpacked[1],  '02x').upper()
print "  Length:                0x" + format(unpacked[2],  '02x').upper() + '    - ' + format(unpacked[2])
print "  EEPROM version:        0x" + format(unpacked[3],  '02x').upper() + '    - ' + format(unpacked[3])
print "  HW version:            0x" + format(unpacked[4],  '02x').upper() + '    - ' + format(unpacked[4]/10.0, '02.2f')
print "  SW version:            0x" + format(unpacked[5],  '02x').upper() + '    - ' + format(unpacked[5]/10.0, '02.2f')
print "  Curve version:         0x" + format(unpacked[6],  '02x').upper() + '    - ' + format(unpacked[6]/10.0, '02.2f')
print "  Error code:            0x" + format(unpacked[7],  '04x').upper()
print "  Input voltage flag:    0x" + format(unpacked[8],  '02x').upper() + '    - (1=>120VAC, 2=>240VAC)'
print "  Internal temp:         "   + format(unpacked[9],  '04.2f')         + '   - degrees C'
print "  Internal temp start:   "   + format(unpacked[10], '04.2f')         + '   - degrees C'
print "  External temp:         "   + format(unpacked[11], '04.2f')
print "  DC Voltage:            "   + format(unpacked[12], '04.2f')
print "  DC Current:            "   + format(unpacked[13], '04.2f')
print "  DC Current Wave:       "   + format(unpacked[14], '04.2f')
print "  Battery Voltage:       "   + format(unpacked[15], '04.2f')
print "  Outside temp state:    0x" + format(unpacked[16], '02x').upper()
print "  Battry over temp flag: 0x" + format(unpacked[17], '02x').upper()
print "  Battery temp:          "   + format(unpacked[18], '04.2f')
print "  Voltage temp compens:  "   + format(unpacked[19], '04.2f')
print "  PFC Voltage:           "   + format(unpacked[20], '04.2f')
print "  DC Voltage set:        "   + format(unpacked[21], '04.2f')
print "  DC Current set:        "   + format(unpacked[22], '04.2f')
print "  Battery Current set    "   + format(unpacked[23], '04.2f')
print "  DVDT 15min:            "   + format(unpacked[24], '04.2f')
print "  AH total delivered:    "   + format(unpacked[25], '04.2f')
print "  Time charging minutes: 0x" + format(unpacked[26], '04x').upper() + '    - ' + format(unpacked[26])
print "  Charge state:          0x" + format(unpacked[27], '02x').upper()
print "  Relay flag:            0x" + format(unpacked[28], '02x').upper()
print "  Serial error count:    0x" + format(unpacked[29], '02x').upper()
print "  Check sum:             0x" + format(unpacked[30], '02x').upper()

exit(0)
