from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPen, QPainter, QPixmap, QBrush, QPen
from PyQt5.QtWidgets import QLabel, QFrame, QBoxLayout, QSpinBox, QComboBox, QGroupBox, QPushButton, QSizePolicy, QCheckBox
import sys
from customWidgets import *
from customFuncs import *


class Ui_MainWindow(object):
    def __init__(self):
        self.move_x_p1 = False
        self.move_x_p2 = False
        self.move_y_p1 = False
        self.move_y_p2 = False

        # What we see as proximity when moving points/edges of selection
        self.prox = 5

        # Points used for drawing a polygon
        self.points = []
        # Index of the poly point being moved
        self.p_move_i = None

        # Keeps track of what items are in self.points_layout
        self.points_items = []

        self.mode_name = "rect"

        self.saved_selections = []

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

        self.p1c = PointControl(self.keyPressEventRect)
        self.p2c = PointControl(self.keyPressEventRect)

        self.sel_mode = QComboBox()
        self.sel_mode.setFixedSize(QSize(60, 25))
        self.sel_mode.addItem("Rect")
        self.sel_mode.addItem("Poly")
        self.sel_mode.currentIndexChanged.connect(self.changeSelectionMode)

        self.poly_reset = QPushButton("Clear")
        self.poly_reset.clicked.connect(self.clearPoly)
        self.poly_reset.hide()
        self.poly_reset.setMaximumWidth(60)

        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Minimum)

        self.save_selection = QPushButton("Save current")
        self.save_selection.setMaximumSize(self.save_selection.sizeHint())
        self.save_selection.setSizePolicy(sp)
        self.save_selection.clicked.connect(self.saveSelection)

        self.clear_selections = QPushButton("Clear all")
        self.clear_selections.setMaximumSize(self.clear_selections.sizeHint())
        self.clear_selections.setSizePolicy(sp)
        self.clear_selections.clicked.connect(self.clearSelections)

        self.display_selections = QCheckBox("Display selections")
        self.display_selections.setMaximumSize(self.display_selections.sizeHint())
        self.display_selections.setSizePolicy(sp)
        self.display_selections.stateChanged.connect(self.displaySelection)


        MainWindow.setCentralWidget(self.centralwidget)


     

        ###############
        ### LAYOUTS ###
        ###############

        self.screen_layout = QBoxLayout(QBoxLayout.TopToBottom, self.centralwidget)

        self.control_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.control_box = QGroupBox("Control")
        self.control_box.setMaximumHeight(200)
        self.control_box.setLayout(self.control_layout)

        self.screen_layout.addWidget(self.control_box)

        self.selections_box = QGroupBox("Selection management")
        self.selections_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.selections_box.setLayout(self.selections_layout)
        self.control_layout.addWidget(self.selections_box)

        self.mode_sel_box = QGroupBox("Select selection mode")
        self.mode_sel_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.mode_sel_box.setLayout(self.mode_sel_layout)
        self.control_layout.addWidget(self.mode_sel_box)

        self.points_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.points_box = QGroupBox("Points")
        self.points_box.setLayout(self.points_layout)
        self.control_layout.addWidget(self.points_box)


        self.mode_sel_layout.addWidget(self.sel_mode)
        self.mode_sel_layout.addWidget(self.poly_reset)
        self.points_layout.addWidget(self.p1c)
        self.points_layout.addWidget(self.p2c)
        self.screen_layout.addWidget(self.map)
        self.selections_layout.addWidget(self.save_selection)
        self.selections_layout.addWidget(self.clear_selections)
        self.selections_layout.addWidget(self.display_selections)

        
        


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

        self.p1c.setValue(self.p1)

        self.p2c.setValue(self.p2)


    def mouseMoveEventRect(self, event):

        move_p1_h = False
        move_p1_v = False
        move_p2_h = False
        move_p2_v = False

        # Mouse near x axis of p1
        if abs(event.y()-self.p1.y()) <= self.prox and ((event.x() > self.p1.x()-self.prox and event.x() < self.p2.x()+self.prox) or (event.x() > self.p2.x()-self.prox and event.x() < self.p1.x()+self.prox)):
            move_p1_v = True
        # Mouse near x axis of p2
        elif abs(event.y()-self.p2.y()) <= self.prox and ((event.x() > self.p1.x()-self.prox and event.x() < self.p2.x()+self.prox) or (event.x() > self.p2.x()-self.prox and event.x() < self.p1.x()+self.prox)):
            move_p2_v = True
        # Mouse near y axis of p1
        if abs(event.x()-self.p1.x()) <= self.prox and ((event.y() > self.p1.y()-self.prox and event.y() < self.p2.y()+self.prox) or (event.y() > self.p2.y()-self.prox and event.y() < self.p1.y()+self.prox)):
            move_p1_h = True
        # Mouse near y axis of p2
        elif abs(event.x()-self.p2.x()) <= self.prox and ((event.y() > self.p1.y()-self.prox and event.y() < self.p2.y()+self.prox) or (event.y() > self.p2.y()-self.prox and event.y() < self.p1.y()+self.prox)):
            move_p2_h = True

        if (move_p1_v and move_p2_h) or (move_p2_v and move_p1_h) or (move_p1_v and move_p1_h) or (move_p2_v and move_p2_h):
            self.map.setCursor(Qt.SizeAllCursor)
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

            self.p1c.setValue(self.p1)

            self.p2c.setValue(self.p2)

    def mouseMoveReleaseRect(self, event):
        self.move_x_p1 = False
        self.move_x_p2 = False
        self.move_y_p1 = False
        self.move_y_p2 = False

    def mousePressEventPoly(self, event):
        if not self.map.poly_complete:
            new_p = event.pos()
            if len(self.points) > 3:
                # First check if polygon is complete
                if euclDist(self.points[0], new_p) <= self.prox:
                    self.map.poly_complete = True
                    self.map.setPoints(self.points)
                    self.map.update()
                    return
                # Else for intersections of the new line segment
                else:
                    for i in range(len(self.points) - 2):
                        if intersect(self.points[i], self.points[i+1], self.points[-1], new_p):
                            # TODO: (optional) create a popup error message
                            return

            # If no intersections were found, add the new point
            self.points.append(new_p)
            self.map.setPoints(self.points)

            self.map.update()

            new_widget = PointControl(self.keyPressEventPoly)
            new_widget.setValue(new_p)
            self.points_items.append(new_widget)
            self.points_layout.addWidget(new_widget)
        else:
            c_pos = event.pos()
            for i, p in enumerate(self.points):
                if euclDist(c_pos, p) <= self.prox:
                    self.p_move_i = i


    def mouseMoveEventPoly(self, event):
        pos = event.pos()

        if self.map.poly_complete:
            norm_cursor = True
            for p in self.points:
                if euclDist(pos, p) <= self.prox:
                    self.map.setCursor(Qt.SizeAllCursor)
                    norm_cursor = False
            if norm_cursor:
                self.map.setCursor(Qt.ArrowCursor)
        else:
            self.map.setPoints(self.points + [pos])
            self.map.update()

        if self.p_move_i != None:
            self.points[self.p_move_i] = pos
            self.points_items[self.p_move_i].setValue(pos)
            self.map.setPoints(self.points)
            self.map.update()

    def mouseReleaseEventPoly(self, event):
        self.p_move_i = None

    def clearPoly(self):
        self.points = []
        for item in self.points_items:
            item.deleteLater()
        self.points_items = []
        self.points = []
        self.map.points = []
        self.map.poly_complete = False

    def keyPressEventRect(self, event):
        self.p1.setX(self.p1c.x.value())
        self.p1.setY(self.p1c.y.value())
        self.p2.setX(self.p2c.x.value())
        self.p2.setY(self.p2c.y.value())

        self.map.setP1(self.p1)
        self.map.setP2(self.p2)
        self.map.update()

    def keyPressEventPoly(self, event):
        for i, pc in enumerate(self.points_items):
            self.points[i] = pc.getPoint()
        self.map.setPoints(self.points)
        self.map.update()

    def changeSelectionMode(self, index):
        if index == 0:
            for item in self.points_items:
                item.hide()
            self.poly_reset.hide()

            self.p1c.show()
            self.p2c.show()

            self.map.mousePressEvent = self.mousePressEventRect
            self.map.mouseMoveEvent = self.mouseMoveEventRect
            self.map.mouseReleaseEvent = self.mouseMoveReleaseRect

            self.mode_name = "rect"
            self.map.setRectMode()
        elif index == 1:
            self.p1c.hide()
            self.p2c.hide()
            for item in self.points_items:
                item.show()
            self.poly_reset.show()

            self.map.mousePressEvent = self.mousePressEventPoly
            self.map.mouseMoveEvent = self.mouseMoveEventPoly
            self.map.mouseReleaseEvent = self.mouseReleaseEventPoly

            self.mode_name = "poly"
            self.map.setPolyMode()

        self.map.update()

    def saveSelection(self):
        if self.mode_name == "rect":
            self.saved_selections.append([self.mode_name] + [self.p1] + [self.p2])
        else:
            self.saved_selections.append([self.mode_name] + self.points)

        self.map.update()

    def clearSelections(self):
        self.saved_selections = []
        self.map.update()

    def displaySelection(self, s):
        if s == 0:
            self.map.setDisplaySelections(False)
        else:
            self.map.setSelections(self.saved_selections)
            self.map.setDisplaySelections(True)
        self.map.update()




def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gui = Ui_MainWindow()
    gui.setupUi(MainWindow)
    MainWindow.show()
    app.exec_()

if __name__ == "__main__":
    main()
