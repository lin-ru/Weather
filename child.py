from PyQt5.QtCore import QThread, pyqtSignal


class MyThread(QThread):
    my_signal = pyqtSignal([int])
    def __init__(self):
        super(MyThread, self).__init__()
        self.count = 0

    def run(self):
        while True:
            self.my_signal.emit(self.count)
            if self.count == 6:
                self.count = 0
            else:
                self.count += 1
            self.sleep(20)