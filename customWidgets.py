from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPen, QPainter, QPixmap, QBrush, QPen
from PyQt5.QtWidgets import QLabel, QFrame, QBoxLayout, QSpinBox, QComboBox, QGroupBox, QWidget

class Map(QWidget):
    def __init__(self, *args, **kw):
        super(Map, self).__init__(*args, **kw)
        self.image = QPixmap("si-04.jpg")

        self.br_sel = QBrush(QtGui.QColor(10, 10, 150, 40))
        self.pen_sel = QPen(QtGui.QColor(10, 10, 100), 1)

        self.br_dot = QBrush(QtGui.QColor(0, 0, 0))
        self.pen_dot = QPen(QtGui.QColor(0, 0, 0))

        self.p1_rect = QPoint(-3, -3)
        self.p2_rect = QPoint(-3, -3)

        self.paintEvent = self.paintRect

        self.setMouseTracking(True)

    def paintRect(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

        # Draw selection area
        painter.setBrush(self.br_sel)
        painter.setPen(self.pen_sel)
        painter.drawRect(self.p1_rect.x(), self.p1_rect.y(), self.p2_rect.x()-self.p1_rect.x(), self.p2_rect.y()-self.p1_rect.y())

        # Draw configurable dots
        painter.setBrush(self.br_dot)
        painter.setPen(self.pen_dot)
        painter.drawEllipse(self.p1_rect, 3, 3)
        painter.drawEllipse(self.p2_rect, 3, 3)

    def setP1(self, p):
        self.p1_rect = p

    def setP2(self, p):
        self.p2_rect = p

    def setRectMode(self):
        self.paintEvent = self.paintRect

    def setPolyMode(self):
        # self.paintEvent = self.paintPoly
        pass
        
class CoordControl(QSpinBox):
    def __init__(self, coord, *args, **kw):
        super(CoordControl, self).__init__(*args, **kw)
        self.p_disp_size = QSize(60, 25)
        self.setFixedSize(self.p_disp_size)
        self.setFocusPolicy(Qt.StrongFocus)
        self.addedKeyPressEvent = None
        if coord == 'x':
            self.setRange(0, 1075)
        elif coord == 'y':
            self.setRange(0, 820)
    
    def addKeyPressEvent(self, func):
        self.addedKeyEvent = func

    def keyPressEvent(self, event):
        super(CoordControl, self).keyPressEvent(event)
        self.addedKeyEvent(event)

    def mouseReleaseEvent(self, event):
        super(CoordControl, self).mouseReleaseEvent(event)
        self.addedKeyEvent(event)

class PointControl(QWidget):
    def __init__(self, *args, **kw):
        super(CoordControl1, self).__init__(*args, **kw)

        self.p_disp_size = QSize(60, 60)
        self.setFixedSize(self.p_disp_size)

        self.x = CoordControl('x', self)
        self.x.setGeometry(0, 0, 60, 25)
        self.x.setRange(0, 1075)
        self.x.setFocusPolicy(Qt.StrongFocus)

        self.y = CoordControl('y', self)
        self.y.setGeometry(0, 35, 60, 25)
        self.y.setRange(0, 820)
        self.y.setFocusPolicy(Qt.StrongFocus)
