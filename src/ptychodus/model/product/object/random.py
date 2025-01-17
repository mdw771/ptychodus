from __future__ import annotations
from collections.abc import Sequence

import numpy

from ptychodus.api.object import Object, ObjectGeometryProvider
from ptychodus.model.analysis.phaseUnwrapper import PhaseUnwrapper

from .builder import ObjectBuilder
from .settings import ObjectSettings


class RandomObjectBuilder(ObjectBuilder):
    def __init__(self, rng: numpy.random.Generator, settings: ObjectSettings) -> None:
        super().__init__(settings, 'random')
        self._rng = rng
        self._settings = settings

        self.extraPaddingX = settings.extraPaddingX.copy()
        self._addParameter('extra_padding_x', self.extraPaddingX)
        self.extraPaddingY = settings.extraPaddingY.copy()
        self._addParameter('extra_padding_y', self.extraPaddingY)

        self.amplitudeMean = settings.amplitudeMean.copy()
        self._addParameter('amplitude_mean', self.amplitudeMean)
        self.amplitudeDeviation = settings.amplitudeDeviation.copy()
        self._addParameter('amplitude_deviation', self.amplitudeDeviation)

        self.phaseDeviation = settings.phaseDeviation.copy()
        self._addParameter('phase_deviation', self.phaseDeviation)

    def copy(self) -> RandomObjectBuilder:
        builder = RandomObjectBuilder(self._rng, self._settings)

        for key, value in self.parameters().items():
            builder.parameters()[key].setValue(value.getValue())

        return builder

    def build(
        self,
        geometryProvider: ObjectGeometryProvider,
        layerDistanceInMeters: Sequence[float],
    ) -> Object:
        geometry = geometryProvider.getObjectGeometry()
        heightInPixels = geometry.heightInPixels + 2 * self.extraPaddingY.getValue()
        widthInPixels = geometry.widthInPixels + 2 * self.extraPaddingX.getValue()
        objectShape = (1 + len(layerDistanceInMeters), heightInPixels, widthInPixels)

        amplitude = self._rng.normal(
            self.amplitudeMean.getValue(),
            self.amplitudeDeviation.getValue(),
            objectShape,
        )
        phase = self._rng.normal(
            0.0,
            self.phaseDeviation.getValue(),
            objectShape,
        )

        return Object(
            array=numpy.clip(amplitude, 0.0, 1.0) * numpy.exp(1j * phase),
            layerDistanceInMeters=layerDistanceInMeters,
            pixelGeometry=geometry.getPixelGeometry(),
            center=geometry.getCenter(),
        )


class UserObjectBuilder(ObjectBuilder):
    def __init__(self, object: Object, settings: ObjectSettings) -> None:
        """Create an object from an existing object with a potentially
        different number of slices. 
        
        If the new object is supposed to be a multislice object with a
        different number of slices than the existing object, the object is
        created as 
        `abs(o) ** (1 / nSlices) * exp(i * unwrapPhase(o) / nSlices)`.
        Otherwise, the object is copied as is. 

        Parameters
        ----------
        object : Object
            The existing object.
        settings : ObjectSettings
            The settings for the new object.
        """
        super().__init__(settings, 'user')
        self._existingObject = object
        
    def copy(self) -> UserObjectBuilder:
        builder = UserObjectBuilder(self._existingObject, self._settings)

        for key, value in self.parameters().items():
            builder.parameters()[key].setValue(value.getValue())

        return builder
    
    def build(
        self,
        layerDistanceInMeters: Sequence[float]
    ) -> Object:
        geometry = self._existingObject.getGeometry()
        
        exitingObjectArr = self._existingObject.getArray()
        nSlices = len(layerDistanceInMeters) + 1
        if nSlices > 1 and nSlices != exitingObjectArr.shape[0]:
            amplitude = numpy.abs(exitingObjectArr[0:1]) ** (1.0 / nSlices)
            amplitude = amplitude.repeat(nSlices, axis=0)
            phase = PhaseUnwrapper().unwrap(exitingObjectArr[0])[None, ...] / nSlices
            phase = phase.repeat(nSlices, axis=0)
            data = numpy.clip(amplitude, 0.0, 1.0) * numpy.exp(1j * phase)
        else:
            data = exitingObjectArr
        return Object(
            array=data,
            layerDistanceInMeters=layerDistanceInMeters,
            pixelGeometry=geometry.getPixelGeometry(),
            center=geometry.getCenter(),
        )
