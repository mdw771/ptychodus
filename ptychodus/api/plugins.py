from __future__ import annotations
from dataclasses import dataclass
from types import ModuleType
from typing import Generic, Iterator, TypeVar
import importlib
import logging
import pkgutil

from .data import DataFileReader
from .image import ComplexToRealStrategy, ScalarTransformation
from .object import ObjectFileReader, ObjectFileWriter
from .observer import Observable
from .probe import ProbeFileReader, ProbeFileWriter
from .scan import ScanFileReader, ScanFileWriter

T = TypeVar('T', DataFileReader, ComplexToRealStrategy, ScalarTransformation, ScanFileReader,
            ScanFileWriter, ProbeFileReader, ProbeFileWriter, ObjectFileReader, ObjectFileWriter)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PluginEntry(Generic[T]):
    simpleName: str
    displayName: str
    strategy: T


class PluginChooser(Generic[T], Observable):
    def __init__(self, defaultEntry: PluginEntry[T]) -> None:
        super().__init__()
        self._entryList: list[PluginEntry[T]] = [defaultEntry]
        self._entry: PluginEntry[T] = defaultEntry

    @classmethod
    def createFromList(cls, entryList: list[PluginEntry[T]]) -> PluginChooser:
        chooser = cls(entryList[0])
        chooser._entryList = entryList.copy()
        return chooser

    def addStrategy(self, entry: PluginEntry[T]) -> None:
        self._entryList.insert(0, entry)

    def setToDefault(self) -> None:
        self._setEntry(self._entryList[-1])

    def getSimpleNameList(self) -> list[str]:
        return [entry.simpleName for entry in self._entryList]

    def setFromSimpleName(self, name: str) -> None:
        try:
            entry = next(entry for entry in self._entryList
                         if name.casefold() == entry.simpleName.casefold())
        except StopIteration:
            logger.debug(f'Invalid strategy simple name \"{name}\"')
            return

        self._setEntry(entry)

    def getDisplayNameList(self) -> list[str]:
        return [entry.displayName for entry in self._entryList]

    def setFromDisplayName(self, name: str) -> None:
        try:
            entry = next(entry for entry in self._entryList if name == entry.displayName)
        except StopIteration:
            logger.debug(f'Invalid strategy display name \"{name}\"')
            return

        self._setEntry(entry)

    def getCurrentSimpleName(self) -> str:
        return self._entry.simpleName

    def getCurrentDisplayName(self) -> str:
        return self._entry.displayName

    def getCurrentStrategy(self) -> T:
        return self._entry.strategy

    def _setEntry(self, entry: PluginEntry[T]) -> None:
        if self._entry is not entry:
            self._entry = entry
            self.notifyObservers()

    def __iter__(self) -> Iterator[PluginEntry[T]]:
        return iter(self._entryList)

    def __getitem__(self, index: int) -> PluginEntry[T]:
        return self._entryList[index]

    def __len__(self) -> int:
        return len(self._entryList)


class PluginRegistry:
    def __init__(self) -> None:
        self.dataFileReaders: list[PluginEntry[DataFileReader]] = list()
        self.complexToRealStrategies: list[PluginEntry[ComplexToRealStrategy]] = list()
        self.scalarTransformations: list[PluginEntry[ScalarTransformation]] = list()
        self.scanFileReaders: list[PluginEntry[ScanFileReader]] = list()
        self.scanFileWriters: list[PluginEntry[ScanFileWriter]] = list()
        self.probeFileReaders: list[PluginEntry[ProbeFileReader]] = list()
        self.probeFileWriters: list[PluginEntry[ProbeFileWriter]] = list()
        self.objectFileReaders: list[PluginEntry[ObjectFileReader]] = list()
        self.objectFileWriters: list[PluginEntry[ObjectFileWriter]] = list()

    @classmethod
    def loadPlugins(cls) -> PluginRegistry:
        registry = cls()

        import ptychodus.plugins
        ns_pkg: ModuleType = ptychodus.plugins

        # Specifying the second argument (prefix) to iter_modules makes the
        # returned name an absolute name instead of a relative one. This allows
        # import_module to work without having to do additional modification to
        # the name.
        for moduleInfo in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + '.'):
            logger.info(f'Importing {moduleInfo.name}')
            module = importlib.import_module(moduleInfo.name)
            module.registerPlugins(registry)

        return registry

    def registerPlugin(self, plugin: T) -> None:
        if isinstance(plugin, DataFileReader):
            entry = PluginEntry[DataFileReader](simpleName=plugin.simpleName,
                                                displayName=plugin.fileFilter,
                                                strategy=plugin)
            self.dataFileReaders.append(entry)
        elif isinstance(plugin, ComplexToRealStrategy):
            entry = PluginEntry[ComplexToRealStrategy](simpleName=plugin.name,
                                                       displayName=plugin.name,
                                                       strategy=plugin)
            self.complexToRealStrategies.append(entry)
        elif isinstance(plugin, ScalarTransformation):
            entry = PluginEntry[ScalarTransformation](simpleName=plugin.name,
                                                      displayName=plugin.name,
                                                      strategy=plugin)
            self.scalarTransformations.append(entry)
        elif isinstance(plugin, ScanFileReader):
            entry = PluginEntry[ScanFileReader](simpleName=plugin.simpleName,
                                                displayName=plugin.fileFilter,
                                                strategy=plugin)
            self.scanFileReaders.append(entry)
        elif isinstance(plugin, ScanFileWriter):
            entry = PluginEntry[ScanFileWriter](simpleName=plugin.simpleName,
                                                displayName=plugin.fileFilter,
                                                strategy=plugin)
            self.scanFileWriters.append(entry)
        elif isinstance(plugin, ProbeFileReader):
            entry = PluginEntry[ProbeFileReader](simpleName=plugin.simpleName,
                                                 displayName=plugin.fileFilter,
                                                 strategy=plugin)
            self.probeFileReaders.append(entry)
        elif isinstance(plugin, ProbeFileWriter):
            entry = PluginEntry[ProbeFileWriter](simpleName=plugin.simpleName,
                                                 displayName=plugin.fileFilter,
                                                 strategy=plugin)
            self.probeFileWriters.append(entry)
        elif isinstance(plugin, ObjectFileReader):
            entry = PluginEntry[ObjectFileReader](simpleName=plugin.simpleName,
                                                  displayName=plugin.fileFilter,
                                                  strategy=plugin)
            self.objectFileReaders.append(entry)
        elif isinstance(plugin, ObjectFileWriter):
            entry = PluginEntry[ObjectFileWriter](simpleName=plugin.simpleName,
                                                  displayName=plugin.fileFilter,
                                                  strategy=plugin)
            self.objectFileWriters.append(entry)
        else:
            raise TypeError(f'Invalid plugin type \"{type(plugin).__name__}\".')

    def buildDataFileReaderChooser(self) -> PluginChooser[DataFileReader]:
        return PluginChooser[DataFileReader].createFromList(self.dataFileReaders)

    def buildComplexToRealStrategyChooser(self) -> PluginChooser[ComplexToRealStrategy]:
        return PluginChooser[ComplexToRealStrategy].createFromList(self.complexToRealStrategies)

    def buildScalarTransformationChooser(self) -> PluginChooser[ScalarTransformation]:
        return PluginChooser[ScalarTransformation].createFromList(self.scalarTransformations)

    def buildScanFileReaderChooser(self) -> PluginChooser[ScanFileReader]:
        return PluginChooser[ScanFileReader].createFromList(self.scanFileReaders)

    def buildScanFileWriterChooser(self) -> PluginChooser[ScanFileWriter]:
        return PluginChooser[ScanFileWriter].createFromList(self.scanFileWriters)

    def buildProbeFileReaderChooser(self) -> PluginChooser[ProbeFileReader]:
        return PluginChooser[ProbeFileReader].createFromList(self.probeFileReaders)

    def buildProbeFileWriterChooser(self) -> PluginChooser[ProbeFileWriter]:
        return PluginChooser[ProbeFileWriter].createFromList(self.probeFileWriters)

    def buildObjectFileReaderChooser(self) -> PluginChooser[ObjectFileReader]:
        return PluginChooser[ObjectFileReader].createFromList(self.objectFileReaders)

    def buildObjectFileWriterChooser(self) -> PluginChooser[ObjectFileWriter]:
        return PluginChooser[ObjectFileWriter].createFromList(self.objectFileWriters)