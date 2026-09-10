import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from CmdTools import Command
from Parameters import ParamType
from Statistic import Statistic
from UI.pyqt_prototype.runner import coerce_value, execute_point_query


APP_STYLE = """
QWidget {
    background: #f5f7fb;
    color: #182233;
    font-family: Inter, SF Pro Display, Segoe UI, Arial, sans-serif;
    font-size: 14px;
}
QLabel#eyebrow {
    color: #5b6b82;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.6px;
    text-transform: uppercase;
}
QLabel#title {
    color: #101828;
    font-size: 30px;
    font-weight: 800;
}
QLabel#subtitle {
    color: #5b6b82;
    font-size: 14px;
}
QLabel#sectionTitle {
    color: #101828;
    font-size: 18px;
    font-weight: 750;
}
QLabel#fieldHint {
    color: #667085;
    font-size: 12px;
}
QFrame#card {
    background: #ffffff;
    border: 1px solid #d9e2ef;
    border-radius: 18px;
}
QComboBox, QLineEdit, QSpinBox {
    background: #ffffff;
    border: 1px solid #cfd8e6;
    border-radius: 10px;
    padding: 8px 10px;
    min-height: 28px;
}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #4f7cff;
}
QCheckBox {
    spacing: 10px;
    color: #344054;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
}
QPushButton {
    background: #315efb;
    border: none;
    border-radius: 12px;
    color: white;
    font-size: 15px;
    font-weight: 700;
    padding: 12px 18px;
}
QPushButton:hover {
    background: #244ddd;
}
QPushButton:pressed {
    background: #1c3fb7;
}
QPushButton:disabled {
    background: #98a2b3;
}
QTextEdit {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 16px;
    color: #dbeafe;
    font-family: JetBrains Mono, SF Mono, Consolas, monospace;
    font-size: 13px;
    padding: 14px;
}
"""


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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setHorizontalSpacing(22)
        self.layout.setVerticalSpacing(16)
        self.layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
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
            self.layout.addRow(self._make_label(parameter), editor)
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

    def _make_label(self, parameter):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        name = QLabel(parameter.name + ("  *" if parameter.required else ""))
        name.setStyleSheet("font-weight: 700; color: #243047;")
        hint = QLabel(parameter.description or "Optional value")
        hint.setObjectName("fieldHint")
        hint.setWordWrap(True)
        layout.addWidget(name)
        layout.addWidget(hint)
        return wrapper

    def _make_editor(self, parameter):
        match parameter.param_type:
            case ParamType.BOOL:
                editor = QCheckBox("Enabled")
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
        editor.setMinimumWidth(280)
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
        self.output.setPlaceholderText("Run a query to see results here.")
        self.run_button = QPushButton("Run point query")
        self.status = QLabel("Ready")
        self.status.setObjectName("fieldHint")

        central = QWidget()
        shell = QVBoxLayout(central)
        shell.setContentsMargins(28, 26, 28, 28)
        shell.setSpacing(20)
        shell.addLayout(self._make_header())
        shell.addLayout(self._make_body(), 1)
        self.setCentralWidget(central)

        self.command_picker.currentIndexChanged.connect(self.refresh_form)
        self.run_button.clicked.connect(self.run_query)
        self.refresh_form()

    def _make_header(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        eyebrow = QLabel("SEQUENCER PROTOTYPE")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Build mathematical queries directly from Python metadata")
        title.setObjectName("title")
        subtitle = QLabel("A cleaner Qt Widgets direction before expanding coverage beyond point queries.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return layout

    def _make_body(self):
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(20)
        layout.addWidget(self._make_query_card(), 0, 0)
        layout.addWidget(self._make_result_card(), 0, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        return layout

    def _make_query_card(self):
        card, layout = self._card("Query setup", "Choose an object, select an optional statistic, then fill in the generated parameters.")

        pickers = QFormLayout()
        pickers.setContentsMargins(0, 0, 0, 0)
        pickers.setHorizontalSpacing(16)
        pickers.setVerticalSpacing(14)
        pickers.addRow("Object", self.command_picker)
        pickers.addRow("Statistic", self.statistic_picker)
        layout.addLayout(pickers)
        layout.addSpacing(8)
        layout.addWidget(self.form)
        layout.addSpacing(4)
        layout.addWidget(self.print_elements)
        layout.addStretch(1)
        layout.addWidget(self.run_button)
        layout.addWidget(self.status)
        return card

    def _make_result_card(self):
        card, layout = self._card("Result", "Captured command output appears here without freezing the interface.")
        self.output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.output, 1)
        return card

    def _card(self, title, subtitle):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        return card, layout

    @Slot()
    def refresh_form(self):
        self.form.set_command(self.command_picker.currentData())
        self.status.setText("Ready")

    @Slot()
    def run_query(self):
        try:
            parameters = self.form.values()
        except Exception as exc:
            QMessageBox.warning(self, "Invalid parameters", str(exc))
            return

        self.run_button.setEnabled(False)
        self.status.setText("Running query…")
        self.output.setPlainText("Running…")
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
        self.status.setText("Complete")
        self.output.setPlainText(output.strip())

    @Slot(str)
    def query_failed(self, message):
        self.run_button.setEnabled(True)
        self.status.setText("Failed")
        self.output.setPlainText(message)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    app.setFont(QFont("Inter", 10))
    window = SequencerPrototypeWindow()
    window.resize(1180, 760)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
