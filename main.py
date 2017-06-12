# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import threading
import struct
import ctypes
import re
import ui_main
import ControlCAN

class MainDlg(QDialog, ui_main.Ui_dlgMain):
  __USBCAN = None
  __DevTypeList = {"DEV_USBCAN"  : 3,
                   "DEV_USBCAN2" : 4 }
  __devType = None
  __devIdx  = None
  __Chn     = None
  __timer   = None
  __baud    = '''
            Time0    Time1
10 Kbps      0x9F     0xFF
20 Kbps      0x18     0x1C
40 Kbps      0x87     0xFF
50 Kbps      0x09     0x1C
80 Kbps      0x83     0xFF
100 Kbps     0x04     0x1C
125 Kbps     0x03     0x1C
200 Kbps     0x81     0xFA
250 Kbps     0x01     0x1C
400 Kbps     0x80     0xFA
500 Kbps     0x00     0x1C
666 Kbps     0x80     0xB6
800 Kbps     0x00     0x16
1000 Kbps    0x00     0x14
'''
  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def __init__(self, parent=None):
    super(MainDlg, self).__init__(parent)
    self.setupUi(self)

    self.cmb_devType.addItem("DEV_USBCAN")
    self.cmb_devType.addItem("DEV_USBCAN2")
    self.cmb_devType.setCurrentIndex(1)

    self.cmb_Chn.addItem("1")
    self.cmb_Chn.addItem("2")
    self.cmb_Chn.setCurrentIndex(0)

    self.lineEdit_AccCode.setText("00000000")
    self.lineEdit_AccMask.setText("FFFFFFFF")
    self.lineEdit_Time0.setText("00")
    self.lineEdit_Time1.setText("1C")

    self.cmb_Filter.addItem(u"接收全部类型")
    self.cmb_Filter.addItem(u"只接收标准帧")
    self.cmb_Filter.addItem(u"只接收扩展帧")
    self.cmb_Filter.setCurrentIndex(0)

    self.cmb_Mode.addItem(u"正常")
    self.cmb_Mode.addItem(u"只听")
    self.cmb_Mode.addItem(u"自测")
    self.cmb_Mode.setCurrentIndex(0)

    self.cmb_FrameType.addItem(u"标准帧")
    self.cmb_FrameType.addItem(u"扩展帧")
    self.cmb_FrameType.setCurrentIndex(0)

    self.cmb_FrameFormat.addItem(u"数据帧")
    self.cmb_FrameFormat.addItem(u"远程帧")
    self.cmb_FrameFormat.setCurrentIndex(0)

    self.pushBtn_startCAN.setDisabled(1)
    self.pushBtn_txdata.setDisabled(1)

    try:
      self.__USBCAN = ctypes.windll.LoadLibrary(".\ControlCAN.dll")
      self.pushBtn_connect.setDisabled(0)
    except:
      QMessageBox.information(self, u"错误",  u"找不到ControlCAN.dll")
      sys.exit

    boardInfo = ControlCAN.VCI_BOARD_INFO1()
    x = self.__USBCAN.VCI_FindUsbDevice(ctypes.byref(boardInfo))
    for i in range(x):
      self.cmb_devIndex.addItem(str(i))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  #自动关联的槽函数
  @pyqtSlot()
  def on_pushBtn_connect_clicked(self):
    if self.pushBtn_connect.text() == u'连接':
      text = self.cmb_devType.currentText()
      text = text.toLatin1()
      str = ""
      for i in text:
        str += i
      self.__devType = self.__DevTypeList.get(str)
      
      self.__devIdx = self.cmb_devIndex.currentIndex()
      err = self.__USBCAN.VCI_OpenDevice(self.__devType, self.__devIdx, 0)
      if err == 1:
        #QMessageBox.information(self, u"恭喜",  u"连接成功!")
        self.cmb_devType.setDisabled(1)
        self.cmb_devIndex.setDisabled(1)
        self.cmb_Chn.setDisabled(1)
        self.pushBtn_startCAN.setDisabled(0)
        self.pushBtn_connect.setText(u'关闭')
      else:
        QMessageBox.information(self, u"错误",  u"找不到设备")

    elif self.pushBtn_connect.text() == u'关闭':
      self.__timer.cancel()
      self.__USBCAN.VCI_CloseDevice(self.__devType, self.__devIdx)
      self.cmb_devType.setDisabled(0)
      self.cmb_devIndex.setDisabled(0)
      self.cmb_Chn.setDisabled(0)
      self.pushBtn_startCAN.setDisabled(1)
      self.pushBtn_txdata.setDisabled(1)
      self.pushBtn_connect.setText(u'连接')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot()
  def on_pushBtn_startCAN_clicked(self):
    self.__Chn = self.cmb_Chn.currentIndex()

    qs = self.lineEdit_AccCode.text();  qs = qs.toUInt(16);  AccCode = qs[0];
    qs = self.lineEdit_AccMask.text();  qs = qs.toUInt(16);  AccMask = qs[0];
    qs = self.lineEdit_Time0.text();    qs = qs.toUInt(16);  time0   = qs[0];
    qs = self.lineEdit_Time1.text();    qs = qs.toUInt(16);  time1   = qs[0];
    filter = self.cmb_Filter.currentIndex() + 1
    mode   = self.cmb_Mode.currentIndex()

    initcfg = ControlCAN.VCI_INIT_CONFIG()
    initcfg.AccCode  = AccCode
    initcfg.AccMask  = AccMask
    initcfg.Reserved = 0
    initcfg.Filter   = filter
    initcfg.Timing0  = time0
    initcfg.Timing1  = time1
    initcfg.Mode     = mode
    err = self.__USBCAN.VCI_InitCAN(self.__devType, self.__devIdx, self.__Chn, ctypes.addressof(initcfg))
    if err == 1:
      self.__USBCAN.VCI_StartCAN(self.__devType, self.__devIdx, self.__Chn)
      self.pushBtn_txdata.setDisabled(0)
      self.__timer = threading.Timer(0.1, self.can_rx)
      self.__timer.start()
    elif err == 0:
      QMessageBox.information(self, u"错误",  u"初始化失败")
    elif err == -1:
      QMessageBox.information(self, u"错误",  u"设备不存在")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot(str)
  def on_lineEdit_AccCode_textChanged(self, s):
    if self.pushBtn_connect.text() == u'关闭':
      self.on_pushBtn_startCAN_clicked()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot(str)
  def on_lineEdit_AccMask_textChanged(self, s):
    if self.pushBtn_connect.text() == u'关闭':
      self.on_pushBtn_startCAN_clicked()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot(str)
  def on_lineEdit_Time0_textChanged(self, s):
    if self.pushBtn_connect.text() == u'关闭':
      self.on_pushBtn_startCAN_clicked()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot(str)
  def on_lineEdit_Time1_textChanged(self, s):
    if self.pushBtn_connect.text() == u'关闭':
      self.on_pushBtn_startCAN_clicked()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot(int)
  def on_cmb_Filter_currentIndexChanged(self, i):
    if self.pushBtn_connect.text() == u'关闭':
      self.on_pushBtn_startCAN_clicked()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot(int)
  def on_cmb_Mode_currentIndexChanged(self, i):
    if self.pushBtn_connect.text() == u'关闭':
      self.on_pushBtn_startCAN_clicked()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot()
  def on_pushBtn_txdata_clicked(self):
    type   = self.cmb_FrameType.currentIndex()
    format = self.cmb_FrameFormat.currentIndex()
    qs = self.lineEdit_ID.text();   qs = qs.toUInt(16);  ID = qs[0];
    
    qs = self.lineEdit_Data.text();
    qs = qs.toLatin1()
    s  = ""
    for i in qs: s += i
    s = s.strip()            #去除前后空格
    t = re.split("\\s+", s)
    sz = len(t)
    if sz > 8: sz = 8
    data = (ctypes.c_ubyte * 8)()
    for i in range(sz):
      data[i] = int(t[i], 16)

    canobj = ControlCAN.VCI_CAN_OBJ()
    canobj.ID = ID
    #canobj.TimeStamp
    #canobj.TimeFlag
    #canobj.SendType
    canobj.RemoteFlag = format  #1 远程 0 数据
    canobj.ExternFlag = type    #1 扩展 0 标准
    canobj.DataLen    = sz
    canobj.Data       = data
    frameNum = self.__USBCAN.VCI_Transmit(self.__devType, self.__devIdx, self.__Chn, ctypes.addressof(canobj), 1)
    if frameNum == -1:
      QMessageBox.information(self, u"错误",  u"设备错误")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot()
  def on_pushBtn_baudHelp_clicked(self):
    self.textEdit_recv.insertPlainText(self.__baud)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  @pyqtSlot()
  def on_pushBtn_clr_clicked(self):
    self.textEdit_recv.clear()
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def can_rx(self):
    rxobj = ControlCAN.VCI_CAN_OBJ()
    res = self.__USBCAN.VCI_Receive(self.__devType, self.__devIdx, self.__Chn, ctypes.addressof(rxobj), 1000, 100);
    if res > 0:
      #print res
      dl     = rxobj.DataLen;
      type   = rxobj.ExternFlag;  type   = (type==0)   and (u'标准帧') or (u'扩展帧')
      format = rxobj.RemoteFlag;  format = (format==0) and (u'数据帧') or (u'远程帧')
      id     = rxobj.ID
      rx = 'ID: 0x' + ("%02X" %(id)) + ' ' + type + ' ' + format + ' ' + str(dl) + 'B:  '

      data = rxobj.Data
      s = ""
      for i in range(dl):
        s += "%02X " %(data[i])

      self.textEdit_recv.insertPlainText(rx + s + '\r\n')

    self.__timer = threading.Timer(0.1, self.can_rx)
    self.__timer.start()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app = QApplication(sys.argv)
mainDlg = MainDlg()
mainDlg.show()
app.exec_()



