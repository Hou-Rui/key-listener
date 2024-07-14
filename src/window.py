from typing import override

from PySide6.QtCore import QItemSelection, QModelIndex, Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import (QDockWidget, QMainWindow, QSizePolicy,
                               QStackedWidget, QTreeView, QWidget)

from executor import Executor
from forms import BindingSettingsForm, PresetSettingsForm
from listener import EventListener
from models import Binding, ConfigModel, Preset
from utils import (MAIN_WINDOW_HEIGHT_MIN, MAIN_WINDOW_WIDTH_MIN,
                   PROJECT_DISPLAY_NAME, ROW_HEIGHT)


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # backend
        self._listener = EventListener(self)
        self._model = ConfigModel(self)
        self._executor = Executor(self)

        # UI
        self._initWindow()
        self._initDockWidget()
        self._initSettingsForm()
        self._initActions()
        self._initToolBar()
        self._initStatusBar()
        self._initListener()

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        self._listener.cleanUp()
        super().closeEvent(event)

    def _initWindow(self) -> None:
        self.setMinimumSize(MAIN_WINDOW_WIDTH_MIN, MAIN_WINDOW_HEIGHT_MIN)
        self.setWindowTitle(self.tr(PROJECT_DISPLAY_NAME))

    def _initActions(self) -> None:
        # actions
        self._actionAddPreset = QAction(QIcon.fromTheme(
            QIcon.ThemeIcon.ListAdd), self.tr('Add Preset'), self)
        self._actionAddBinding = QAction(QIcon.fromTheme(
            QIcon.ThemeIcon.ListAdd), self.tr('Add Binding'), self)
        self._actionRemove = QAction(QIcon.fromTheme(
            QIcon.ThemeIcon.ListRemove), self.tr('Remove'), self)
        self._actionStart = QAction(QIcon.fromTheme(
            QIcon.ThemeIcon.MediaPlaybackStart), self.tr('Start'), self)
        self._actionStop = QAction(QIcon.fromTheme(
            QIcon.ThemeIcon.MediaPlaybackStop), self.tr('Stop'), self)

        self._actionStart.setEnabled(False)
        self._actionStop.setEnabled(False)

        # connections
        @self._listener.listeningChanged.connect
        def _():
            listening = self._listener.isListening()
            self._actionStart.setEnabled(not listening)
            self._actionStop.setEnabled(listening)

        @self._actionStart.triggered.connect
        def _():
            if preset := self._selectedPreset():
                keys = [(b.key, b.event) for b in preset.bindings]
                self._executor.start(preset.shell)
                self._listener.startListening(keys)

        @self._actionStop.triggered.connect
        def _():
            self._listener.stopListening()
            self._executor.stop()

    def _initToolBar(self) -> None:
        # left side actions
        toolBar = self.addToolBar(self.tr('Tool Bar'))
        toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolBar.setMovable(False)
        toolBar.addActions((self._actionAddPreset, self._actionAddBinding))
        toolBar.addSeparator()
        toolBar.addAction(self._actionRemove)

        # spacer
        spacer = QWidget()
        policy = QSizePolicy.Policy.Expanding
        spacer.setSizePolicy(policy, policy)
        toolBar.addWidget(spacer)

        # right side actions
        toolBar.addActions((self._actionStart, self._actionStop))

    def _initDockWidget(self) -> None:
        # tree view
        self._treeView = QTreeView()
        self._treeView.setHeaderHidden(True)
        self._treeView.setUniformRowHeights(True)
        self._treeView.setSelectionMode(
            QTreeView.SelectionMode.SingleSelection)
        self._treeView.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self._treeView.setModel(self._model)
        self._selectionModel = self._treeView.selectionModel()

        # dock widget
        dock = QDockWidget(self.tr('Preset List'))
        dock.setWidget(self._treeView)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _selectedIndex(self, selected: QItemSelection | None = None) -> QModelIndex:
        if selected:
            indexes = selected.indexes()
        else:
            indexes = self._selectionModel.selectedIndexes()
        if indexes and indexes[0].isValid():
            return indexes[0]
        return QModelIndex()

    def _selectedPreset(self) -> Preset | None:
        if item := self._model.itemFromIndex(self._selectedIndex()):
            if data := item.data(ConfigModel.PresetRole):
                return data
            elif item.data(ConfigModel.BindingRole):
                return item.parent().data(ConfigModel.PresetRole)
        return None

    def _selectedBinding(self) -> Binding | None:
        item = self._model.itemFromIndex(self._selectedIndex())
        if binding := item.data(ConfigModel.BindingRole):
            return binding
        return None

    def _initSettingsForm(self) -> None:
        # forms
        self._stackedWidget = QStackedWidget()
        self.setCentralWidget(self._stackedWidget)

        presetForm = PresetSettingsForm()
        self._stackedWidget.addWidget(presetForm)

        bindingForm = BindingSettingsForm()
        self._stackedWidget.addWidget(bindingForm)

        placeholderForm = QWidget()
        self._stackedWidget.addWidget(placeholderForm)
        self._stackedWidget.setCurrentWidget(placeholderForm)

        # connections
        @presetForm.applyRequested.connect
        def _():
            if preset := self._selectedPreset():
                preset.desc = presetForm.desc()
                preset.shell = presetForm.shell()
                index = self._selectedIndex()
                self._model.dataChanged.emit(index, index)
                self._model.save()

        @presetForm.resetRequested.connect
        def _():
            if preset := self._selectedPreset():
                presetForm.setDesc(preset.desc)
                presetForm.setShell(preset.shell)

        @bindingForm.applyRequested.connect
        def _():
            if binding := self._selectedBinding():
                binding.desc = bindingForm.desc()
                binding.key = bindingForm.key()
                binding.event = bindingForm.keyEvent()
                binding.cmd = bindingForm.cmd()
                binding.useShell = bindingForm.useShell()
                index = self._selectedIndex()
                self._model.dataChanged.emit(index, index)
                self._model.save()

        @bindingForm.resetRequested.connect
        def _():
            if binding := self._selectedBinding():
                bindingForm.setDesc(binding.desc)
                bindingForm.setKey(binding.key)
                bindingForm.setKeyEvent(binding.event)
                bindingForm.setCmd(binding.cmd)
                bindingForm.setUseShell(binding.useShell)

        @self._selectionModel.selectionChanged.connect
        def _(selected: QItemSelection, _):
            index = self._selectedIndex(selected)
            self._actionStart.setEnabled(index.isValid())
            item = self._model.itemData(index)

            preset: Preset | None
            binding: Binding | None
            if preset := item.get(ConfigModel.PresetRole):
                presetForm.setDesc(preset.desc)
                presetForm.setShell(preset.shell)
                self._stackedWidget.setCurrentWidget(presetForm)
            elif binding := item.get(ConfigModel.BindingRole):
                bindingForm.setDesc(binding.desc)
                bindingForm.setKey(binding.key)
                bindingForm.setKeyEvent(binding.event)
                bindingForm.setUseShell(binding.useShell)
                bindingForm.setCmd(binding.cmd)
                self._stackedWidget.setCurrentWidget(bindingForm)

    def _setEditable(self, editable: bool) -> None:
        self._treeView.setEnabled(editable)
        self._stackedWidget.setEnabled(editable)

    def _initStatusBar(self) -> None:
        statusBar = self.statusBar()
        statusBar.showMessage(self.tr('Ready.'))

    def _initListener(self) -> None:
        _listeningPreset: list[Preset | None] = [None]

        @self._listener.keyCaptured.connect
        def _(key: str, event: str):
            if preset := _listeningPreset[0]:
                for binding in preset.getBindings(key, event):
                    self._executor.run(binding.cmd, binding.useShell)
            self.statusBar().showMessage(
                self.tr('Key event captured: {} {}').format(key, event))

        @self._listener.listeningChanged.connect
        def _():
            if self._listener.isListening():
                self._setEditable(False)
                _listeningPreset[0] = self._selectedPreset()
                self.statusBar().showMessage(self.tr('Listener started.'))
            else:
                _listeningPreset[0] = None
                self.statusBar().showMessage(self.tr('Listener stopped.'))
                self._setEditable(True)
