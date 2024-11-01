from PyQt5.QtWidgets import QFormLayout, QGroupBox, QWidget

from ptychodus.api.observer import Observable, Observer

from ...model.pty_chi import PtyChiObjectSettings
from ..parametric import DecimalLineEditParameterViewController, ParameterViewController
from .optimizer import PtyChiOptimizationPlanViewController, PtyChiOptimizerParameterViewController


class PtyChiObjectViewController(ParameterViewController, Observer):
    def __init__(self, settings: PtyChiObjectSettings) -> None:
        super().__init__()
        self._isOptimizable = settings.isOptimizable
        self._optimizationPlanViewController = PtyChiOptimizationPlanViewController(
            settings.optimizationPlanStart,
            settings.optimizationPlanStop,
            settings.optimizationPlanStride,
        )
        self._optimizerViewController = PtyChiOptimizerParameterViewController(settings.optimizer)
        self._stepSizeViewController = DecimalLineEditParameterViewController(
            settings.stepSize, tool_tip='Optimizer step size'
        )
        self._widget = QGroupBox('Optimize Object')
        self._widget.setCheckable(True)

        layout = QFormLayout()
        layout.addRow('Plan:', self._optimizationPlanViewController.getWidget())
        layout.addRow('Optimizer:', self._optimizerViewController.getWidget())
        layout.addRow('Step Size:', self._stepSizeViewController.getWidget())
        self._widget.setLayout(layout)

        self._syncModelToView()
        self._widget.toggled.connect(self._isOptimizable.setValue)
        self._isOptimizable.addObserver(self)

    def getWidget(self) -> QWidget:
        return self._widget

    def _syncModelToView(self) -> None:
        self._widget.setChecked(self._isOptimizable.getValue())

    def update(self, observable: Observable) -> None:
        if observable is self._isOptimizable:
            self._syncModelToView()


# FIXME l1_norm_constraint_weight
# FIXME l1_norm_constraint_stride
# FIXME smoothness_constraint_alpha
# FIXME smoothness_constraint_stride
# FIXME total_variation_weight
# FIXME total_variation_stride