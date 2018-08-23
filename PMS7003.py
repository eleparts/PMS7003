"""
* PMS7003 데이터 수신 프로그램
* 수정 : 2018. 08. 14
* 제작 : eleparts 부설연구소
* SW ver. 1.0.0

참조
파이썬 라이브러리
https://docs.python.org/3/library/struct.html

점프 투 파이썬
https://wikidocs.net/book/1

PMS7003 datasheet
http://eleparts.co.kr/data/_gextends/good-pdf/201803/good-pdf-4208690-1.pdf
"""
import serial
import struct
import time


class PMS7003(object):

  # PMS7003 protocol data (HEADER 2byte + 30byte)
  PMS_7003_PROTOCOL_SIZE = 32

  # PMS7003 data list
  HEADER_HIGH            = 0
  HEADER_LOW             = 1
  FRAME_LENGTH           = 2
  DUST_PM1_0_CF1         = 3
  DUST_PM2_5_CF1         = 4
  DUST_PM10_0_CF1        = 5
  DUST_PM1_0_ATM         = 6
  DUST_PM2_5_ATM         = 7
  DUST_PM10_0_ATM        = 8
  DUST_AIR_0_3           = 9
  DUST_AIR_0_5           = 10
  DUST_AIR_1_0           = 11
  DUST_AIR_2_5           = 12
  DUST_AIR_5_0           = 13
  DUST_AIR_10_0          = 14
  RESERVEDF              = 15
  RESERVEDB              = 16 
  CHECKSUM               = 17


  # header check 
  def header_chk(self, buffer):

    if (buffer[self.HEADER_HIGH] == 66 and buffer[self.HEADER_LOW] == 77):
      return True

    else:
      return False

  # chksum value calculation
  def chksum_cal(self, buffer):

    buffer = buffer[0:self.PMS_7003_PROTOCOL_SIZE]

    # data unpack (Byte -> Tuple (30 x unsigned char <B> + unsigned short <H>))
    chksum_data = struct.unpack('!30BH', buffer)
    
    chksum = 0

    for i in range(30):
      chksum = chksum + chksum_data[i]

    return chksum

  # checksum check
  def chksum_chk(self, buffer):   
    
    chk_result = self.chksum_cal(buffer)
    
    chksum_buffer = buffer[30:self.PMS_7003_PROTOCOL_SIZE]
    chksum = struct.unpack('!H', chksum_buffer)
 
    if (chk_result == chksum[0]):
      return True

    else:
      return False

  # protocol size(small) check
  def protocol_size_chk(self, buffer):

    if(self.PMS_7003_PROTOCOL_SIZE <= len(buffer)):
      return True

    else:
      return False

  # protocol check
  def protocol_chk(self, buffer):
    
    if(self.header_chk(buffer) and self.protocol_size_chk(buffer) and self.chksum_chk(buffer)):
      return True
    else:
      return False 

  # unpack data 
  # <Tuple (13 x unsigned short <H> + 2 x unsigned char <B> + unsigned short <H>)>
  def unpack_data(self, buffer):
    
    buffer = buffer[0:self.PMS_7003_PROTOCOL_SIZE]

    # data unpack (Byte -> Tuple (13 x unsigned short <H> + 2 x unsigned char <B> + unsigned short <H>))
    data = struct.unpack('!2B13H2BH', buffer)

    return data


  def print_serial(self, buffer):
    
    chksum = self.chksum_cal(buffer)
    data = self.unpack_data(buffer)

    print ("============================================================================")
    print ("Header : %c %c \t\t | Frame length : %s" % (data[self.HEADER_HIGH], data[self.HEADER_LOW], data[self.FRAME_LENGTH]))
    print ("PM 1.0 (CF=1) : %s\t | PM 1.0 : %s" % (data[self.DUST_PM1_0_CF1], data[self.DUST_PM1_0_ATM]))
    print ("PM 2.5 (CF=1) : %s\t | PM 2.5 : %s" % (data[self.DUST_PM2_5_CF1], data[self.DUST_PM2_5_ATM]))
    print ("PM 10.0 (CF=1) : %s\t | PM 10.0 : %s" % (data[self.DUST_PM10_0_CF1], data[self.DUST_PM10_0_ATM]))
    print ("0.3um in 0.1L of air : %s" % (data[self.DUST_AIR_0_3]))
    print ("0.5um in 0.1L of air : %s" % (data[self.DUST_AIR_0_5]))
    print ("1.0um in 0.1L of air : %s" % (data[self.DUST_AIR_1_0]))
    print ("2.5um in 0.1L of air : %s" % (data[self.DUST_AIR_2_5]))
    print ("5.0um in 0.1L of air : %s" % (data[self.DUST_AIR_5_0]))
    print ("10.0um in 0.1L of air : %s" % (data[self.DUST_AIR_10_0]))
    print ("Reserved F : %s | Reserved B : %s" % (data[self.RESERVEDF],data[self.RESERVEDB]))
    print ("CHKSUM : %s | read CHKSUM : %s | CHKSUM result : %s" % (chksum, data[self.CHECKSUM], chksum == data[self.CHECKSUM]))
    print ("============================================================================")



# UART / USB Serial : 'dmesg | grep ttyUSB'
USB = '/dev/ttyUSB0'
UART = '/dev/ttyAMA0'

# Baud Rate
Speed = 9600


# example
if __name__=='__main__':

  #serial setting 
  ser = serial.Serial(UART, Speed, timeout = 1)

  dust = PMS7003()

  while True:
    
    ser.flushInput()
    buffer = ser.read(1024)

    if(dust.protocol_chk(buffer)):
    
      print("DATA read success")
    
      # print data
      dust.print_serial(buffer)
      
    else:

      print("DATA read fail...")     


  ser.close()

