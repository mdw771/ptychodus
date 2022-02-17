from __future__ import annotations
from decimal import Decimal

from ..model import Observer, Observable
from ..view import TikeParametersView
from .reconstructor import ReconstructorViewControllerFactory


class TikeAdaptiveMomentController(Observer):
    def __init__(self, presenter: TikeAdaptiveMomentPresenter, view: TikeAdaptiveMomentView) -> None:
        super().__init__()
        self._presenter = presenter
        self._view = view

    @classmethod
    def createInstance(cls, presenter: TikeAdaptiveMomentPresenter, view: TikeAdaptiveMomentView) -> TikeAdaptiveMomentController:
        controller = cls(presenter, view)
        presenter.addObserver(controller)

        view.toggled.connect(presenter.setAdaptiveMomentEnabled)

        view.mdecaySpinBox.valueChanged.connect(presenter.setMDecay)
        view.mdecaySpinBox.setDecimals(3)
        view.mdecaySpinBox.setSingleStep(1.e-3)

        view.vdecaySpinBox.valueChanged.connect(presenter.setVDecay)
        view.vdecaySpinBox.setDecimals(3)
        view.vdecaySpinBox.setSingleStep(1.e-3)

        controller._syncModelToView()

        return controller

    def _syncModelToView(self) -> None:
        self._view.setChecked(self._presenter.isAdaptiveMomentEnabled())

        self._view.mdecaySpinBox.blockSignals(True)
        self._view.mdecaySpinBox.setRange(self._presenter.getMinMDecay(),
                self._presenter.getMaxMDecay())
        self._view.mdecaySpinBox.setValue(self._presenter.getMDecay())
        self._view.mdecaySpinBox.blockSignals(False)

        self._view.vdecaySpinBox.blockSignals(True)
        self._view.vdecaySpinBox.setRange(self._presenter.getMinVDecay(),
                self._presenter.getMaxVDecay())
        self._view.vdecaySpinBox.setValue(self._presenter.getVDecay())
        self._view.vdecaySpinBox.blockSignals(False)

    def update(self, observable: Observable) -> None:
        if observable is self._presenter:
            self._syncModelToView()


class TikeProbeCorrectionController(Observer):
    def __init__(self, presenter: TikeProbeCorrectionPresenter, view: TikeProbeCorrectionView) -> None:
        super().__init__()
        self._presenter = presenter
        self._view = view
        self._adaptiveMomentController = TikeAdaptiveMomentController.createInstance(presenter, view.adaptiveMomentView)

    @classmethod
    def createInstance(cls, presenter: TikeProbeCorrectionPresenter, view: TikeProbeCorrectionView) -> TikeProbeCorrectionController:
        controller = cls(presenter, view)
        presenter.addObserver(controller)

        view.sparsityConstraintSpinBox.valueChanged.connect(
                presenter.setSparsityConstraint)
        view.sparsityConstraintSpinBox.setDecimals(3)
        view.sparsityConstraintSpinBox.setSingleStep(1.e-3)

        view.orthogonalityConstraintCheckBox.toggled.connect(
                presenter.setOrthogonalityConstraintEnabled)
        view.centeredIntensityConstraintCheckBox.toggled.connect(
                presenter.setCenteredIntensityConstraintEnabled)

        controller._syncModelToView()

        return controller

    def _syncModelToView(self) -> None:
        self._view.sparsityConstraintSpinBox.blockSignals(True)
        self._view.sparsityConstraintSpinBox.setRange(self._presenter.getMinSparsityConstraint(),
                self._presenter.getMaxSparsityConstraint())
        self._view.sparsityConstraintSpinBox.setValue(self._presenter.getSparsityConstraint())
        self._view.sparsityConstraintSpinBox.blockSignals(False)

        self._view.orthogonalityConstraintCheckBox.setChecked(
                self._presenter.isOrthogonalityConstraintEnabled())
        self._view.centeredIntensityConstraintCheckBox.setChecked(
                self._presenter.isCenteredIntensityConstraintEnabled())

    def update(self, observable: Observable) -> None:
        if observable is self._presenter:
            self._syncModelToView()


class TikeObjectCorrectionController(Observer):
    def __init__(self, presenter: TikeObjectCorrectionPresenter, view: TikeObjectCorrectionView) -> None:
        super().__init__()
        self._presenter = presenter
        self._view = view
        self._adaptiveMomentController = TikeAdaptiveMomentController.createInstance(presenter, view.adaptiveMomentView)

    @classmethod
    def createInstance(cls, presenter: TikeObjectCorrectionPresenter, view: TikeObjectCorrectionView) -> TikeObjectCorrectionController:
        controller = cls(presenter, view)
        presenter.addObserver(controller)

        view.positivityConstraintSpinBox.valueChanged.connect(
                presenter.setPositivityConstraint)
        view.positivityConstraintSpinBox.setDecimals(3)
        view.positivityConstraintSpinBox.setSingleStep(1.e-3)

        view.smoothnessConstraintSpinBox.valueChanged.connect(
                presenter.setSmoothnessConstraint)
        view.smoothnessConstraintSpinBox.setDecimals(3)
        view.smoothnessConstraintSpinBox.setSingleStep(1.e-3)

        controller._syncModelToView()

        return controller

    def _syncModelToView(self) -> None:
        self._view.positivityConstraintSpinBox.blockSignals(True)
        self._view.positivityConstraintSpinBox.setRange(self._presenter.getMinPositivityConstraint(),
                self._presenter.getMaxPositivityConstraint())
        self._view.positivityConstraintSpinBox.setValue(self._presenter.getPositivityConstraint())
        self._view.positivityConstraintSpinBox.blockSignals(False)

        self._view.smoothnessConstraintSpinBox.blockSignals(True)
        self._view.smoothnessConstraintSpinBox.setRange(self._presenter.getMinSmoothnessConstraint(),
                self._presenter.getMaxSmoothnessConstraint())
        self._view.smoothnessConstraintSpinBox.setValue(self._presenter.getSmoothnessConstraint())
        self._view.smoothnessConstraintSpinBox.blockSignals(False)

    def update(self, observable: Observable) -> None:
        if observable is self._presenter:
            self._syncModelToView()


class TikePositionCorrectionController(Observer):
    def __init__(self, presenter: TikePositionCorrectionPresenter, view: TikePositionCorrectionView) -> None:
        super().__init__()
        self._presenter = presenter
        self._view = view
        self._adaptiveMomentController = TikeAdaptiveMomentController.createInstance(presenter, view.adaptiveMomentView)

    @classmethod
    def createInstance(cls, presenter: TikePositionCorrectionPresenter, view: TikePositionCorrectionView) -> TikePositionCorrectionController:
        controller = cls(presenter, view)
        presenter.addObserver(controller)

        view.positionRegularizationCheckBox.toggled.connect(
                presenter.setPositionRegularizationEnabled)

        controller._syncModelToView()

        return controller

    def _syncModelToView(self) -> None:
        self._view.positionRegularizationCheckBox.setChecked(
                self._presenter.isPositionRegularizationEnabled())

    def update(self, observable: Observable) -> None:
        if observable is self._presenter:
            self._syncModelToView()


class TikeIterationController(Observer):
    def __init__(self, presenter: TikeIterationPresenter, view: TikeIterationView) -> None:
        super().__init__()
        self._presenter = presenter
        self._view = view

    @classmethod
    def createInstance(cls, presenter: TikeIterationPresenter, view: TikeIterationView) -> TikeIterationController:
        controller = cls(presenter, view)
        presenter.addObserver(controller)

        view.numBatchSpinBox.valueChanged.connect(presenter.setNumBatch)
        view.numIterSpinBox.valueChanged.connect(presenter.setNumIter)
        view.cgIterSpinBox.valueChanged.connect(presenter.setCgIter)

        view.alphaSpinBox.valueChanged.connect(presenter.setAlpha)
        view.alphaSpinBox.setDecimals(3)
        view.alphaSpinBox.setSingleStep(1.e-3)

        view.stepLengthSpinBox.valueChanged.connect(presenter.setStepLength)
        view.stepLengthSpinBox.setDecimals(3)
        view.stepLengthSpinBox.setSingleStep(1.e-3)

        controller._syncModelToView()

        return controller

    def _syncModelToView(self) -> None:
        self._view.numBatchSpinBox.blockSignals(True)
        self._view.numBatchSpinBox.setRange(self._presenter.getMinNumBatch(),
                self._presenter.getMaxNumBatch())
        self._view.numBatchSpinBox.setValue(self._presenter.getNumBatch())
        self._view.numBatchSpinBox.blockSignals(False)

        self._view.numIterSpinBox.blockSignals(True)
        self._view.numIterSpinBox.setRange(self._presenter.getMinNumIter(),
                self._presenter.getMaxNumIter())
        self._view.numIterSpinBox.setValue(self._presenter.getNumIter())
        self._view.numIterSpinBox.blockSignals(False)

        self._view.cgIterSpinBox.blockSignals(True)
        self._view.cgIterSpinBox.setRange(self._presenter.getMinCgIter(),
                self._presenter.getMaxCgIter())
        self._view.cgIterSpinBox.setValue(self._presenter.getCgIter())
        self._view.cgIterSpinBox.blockSignals(False)

        self._view.alphaSpinBox.blockSignals(True)
        self._view.alphaSpinBox.setRange(self._presenter.getMinAlpha(),
                self._presenter.getMaxAlpha())
        self._view.alphaSpinBox.setValue(self._presenter.getAlpha())
        self._view.alphaSpinBox.blockSignals(False)

        self._view.stepLengthSpinBox.blockSignals(True)
        self._view.stepLengthSpinBox.setRange(self._presenter.getMinStepLength(),
                self._presenter.getMaxStepLength())
        self._view.stepLengthSpinBox.setValue(self._presenter.getStepLength())
        self._view.stepLengthSpinBox.blockSignals(False)

    def update(self, observable: Observable) -> None:
        if observable is self._presenter:
            self._syncModelToView()


class TikeParametersController:
    def __init__(self, model: TikeBackend, view: TikeParametersView) -> None:
        self._model = model
        self._view = view
        self._positionCorrectionController = TikePositionCorrectionController.createInstance(
                model.positionCorrectionPresenter, view.positionCorrectionView)
        self._probeCorrectionController = TikeProbeCorrectionController.createInstance(
                model.probeCorrectionPresenter, view.probeCorrectionView)
        self._objectCorrectionController = TikeObjectCorrectionController.createInstance(
                model.objectCorrectionPresenter, view.objectCorrectionView)
        self._iterationOptionsController = TikeIterationController.createInstance(
                model.iterationPresenter, view.iterationOptionsView)

    @classmethod
    def createInstance(cls, model: TikeBackend, view: TikeParametersView) -> TikeParametersController:
        controller = cls(model, view)
        return controller


class TikeViewControllerFactory(ReconstructorViewControllerFactory):
    def __init__(self, model: TikeBackend) -> None:
        self._model = model
        self._controllerList: list[TikeParametersController] = list()

    @property
    def backendName(self):
        return 'Tike'

    def createViewController(self, reconstructorName: str) -> QWidget:
        view = TikeParametersView.createInstance()
        controller = TikeParametersController.createInstance(self._model, view)

        if reconstructorName == 'rpie':
            view.iterationOptionsView.cgIterSpinBox.setVisible(False)
            view.iterationOptionsView.stepLengthSpinBox.setVisible(False)
        elif reconstructorName == 'adam_grad':
            view.iterationOptionsView.cgIterSpinBox.setVisible(False)
        elif reconstructorName == 'cgrad':
            view.iterationOptionsView.alphaSpinBox.setVisible(False)
        elif reconstructorName == 'lstsq_grad':
            view.iterationOptionsView.cgIterSpinBox.setVisible(False)
            view.iterationOptionsView.alphaSpinBox.setVisible(False)
            view.iterationOptionsView.stepLengthSpinBox.setVisible(False)

        self._controllerList.append(controller)

        return view
