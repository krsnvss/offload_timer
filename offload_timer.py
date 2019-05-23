#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from datetime import datetime, timedelta
from sql import *
from reporter import *
from mesconnector import *
from configparser import ConfigParser


# Load configuration file
cfg = ConfigParser()
cfg.read("settings.ini")
shift = int(cfg['common']['shift'])
timer_refresh = int(cfg['common']['timer_refresh'])


# Application GUI
class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.countdown)
        self.timer.setInterval(timer_refresh)
        self.timer.start()
        self.timer_limit = datetime(2018, 3, 4, 12, 3, 0)
        self.timer_step = timedelta(seconds=1)
        self.current_time = self.timer_limit
        self.countdown_positive = False
        self.current_shift = shift
        # Simple way to count seconds for MES
        self.mes_counter = 0
        self.gui()
    
    # Show window at the center of the screen
    def center(self, _widget):
        self.widget_size = _widget.frameGeometry()
        self.display_center = QtWidgets.QDesktopWidget().availableGeometry().center()
        self.widget_size.moveCenter(self.display_center)
        _widget.move(self.widget_size.topLeft())
        
    def gui(self):
        self.ui = uic.loadUi('./ui/mainwindow.ui')
        self.ui.countdownLcd.display(self.timer_limit.strftime('%M:%S'))
        self.ui.timeLimitLcd.display(self.timer_limit.strftime('%M:%S'))
        self.ui.actionOffloadStamp.triggered.connect(self.offload_stamp)
        self.lcd_color = QtGui.QPalette()
        self.lcd_color.setColor(self.lcd_color.WindowText, QtGui.QColor(0, 255, 0))
        self.lcd_color_warning = QtGui.QPalette()
        self.lcd_color_warning.setColor(self.lcd_color.WindowText, QtGui.QColor(255, 255, 0))
        self.lcd_color_late = QtGui.QPalette()
        self.lcd_color_late.setColor(self.lcd_color.WindowText, QtGui.QColor(255, 0, 0))        
        self.ui.countdownLcd.setPalette(self.lcd_color)
        self.ui.shiftTotalLcd.setPalette(self.lcd_color)
        self.ui.hourTotalLcd.setPalette(self.lcd_color)
        self.ui.timeLimitLcd.setPalette(self.lcd_color)
        self.ui.actionShiftChange.triggered.connect(self.shift_pick)
        self.ui.actionReport.triggered.connect(lambda: create_report())
        self.set_totals()
        self.center(self.ui)
        self.ui.show()        

    # Timer countdown
    def countdown(self):
        if self.countdown_positive:
            self.current_time += self.timer_step
            self.mes_counter -= 1
            self.ui.countdownLcd.setPalette(self.lcd_color_late)
            self.ui.timeLimitLcd.setPalette(self.lcd_color_late)
            self.ui.countdownLcd.display(self.current_time.strftime('%M:%S'))
        else:
            self.current_time -= self.timer_step
            if self.current_time.minute == 0 and self.current_time.second == 0:
                self.countdown_positive = True
                self.mes_counter = 0
            elif self.current_time.minute < 1:
                self.ui.countdownLcd.setPalette(self.lcd_color_warning)
                self.ui.timeLimitLcd.setPalette(self.lcd_color_warning)
            else:
                self.ui.countdownLcd.setPalette(self.lcd_color)
            self.ui.countdownLcd.display(self.current_time.strftime('%M:%S'))
            self.mes_counter += 1
        self.write_to_txt()

    # Set offload stamp, save db record
    def offload_stamp(self):
        self.current_time = self.timer_limit
        self.stamp = "{} отмечена выгрузка. Смена {}. "\
            .format(datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    self.current_shift)
        self.ui.statusbar.showMessage(self.stamp)
        self.countdown_positive = False
        record_insert(datetime.now(), self.current_shift)
        self.ui.timeLimitLcd.setPalette(self.lcd_color)
        self.set_totals()
        self.write_to_mes()

    # Show shift picker
    def shift_pick(self):
        self.shift_picker = uic.loadUi("./ui/shift_pick.ui")
        self.shift_picker.spinBox.setValue(self.current_shift)
        self.shift_picker.pushButton.clicked.connect(self.shift_change)
        self.center(self.shift_picker)
        self.shift_picker.show()

    # Change current shift
    def shift_change(self):
        self.current_shift = self.shift_picker.spinBox.value()
        self.shift_picker.close()

    # Update totalizers
    def set_totals(self):
        self.shift_totals = shift_total()
        self.hour_totals = hour_total()
        self.ui.shiftTotalLcd.display(self.shift_totals)
        self.ui.hourTotalLcd.display(self.hour_totals)

    # Write output to text file. For testing purposes only
    def write_to_txt(self):
        self.text = fill_txt(self.shift_totals,
                             self.hour_totals,
                             self.timer_limit.strftime('%M:%S'),
                             self.current_time.strftime('%M:%S'))
        with open("ledboard.txt", 'w') as ledboard:
            ledboard.write(self.text)

    # Save value to MES database
    def write_to_mes(self):
        if check_mes():
            mes_token = read_token()
            self.result = write_tag(mes_token, self.mes_counter)
            if self.result == 200:
                self.ui.statusbar.showMessage(self.stamp + "Сохранено в MES!")
        else:
            self.ui.statusbar.showMessage(self.stamp + " Сервер MES недоступен!")


# Run application
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    _gui = MainWindow()
    sys.exit(app.exec_())
