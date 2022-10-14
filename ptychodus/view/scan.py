from __future__ import annotations
from typing import Generic, Optional, TypeVar

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import (QAbstractButton, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QGroupBox, QHeaderView, QHBoxLayout, QMenu, QPushButton, QSpinBox,
                             QTableView, QVBoxLayout, QWidget)

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib

from .widgets import AngleWidget, LengthWidget

__all__ = [
    'CartesianScanView',
    'LissajousScanView',
    'ScanButtonBox',
    'ScanEditorDialog',
    'ScanParametersView',
    'ScanPlotView',
    'ScanPositionDataView',
    'ScanTransformView',
    'SpiralScanView',
]

T = TypeVar('T', bound=QGroupBox)


class CartesianScanView(QGroupBox):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__('Parameters', parent)
        self.numberOfPointsXSpinBox = QSpinBox()
        self.numberOfPointsYSpinBox = QSpinBox()
        self.stepSizeXWidget = LengthWidget.createInstance()
        self.stepSizeYWidget = LengthWidget.createInstance()

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> CartesianScanView:
        view = cls(parent)

        MAX_INT = 0x7FFFFFFF
        view.numberOfPointsXSpinBox.setRange(0, MAX_INT)
        view.numberOfPointsYSpinBox.setRange(0, MAX_INT)

        layout = QFormLayout()
        layout.addRow('Number Of Points X:', view.numberOfPointsXSpinBox)
        layout.addRow('Number Of Points Y:', view.numberOfPointsYSpinBox)
        layout.addRow('Step Size X:', view.stepSizeXWidget)
        layout.addRow('Step Size Y:', view.stepSizeYWidget)
        view.setLayout(layout)

        return view


class SpiralScanView(QGroupBox):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__('Parameters', parent)
        self.numberOfPointsSpinBox = QSpinBox()
        self.radiusScalarWidget = LengthWidget.createInstance()
        self.angularStepWidget = AngleWidget.createInstance()

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> SpiralScanView:
        view = cls(parent)

        MAX_INT = 0x7FFFFFFF
        view.numberOfPointsSpinBox.setRange(0, MAX_INT)

        layout = QFormLayout()
        layout.addRow('Number Of Points:', view.numberOfPointsSpinBox)
        layout.addRow('Radius Scalar:', view.radiusScalarWidget)
        layout.addRow('Angular Step:', view.angularStepWidget)
        view.setLayout(layout)

        return view


class LissajousScanView(QGroupBox):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__('Parameters', parent)
        self.numberOfPointsSpinBox = QSpinBox()
        self.amplitudeXWidget = LengthWidget.createInstance()
        self.amplitudeYWidget = LengthWidget.createInstance()
        self.angularStepXWidget = AngleWidget.createInstance()
        self.angularStepYWidget = AngleWidget.createInstance()
        self.angularShiftWidget = AngleWidget.createInstance()

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> LissajousScanView:
        view = cls(parent)

        MAX_INT = 0x7FFFFFFF
        view.numberOfPointsSpinBox.setRange(0, MAX_INT)

        layout = QFormLayout()
        layout.addRow('Number Of Points:', view.numberOfPointsSpinBox)
        layout.addRow('Amplitude X:', view.amplitudeXWidget)
        layout.addRow('Amplitude Y:', view.amplitudeYWidget)
        layout.addRow('Angular Step X:', view.angularStepXWidget)
        layout.addRow('Angular Step Y:', view.angularStepYWidget)
        layout.addRow('Angular Shift:', view.angularShiftWidget)
        view.setLayout(layout)

        return view


class ScanTransformView(QGroupBox):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__('Transform', parent)
        self.transformComboBox = QComboBox()
        self.jitterRadiusWidget = LengthWidget.createInstance()
        self.centroidXWidget = LengthWidget.createInstance()
        self.centroidYWidget = LengthWidget.createInstance()

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> ScanTransformView:
        view = cls(parent)

        layout = QFormLayout()
        layout.addRow('(x,y) \u2192', view.transformComboBox)
        layout.addRow('Jitter Radius:', view.jitterRadiusWidget)
        layout.addRow('Centroid X:', view.centroidXWidget)
        layout.addRow('Centroid Y:', view.centroidYWidget)
        view.setLayout(layout)

        return view


class ScanEditorDialog(Generic[T], QDialog):

    def __init__(self, editorView: T, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.editorView = editorView
        self.transformView = ScanTransformView.createInstance()
        self.centerWidget = QWidget()
        self.buttonBox = QDialogButtonBox()

    @classmethod
    def createInstance(cls,
                       editorView: T,
                       parent: Optional[QWidget] = None) -> ScanEditorDialog[T]:
        view = cls(editorView, parent)

        centerLayout = QVBoxLayout()
        centerLayout.addWidget(editorView)
        centerLayout.addWidget(view.transformView)
        view.centerWidget.setLayout(centerLayout)

        view.buttonBox.addButton(QDialogButtonBox.Ok)
        view.buttonBox.clicked.connect(view._handleButtonBoxClicked)

        layout = QVBoxLayout()
        layout.addWidget(view.centerWidget)
        layout.addWidget(view.buttonBox)
        view.setLayout(layout)

        return view

    def _handleButtonBoxClicked(self, button: QAbstractButton) -> None:
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.AcceptRole:
            self.accept()
        else:
            self.reject()


class ScanButtonBox(QWidget):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.insertMenu = QMenu()
        self.insertButton = QPushButton('Insert')
        self.saveButton = QPushButton('Save')
        self.editButton = QPushButton('Edit')
        self.removeButton = QPushButton('Remove')

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> ScanButtonBox:
        view = cls(parent)

        view.insertButton.setMenu(view.insertMenu)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view.insertButton)
        layout.addWidget(view.saveButton)
        layout.addWidget(view.editButton)
        layout.addWidget(view.removeButton)
        view.setLayout(layout)

        return view


class ScanPositionDataView(QGroupBox):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__('Position Data', parent)
        self.tableView = QTableView()
        self.buttonBox = ScanButtonBox.createInstance()

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> ScanPositionDataView:
        view = cls(parent)

        view.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(view.tableView)
        layout.addWidget(view.buttonBox)
        view.setLayout(layout)

        return view


class ScanParametersView(QWidget):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.positionDataView = ScanPositionDataView.createInstance()

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> ScanParametersView:
        view = cls(parent)

        layout = QVBoxLayout()
        layout.addWidget(view.positionDataView)
        view.setLayout(layout)

        return view


class ScanPlotView(QWidget):

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.figure = Figure()
        self.figureCanvas = FigureCanvas(self.figure)
        self.navigationToolbar = NavigationToolbar(self.figureCanvas, self)
        self.axes = self.figure.add_subplot(111)

    @classmethod
    def createInstance(cls, parent: Optional[QWidget] = None) -> ScanPlotView:
        view = cls(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view.navigationToolbar)
        layout.addWidget(view.figureCanvas)
        view.setLayout(layout)

        return view
