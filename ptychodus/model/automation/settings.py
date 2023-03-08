from __future__ import annotations
from pathlib import Path

from ...api.observer import Observable, Observer
from ...api.settings import SettingsRegistry, SettingsGroup


class AutomationSettings(Observable, Observer):

    def __init__(self, settingsGroup: SettingsGroup) -> None:
        super().__init__()
        self._settingsGroup = settingsGroup
        self.strategy = settingsGroup.createStringEntry('Strategy', 'CNM/APS Hard X-Ray Nanoprobe')
        self.useWatchdogPollingObserver = settingsGroup.createBooleanEntry(
            'UseWatchdogPollingObserver', False)
        self.watchdogDirectory = settingsGroup.createPathEntry('WatchdogDirectory',
                                                               Path('/path/to/data'))
        self.watchdogDelayInSeconds = settingsGroup.createIntegerEntry(
            'WatchdogDelayInSeconds', 15)

    @classmethod
    def createInstance(cls, settingsRegistry: SettingsRegistry) -> AutomationSettings:
        settings = cls(settingsRegistry.createGroup('Automation'))
        settings._settingsGroup.addObserver(settings)
        return settings

    def update(self, observable: Observable) -> None:
        if observable is self._settingsGroup:
            self.notifyObservers()
