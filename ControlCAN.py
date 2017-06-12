# -*- coding: utf-8 -*-

from ctypes import *

class VCI_BOARD_INFO(Structure):
  _fields_ = [
  ("hw_Version", c_ushort),
  ("fw_Version", c_ushort),
  ("dr_Version", c_ushort),
  ("in_Version", c_ushort),
  ("irq_Num",    c_ushort),
  ("can_Num",    c_byte),
  ("str_Serial_Num", c_char * 20),
  ("str_hw_Type",    c_char * 40),
  ("Reserved",       c_ushort * 4)
  ]

class VCI_CAN_OBJ(Structure):
  _fields_ = [
  ("ID",          c_uint),
  ("TimeStamp",   c_uint),
  ("TimeFlag",    c_ubyte),
  ("SendType",    c_ubyte),
  ("RemoteFlag",  c_ubyte),
  ("ExternFlag",  c_ubyte),
  ("DataLen",     c_ubyte),
  ("Data",        c_ubyte * 8),
  ("Reserved",    c_ubyte * 3)
  ]

class VCI_CAN_STATUS(Structure):
  _fields_ = [
  ("ErrInterrupt", c_char),
  ("regMode",      c_char),
  ("regStatus",    c_char),
  ("regALCapture", c_char),
  ("regECCapture", c_char),
  ("regEWLimit",   c_char),
  ("regRECounter", c_char),
  ("regTECounter", c_char),
  ("Reserved",     c_int)
  ]

class VCI_ERR_INFO(Structure):
  _fields_ = [
  ("ErrCode",         c_uint),
  ("Passive_ErrData", c_byte * 3),
  ("ArLost_ErrData",  c_byte)
  ]

class VCI_INIT_CONFIG(Structure):
  _fields_ = [
  ("AccCode",   c_int),
  ("AccMask",   c_int),
  ("Reserved",  c_int),
  ("Filter",    c_ubyte),
  ("Timing0",   c_ubyte),
  ("Timing1",   c_ubyte),
  ("Mode",      c_ubyte)
  ]

class VCI_FILTER_RECORD(Structure):
  _fields_ = [
  ("ExtFrame",   c_int),
  ("Start",      c_int),
  ("End",        c_int)
  ]

#其他
class VCI_BOARD_INFO1(Structure):
  _fields_ = [
  ("hw_Version", c_ushort),
  ("fw_Version", c_ushort),
  ("dr_Version", c_ushort),
  ("in_Version", c_ushort),
  ("irq_Num",    c_ushort),
  ("can_Num",    c_byte),
  ("Reserved",   c_byte),
  ("str_Serial_Num",  c_char * 8),
  ("str_hw_Type",     c_char * 16),
  ("str_Usb_Serial",  c_char * 16)
  ]

class VCI_BOARD_INFO2(Structure):
  _fields_ = [
  ("hw_Version", c_ushort),
  ("fw_Version", c_ushort),
  ("dr_Version", c_ushort),
  ("in_Version", c_ushort),
  ("irq_Num",    c_ushort),
  ("can_Num",    c_byte),
  ("Reserved",   c_byte),
  ("str_Serial_Num",  c_char * 8),
  ("str_hw_Type",     c_char * 16),
  ("str_Usb_Serial",  c_char * 40)
  ]


