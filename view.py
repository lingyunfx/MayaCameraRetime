from PySide2 import QtWidgets
import retime_mod
reload(retime_mod)


class MainUI(QtWidgets.QWidget):

    def __init__(self):
        super(MainUI, self).__init__()
        self.top_la = QtWidgets.QHBoxLayout()
        self.button_la = QtWidgets.QHBoxLayout()
        self.layout = QtWidgets.QVBoxLayout()

        self.type_label = QtWidgets.QLabel('Type: ')
        self.type_choose = QtWidgets.QComboBox()
        self.path_input = QtWidgets.QLineEdit()
        self.path_bt = QtWidgets.QPushButton('..')
        self.run_bt = QtWidgets.QPushButton('Run')
        self.cancel_bt = QtWidgets.QPushButton('Cancel')
        self.build_ui()
        self.setLayout(self.layout)

    def build_ui(self):
        widgets = ((self.type_label, self.type_choose, self.path_input, self.path_bt),
                   (self.run_bt, self.cancel_bt))
        layouts = (self.top_la, self.button_la)

        map(lambda widget: self.top_la.addWidget(widget), widgets[0])
        map(lambda widget: self.button_la.addWidget(widget), widgets[1])
        map(lambda layout: self.layout.addLayout(layout), layouts)
        self.adjust_ui()
        self.connect_cmd()

    def adjust_ui(self):
        types = ('Motion', 'Frame', 'None')
        self.type_choose.addItems(types)
        self.path_input.setPlaceholderText('Your retime txt file path here..')
        self.setWindowTitle('Maya Retime Tool')
        self.setMinimumWidth(500)

    def connect_cmd(self):
        self.path_bt.clicked.connect(self.choose_file)
        self.run_bt.clicked.connect(self.run_retime)
        self.cancel_bt.clicked.connect(self.close)

    def choose_file(self):
        txt_file, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        if txt_file:
            self.path_input.setText(txt_file)

    def run_retime(self):
        typ = self.type_choose.currentText()
        node_path = self.path_input.text()
        task = retime_mod.CurvesRetime(node_path, typ)
        task.do_retime()
        self.done_message()

    def done_message(self):
        QtWidgets.QMessageBox.information(self, 'information', 'Done!')

