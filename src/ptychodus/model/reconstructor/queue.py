from __future__ import annotations
from abc import ABC, abstractmethod
import logging
import queue
import threading
import time

from ptychodus.api.reconstructor import Reconstructor, ReconstructInput, ReconstructOutput

from ..product import ProductRepositoryItem

logger = logging.getLogger(__name__)

__all__ = ['ReconstructionQueue']


class ReconstructionTask(ABC):
    @abstractmethod
    def execute(self) -> ReconstructionTask | None:
        pass


class UpdateProductTask(ReconstructionTask):
    def __init__(self, result: ReconstructOutput, product: ProductRepositoryItem) -> None:
        self._result = result
        self._product = product

    def execute(self) -> None:
        name = self._product.getName()
        self._product.assign(self._result.product)
        self._product.setName(name)


class ExecuteReconstructorTask(ReconstructionTask):
    def __init__(
        self,
        reconstructor: Reconstructor,
        parameters: ReconstructInput,
        product: ProductRepositoryItem,
    ) -> None:
        self._reconstructor = reconstructor
        self._parameters = parameters
        self._product = product

    def execute(self) -> UpdateProductTask:
        tic = time.perf_counter()
        result = self._reconstructor.reconstruct(self._parameters)
        toc = time.perf_counter()
        logger.info(f'Reconstruction time {toc - tic:.4f} seconds. (code={result.result})')
        return UpdateProductTask(result, self._product)


class ReconstructionQueue:
    def __init__(self) -> None:
        self._inputQueue: queue.Queue[ExecuteReconstructorTask] = queue.Queue()
        self._outputQueue: queue.Queue[UpdateProductTask] = queue.Queue()
        self._stopWorkEvent = threading.Event()
        self._worker = threading.Thread(target=self._reconstruct)

    @property
    def isReconstructing(self) -> bool:
        return self._inputQueue.unfinished_tasks > 0

    def _reconstruct(self) -> None:
        while not self._stopWorkEvent.is_set():
            try:
                inputTask = self._inputQueue.get(block=True, timeout=1)

                try:
                    outputTask = inputTask.execute()
                except Exception:
                    logger.exception('Reconstructor error!')
                else:
                    self._outputQueue.put(outputTask)
                finally:
                    self._inputQueue.task_done()
            except queue.Empty:
                pass

    def put(
        self,
        reconstructor: Reconstructor,
        parameters: ReconstructInput,
        product: ProductRepositoryItem,
    ) -> None:
        task = ExecuteReconstructorTask(reconstructor, parameters, product)
        self._inputQueue.put(task)

    def processResults(self, *, block: bool) -> None:
        while True:
            try:
                task = self._outputQueue.get(block=block)

                try:
                    task.execute()
                finally:
                    self._outputQueue.task_done()
            except queue.Empty:
                break

    def start(self) -> None:
        logger.info('Starting reconstructor...')
        self._worker.start()
        logger.info('Reconstructor started.')

    def stop(self) -> None:
        logger.info('Finishing reconstructions...')
        self._inputQueue.join()

        logger.info('Stopping reconstructor...')
        self._stopWorkEvent.set()
        self._worker.join()
        self.processResults(block=False)
        logger.info('Reconstructor stopped.')

    def __len__(self) -> int:
        return self._inputQueue.qsize()