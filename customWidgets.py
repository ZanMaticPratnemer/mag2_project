from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPen, QPainter, QPixmap, QBrush, QPen, QPolygon
from PyQt5.QtWidgets import QLabel, QFrame, QBoxLayout, QDoubleSpinBox, QComboBox, QGroupBox, QWidget

from customFuncs import *

map_height = 676
map_width = 1487

class Map(QWidget):
    def __init__(self, *args, **kw):
        super(Map, self).__init__(*args, **kw)
        self.image = QPixmap("slovenia.png")
        self.setFixedSize(map_width, map_height)

        self.br_sel = QBrush(QtGui.QColor(10, 10, 150, 40))
        self.pen_sel = QPen(QtGui.QColor(10, 10, 100), 1)

        self.br_dot = QBrush(QtGui.QColor(0, 0, 0))
        self.pen_dot = QPen(QtGui.QColor(0, 0, 0))

        self.br_saved = QBrush(QtGui.QColor(10, 10, 150, 10))
        self.pen_saved = QPen(QtGui.QColor(10, 10, 100), 0)

        self.p1_rect = QPoint(-3, -3)
        self.p2_rect = QPoint(-3, -3)

        self.points = []

        self.setMouseTracking(True)

        self.setRectMode()

        self.poly_complete = False

        self.selections = []
        self.display_selections = False

        self.paintCurSel = self.paintRect

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

        if self.display_selections:
            self.paintSelections(painter)
        self.paintCurSel(painter)

    def paintSelections(self, painter):
        painter.setBrush(self.br_saved)
        painter.setPen(self.pen_saved)

        for sel in self.selections:
            poly = QPolygon()
            for p in sel:
                poly.append(p)
            painter.drawPolygon(poly)


    def paintRect(self, painter):

        # Draw selection area
        painter.setBrush(self.br_sel)
        painter.setPen(self.pen_sel)
        painter.drawRect(self.p1_rect.x(), self.p1_rect.y(), self.p2_rect.x()-self.p1_rect.x(), self.p2_rect.y()-self.p1_rect.y())

        # Draw configurable dots
        painter.setBrush(self.br_dot)
        painter.setPen(self.pen_dot)
        painter.drawEllipse(self.p1_rect, 3, 3)
        painter.drawEllipse(self.p2_rect, 3, 3)

    def paintPoly(self, painter):
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
        self.paintCurSel = self.paintRect

    def setPolyMode(self):
        self.paintCurSel = self.paintPoly

    def setSelections(self, sel):
        self.selections = sel

    def setDisplaySelections(self, b):
        self.display_selections = b
        
class CoordControl(QDoubleSpinBox):
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
        self.x.setRange(inToGeox(0), inToGeox(map_width))

        self.y = CoordControl(self)
        self.y.setGeometry(0, 35, 60, 25)
        self.y.setRange(inToGeoy(map_height), inToGeoy(0))

        self.x.addKeyPressEvent(keyEvent)
        self.y.addKeyPressEvent(keyEvent)



    def setValue(self, p):
        self.x.setValue(inToGeox(p.x()))
        self.y.setValue(inToGeoy(p.y()))

    def getPoint(self):
        return QPoint(geoToInx(self.x.value()), geoToIny(self.y.value()))
