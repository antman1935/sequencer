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
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from CmdTools import Command
from Parameters import OutputType, ParamType
from SequencerAPI import SequencerAPI
from Statistic import Dimension, DimensionType, Statistic
from UI.pyqt_prototype.runner import QueryResult, coerce_value, run_query
from UI.pyqt_prototype.theme import LAYOUT, TYPOGRAPHY, qt_stylesheet


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class QueryWorker(QRunnable):
    def __init__(self, api_name, command_name, parameters, statistic_name, print_elements, dimensions, output_type):
        super().__init__()
        self.api_name = api_name
        self.command_name = command_name
        self.parameters = parameters
        self.statistic_name = statistic_name
        self.print_elements = print_elements
        self.dimensions = dimensions
        self.output_type = output_type
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = run_query(
                self.api_name,
                self.command_name,
                self.parameters,
                self.statistic_name,
                self.print_elements,
                self.dimensions,
                self.output_type,
            )
        except Exception as exc:
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class GeneratedParameterForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("parameterList")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)
        self.command_name = None
        self.editors = {}

    def set_command(self, command_name):
        self.command_name = command_name
        self.editors = {}
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        command_class = Command.commands[command_name]
        for parameter in sorted(command_class.parameters, key=lambda p: not p.required):
            editor = self._make_editor(parameter)
            self.layout.addWidget(self._make_parameter_row(parameter, editor))
            self.editors[parameter.name] = (parameter, editor)
        self.layout.addStretch(1)

    def values(self):
        result = {}
        for name, (parameter, editor) in self.editors.items():
            value = self._editor_value(parameter, editor)
            if value is None and parameter.required:
                raise ValueError(f"{name} is required.")
            if value is not None:
                result[name] = value
        return result

    def _make_parameter_row(self, parameter, editor):
        row = QFrame()
        row.setObjectName("parameterRow")
        row.setFrameShape(QFrame.NoFrame)
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        label = QLabel(parameter.name + ("  *" if parameter.required else ""))
        label.setObjectName("fieldLabel")
        hint = QLabel(parameter.description or "Optional value")
        hint.setObjectName("fieldHint")
        hint.setWordWrap(True)
        hint.setMinimumHeight(30)
        row_layout.addWidget(label)
        row_layout.addWidget(hint)
        row_layout.addWidget(editor)
        return row

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
        editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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


class DimensionSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("parameterList")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.checkboxes = []

    def set_command(self, command_name):
        self.checkboxes = []
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        command_class = Command.commands[command_name]
        for parameter in command_class.parameters:
            if parameter.param_type in (ParamType.NATURAL, ParamType.INT_POS):
                self._add_dimension(parameter.name, DimensionType.PARAMETER, f"Parameter: {parameter.name}")
        for key, statistic_class in Statistic.statistics.items():
            self._add_dimension(key, DimensionType.COMPUTED, f"Computed: {statistic_class.ui_name}")
        self.layout.addStretch(1)

    def values(self):
        return [Dimension(dim_type, name) for box, name, dim_type in self.checkboxes if box.isChecked()]

    def _add_dimension(self, name, dim_type, label):
        checkbox = QCheckBox(label)
        checkbox.setToolTip("Use this dimension to group range results")
        self.checkboxes.append((checkbox, name, dim_type))
        self.layout.addWidget(checkbox)


class SequencerPrototypeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequencer Python-first Qt Prototype")
        self.thread_pool = QThreadPool.globalInstance()

        self.api_picker = QComboBox()
        for key, api_class in SequencerAPI.apis.items():
            self.api_picker.addItem(api_class.ui_name, key)

        self.command_picker = QComboBox()
        for key, command_class in Command.commands.items():
            self.command_picker.addItem(command_class.ui_name, key)

        self.statistic_picker = QComboBox()
        self.statistic_picker.addItem("Count objects", None)
        for key, statistic_class in Statistic.statistics.items():
            self.statistic_picker.addItem(statistic_class.ui_name, key)

        self.output_picker = QComboBox()
        self.output_picker.addItem("Rendered table", OutputType.ASCII_TABLE)
        self.output_picker.addItem("OEIS sequence", OutputType.OEIS_LOOKUP)
        self.output_picker.addItem("Raw data", OutputType.RAW)
        self.output_picker.addItem("LaTeX file", OutputType.LATEX_TABLE)

        self.print_elements = QCheckBox("Show generated elements")
        self.form = GeneratedParameterForm()
        self.dimensions = DimensionSelector()
        self.output_tabs = QTabWidget()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("Run a query to see results here.")
        self.output_tabs.addTab(self.text_output, "Text")
        self.run_button = QPushButton("Run query")
        self.status = QLabel("Ready")
        self.status.setObjectName("statusText")

        root = QWidget()
        root.setObjectName("appRoot")
        shell = QVBoxLayout(root)
        shell.setContentsMargins(LAYOUT["shell_margin_x"], LAYOUT["shell_margin_top"], LAYOUT["shell_margin_x"], LAYOUT["shell_margin_bottom"])
        shell.setSpacing(LAYOUT["shell_gap"])
        shell.addLayout(self._make_header())
        shell.addLayout(self._make_body(), 1)
        self.setCentralWidget(root)

        self.api_picker.currentIndexChanged.connect(self.refresh_visibility)
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
        subtitle = QLabel("Python-first Qt coverage for point and range queries, with real rendered range tables.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return layout

    def _make_body(self):
        layout = QHBoxLayout()
        layout.setSpacing(18)
        layout.addWidget(self._make_query_card())
        layout.addWidget(self._make_result_card(), 1)
        return layout

    def _make_query_card(self):
        card, layout = self._card("Query setup", "Choose API, object family, optional statistic, and typed parameters.")
        card.setFixedWidth(LAYOUT["query_card_width"])
        layout.addWidget(self._make_field_block("API", self.api_picker))
        layout.addWidget(self._make_field_block("Object", self.command_picker))
        layout.addWidget(self._make_field_block("Statistic", self.statistic_picker))
        self.output_block = self._make_field_block("Range output", self.output_picker)
        layout.addWidget(self.output_block)

        command_scroller = QScrollArea()
        command_scroller.setWidgetResizable(True)
        command_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        command_scroller.setWidget(self.form)
        command_scroller.setMinimumHeight(190)
        layout.addWidget(command_scroller, 1)

        self.dimension_block = self._make_field_block("Range dimensions", self._scroll_widget(self.dimensions, 150))
        layout.addWidget(self.dimension_block)
        layout.addWidget(self.print_elements)
        layout.addWidget(self.run_button)
        layout.addWidget(self.status)
        return card

    def _make_result_card(self):
        card, layout = self._card("Result", "Range table output is rendered as selectable Qt tables; text output remains available.")
        self.output_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.output_tabs, 1)
        return card

    def _scroll_widget(self, widget, minimum_height):
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroller.setWidget(widget)
        scroller.setMinimumHeight(minimum_height)
        return scroller

    def _make_field_block(self, label_text, editor):
        block = QWidget()
        block.setObjectName("fieldBlock")
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(editor)
        return block

    def _card(self, title, subtitle):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(LAYOUT["card_padding_x"], LAYOUT["card_padding_y"], LAYOUT["card_padding_x"], LAYOUT["card_padding_y"])
        layout.setSpacing(13)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("helpText")
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        return card, layout

    @Slot()
    def refresh_form(self):
        command_name = self.command_picker.currentData()
        self.form.set_command(command_name)
        self.dimensions.set_command(command_name)
        self.status.setText("Ready")
        self.refresh_visibility()

    @Slot()
    def refresh_visibility(self):
        is_range = self.api_picker.currentData() == "range"
        self.dimension_block.setVisible(is_range)
        self.output_block.setVisible(is_range)
        self.status.setText("Ready")

    @Slot()
    def run_query(self):
        try:
            parameters = self.form.values()
            dimensions = self.dimensions.values() if self.api_picker.currentData() == "range" else None
        except Exception as exc:
            QMessageBox.warning(self, "Invalid parameters", str(exc))
            return

        self.run_button.setEnabled(False)
        self.status.setText("Running query…")
        self.text_output.setPlainText("Running…")
        self._clear_table_tabs()
        worker = QueryWorker(
            self.api_picker.currentData(),
            self.command_picker.currentData(),
            parameters,
            self.statistic_picker.currentData(),
            self.print_elements.isChecked(),
            dimensions,
            self.output_picker.currentData(),
        )
        worker.signals.finished.connect(self.query_finished)
        worker.signals.failed.connect(self.query_failed)
        self.thread_pool.start(worker)

    @Slot(object)
    def query_finished(self, result: QueryResult):
        self.run_button.setEnabled(True)
        self.status.setText("Complete")
        self.text_output.setPlainText(result.text.strip())
        self._clear_table_tabs()
        for table in result.tables:
            self.output_tabs.addTab(self._table_widget(table), table.label or "Table")
        if result.tables:
            self.output_tabs.setCurrentIndex(1)

    @Slot(str)
    def query_failed(self, message):
        self.run_button.setEnabled(True)
        self.status.setText("Failed")
        self._clear_table_tabs()
        self.text_output.setPlainText(message)

    def _clear_table_tabs(self):
        while self.output_tabs.count() > 1:
            self.output_tabs.removeTab(1)

    def _table_widget(self, table):
        row_start, row_end = table.row_bounds
        col_start, col_end = table.column_bounds
        widget = QTableWidget(row_end - row_start + 1, col_end - col_start + 1)
        widget.setObjectName("resultTable")
        widget.setHorizontalHeaderLabels([f"{table.column_dimension}={col}" for col in range(col_start, col_end + 1)])
        widget.setVerticalHeaderLabels([f"{table.row_dimension}={row}" for row in range(row_start, row_end + 1)])
        for row_index, row in enumerate(table.data):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem("" if value == 0 else str(value))
                item.setTextAlignment(Qt.AlignCenter)
                widget.setItem(row_index, col_index, item)
        widget.resizeColumnsToContents()
        return widget


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(qt_stylesheet())
    app.setFont(QFont(TYPOGRAPHY["qt_ui_font"], 10))
    window = SequencerPrototypeWindow()
    window.resize(LAYOUT["window_width"], LAYOUT["window_height"])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
