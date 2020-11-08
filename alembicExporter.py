'''
-----------------------------------------------
alembicExporter is a tool to automatize alembic 
exports for BWater pipeline on demand requests.

Autor: AlbertoGZ
Email: albertogzonline@gmail.com
-----------------------------------------------
'''

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import shiboken2

import os
import platform
import subprocess



''' 
-----------------------------------
            VARIABLES
-----------------------------------
'''
### GENERAL VARS
version = '0.1.0'
winWidth = 350
winHeight = 250
red = '#872323'
green = '#207527'

### BWATER VARS
exportDir = '04_FILES'
mayaExt = '.ma'

### MAYA VARS
# Get frame start and frame end from timeline
fStart = cmds.playbackOptions(q=True, animationStartTime=True)
fEnd = cmds.playbackOptions(q=True, animationEndTime=True)
# Get scene path
mayaScenePathFull = cmds.file(q=True, sn=True, shortName=False)
mayaScenePathStrip = str('/'.join(mayaScenePathFull.split("/")[0:8]) + '/' + exportDir + '/')



def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class alembicExporter(QtWidgets.QMainWindow):

    def __init__(self, parent=getMainWindow()):
        super(alembicExporter, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        ''' 
        -----------------------------------
                    UI WINDOW
        -----------------------------------
        '''
        self.setObjectName('alembicExporterUI')
        self.setWindowTitle('Alembic Exporter' + ' ' + 'v' + version)
        

        ''' 
        -----------------------------------
                    UI LAYOUT
        -----------------------------------
        '''
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating vertical layouts for each column
        self.col1 = QtWidgets.QVBoxLayout()
        self.col2 = QtWidgets.QVBoxLayout()
        self.col3 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 1)
        columns.addLayout(self.col2, 1)
        columns.addLayout(self.col3, 3)
        
        layout1A = QtWidgets.QVBoxLayout()
        layout1B = QtWidgets.QGridLayout()
        layout1C = QtWidgets.QVBoxLayout()
        layout2A = QtWidgets.QVBoxLayout()
        layout3A = QtWidgets.QVBoxLayout()

        self.col1.addLayout(layout1A)
        self.col1.addLayout(layout1B)
        self.col1.addLayout(layout1C)
        self.col2.addLayout(layout2A)
        self.col3.addLayout(layout3A)

        
        ''' 
        -----------------------------------
                    UI ELEMENTS
        -----------------------------------
        '''

        # FilterBox inpqut for objects list
        self.itemsFilter = QtWidgets.QLineEdit('', self)
        self.itemsRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.itemsValidator = QtGui.QRegExpValidator(self.itemsRegex)
        self.itemsFilter.setValidator(self.itemsValidator)
        self.itemsFilter.textChanged.connect(self.objectFilter)

        # List of objects
        self.itemsList = QtWidgets.QListWidget(self)
        self.itemsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.itemsList.setMinimumWidth(170)
        self.itemsList.itemClicked.connect(self.objectSel)

        # Button for ADD items to list
        self.addItemsBtn = QtWidgets.QPushButton('Add selected items')
        self.addItemsBtn.setEnabled(True)
        self.addItemsBtn.setMinimumWidth(100)
        self.addItemsBtn.clicked.connect(self.addSelItems)

        # Button for CLEAR items list
        self.clearItemsBtn = QtWidgets.QPushButton('Clear list')
        self.clearItemsBtn.setEnabled(True)
        self.clearItemsBtn.setMinimumWidth(100)
        self.clearItemsBtn.clicked.connect(self.clearItems)

        # Subdiv parameters
        self.subdivCheck = QtWidgets.QCheckBox('Subdiv', self)
        self.subdivCheck.setChecked(True)
        self.subdivCheck.clicked.connect(self.checkboxControls)
        self.subdivIterations = QtWidgets.QSpinBox(self)
        self.subdivIterations.setValue(2)
        
        # Frame range controls
        self.timelineStart = QtWidgets.QCheckBox('Timeline start', self)
        self.timelineStart.clicked.connect(self.fstartControls)
        self.timelineStart.setChecked(True)
        self.fstart = QtWidgets.QSpinBox(self)
        self.fstart.setEnabled(False)
        self.fstart.setRange(0,9999)
        self.fstart.setValue(fStart)
        
        self.timelineEnd = QtWidgets.QCheckBox('Timeline end', self)
        self.timelineEnd.setChecked(True)
        self.timelineEnd.clicked.connect(self.fendControls)
        self.fend = QtWidgets.QSpinBox(self)
        self.fend.setEnabled(False)
        self.fend.setRange(0,9999)
        self.fend.setValue(fEnd)

        # Name for alembic file and group
        self.filenameBox = QtWidgets.QLineEdit(self)
        self.filenameBox.setText('AlembicFilename')
        self.filenameBox.textChanged.connect(self.filename)

        # Button to get name from selected item
        self.getAbcNameBtn = QtWidgets.QPushButton('Get name from selection')
        self.getAbcNameBtn.clicked.connect(self.getAbcName)

        # Button for open export FOLDER
        self.exportFolderBtn = QtWidgets.QPushButton('Open export folder')
        self.exportFolderBtn.setToolTip('Export folder: ' + mayaScenePathStrip + str(self.filenameBox.text()) + '.abc' )
        self.exportFolderBtn.clicked.connect(self.openFolder)

        # Button for EXPORT
        self.exportBtn = QtWidgets.QPushButton('Export')
        self.exportBtn.setEnabled(True)
        self.exportBtn.setStyleSheet('background-color: #566b76')
        self.exportBtn.clicked.connect(self.export)

        # Check for open viewer to show object(s)
        self.objectViewCheckbox = QtWidgets.QCheckBox('Object viewer')
        self.objectViewCheckbox.setEnabled(True)
        self.objectViewCheckbox.clicked.connect(self.showViewer)

        # Add status bar widget
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.messageChanged.connect(self.statusChanged)

        ### MAYA embedding modelEditor widget in Pyside layout
        self.paneLayoutName = cmds.paneLayout()
        global modelEditorName
        global viewer
        
        self.createCam()

        #objectViewerCam = 'objectViewerCam1'
        modelEditorName = 'modelEditor#'
        viewer = cmds.modelEditor(modelEditorName, cam=objectViewerCam, hud=False, grid=False, da='smoothShaded', wos=True, smoothWireframe=True, sel=False)
        self.ptr = omui.MQtUtil.findControl(self.paneLayoutName)            
        self.objectViewer = shiboken2.wrapInstance(long(self.ptr), QtWidgets.QWidget)
        self.objectViewer.setVisible(False)

        

        ### Add elements to layout
        layout1A.addWidget(self.addItemsBtn)
        layout1A.addWidget(self.clearItemsBtn)
        
        layout1B.addWidget(self.subdivCheck)
        layout1B.addWidget(self.subdivIterations, 0,1)
        layout1B.addWidget(self.timelineStart)
        layout1B.addWidget(self.fstart, 1,1)
        layout1B.addWidget(self.timelineEnd)
        layout1B.addWidget(self.fend, 2,1)
        
        layout1C.addWidget(self.getAbcNameBtn)
        layout1C.addWidget(self.filenameBox)
        layout1C.addWidget(self.exportFolderBtn)
        layout1C.addWidget(self.exportBtn)
        
        layout2A.addWidget(self.itemsFilter)
        layout2A.addWidget(self.itemsList)
        layout2A.addWidget(self.objectViewCheckbox)
        
        layout3A.addWidget(self.objectViewer)
        
        self.resize(winWidth, winHeight)
        #self.statusBar.showMessage('Export folder: ' + mayaScenePathStrip + str(self.filenameBox.text()))


        
    ''' 
    -----------------------------------
                FUNCTIONS
    -----------------------------------
    '''

    ### Get Alembic filename from selected item
    def getAbcName(self):
        abcName = cmds.ls(sl=True)

        if not abcName:
            self.filenameBox.setText('AlembicFilename')
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('None selected. Setted default name', 4000) 
        
        elif len(abcName) > 1:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('You must select one item only', 4000)
        
        else:
            self.filenameBox.setText(str(abcName[0]))
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Setted name from selected item', 4000)
        return

    ### Alembic filename
    def filename(self):
        self.exportFolderBtn.setToolTip('Export folder: ' + mayaScenePathStrip + str(self.filenameBox.text()) + '.abc' )
        return

    ### Open export folder
    def openFolder(self):
        if platform.system() == "Windows":
            os.startfile(mayaScenePathStrip)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", mayaScenePathStrip])
        else:
            subprocess.Popen(["xdg-open", mayaScenePathStrip])
        return

    ### Subdiv checkbox controls
    def checkboxControls(self):
        if self.subdivCheck.isChecked():
            self.subdivIterations.setEnabled(True)
        else:
            self.subdivIterations.setEnabled(False)
    
    ### Frame range controls
    def fstartControls(self):
        if self.timelineStart.isChecked():
            self.fstart.setValue(fStart)
            self.fstart.setEnabled(False)
        else:
            self.fstart.setValue(1)
            self.fstart.setEnabled(True)
        return
    
    def fendControls(self):
        if self.timelineEnd.isChecked():
            self.fend.setValue(fEnd)
            self.fend.setEnabled(False)
        else:
            self.fend.setValue(1)
            self.fend.setEnabled(True)
        return

    ### Add selected items to list
    def addSelItems(self):
        global items
        if cmds.ls(sl=False):
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('You must select almost one visible mesh object', 4000)
        
        if cmds.ls(sl=True):
            items = cmds.ls(selection=True, visible=True)
            #shapes = cmds.listRelatives(items, shapes=True, type='mesh')
            self.itemsList.clear()
            self.itemsList.addItems(items)
            cmds.select(clear=True)
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Added items: ' + str(items[0]), 4000)
        return

    ### Clear list
    def clearItems(self):
        if self.itemsList.count() <= 0:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('Nothing done! List already empty', 4000)
        else:
            self.itemsList.clear()
            cmds.select(clear=True)
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Clear list successfully!', 4000)
        return
    
    ### Filter by typing for items list
    def objectFilter(self):
        textFilter = str(self.itemsFilter.text()).lower()
        if not textFilter:
            for row in range(self.itemsList.count()):
                self.itemsList.setRowHidden(row, False)
        else:
            for row in range(self.itemsList.count()):
                if textFilter in str(self.itemsList.item(row).text()).lower():
                    self.itemsList.setRowHidden(row, False)
                else:
                    self.itemsList.setRowHidden(row, True)
    
    ### Subdivision control
    def applySubdiv(self): 
        return

    ### EXPORT ACTION
    def export(self):
        abcFileName = str(self.filenameBox.text())
        exportPath = mayaScenePathStrip + abcFileName + '.abc'

        if self.itemsList.count() <= 0:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('List empty. You must add items before', 4000)
            #self.statusBar.showMessage(exportPath)
        else:
            # Select items in list
            #items = []
            #for i in range(self.itemsList.count()):
            #    items.append(str(self.itemsList.item(i).text()))
            #cmds.select(items)
            
            # Apply subdivision to mesh
            iterations = self.subdivIterations.value()
            if self.subdivCheck.isChecked():
                for item in items:
                    cmds.polySmooth(item, dv=iterations)

            frameStart = self.fstart.value()
            frameEnd = self.fend.value()

            # OPTION 1 
            # Build a list with prefix '-root' for each item in the list
            listExport = []
            for item in items:
                listExport.append('-root ' + item)
            itemsToExport = " ".join(map(str, listExport))

            # OPTION 2
            # Duplicate selected items to avoid "Read-only parents lock state" 
            # allowing make the temp group as root for .abc export
            cmds.duplicate(items)
            tempSelection = cmds.ls(selection=True)
            tempGroup = cmds.group(tempSelection, n=abcFileName)

            # OPTION 1 command
            command1 = '-frameRange ' + str(frameStart) + ' ' + str(frameEnd) + ' -uvWrite -worldSpace ' + itemsToExport + ' -file ' + str(exportPath)
            
            # OPTION 2 command
            command2 = '-frameRange ' + str(frameStart) + ' ' + str(frameEnd) + ' -uvWrite -worldSpace ' + '-root ' + str(tempGroup) + ' -file ' + str(exportPath)

            cmds.AbcExport ( j = command2 )
            
            cmds.delete(tempGroup)

            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Alembic exported successfully!', 4000)
        return

    ### Create cam for viewer
    def createCam(self):
            global objectViewerCam
            objectViewerCam = 'objectViewerCam1'
            cmds.camera(name=objectViewerCam)
            cmds.xform(t=(28.000, 21.000, 28.000), ro=(-27.938, 45.0, -0.0) )
            cmds.hide(objectViewerCam)
    
    ### Show viewer in the GUI
    def showViewer(self):
        if self.objectViewCheckbox.isChecked():
            
            self.objectViewer.setVisible(True)
            winWidth = 600
            self.resize(winWidth, winHeight)

            if self.itemsList.currentItem():
                #cmds.showHidden(grpTemp+'*')
                cmds.select(objs)
                cmds.isolateSelect(viewer, s=False)
                cmds.isolateSelect(viewer, s=True)
                cmds.viewFit(objectViewerCam)
                #cmds.refresh()
        else:
            self.hideViewer()

    ### Hide viewer in the GUI
    def hideViewer(self):
            self.objectViewer.setVisible(False)
            winWidth = 350
            self.resize(winWidth, winHeight)

    ### Actions for item(s) selected in list
    def objectSel(self, item):
        self.objectViewCheckbox.setEnabled(True)
        global objs
        items = self.itemsList.selectedItems()
        objs = []
        for i in list(items):
            objs.append(i.text())
        self.statusBar.showMessage(str(objs), 4000)

        #cmds.showHidden(grpTemp+'*')
        cmds.select(objs)
        cmds.isolateSelect(viewer, s=False)
        cmds.isolateSelect(viewer, s=True)
        cmds.viewFit(objectViewerCam)
        #cmds.refresh()

    ### Restore status bar
    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      
    ### Remove temporary group
    def objectUnload(self):
        self.itemsList.clear()
        self.addItemsBtn.setEnabled(True)
        self.clearItemsBtn.setEnabled(False)
        self.objectViewCheckbox.setEnabled(False)
        
        if self.objectViewCheckbox.isChecked():
            self.hideViewer()
            self.objectViewCheckbox.setChecked(False)

        if cmds.objExists('___tmp___*'):
            cmds.delete('___tmp___*')

    ### Remove temporary elements created in scene
    def cleanScene(self):
        node1 = '*_hyperShadePrimaryNodeEditorSavedTabsInfo*'
        node2 = '*ConfigurationScriptNode*'
        if cmds.objExists(node1):
            cmds.delete(node1)
        if cmds.objExists(node2):
            cmds.delete(node2)
        cmds.delete(objectViewerCam)        
        cmds.deleteUI(modelEditorName+'*')
        mel.eval('MLdeleteUnused;')
        
    ### Prevent groupname as prefix of any node
    def removePrefix(self):
        groupname = cmds.ls(asset + '_*')
        for gn in groupname:
            new = gn.split(str(asset + '_model_v01_'))
            cmds.rename(gn, new[1])


    def closeEvent(self, event):
        self.objectUnload()
        self.cleanScene()
        #self.removePrefix()



''' 
-----------------------------------
            WAKE UP WINDOW
-----------------------------------
'''
if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = alembicExporter(parent=getMainWindow())
  win.show()
  win.raise_()