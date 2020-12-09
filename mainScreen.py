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

        self.p1c = PointControl()
        self.p1c.addKeyPressEvent(self.pointKeyPressEvent)
        self.p2c = PointControl()
        self.p2c.addKeyPressEvent(self.pointKeyPressEvent)

        self.sel_mode = QComboBox()
        self.sel_mode.setFixedSize(QSize(60, 25))
        self.sel_mode.addItem("Rect")
        self.sel_mode.addItem("Poly")
        self.sel_mode.currentIndexChanged.connect(self.changeSelectionMode)

        MainWindow.setCentralWidget(self.centralwidget)


     

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

        self.mode_sel_layout.addWidget(self.sel_mode)
        self.points_layout.addWidget(self.p1c)
        self.points_items.append(self.p1c)
        self.points_layout.addWidget(self.p2c)
        self.points_items.append(self.p2c)
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

        self.p1c.x.setValue(self.p1.x())
        self.p1c.y.setValue(self.p1.y())

        self.p2c.x.setValue(self.p2.x())
        self.p2c.y.setValue(self.p2.y())


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

            self.p1c.x.setValue(self.p1.x())
            self.p1c.y.setValue(self.p1.y())

            self.p2c.x.setValue(self.p2.x())
            self.p2c.y.setValue(self.p2.y())

    def mouseMoveReleaseRect(self, event):
        self.move_x_p1 = False
        self.move_x_p2 = False
        self.move_y_p1 = False
        self.move_y_p2 = False

    def mousePressEventPoly(self, event):
        if len(self.points) > 3:
            for i in range(len(self.points)):


        self.points.append(event.pos())


    def mouseMoveEventPoly(self, event):
        pass

    def mouseReleaseEventPoly(self, event):
        pass

    def pointKeyPressEvent(self, event):
        self.p1.setX(self.p1c.x.value())
        self.p1.setY(self.p1c.y.value())
        self.p2.setX(self.p2c.x.value())
        self.p2.setY(self.p2c.y.value())

        self.map.setP1(self.p1)
        self.map.setP2(self.p2)
        self.map.update()

    def changeSelectionMode(self, index):
        if index == 0:
            for item in self.points_items:
                item.deleteLater()
            self.points_items = []
            self.points = []

            self.p1c.show()
            self.points_items.append(self.p1c)
            self.p2c.show()
            self.points_items.append(self.p2c)

            self.map.mousePressEvent = self.mousePressEventRect
            self.map.mouseMoveEvent = self.mouseMoveEventRect
            self.map.mouseReleaseEvent = self.mouseMoveReleaseRect

            self.mode_name = "rect"
        elif index == 1:
            for item in self.points_items:
                item.hide()
            self.points_items = []

            for p in self.points:
                self.points_items.append(p)
                self.points_layout.addWidget(p)

            self.map.mousePressEvent = self.mousePressEventPoly
            self.map.mouseMoveEvent = self.mouseMoveEventPoly
            self.map.mouseReleaseEvent = self.mouseReleaseEventPoly

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
    