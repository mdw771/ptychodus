from pathlib import Path
from typing import Final, Sequence

import numpy
import scipy.io

from ptychodus.api.geometry import PixelGeometry
from ptychodus.api.object import Object
from ptychodus.api.plugins import PluginRegistry
from ptychodus.api.probe import Probe
from ptychodus.api.product import (
    ELECTRON_VOLT_J,
    LIGHT_SPEED_M_PER_S,
    PLANCK_CONSTANT_J_PER_HZ,
    Product,
    ProductFileReader,
    ProductMetadata,
)
from ptychodus.api.scan import Scan, ScanPoint


class PtychoShelvesProductFileReader(ProductFileReader):
    SIMPLE_NAME: Final[str] = 'PtychoShelves'
    DISPLAY_NAME: Final[str] = 'PtychoShelves Files (*.mat)'

    def read(self, filePath: Path) -> Product:
        scanPointList: list[ScanPoint] = list()

        hc_eVm = PLANCK_CONSTANT_J_PER_HZ * LIGHT_SPEED_M_PER_S / ELECTRON_VOLT_J
        matDict = scipy.io.loadmat(filePath, simplify_cells=True)
        p_struct = matDict['p']
        probe_energy_eV = hc_eVm / p_struct['lambda']

        metadata = ProductMetadata(
            name=filePath.stem,
            comments='',
            detectorDistanceInMeters=0.0,  # not included in file
            probeEnergyInElectronVolts=probe_energy_eV,
            probePhotonCount=0.0,  # not included in file
            exposureTimeInSeconds=0.0,  # not included in file
        )

        dx_spec = p_struct['dx_spec']
        pixel_width_m = dx_spec[0]
        pixel_height_m = dx_spec[1]
        pixel_geometry = PixelGeometry(widthInMeters=pixel_width_m, heightInMeters=pixel_height_m)

        outputs_struct = matDict['outputs']
        probe_positions = outputs_struct['probe_positions']

        for idx, pos_px in enumerate(probe_positions):
            point = ScanPoint(
                idx,
                pos_px[0] * pixel_width_m,
                pos_px[1] * pixel_height_m,
            )
            scanPointList.append(point)

        probe_array = matDict['probe']

        if probe_array.ndim == 3:
            # probe_array[height, width, num_shared_modes]
            probe_array = probe_array.transpose(2, 0, 1)
        elif probe_array.ndim == 4:
            # probe_array[height, width, num_shared_modes, num_varying_modes]
            probe_array = probe_array.transpose(3, 2, 0, 1)

        probe = Probe(array=probe_array, pixelGeometry=pixel_geometry)

        object_array = matDict['object']

        if object_array.ndim == 3:
            # object_array[height, width, num_layers]
            object_array = object_array.transpose(2, 0, 1)

        layer_distance_m: Sequence[float] = list()

        try:
            multi_slice_param = p_struct['multi_slice_param']
            z_distance = multi_slice_param['z_distance']
        except KeyError:
            pass
        else:
            num_spaces = object_array.shape[-3] - 1
            layer_distance_m = numpy.squeeze(z_distance)[:num_spaces]

        object_ = Object(
            array=object_array,
            pixelGeometry=pixel_geometry,
            center=None,
            layerDistanceInMeters=layer_distance_m,
        )
        costs = outputs_struct['fourier_error_out']

        return Product(
            metadata=metadata,
            scan=Scan(scanPointList),
            probe=probe,
            object_=object_,
            costs=costs,
        )


def registerPlugins(registry: PluginRegistry) -> None:
    registry.productFileReaders.registerPlugin(
        PtychoShelvesProductFileReader(),
        simpleName=PtychoShelvesProductFileReader.SIMPLE_NAME,
        displayName=PtychoShelvesProductFileReader.DISPLAY_NAME,
    )
