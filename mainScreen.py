from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPen, QPainter, QPixmap, QBrush, QPen
from PyQt5.QtWidgets import QLabel, QFrame, QBoxLayout, QSpinBox, QComboBox, QGroupBox
import sys
from customWidgets import *


class Ui_MainWindow(object):
    def __init__(self):
        self.move_x_p1 = False
        self.move_x_p2 = False
        self.move_y_p1 = False
        self.move_y_p2 = False

        # What we see as proximity when moving points/edges of selection
        self.prox = 3

        # Points used for drawing a polygon
        self.points = []

        # Keeps track of what items are in self.points_layout
        self.points_items = []

        self.mode_name = "rect"

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("Satelit")
        MainWindow.setGeometry(QtCore.QRect(50, 50, 1075, 870))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.p1 = QPoint(0, 0)
        self.p2 = QPoint(0, 0)


        self.map = Map()
        self.map.setEnabled(True)
        self.map.setGeometry(QtCore.QRect(0, 50, 1075, 820))
        self.map.setObjectName("label")

        self.map.mousePressEvent = self.mousePressEventRect
        self.map.mouseMoveEvent = self.mouseMoveEventRect
        self.map.mouseReleaseEvent = self.mouseMoveReleaseRect

        self.p1x = CoordControl('x')
        self.p1y = CoordControl('y')
        self.p1x.addKeyPressEvent(self.pointKeyPressEvent)
        self.p1y.addKeyPressEvent(self.pointKeyPressEvent)
        self.points_items.append(self.p1x)
        self.points_items.append(self.p1y)

        self.p2x = CoordControl('x')
        self.p2y = CoordControl('y')
        self.p2x.addKeyPressEvent(self.pointKeyPressEvent)
        self.p2y.addKeyPressEvent(self.pointKeyPressEvent)
        self.points_items.append(self.p2x)
        self.points_items.append(self.p2y)

        self.sel_mode = QComboBox()
        self.sel_mode.setFixedSize(QSize(60, 25))
        self.sel_mode.addItem("Rect")
        self.sel_mode.addItem("Poly")
        self.sel_mode.currentIndexChanged.connect(self.changeSelectionMode)

        MainWindow.setCentralWidget(self.centralwidget)


        ## TEST
        self.test = PointControl()
        self.test.addKeyPressEvent(self.pointKeyPressEvent)

        ################
        #### LAYOUTS ###
        ################

        self.screen_layout = QBoxLayout(QBoxLayout.TopToBottom, self.centralwidget)

        self.control_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.control_box = QGroupBox("Control")
        self.control_box.setMaximumHeight(150)
        self.control_box.setLayout(self.control_layout)

        self.screen_layout.addWidget(self.control_box)

        self.mode_sel_box = QGroupBox("Select selection mode")
        self.mode_sel_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.mode_sel_box.setLayout(self.mode_sel_layout)
        self.control_layout.addWidget(self.mode_sel_box)

        self.points_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.points_box = QGroupBox("Points")
        self.points_box.setLayout(self.points_layout)
        self.control_layout.addWidget(self.points_box)

        self.p1_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.p2_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.points_layout.addLayout(self.p1_layout)
        self.points_layout.addLayout(self.p2_layout)
        self.points_layout.addWidget(self.test)

        self.mode_sel_layout.addWidget(self.sel_mode)
        self.p1_layout.addWidget(self.p1x)
        self.p1_layout.addWidget(self.p1y)
        self.p2_layout.addWidget(self.p2x)
        self.p2_layout.addWidget(self.p2y)
        self.screen_layout.addWidget(self.map)

        
        


        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    ###############
    ### SIGNALS ###
    ###############

    def mousePressEventRect(self, event):

        move_p = False

        # Mouse press hapened near x axis of p1
        if abs(event.y()-self.p1.y()) < self.prox and ((event.x() > self.p1.x()-self.prox and event.x() < self.p2.x()+self.prox) or (event.x() > self.p2.x()-self.prox and event.x() < self.p1.x()+self.prox)):
            self.move_y_p1 = True
            self.p1.setY(event.y())
            move_p = True
        # Mouse press hapened near x axis of p2
        elif abs(event.y()-self.p2.y()) < self.prox and ((event.x() > self.p1.x()-self.prox and event.x() < self.p2.x()+self.prox) or (event.x() > self.p2.x()-self.prox and event.x() < self.p1.x()+self.prox)):
            self.move_y_p2 = True
            self.p2.setY(event.y())
            move_p = True
        # Mouse press hapened near y axis of p1
        if abs(event.x()-self.p1.x()) < self.prox and ((event.y() > self.p1.y()-self.prox and event.y() < self.p2.y()+self.prox) or (event.y() > self.p2.y()-self.prox and event.y() < self.p1.y()+self.prox)):
            self.move_x_p1 = True
            self.p1.setX(event.x())
            move_p = True
        # Mouse press hapened near y axis of p2
        elif abs(event.x()-self.p2.x()) < self.prox and ((event.y() > self.p1.y()-self.prox and event.y() < self.p2.y()+self.prox) or (event.y() > self.p2.y()-self.prox and event.y() < self.p1.y()+self.prox)):
            self.move_x_p2 = True
            self.p2.setX(event.x())
            move_p = True

    	# Start creating a new selection
        if not move_p:
            self.p1 = event.pos()
            self.p2 = event.pos()

        # Update maps points, map and point widgets
        self.map.setP1(self.p1)
        self.map.setP2(self.p2)
        self.map.update()

        self.p1x.setValue(self.p1.x())
        self.p1y.setValue(self.p1.y())
        self.p1x.adjustSize()
        self.p1y.adjustSize()

        self.p2x.setValue(self.p2.x())
        self.p2y.setValue(self.p2.y())
        self.p2x.adjustSize()
        self.p2y.adjustSize()


    def mouseMoveEventRect(self, event):

        move_p1_h = False
        move_p1_v = False
        move_p2_h = False
        move_p2_v = False

        # Mouse near x axis of p1
        if abs(event.y()-self.p1.y()) < self.prox and ((event.x() > self.p1.x()-self.prox and event.x() < self.p2.x()+self.prox) or (event.x() > self.p2.x()-self.prox and event.x() < self.p1.x()+self.prox)):
            move_p1_v = True
        # Mouse near x axis of p2
        elif abs(event.y()-self.p2.y()) < self.prox and ((event.x() > self.p1.x()-self.prox and event.x() < self.p2.x()+self.prox) or (event.x() > self.p2.x()-self.prox and event.x() < self.p1.x()+self.prox)):
            move_p2_v = True
        # Mouse near y axis of p1
        if abs(event.x()-self.p1.x()) < self.prox and ((event.y() > self.p1.y()-self.prox and event.y() < self.p2.y()+self.prox) or (event.y() > self.p2.y()-self.prox and event.y() < self.p1.y()+self.prox)):
            move_p1_h = True
        # Mouse near y axis of p2
        elif abs(event.x()-self.p2.x()) < self.prox and ((event.y() > self.p1.y()-self.prox and event.y() < self.p2.y()+self.prox) or (event.y() > self.p2.y()-self.prox and event.y() < self.p1.y()+self.prox)):
            move_p2_h = True

        if (move_p1_v and move_p1_h) or (move_p2_v and move_p2_h):
            if (self.p1.x() < self.p2.x() and self.p1.y() < self.p2.y()) or (self.p1.x() > self.p2.x() and self.p1.y() > self.p2.y()):
                self.map.setCursor(Qt.SizeFDiagCursor)
            else:
                self.map.setCursor(Qt.SizeBDiagCursor)
        elif (move_p1_v and move_p2_h) or (move_p2_v and move_p1_h):
            if (self.p1.x() < self.p2.x() and self.p1.y() < self.p2.y()) or (self.p1.x() > self.p2.x() and self.p1.y() > self.p2.y()):
                self.map.setCursor(Qt.SizeBDiagCursor)
            else:
                self.map.setCursor(Qt.SizeFDiagCursor)
        elif move_p1_h or move_p2_h:
            self.map.setCursor(Qt.SizeHorCursor)
        elif move_p1_v or move_p2_v:
            self.map.setCursor(Qt.SizeVerCursor)
        else:
            self.map.setCursor(Qt.ArrowCursor)

        if event.buttons() & Qt.LeftButton:
            move_p2 = True

            if self.move_x_p1:
                self.p1.setX(event.x())
                move_p2 = False
            elif self.move_x_p2:
                self.p2.setX(event.x())
                move_p2 = False
            if self.move_y_p1:
                self.p1.setY(event.y())
                move_p2 = False
            elif self.move_y_p2:
                self.p2.setY(event.y())
                move_p2 = False

            if move_p2:
                self.p2 = event.pos()

            self.map.setP1(self.p1)
            self.map.setP2(self.p2)
            self.map.update()

            self.p1x.setValue(self.p1.x())
            self.p1y.setValue(self.p1.y())
            self.p1x.adjustSize()
            self.p1y.adjustSize()

            self.p2x.setValue(self.p2.x())
            self.p2y.setValue(self.p2.y())
            self.p2x.adjustSize()
            self.p2y.adjustSize()

    def mouseMoveReleaseRect(self, event):
        self.move_x_p1 = False
        self.move_x_p2 = False
        self.move_y_p1 = False
        self.move_y_p2 = False

    def pointKeyPressEvent(self, event):
        self.p1.setX(self.p1x.value())
        self.p1.setY(self.p1y.value())
        self.p2.setX(self.p2x.value())
        self.p2.setY(self.p2y.value())

        self.map.setP1(self.p1)
        self.map.setP2(self.p2)
        self.map.update()

    def changeSelectionMode(self, index):
        if index == 0:
            for item in self.points_items:
                item.deleteLater()
            self.points_items = []

            self.p1x.show()
            self.p1y.show()
            self.points_items.append(self.p1x)
            self.points_items.append(self.p1y)
            self.p2x.show()
            self.p2y.show()
            self.points_items.append(self.p2x)
            self.points_items.append(self.p2y)

            self.mode_name = "rect"
        elif index == 1:
            for item in self.points_items:
                item.hide()
            self.points_items = []

            self.points.append(PointControl())

            for p in self.points:
                self.points_items.append(p)
                self.points_layout.addWidget(p)

            self.mode_name = "poly"




def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gui = Ui_MainWindow()
    gui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()

if __name__ == "__main__":
    main()