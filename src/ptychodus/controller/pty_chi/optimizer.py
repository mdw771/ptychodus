from PyQt5.QtWidgets import QHBoxLayout, QSpinBox, QWidget

from ptychodus.api.observer import Observable, Observer
from ptychodus.api.parametric import IntegerParameter, StringParameter

from ...model.pty_chi import PtyChiEnumerators
from ..parametric import (
    ComboBoxParameterViewController,
    SpinBoxParameterViewController,
    ParameterViewController,
)


class StopSpinBoxParameterViewController(ParameterViewController, Observer):
    def __init__(
        self, stop: IntegerParameter, num_epochs: IntegerParameter, *, tool_tip: str = ''
    ) -> None:
        super().__init__()
        self._stop = stop
        self._num_epochs = num_epochs
        self._widget = QSpinBox()

        if tool_tip:
            self._widget.setToolTip(tool_tip)

        self._syncModelToView()
        self._widget.valueChanged.connect(self._syncViewToModel)
        stop.addObserver(self)
        num_epochs.addObserver(self)

    def getWidget(self) -> QWidget:
        return self._widget

    def _syncViewToModel(self, value: int) -> None:
        num_epochs = self._num_epochs.getValue()
        self._stop.setValue(value if value < num_epochs else -1)

    def _syncModelToView(self) -> None:
        num_epochs = self._num_epochs.getValue()
        stop = self._stop.getValue()

        self._widget.blockSignals(True)
        self._widget.setRange(0, num_epochs)
        self._widget.setValue(num_epochs if stop < 0 else stop)
        self._widget.blockSignals(False)

    def update(self, observable: Observable) -> None:
        if observable in (self._stop, self._num_epochs):
            self._syncModelToView()


class PtyChiOptimizationPlanViewController(ParameterViewController):
    def __init__(
        self,
        start: IntegerParameter,
        stop: IntegerParameter,
        stride: IntegerParameter,
        num_epochs: IntegerParameter,
    ) -> None:
        super().__init__()
        self._startViewController = SpinBoxParameterViewController(
            start, tool_tip='Iteration to start optimizing'
        )
        self._stopViewController = StopSpinBoxParameterViewController(
            stop, num_epochs, tool_tip='Iteration to stop optimizing'
        )
        self._strideViewController = SpinBoxParameterViewController(
            stride, tool_tip='Number of iterations between updates'
        )
        self._widget = QWidget()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._startViewController.getWidget())
        layout.addWidget(self._stopViewController.getWidget())
        layout.addWidget(self._strideViewController.getWidget())
        self._widget.setLayout(layout)

    def getWidget(self) -> QWidget:
        return self._widget


class PtyChiOptimizerParameterViewController(ComboBoxParameterViewController):
    def __init__(self, parameter: StringParameter, enumerators: PtyChiEnumerators) -> None:
        super().__init__(parameter, enumerators.optimizers())
