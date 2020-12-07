from PyQt5 import QtWidgets
import sys
import mainScreen

def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gui = mainScreen.Ui_MainWindow()
    gui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()

if __name__ == "__main__":
    main()