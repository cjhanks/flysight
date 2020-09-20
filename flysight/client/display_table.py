from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QColor
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )


class TrackerTableView(QtWidgets.QTableView):
    """
    :class TrackerTableView:

    Column/row table for displaying the peak detections.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We already have an ID column.
        self.verticalHeader().hide()

    def sizeHint(self):
        return QtCore.QSize(156, 256)

    def keyPressEvent(self, kp):
        """
        This implements the logic for copying data from the table to the
        paste buffer as a CSV style paste.
        """
        if kp != QtGui.QKeySequence.Copy:
            return

        model = self.model()
        data = {}
        selection = self.selectionModel().selectedIndexes()

        for item in selection:
            row = item.row()
            col = item.column()
            data[(row, col)] = model.data(item)

        # {
        # This slightly convoluted implementation
        line = []
        lines = []
        data = list(sorted(data.items()))
        if not len(data):
            return None

        row = data[0][0][0]
        for ((r, c), data) in data:
            if r != row:
                lines.append(','.join(map(str, line)))
                line = []
                row = r

            line.append(data)
        lines.append(','.join(map(str, line)))
        # }

        QtWidgets.QApplication.clipboard().setText('\n'.join(lines))


class TrackerTableModel(QAbstractTableModel):
    """
    :class TrackerTableModel:

    This implements the model class for a `QtWidgets.QTableView`.  The objective
    is to have a minimally widthed 3 column table which can be copy/pasted into
    an excel style program.

    Columns are:
        +----+---+---+
        | Id | X | Y |
        +----+---+---+

    This is a display tool, actual identification association is not handled in
    this tool.
    """
    Columns = ['Id', 'X', 'Y']

    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.col_count = len(self.Columns)
        self.peaks = []

    def load_data(self, peaks):
        """
        The peaks structure is of the format:
            [(index, (x, y)), ...]
        """
        self.peaks = peaks
        self.beginResetModel()
        self.beginInsertRows(QtCore.QModelIndex(),
                             0,
                             self.rowCount())
        self.endInsertRows()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self.peaks)

    def columnCount(self, parent=QModelIndex()):
        return self.col_count

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.Columns[section]
            else:
                return "{}".format(section)

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable     \
             | QtCore.Qt.ItemIsEnabled      \
             | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=Qt.DisplayRole):
        col = index.column()
        row = index.row()

        if role != Qt.DisplayRole:
            return

        r = self.peaks[row]
        if col == 0:
            val = r[0]
        else:
            val = r[1][col - 1]

        return val

