import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from CmdTools import Command
from Parameters import ParamType
from Statistic import Statistic
from UI.pyqt_prototype.runner import coerce_value, execute_point_query


class WorkerSignals(QObject):
    finished = Signal(str)
    failed = Signal(str)


class QueryWorker(QRunnable):
    def __init__(self, command_name, parameters, statistic_name, print_elements):
        super().__init__()
        self.command_name = command_name
        self.parameters = parameters
        self.statistic_name = statistic_name
        self.print_elements = print_elements
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            output = execute_point_query(self.command_name, self.parameters, self.statistic_name, self.print_elements)
        except Exception as exc:
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(output)


class GeneratedParameterForm(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.command_name = None
        self.editors = {}

    def set_command(self, command_name):
        self.command_name = command_name
        self.editors = {}
        while self.layout.rowCount():
            self.layout.removeRow(0)

        command_class = Command.commands[command_name]
        for parameter in sorted(command_class.parameters, key=lambda p: not p.required):
            editor = self._make_editor(parameter)
            label = parameter.name + (" *" if parameter.required else "")
            self.layout.addRow(label, editor)
            self.editors[parameter.name] = (parameter, editor)

    def values(self):
        result = {}
        for name, (parameter, editor) in self.editors.items():
            value = self._editor_value(parameter, editor)
            if value is None and parameter.required:
                raise ValueError(f"{name} is required.")
            if value is not None:
                result[name] = value
        return result

    def _make_editor(self, parameter):
        match parameter.param_type:
            case ParamType.BOOL:
                editor = QCheckBox(parameter.description)
            case ParamType.NATURAL | ParamType.INT_POS:
                editor = QSpinBox()
                editor.setMinimum(ParamType.typeMin(parameter.param_type))
                editor.setMaximum(1000000)
                if not parameter.required:
                    editor.setSpecialValueText("unset")
            case ParamType.INTEGER:
                editor = QSpinBox()
                editor.setMinimum(-1000000)
                editor.setMaximum(1000000)
                if not parameter.required:
                    editor.setSpecialValueText("unset")
            case _:
                editor = QLineEdit()
                editor.setPlaceholderText(parameter.description)
        editor.setToolTip(parameter.description)
        return editor

    def _editor_value(self, parameter, editor):
        if isinstance(editor, QCheckBox):
            return editor.isChecked() if parameter.required or editor.isChecked() else None
        if isinstance(editor, QSpinBox):
            value = editor.value()
            if not parameter.required and value == editor.minimum():
                return None
            return coerce_value(parameter.param_type, value)
        text = editor.text().strip()
        return coerce_value(parameter.param_type, text)


class SequencerPrototypeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequencer Python-first Qt Prototype")
        self.thread_pool = QThreadPool.globalInstance()

        self.command_picker = QComboBox()
        for key, command_class in Command.commands.items():
            self.command_picker.addItem(command_class.ui_name, key)

        self.statistic_picker = QComboBox()
        self.statistic_picker.addItem("Count objects", None)
        for key, statistic_class in Statistic.statistics.items():
            self.statistic_picker.addItem(statistic_class.ui_name, key)

        self.print_elements = QCheckBox("Show generated elements")
        self.form = GeneratedParameterForm()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.run_button = QPushButton("Run point query")

        header = QHBoxLayout()
        header.addWidget(QLabel("Object"))
        header.addWidget(self.command_picker, 1)
        header.addWidget(QLabel("Statistic"))
        header.addWidget(self.statistic_picker, 1)

        body = QVBoxLayout()
        body.addLayout(header)
        body.addWidget(self.form)
        body.addWidget(self.print_elements)
        body.addWidget(self.run_button)
        body.addWidget(QLabel("Result"))
        body.addWidget(self.output, 1)

        central = QWidget()
        central.setLayout(body)
        self.setCentralWidget(central)

        self.command_picker.currentIndexChanged.connect(self.refresh_form)
        self.run_button.clicked.connect(self.run_query)
        self.refresh_form()

    @Slot()
    def refresh_form(self):
        self.form.set_command(self.command_picker.currentData())

    @Slot()
    def run_query(self):
        try:
            parameters = self.form.values()
        except Exception as exc:
            QMessageBox.warning(self, "Invalid parameters", str(exc))
            return

        self.run_button.setEnabled(False)
        self.output.setPlainText("Running...")
        worker = QueryWorker(
            self.command_picker.currentData(),
            parameters,
            self.statistic_picker.currentData(),
            self.print_elements.isChecked(),
        )
        worker.signals.finished.connect(self.query_finished)
        worker.signals.failed.connect(self.query_failed)
        self.thread_pool.start(worker)

    @Slot(str)
    def query_finished(self, output):
        self.run_button.setEnabled(True)
        self.output.setPlainText(output.strip())

    @Slot(str)
    def query_failed(self, message):
        self.run_button.setEnabled(True)
        self.output.setPlainText(message)


def main():
    app = QApplication(sys.argv)
    window = SequencerPrototypeWindow()
    window.resize(900, 650)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
