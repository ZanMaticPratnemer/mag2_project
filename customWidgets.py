from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint, QSize, QPointF
from PyQt5.QtGui import QPen, QPainter, QPixmap, QBrush, QPen, QPolygon, QPolygonF, QFont
from PyQt5.QtWidgets import QLabel, QFrame, QBoxLayout, QDoubleSpinBox, QComboBox, QGroupBox, QWidget

import copy

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

        self.br_covered = QBrush(QtGui.QColor(150, 10, 10, 7))
        self.pen_covered = QPen(QtGui.QColor(10, 10, 100), 0)
        self.pen_covered.setStyle(Qt.DashLine)

        self.p1_rect = QPoint(-3, -3)
        self.p2_rect = QPoint(-3, -3)

        self.points = []

        self.setMouseTracking(True)

        self.setRectMode()

        self.poly_complete = False

        self.selections = []
        self.display_selections = False

        self.paintCurSel = self.paintRect

        self.display_flights = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

        if self.display_selections:
            self.paintSelections(painter)
        self.paintCurSel(painter)

        if self.display_flights:
            self.displayFlights(painter)

        painter.end()

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

    def showFlights(self, flights):
        self.flights = copy.deepcopy(flights)
        self.display_flights = True
        self.update()

    def displayFlights(self, painter):
        painter.setBrush(self.br_covered)
        painter.setPen(self.pen_covered)

        for f in self.flights:
            gamma = f[2]
            pos = f[0]
            th = self.th

            # Get the needed parameters
            c, w = angleToWidth(gamma, self.alpha/2, self.h)
            p = np.array([[geoToInx(pos)], [geoToIny(a_lat)]], dtype=float)

            # Get points that lie on picture edges
            A = p + np.array([[np.cos(np.radians(th))*c], [np.sin(np.radians(th))*c]], dtype=float)
            B = p + np.array([[np.cos(np.radians(th))*(c+w)], [np.sin(np.radians(th))*(c+w)]], dtype=float)

            # Define a line that represents picture edges
            k = -np.tan(np.pi/2-np.radians(np.abs(th)))
            nA = A[1][0] - (k*A[0][0])
            nB = B[1][0] - (k*B[0][0])

            # Get end points of the whole picture that the satelite takes
            p11 = QPointF((0 - nA)/k, 0)
            p21 = QPointF((map_height - nA)/k, map_height)
            p12 = QPointF((0 - nB)/k, 0)
            p22 = QPointF((map_height - nB)/k, map_height)

            poly = QPolygonF()
            poly << p11 << p12 << p22 << p21 << p11

            painter.drawPolygon(poly)





        
class CoordControl(QDoubleSpinBox):
    def __init__(self, *args, **kw):
        super(CoordControl, self).__init__(*args, **kw)
        self.setFocusPolicy(Qt.StrongFocus)
        self.addedKeyEvent = None
        self.setSingleStep(0.01)
    
    def addKeyPressEvent(self, func):
        self.addedKeyEvent = func

    def keyPressEvent(self, event):
        super(CoordControl, self).keyPressEvent(event)
        self.addedKeyEvent(event)

    def mouseReleaseEvent(self, event):
        super(CoordControl, self).mouseReleaseEvent(event)
        self.addedKeyEvent(event)

class PointControl(QWidget):
    def __init__(self, keyEvent, *args, **kw):
        super(PointControl, self).__init__(*args, **kw)

        self.setFocusPolicy(Qt.StrongFocus)

        self.p_disp_size = QSize(60, 60)
        self.setFixedSize(self.p_disp_size)

        self.x = CoordControl(self)
        self.x.setGeometry(0, 35, 60, 25)
        self.x.setRange(inToGeox(0), inToGeox(map_width))

        self.y = CoordControl(self)
        self.y.setGeometry(0, 0, 60, 25)
        self.y.setRange(inToGeoy(map_height), inToGeoy(0))

        self.x.addKeyPressEvent(keyEvent)
        self.y.addKeyPressEvent(keyEvent)



    def setValue(self, p):
        self.x.setValue(inToGeox(p.x()))
        self.y.setValue(inToGeoy(p.y()))

    def getPoint(self):
        return QPoint(geoToInx(self.x.value()), geoToIny(self.y.value()))

class ParameterInput(QWidget):
    def __init__(self, param, *args, **kw):
        super(ParameterInput, self).__init__(*args, **kw)

        self.setFocusPolicy(Qt.StrongFocus)

        self.param_name = QLabel(param + ":", self)
        self.param_name.setGeometry(0,0,15,25)
        self.param_name.setFont(QFont('Arial', 11))

        self.param_val = QDoubleSpinBox(self)
        self.param_val.setGeometry(16, 0, 70, 25)

        if param == "f":
            min_val = 1
            max_val = 25
            dec_n = 1
            suffix = "/day"
        elif param == "θ":
            min_val = -15
            max_val = 15
            dec_n = 1
            suffix = "°"
        elif param == "h":
            min_val = 10
            max_val = 1000
            dec_n = 1
            suffix = " km"
        elif param == "α":
            min_val = 0.01
            max_val = 5
            dec_n = 2
            suffix = "°"
        elif param == "γ":
            min_val = 0
            max_val = 30
            dec_n = 1
            suffix = "°"
        
        self.param_val.setRange(min_val, max_val)
        self.param_val.setDecimals(dec_n)
        self.param_val.setSingleStep(np.power(10.,-dec_n))
        self.param_val.setSuffix(suffix)

    def minimumSizeHint(self):
        return QSize(86, 25)

    def value(self):
        return self.param_val.value()
    
    def setValue(self, value):
        self.param_val.setValue(value)
