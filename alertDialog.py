
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class AlertDialog(QDialog):
    def __init__(self, title, message, acceptBlock=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon('path_to_your_icon.png'))  # 设置图标，如果有的话
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # 设置无边框窗口
        self.setFixedSize(300, 150)  # 设置固定大小
        self.acceptBlock = acceptBlock
        layout = QVBoxLayout()

        # 添加标题和消息
        self.title_label = QLabel(title)
        title_font = self.font()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        self.message_label = QLabel(message)
        layout.addWidget(self.message_label)

        # 添加确定按钮
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.__accept)  # 连接点击信号到accept槽
        layout.addWidget(self.ok_button)

        self.setLayout(layout)


    def show_alert(self):
        # 显示对话框
        self.exec_()

    def __accept(self):
        self.close()
        if self.acceptBlock != None:
            self.acceptBlock()