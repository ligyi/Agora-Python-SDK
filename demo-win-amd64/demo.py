import IAgoraRtcEngine
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import MainWindow
import sys
from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from callBack import EventHandlerData


appId = b""

Engine = IAgoraRtcEngine.pycreateAgoraRtcEngine()
ctx = IAgoraRtcEngine.pyRtcEngineContext()
ctx.eventHandler = IAgoraRtcEngine.pyEventHandler()
ctx.appId = appId
Engine.initialize(ctx)
EngineParam = IAgoraRtcEngine.pyRtcEngineParameters()
localWinId = -1
remoteWinId = -1

class callBackListener(QThread):
    def __init__(self):
        super(callBackListener, self).__init__()

    def run(self):
        while (True):
            if EventHandlerData.localWindowSet == False:
                if EventHandlerData.localUid != -1:
                    window.channelEdit.setEnabled(False)
                    window.joinButton.setEnabled(False)
                    window.leaveButton.setEnabled(True)
                    LocalCanvas = IAgoraRtcEngine.pyVideoCanvas()
                    LocalCanvas.construct_2(localWinId,
                                            IAgoraRtcEngine.pyRENDER_MODE_TYPE.RENDER_MODE_HIDDEN,
                                            EventHandlerData.localUid)
                    Engine.setupLocalVideo(LocalCanvas)
                    EventHandlerData.localWindowSet = True

            if EventHandlerData.remoteUserWindowSet == False:
                if EventHandlerData.remoteUid != -1:
                    RemoteCanvas = IAgoraRtcEngine.pyVideoCanvas()
                    RemoteCanvas.construct_2(remoteWinId, IAgoraRtcEngine.pyRENDER_MODE_TYPE.RENDER_MODE_HIDDEN,
                                             EventHandlerData.remoteUid)
                    Engine.setupRemoteVideo(RemoteCanvas)
                    EventHandlerData.remoteUserWindowSet = True

class joinChannelThread(QThread):
    def __init__(self):
        super(joinChannelThread, self).__init__()
        self.channel = ""

    def run(self):
        Engine.joinChannel(appId, self.channel, b"", 0)
        Engine.enableVideo()
        EngineParam.construct_3(Engine)
        EngineParam.enableLocalVideo(True)
        EngineParam.muteLocalVideoStream(False)


class leaveChannelThread(QThread):
    def __init__(self):
        super(leaveChannelThread, self).__init__()
    def run(self):
        Engine.leaveChannel()

class enableLocalVideoThread(QThread):
    def __init__(self):
        super(enableLocalVideoThread, self).__init__()
    def run(self):
        EngineParam.enableLocalVideo(True)

class disableLocalVideoThread(QThread):
    def __init__(self):
        super(disableLocalVideoThread, self).__init__()
    def run(self):
        EngineParam.enableLocalVideo(False)

class MyWindow(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        MainWindow.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.window1 = GLwindow()
        self.window2 = GLwindow()
        self.gridLayout.addWidget(self.window1)
        self.gridLayout_2.addWidget(self.window2)
        self.joinButton.clicked.connect(self.joinChannel)
        self.leaveButton.clicked.connect(self.leaveChannel)
        self.leaveButton.setEnabled(False)
        self.enableButton.clicked.connect(self.enableLocalVideo)
        self.disableButton.clicked.connect(self.disableLocalVideo)
        self.callBackListener = callBackListener()
        self.callBackListener.start()

    def joinChannel(self):
        if EventHandlerData.joinChannelSuccess == False:
            self.joinThread = joinChannelThread()
            if self.checkChannelName() == False:
                QMessageBox.information(self, "Message",
                                        "The channel name contains illegal character.",
                                        QMessageBox.Yes)
                return
            if len(self.channelEdit.toPlainText()) == 0:
                QMessageBox.information(self, "Message",
                                        "Please input the channel name.",
                                        QMessageBox.Yes)
                return
            if len(self.channelEdit.toPlainText()) > 64:
                QMessageBox.information(self, "Message",
                                        "The length of the channel name must be less than 64.",
                                        QMessageBox.Yes)
                return
            self.joinThread.channel = bytes(self.channelEdit.toPlainText(), 'ascii')

            global localWinId, remoteWinId
            localWinId = self.window1.effectiveWinId().__int__()
            remoteWinId = self.window2.effectiveWinId().__int__()
            self.joinThread.start()

    def leaveChannel(self):
        if EventHandlerData.joinChannelSuccess == True:
            self.leaveThread = leaveChannelThread()
            self.leaveThread.start()
            self.joinButton.setEnabled(True)
            self.leaveButton.setEnabled(False)
            self.channelEdit.setEnabled(True)

    def enableLocalVideo(self):
        if EventHandlerData.joinChannelSuccess == True:
            self.enableThread = enableLocalVideoThread()
            self.enableThread.start()

    def disableLocalVideo(self):
        if EventHandlerData.joinChannelSuccess == True:
            self.disableThread = disableLocalVideoThread()
            self.disableThread.start()

    def checkChannelName(self):
        str = self.channelEdit.toPlainText()
        for char in str:
            if ord(char) >= ord('a') and ord(char) <= ord('z'):
                continue
            elif ord(char) >= ord('A') and ord(char) <= ord('Z'):
                continue
            elif ord(char) >= ord('0') and ord(char) <= ord('9'):
                continue
            elif char in ["!","#","$","%","&","(",")","+","-",":",
                          ";","<","=",".",">","?","@","[","]","^",
                          "_","{","}","|","~",","] or ord(char) == 32:
                continue
            else:
                return False
        return True

class GLwindow(QtOpenGL.QGLWidget):
    def __init__(self):
        QtOpenGL.QGLWidget.__init__(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
