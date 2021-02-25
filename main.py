import sys
from random import randint

from PyQt6 import QtWidgets, QtCore

import threads_ui


class QtApp(QtWidgets.QMainWindow, threads_ui.Ui_MainWindow):
    """
    Класс приложения
    """

    def __init__(self):
        """
        Конструктор класса приложения
        """
        super().__init__()
        # инициализация GUI
        self.setupUi(self)

        # установка обработки событий кнопок
        self.startButton.clicked.connect(self.start_process)
        self.stopButton.clicked.connect(self.stop_process)
        self.exitButton.clicked.connect(lambda x=0: sys.exit(x))

        # создание потоков и экземпляров класса вычислений
        self.threads = [QtCore.QThread(), QtCore.QThread()]
        self.obj = [Calc(), Calc()]

        # перемещение каждого экземпляра класса вычислений в отдельный поток
        for i in range(2):
            self.obj[i].moveToThread(self.threads[i])

        # определение обработки сигналов потоков
        for item in enumerate([self.obj[0].number1, self.obj[1].number2]):
            self.threads[item[0]].started.connect(item[1])
            self.obj[item[0]].newNumber.connect(self.setNumber)
            self.obj[item[0]].finished.connect(lambda x=item[0]: self.onFinish(x))

    def start_process(self):
        """
        Обработчик события запуска вычислений в потоках
        (обработка нажатия кнопки СТАРТ)
        :return: None
        """
        # установка флагов запуска потоков (для корректной остановки выполнения)
        for i in range(2):
            self.obj[i].isRun = True

        # выбор варианта запуска (последовательно/параллельно)
        if self.radioButton1.isChecked():
            self.threads[0].start()
        else:
            for th in self.threads:
                th.start()

    def stop_process(self):
        """
        Остановка процессов по нажатию кнопки
        :return: None
        """
        try:
            for i in range(2):
                self.obj[i].isRun = False
        except:
            pass

    @QtCore.pyqtSlot(int, int)
    def setNumber(self, labelN, number):
        """
        Слот обработки сигнала установки нового значения в метку
        :param labelN: номер метки
        :param number: устанавливаемое значение
        :return:
        """
        if labelN == 1:
            self.label1.setText(str(number))
        elif labelN == 2:
            self.label2.setText(str(number))

    @QtCore.pyqtSlot()
    def onFinish(self, x):
        """
        Слот обработки сигнала окончания работы потока
        :param x: Передаваемый номер потока
        :return: None
        """
        if x == 0:
            self.label1.setText('Поток {:d} завершен'.format(x + 1))
            if self.radioButton1.isChecked():
                self.threads[1].start()
        elif x == 1:
            self.label2.setText('Поток {:d} завершен'.format(x + 1))
        self.threads[x].quit()


class Calc(QtCore.QObject):
    """
    Объект, в экземплярах которого проводятся вычисления
    """

    # определение сигналов, которые генерируют методы класса
    finished = QtCore.pyqtSignal()
    newNumber = QtCore.pyqtSignal(int, int)
    isRun = False

    def number1(self):
        """
        Вычисления первого типа. В этом примере - установка значения метки 1
        :return: None
        """
        for _ in range(0, 10):
            # обработка флага остановки потока
            if not self.isRun:
                break
            # отправка сигнала с новым сгенерированным номером
            self.newNumber.emit(1, randint(1, 10))
            # пауза в 500 мс
            QtCore.QThread.msleep(500)
        # отправка сигнала завершения потока
        self.finished.emit()

    def number2(self):
        """
        Вычисления второго типа. В этом примере - установка значения метки 2
        :return: None
        """
        for _ in range(0, 10):
            if not self.isRun:
                break
            self.newNumber.emit(2, randint(1, 10))
            QtCore.QThread.msleep(500)
        self.finished.emit()


def main():
    app = QtWidgets.QApplication(sys.argv)  # новый экземпляр QApplication
    window = QtApp()  # новый экземпляр класса QtApp (приложения)
    window.show()  # запуск GUI
    app.exec()  # запуск приложения


if __name__ == '__main__':
    main()
