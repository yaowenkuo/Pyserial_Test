# -*- coding: utf-8 -*-

import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer

from win.ui_demo_1 import Ui_Form


class Pyqt5_Serial(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("串列埠測試")
        self.ser = serial.Serial()
        self.port_check()

        # 已接收及發送計數歸0
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))

    def init(self):
        self.formGroupBox.setTitle("串列埠")
        self.verticalGroupBox.setTitle("接收區")
        self.verticalGroupBox_2.setTitle("發送區")
        
        self.s1__lb_1.setText("檢查串列埠")
        self.s1__lb_2.setText("COM")
        self.s1__lb_3.setText("鮑 率")
        self.s1__lb_4.setText("位 元")
        self.s1__lb_5.setText("校 驗")
        self.s1__lb_6.setText("停 止")
        
        self.label.setText("已接收")
        self.label_2.setText("已發送")
        
        self.hex_receive.setText("HEX 接收")
        self.hex_send.setText("HEX 發送")
        self.timer_send_cb.setText("定時傳送")
    
        # 串列埠檢查 Button
        self.s1__box_1.setText("搜 尋")
        self.s1__box_1.clicked.connect(self.port_check)

        # 串列埠資訊
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        # 打開串列埠  Button
        self.open_button.setText("開 啟")
        self.open_button.clicked.connect(self.port_open)

        # 關閉串列埠 Button
        self.close_button.setText("關 閉")
        self.close_button.clicked.connect(self.port_close)

        # 資料發送 Button
        self.s3__send_button.setText("發 送")
        self.s3__send_button.clicked.connect(self.data_send)

        # 設定定時傳送 Timer 執行緒
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.timer_send_cb.stateChanged.connect(self.data_send_timer)

        # 設定定時接收Timer 執行緒
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # 清除發送窗口
        self.s3__clear_button.clicked.connect(self.send_data_clear)

        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)

    # 串列埠檢查
    def port_check(self):
        # 檢查所有可用串列埠，將信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 找不到串列埠")

    # 串列埠信息
    def port_imf(self):
        # 顯示選定的串列埠信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打開串列埠
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = int(self.s1__box_3.currentText())
        self.ser.bytesize = int(self.s1__box_4.currentText())
        self.ser.stopbits = int(self.s1__box_6.currentText())
        self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "串列埠無法打開！")
            return None

        # 串列埠開啟後, 啟動Timer 執行緒(2ms)
        self.timer.start(2)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox1.setTitle("串列埠狀態（已開啟）")

    # 闗閉串列埠
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
            
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        
        # 已接收及發送計數歸0
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.formGroupBox1.setTitle("串列埠狀態（已關閉）")

    # 發送資料
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s3__send_text.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.hex_send.isChecked():
                    # hex發送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '請輸入16進制數據，並以空格分開!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ASCII發送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.lineEdit_2.setText(str(self.data_num_sended))
        else:
            pass

    # 接收資料
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex顯示
            if self.hex_receive.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.s2__receive_text.insertPlainText(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.s2__receive_text.insertPlainText(data.decode('iso-8859-1'))

            # 統計接數的數量
            self.data_num_received += num
            self.lineEdit.setText(str(self.data_num_received))

            # 獲取text指標
            textCursor = self.s2__receive_text.textCursor()
            # 移動到底部
            textCursor.movePosition(textCursor.End)
            # 設置text指標
            self.s2__receive_text.setTextCursor(textCursor)
        else:
            pass

    # 定時發送資料
    def data_send_timer(self):
        if self.timer_send_cb.isChecked():
            self.timer_send.start(int(self.lineEdit_3.text()))
            self.lineEdit_3.setEnabled(False)
        else:
            self.timer_send.stop()
            self.lineEdit_3.setEnabled(True)

    # 清除顯示
    def send_data_clear(self):
        self.s3__send_text.setText("")

    def receive_data_clear(self):
        self.s2__receive_text.setText("")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
