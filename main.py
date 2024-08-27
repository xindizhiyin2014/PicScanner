# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import sys
from projectScanner import Ui_MainWindow
from alertDialog import AlertDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QApplication, QMainWindow, QFileDialog


import warnings
import argparse
from  picScanner import PicScanner




class MyWindow(QMainWindow, Ui_MainWindow):
    # 待扫描文件夹
    folderPath:str = ""
    # 输出结果文件
    resultFile:str = ""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.selectScanFolderBtn.clicked.connect(self.selectScanFolder)
        self.selecResultFolderBtn.clicked.connect(self.selectResultFolder)
        self.scanButton.clicked.connect(self.beginScan)


    def selectScanFolder(self,):

        self.folderPath = QFileDialog.getExistingDirectory(self, '选择文件夹')
        text = "待扫描文件夹：\n" + self.folderPath
        self.selectScanFoldLabel.setText(text)



    def selectResultFolder(self):

        folderPath = QFileDialog.getExistingDirectory(self, '选择文件夹')
        self.resultFile = folderPath + "/picScannerResult.txt"
        text = "扫描结果输出文件：\n" + self.resultFile
        self.scanResultLabel.setText(text)

    def beginScan(self):
        if self.folderPath == "":
            alert = AlertDialog(title="提示", message="请选择待扫描文件夹！", parent=self)
            alert.show_alert()
            return
        if self.resultFile == "":
            alert = AlertDialog(title="提示", message="请选择扫描结果导出文件夹！", parent=self)
            alert.show_alert()
            return
        projectPath = self.folderPath
        resultPath = self.resultFile
        picScanner = PicScanner(projectPath=projectPath, resultPath=resultPath)
        picScanner.scan()

        alert = AlertDialog(title="提示", message="扫描结束！", parent=self)
        alert.show_alert()








# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='扫描工具参数介绍')
    # parser.add_argument('--projectPath', type=str, help='工程项目的路径')
    # parser.add_argument('--resultPath', type=str, help='扫描结果文件目录')
    # args = parser.parse_args()
    # projectPath = args.projectPath
    # resultPath = args.resultPath

    # projectPath = "/Users/jack/work/pxx_app/app/IOS/iOS_Project/YouKeHD"
    # resultPath = "/Users/jack/Desktop/picScannerResult.txt"
    # picScanner = PicScanner(projectPath=projectPath, resultPath=resultPath)
    # picScanner.scan()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
