from __future__ import annotations
from pathlib import Path
from uuid import UUID

from ...api.observer import Observable, Observer
from ...api.settings import SettingsRegistry, SettingsGroup


class WorkflowSettings(Observable, Observer):

    def __init__(self, group: SettingsGroup) -> None:
        super().__init__()
        self.group = group
        self.computeFuncXEndpointID = group.createUUIDEntry('ComputeFuncXEndpointID', UUID(int=0))
        self.statusRefreshIntervalInSeconds = group.createIntegerEntry(
            'StatusRefreshIntervalInSeconds', 10)

    @classmethod
    def createInstance(cls, settingsRegistry: SettingsRegistry) -> WorkflowSettings:
        settings = cls(settingsRegistry.createGroup('Workflow'))
        settings.group.addObserver(settings)
        return settings

    def update(self, observable: Observable) -> None:
        if observable is self.group:
            self.notifyObservers()