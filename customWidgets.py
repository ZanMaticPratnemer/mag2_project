from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPen, QPainter, QPixmap, QBrush, QPen, QPolygon
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

        self.points = []

        self.paintEvent = self.paintRect

        self.setMouseTracking(True)

        self.setRectMode()

        self.poly_complete = False

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

    def paintPoly(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.br_dot)
        painter.setPen(self.pen_dot)

        poly = QPolygon()
        for p in self.points:
            poly.append(p)
            if p is self.points[-1] and not self.poly_complete:
                continue
            painter.drawEllipse(p, 3, 3)

        
        painter.setPen(self.pen_sel)
        painter.setBrush(self.br_sel)
        if self.poly_complete:
            painter.drawPolygon(poly)
        else:
            painter.drawPolyline(poly)

    def setP1(self, p):
        self.p1_rect = p

    def setP2(self, p):
        self.p2_rect = p

    def setPoints(self, points):
        self.points = points

    def setRectMode(self):
        self.paintEvent = self.paintRect

    def setPolyMode(self):
        self.paintEvent = self.paintPoly
        
class CoordControl(QSpinBox):
    def __init__(self, *args, **kw):
        super(CoordControl, self).__init__(*args, **kw)
        self.setFocusPolicy(Qt.StrongFocus)
        self.addedKeyEvent = None
    
    def addKeyPressEvent(self, func):
        self.addedKeyEvent = func

    def keyPressEvent(self, event):
        super(CoordControl, self).keyPressEvent(event)
        self.addedKeyEvent(event)

    def mouseReleaseEvent(self, event):
        super(CoordControl, self).mouseReleaseEvent(event)
        self.addedKeyEvent(event)

class PointControl(QWidget):
    def __init__(self,keyEvent ,*args, **kw):
        super(PointControl, self).__init__(*args, **kw)

        self.setFocusPolicy(Qt.StrongFocus)

        self.p_disp_size = QSize(60, 60)
        self.setFixedSize(self.p_disp_size)

        self.x = CoordControl(self)
        self.x.setGeometry(0, 0, 60, 25)
        self.x.setRange(0, 1075)

        self.y = CoordControl(self)
        self.y.setGeometry(0, 35, 60, 25)
        self.y.setRange(0, 820)

        self.x.addKeyPressEvent(keyEvent)
        self.y.addKeyPressEvent(keyEvent)

    def setValue(self, p):
        self.x.setValue(p.x())
        self.y.setValue(p.y())

    def getPoint(self):
        return QPoint(self.x.value(), self.y.value())
