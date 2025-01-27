from __future__ import annotations
from collections.abc import Sequence
from pathlib import Path
from typing import Any
import logging

import numpy

from ptychodus.api.geometry import PixelGeometry
from ptychodus.api.observer import Observable
from ptychodus.api.probe import Probe
from ptychodus.api.propagator import (
    AngularSpectrumPropagator,
    PropagatorParameters,
    WavefieldArrayType,
    intensity,
)
from ptychodus.api.typing import RealArrayType

from ..product import ProductRepository
from .settings import ProbePropagationSettings

logger = logging.getLogger(__name__)


class ProbePropagator(Observable):
    def __init__(self, settings: ProbePropagationSettings, repository: ProductRepository) -> None:
        super().__init__()
        self._settings = settings
        self._repository = repository

        self._productIndex = -1
        self._propagatedWavefield: WavefieldArrayType | None = None
        self._propagatedIntensity: RealArrayType | None = None

    def setProduct(self, productIndex: int) -> None:
        if self._productIndex != productIndex:
            self._productIndex = productIndex
            self._propagatedWavefield = None
            self._propagatedIntensity = None
            self.notifyObservers()

    def getProductName(self) -> str:
        item = self._repository[self._productIndex]
        return item.getName()

    def propagate(
        self,
        *,
        beginCoordinateInMeters: float,
        endCoordinateInMeters: float,
        numberOfSteps: int,
    ) -> None:  # FIXME OPR
        item = self._repository[self._productIndex]
        probe = item.getProbe().getProbe()
        wavelengthInMeters = item.getGeometry().probeWavelengthInMeters
        propagatedWavefield = numpy.zeros(
            (numberOfSteps, probe.heightInPixels, probe.widthInPixels),
            dtype=probe.dataType,
        )
        propagatedIntensity = numpy.zeros(
            (numberOfSteps, probe.heightInPixels, probe.widthInPixels)
        )
        distanceInMeters = numpy.linspace(
            beginCoordinateInMeters, endCoordinateInMeters, numberOfSteps
        )
        pixelGeometry = probe.getPixelGeometry()

        if pixelGeometry is None:
            raise ValueError('No pixel geometry!')

        for idx, zInMeters in enumerate(distanceInMeters):
            propagatorParameters = PropagatorParameters(
                wavelength_m=wavelengthInMeters,
                width_px=probe.widthInPixels,
                height_px=probe.heightInPixels,
                pixel_width_m=pixelGeometry.widthInMeters,
                pixel_height_m=pixelGeometry.heightInMeters,
                propagation_distance_m=float(zInMeters),
            )
            propagator = AngularSpectrumPropagator(propagatorParameters)

            for mode in range(probe.numberOfIncoherentModes):
                wf = propagator.propagate(probe.getIncoherentMode(mode))
                propagatedWavefield[idx, mode, :, :] = wf
                propagatedIntensity[idx, :, :] += intensity(wf)

        self._settings.beginCoordinateInMeters.setValue(beginCoordinateInMeters)
        self._settings.endCoordinateInMeters.setValue(endCoordinateInMeters)
        self._propagatedWavefield = propagatedWavefield
        self._propagatedIntensity = propagatedIntensity
        self.notifyObservers()

    def getBeginCoordinateInMeters(self) -> float:
        return self._settings.beginCoordinateInMeters.getValue()

    def getEndCoordinateInMeters(self) -> float:
        return self._settings.endCoordinateInMeters.getValue()

    def _getProbe(self) -> Probe:
        item = self._repository[self._productIndex]
        return item.getProbe().getProbe()

    def getPixelGeometry(self) -> PixelGeometry | None:
        try:
            probe = self._getProbe()
        except IndexError:
            return None
        else:
            return probe.getPixelGeometry()

    def getNumberOfSteps(self) -> int:
        if self._propagatedIntensity is None:
            return self._settings.numberOfSteps.getValue()

        return self._propagatedIntensity.shape[0]

    def getXYProjection(self, step: int) -> RealArrayType:
        if self._propagatedIntensity is None:
            raise ValueError('No propagated wavefield!')

        return self._propagatedIntensity[step]

    def getZXProjection(self) -> RealArrayType:
        if self._propagatedIntensity is None:
            raise ValueError('No propagated wavefield!')

        sz = self._propagatedIntensity.shape[-2]
        cutPlaneL = self._propagatedIntensity[:, (sz - 1) // 2, :]
        cutPlaneR = self._propagatedIntensity[:, sz // 2, :]
        return numpy.transpose(numpy.add(cutPlaneL, cutPlaneR) / 2)

    def getZYProjection(self) -> RealArrayType:
        if self._propagatedIntensity is None:
            raise ValueError('No propagated wavefield!')

        sz = self._propagatedIntensity.shape[-1]
        cutPlaneL = self._propagatedIntensity[:, :, (sz - 1) // 2]
        cutPlaneR = self._propagatedIntensity[:, :, sz // 2]
        return numpy.transpose(numpy.add(cutPlaneL, cutPlaneR) / 2)

    def getSaveFileFilterList(self) -> Sequence[str]:
        return [self.getSaveFileFilter()]

    def getSaveFileFilter(self) -> str:
        return 'NumPy Zipped Archive (*.npz)'

    def savePropagatedProbe(self, filePath: Path) -> None:
        if self._propagatedWavefield is None or self._propagatedIntensity is None:
            raise ValueError('No propagated wavefield!')

        contents: dict[str, Any] = {
            'begin_coordinate_m': self.getBeginCoordinateInMeters(),
            'end_coordinate_m': self.getEndCoordinateInMeters(),
            'wavefield': self._propagatedWavefield,
            'intensity': self._propagatedIntensity,
        }

        pixel_geometry = self.getPixelGeometry()

        if pixel_geometry is not None:
            contents['pixel_height_m'] = pixel_geometry.heightInMeters
            contents['pixel_width_m'] = pixel_geometry.widthInMeters

        numpy.savez(filePath, **contents)
