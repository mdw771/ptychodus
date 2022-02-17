from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QWheelEvent
from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, \
        QGraphicsPixmapItem, QGraphicsScene, QGraphicsSceneHoverEvent, \
        QGraphicsSceneMouseEvent, QGraphicsView, QGridLayout, QGroupBox, QHBoxLayout, \
        QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from .widgets import BottomTitledGroupBox


class ImageRibbon(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.imageFileGroupBox = BottomTitledGroupBox('Image')
        self.saveButton = QPushButton('Save')

        self.scalarTransformGroupBox = BottomTitledGroupBox('Scalar Transform')
        self.scalarTransformComboBox = QComboBox()
        self.complexComponentComboBox = QComboBox()

        self.normalizationGroupBox = BottomTitledGroupBox('Normalization')
        self.vminLabel = QLabel('Min:')
        self.vminLineEdit = QLineEdit()
        self.vminAutoCheckBox = QCheckBox('Auto')
        self.vmaxLabel = QLabel('Max:')
        self.vmaxLineEdit = QLineEdit()
        self.vmaxAutoCheckBox = QCheckBox('Auto')

        self.colorMapGroupBox = BottomTitledGroupBox('Color Map')
        self.colorMapComboBox = QComboBox()

        self.frameGroupBox = BottomTitledGroupBox('Frame')
        self.imageSpinBox = QSpinBox()

    @classmethod
    def createInstance(cls, parent: QWidget = None):
        view = cls(parent)

        imageFileLayout = QVBoxLayout()
        imageFileLayout.setContentsMargins(10, 10, 10, 50)
        imageFileLayout.addWidget(view.saveButton)
        view.imageFileGroupBox.setLayout(imageFileLayout)

        scalarTransformLayout = QVBoxLayout()
        scalarTransformLayout.setContentsMargins(10, 10, 10, 50)
        scalarTransformLayout.addWidget(view.scalarTransformComboBox)
        scalarTransformLayout.addWidget(view.complexComponentComboBox)
        view.scalarTransformGroupBox.setLayout(scalarTransformLayout)

        normalizationLayout = QGridLayout()
        normalizationLayout.setContentsMargins(10, 10, 10, 50)
        normalizationLayout.addWidget(view.vminLabel, 0, 1)
        normalizationLayout.addWidget(view.vminLineEdit, 0, 2)
        normalizationLayout.addWidget(view.vminAutoCheckBox, 0, 3)
        normalizationLayout.addWidget(view.vmaxLabel, 1, 1)
        normalizationLayout.addWidget(view.vmaxLineEdit, 1, 2)
        normalizationLayout.addWidget(view.vmaxAutoCheckBox, 1, 3)
        view.normalizationGroupBox.setLayout(normalizationLayout)

        colorMapLayout = QVBoxLayout()
        colorMapLayout.setContentsMargins(10, 10, 10, 50)
        colorMapLayout.addWidget(view.colorMapComboBox)
        view.colorMapGroupBox.setLayout(colorMapLayout)

        frameLayout = QVBoxLayout()
        frameLayout.setContentsMargins(10, 10, 10, 50)
        frameLayout.addWidget(view.imageSpinBox)
        view.frameGroupBox.setLayout(frameLayout)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view.imageFileGroupBox)
        layout.addWidget(view.scalarTransformGroupBox)
        layout.addWidget(view.normalizationGroupBox)
        layout.addWidget(view.colorMapGroupBox)
        layout.addWidget(view.frameGroupBox)
        layout.addStretch(1)
        view.setLayout(layout)

        return view


class ImageItem(QGraphicsPixmapItem):
    def __init__(self) -> None:
        super().__init__()
        self.setTransformationMode(Qt.FastTransformation)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        QApplication.instance().setOverrideCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        QApplication.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setPos(self.scenePos() + event.scenePos() - event.lastScenePos())

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        pass


class ImageWidget(QGraphicsView):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._pixmapItem = ImageItem()

    @classmethod
    def createInstance(cls, parent: QWidget = None):
        widget = cls(parent)

        scene = QGraphicsScene()
        scene.addItem(widget._pixmapItem)
        widget.setScene(scene)

        return widget

    def setPixmap(self, pixmap: QPixmap) -> None:
        self._pixmapItem.setPixmap(pixmap)

    def getPixmap(self) -> QPixmap:
        return self._pixmapItem.pixmap()

    def wheelEvent(self, event: QWheelEvent) -> None:
        oldPosition = self.mapToScene(event.pos())

        zoomBase = 1.25
        zoom = zoomBase if event.angleDelta().y() > 0 else 1. / zoomBase
        self.scale(zoom, zoom)

        newPosition = self.mapToScene(event.pos())

        deltaPosition = newPosition - oldPosition
        self.translate(deltaPosition.x(), deltaPosition.y())


class ImageView(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.imageRibbon = ImageRibbon.createInstance()
        self.imageWidget = ImageWidget.createInstance()

    @classmethod
    def createInstance(cls, parent: QWidget = None):
        view = cls(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMenuBar(view.imageRibbon)
        layout.addWidget(view.imageWidget)
        view.setLayout(layout)

        return view
