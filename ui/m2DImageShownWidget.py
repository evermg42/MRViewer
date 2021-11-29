from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os
from ui.AbstractImageShownWidget import AbstractImageShownWidget
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from utils.util import getDicomWindowCenterAndLevel

class m2DImageShownWidget(AbstractImageShownWidget):
    
    #wheel信号 by evermg42
    sigWheelChanged = pyqtSignal(object)

    def __init__(self):
        AbstractImageShownWidget.__init__(self)
        #初始化GUI配置
        # self.setFixedSize(500,500)
        #初始化数据
        self.seriesPath = ""
        self.filePaths = []
        self.curFilePath = ""
        #初始化逻辑
        self.update2DImageShownSignal = None
        self.reader = None
        self.imageViewer = None
        self.qvtkWidget = None
        self.ren = None
		
    def dropEvent(self, event):
        try:
            self.view.sigWheelChanged.disconnect(self.wheelChangeEvent)
        except:
            pass
        super().dropEvent(event)
        self.seriesPath = event.mimeData().getImageExtraData()["seriesPath"]
        event.mimeData().setText("")
        fileNames = os.listdir(self.seriesPath)
        self.filePaths = [self.seriesPath + '/' + fileName for fileName in fileNames]
        #evermg42: we need numpy array of them
        self.curFilePath = self.filePaths[0]
        self.currentIndex = 0
        self.show2DImage(self.curFilePath)
        self.sigWheelChanged.connect(self.wheelChangeEvent)
        
    def show2DImage(self, filePath):
        print("showXZDicom begin")
        if self.reader is None: self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDataByteOrderToLittleEndian()
        self.reader.SetFileName(filePath)
        self.reader.Update()

        if self.imageViewer is None:self.imageViewer =  vtk.vtkImageViewer2()
        self.imageViewer.SetInputConnection(self.reader.GetOutputPort())
        level,width = getDicomWindowCenterAndLevel(filePath)
        self.imageViewer.SetColorLevel(level)
        self.imageViewer.SetColorWindow(width)

        if self.ren is None:self.ren = vtk.vtkRenderer()

        if self.qvtkWidget is None:self.qvtkWidget = QVTKRenderWindowInteractor(self)
        self.qvtkWidget.setFixedSize(self.size())
        self.qvtkWidget.GetRenderWindow().AddRenderer(self.ren)

        self.imageViewer.SetRenderer(self.ren)
        self.imageViewer.SetRenderWindow(self.qvtkWidget.GetRenderWindow())
        self.imageViewer.UpdateDisplayExtent()
        self.imageViewer.SetupInteractor(self.qvtkWidget.GetRenderWindow().GetInteractor())
		
        self.ren.ResetCamera()
        self.qvtkWidget.GetRenderWindow().Render()

        if not self.qvtkWidget.isVisible(): self.qvtkWidget.setVisible(True)
        print(self.pos())
        print(self.qvtkWidget.pos())
        print("showXZDicom end")

    def wheelEvent(self, ev):
		#rewrite wheelEvent by evermg42#
        #ev.accept()
        self.sigWheelChanged.emit(ev.angleDelta())
        print("wheelEvent")

    def wheelChangeEvent(self, angleDelta):
		#rewrited by evermg42
        
        self.setCurrentIndex(self.currentIndex+(angleDelta.y()//120))
        print(angleDelta.y()//120)
        print(self.currentIndex+(angleDelta.y()//120))

    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        while ind >= len(self.filePaths): ind = ind - len(self.filePaths)
        while ind < 0: ind = ind + len(self.filePaths)
        self.curFilePath = self.filePaths[ind]
        self.currentIndex = ind
        self.show2DImage(self.curFilePath)
        print("setIndex")