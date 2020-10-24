'''
-----------------------------------------
alembicExporter is a toolset to automatize 
alembic exports for BWater pipeline.

Autor: AlbertoGZ
Email: albertogzonline@gmail.com
-----------------------------------------
'''

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import shiboken2

import os



# GENERAL VARS
version = '0.1.0'
winWidth = 300
winHeight = 300
red = '#872323'
green = '#207527'

# BWATER VARS 
exportDir = '04_FILES'
mayaExt = '.ma'

# VARS
fStart = cmds.playbackOptions(q=True, animationStartTime=True)
fEnd = cmds.playbackOptions(q=True, animationEndTime=True)



def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class alembicExporter(QtWidgets.QMainWindow):

    def __init__(self, parent=getMainWindow()):
        super(alembicExporter, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        # Creates object, Title Name and Adds a QtWidget as our central widget/Main Layout
        self.setObjectName('alembicExporterUI')
        self.setWindowTitle('Alembic Exporter' + ' ' + 'v' + version)
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)
        
        # Adding a Horizontal layout to divide the UI in columns
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating N vertical layout
        self.col1 = QtWidgets.QVBoxLayout()
        self.col2 = QtWidgets.QVBoxLayout()
        self.col3 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 1)
        columns.addLayout(self.col2, 1)
        columns.addLayout(self.col3, 3)
        
        layout1 = QtWidgets.QVBoxLayout()
        layout1A = QtWidgets.QGridLayout()
        layout1B = QtWidgets.QVBoxLayout()
        layout2B = QtWidgets.QVBoxLayout()
        layout3 = QtWidgets.QVBoxLayout()

        self.col1.addLayout(layout1)
        self.col1.addLayout(layout1A)
        self.col1.addLayout(layout1B)
        self.col2.addLayout(layout2B)
        self.col3.addLayout(layout3)




        #### UI ELEMENTS
        #
        # FilterBox inpqut for objects list
        self.objectsFilterBox = QtWidgets.QLineEdit('', self)
        self.objectRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.objectValidator = QtGui.QRegExpValidator(self.objectRegex)
        self.objectsFilterBox.setValidator(self.objectValidator)
        self.objectsFilterBox.textChanged.connect(self.objectFilter)

        # List of objects
        self.objectsQList = QtWidgets.QListWidget(self)
        self.objectsQList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.objectsQList.setMinimumWidth(170)
        self.objectsQList.itemClicked.connect(self.objectSel)

        # Button for ADD items to list
        self.addItemsBtn = QtWidgets.QPushButton('Add Items')
        self.addItemsBtn.setEnabled(True)
        self.addItemsBtn.setMinimumWidth(100)
        self.addItemsBtn.clicked.connect(self.addSelItems)

        # Button for CLEAR objects list
        self.clearItemsBtn = QtWidgets.QPushButton('Clear')
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

        # Filename for export and group
        self.filenameBox = QtWidgets.QLineEdit('Filename.abc', self)

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
        #
        layout1.addWidget(self.addItemsBtn)
        layout1.addWidget(self.clearItemsBtn)
        
        layout1A.addWidget(self.subdivCheck)
        layout1A.addWidget(self.subdivIterations, 0,1)
        layout1A.addWidget(self.timelineStart)
        layout1A.addWidget(self.fstart, 1,1)
        layout1A.addWidget(self.timelineEnd)
        layout1A.addWidget(self.fend, 2,1)
        
        layout1B.addWidget(self.filenameBox)
        layout1B.addWidget(self.exportBtn)
        
        layout2B.addWidget(self.objectsFilterBox)
        layout2B.addWidget(self.objectsQList)
        layout2B.addWidget(self.objectViewCheckbox)
        
        layout3.addWidget(self.objectViewer)
        
        self.resize(winWidth, winHeight)



    
    ### FUNCTIONS
    #
    # Subdiv checkbox controls
    def checkboxControls(self):
        if self.subdivCheck.isChecked():
            self.subdivIterations.setEnabled(True)
        else:
            self.subdivIterations.setEnabled(False)
    

    # Frame range controls
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

    ### Add select items to list
    def addSelItems(self):
        if cmds.ls(sl=False):
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('You must select almost one visible mesh object', 4000)
        
        if cmds.ls(sl=True):
            items = cmds.ls(selection=True, visible=True)
            shapes = cmds.listRelatives(items, shapes=True, type='mesh')
            self.objectsQList.clear()
            self.objectsQList.addItems(shapes)
            cmds.select(clear=True)
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Added items: ' + str(items), 4000)
        return

    ### Clear list
    def clearItems(self):
        if self.objectsQList.count() <= 0:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('Nothing done! List already empty', 4000)
        else:
            self.objectsQList.clear()
            cmds.select(clear=True)
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Clear list successfully!', 4000)
        return
    
    ### Filter by typing for OBJECTS list
    def objectFilter(self):
        textFilter = str(self.objectsFilterBox.text()).lower()
        if not textFilter:
            for row in range(self.objectsQList.count()):
                self.objectsQList.setRowHidden(row, False)
        else:
            for row in range(self.objectsQList.count()):
                if textFilter in str(self.objectsQList.item(row).text()).lower():
                    self.objectsQList.setRowHidden(row, False)
                else:
                    self.objectsQList.setRowHidden(row, True)

    

    ### EXPORT ACTION
    def export(self):
        if self.objectsQList.count() <= 0:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('List empty. You must add items before', 4000)
        else:

            # Select items in list
            items = []
            for i in range(self.objectsQList.count()):
                items.append(str(self.objectsQList.item(i).text()))
            cmds.select(items)
            
            # Get scene path
            fullScenePath = cmds.file(q=True, sn=True, shortName=False)
            mayaSceneName = cmds.file(q=True, sn=True, shortName=True)
            mayaScenePath = fullScenePath.replace(mayaSceneName, '')
            mayaScenePathClean = mayaScenePath.replace('v01', '04_FILES')

            start = 1
            end = 1
            abcFileName = str(self.filenameBox.text()).lower()
            exportPath = mayaScenePathClean + abcFileName

            # Apply subdivision to mesh
            iterations = self.subdivIterations.value()
            if self.subdivCheck.isChecked():
                for item in items:
                    cmds.polySmooth(item, dv=iterations)

            group = cmds.group(items, n=abcFileName)

            command = '-frameRange ' + str(start) + ' ' + str(end) + ' -uvWrite -worldSpace ' + '-root ' + str(group) + ' -file ' + str(exportPath)
            cmds.AbcExport ( j = command )

            cmds.ungroup(group)

            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Alembic exported successfully!', 4000)

        return







    '''
    ### Actions for export button
    def export_tmp(self):
        # Check if any objects is selected; then import them
        if self.objectsQList.currentItem():
            try:
                mel.eval('MLdeleteUnused;')
                cmds.select(objs)
                cmds.group(n=asset+'sel1', w=True)
                self.removePrefix()
                self.cleanScene()
                self.objectsQList.clear()
                self.objectUnload()
                self.statusBar.setStyleSheet('background-color:' + green)
                self.statusBar.showMessage('Selected objects from model imported successfully!', 4000)
            except:
                self.statusBar.setStyleSheet('background-color:' + red)
                self.statusBar.showMessage('Object(s) with same name already in scene', 4000)
        # If no object select then import all model
        elif self.assetQList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=str(asset+'tmp1'))
            self.removePrefix()
            self.cleanScene()
            self.statusBar.setStyleSheet('background-color:' + green)
            self.statusBar.showMessage('Model imported successfully!', 4000)
        else:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('No scene selected', 4000)
    '''

    def hideViewer(self):
        self.objectViewer.setVisible(False)
        winWidth = 300
        self.resize(winWidth, winHeight)


    def createCam(self):
            global objectViewerCam
            objectViewerCam = 'objectViewerCam1'
            cmds.camera(name=objectViewerCam)
            cmds.xform(t=(28.000, 21.000, 28.000), ro=(-27.938, 45.0, -0.0) )
            cmds.hide(objectViewerCam)


    def showViewer(self):
        if self.objectViewCheckbox.isChecked():
            
            self.objectViewer.setVisible(True)
            winWidth = 550
            self.resize(winWidth, winHeight)

            if self.objectsQList.currentItem():
                #cmds.showHidden(grpTemp+'*')
                cmds.select(objs)
                cmds.isolateSelect(viewer, s=False)
                cmds.isolateSelect(viewer, s=True)
                cmds.viewFit(objectViewerCam)
                #cmds.refresh()
        else:
            self.hideViewer()



    
    ### Select objects in objects list
    def objectSel(self, item):
        self.objectViewCheckbox.setEnabled(True)
        global objs
        items = self.objectsQList.selectedItems()
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
        
    '''
    ### Actions for list objects button
    def objectLoad(self):
        global grpTemp
        grpTemp = '___tmp___'
        
        if self.assetQList.currentItem():
            mel.eval('MLdeleteUnused;')
            cmds.file(sceneFullPath, i=True, gr=True, dns=False, gn=grpTemp, ifr=True)
            cmds.select(grpTemp+'*')
            cmds.hide(grpTemp+'*')
            #mel.eval('setAttr ___tmp___.hiddenInOutliner true;AEdagNodeCommonRefreshOutliners();')
            objectList = cmds.listRelatives(grpTemp, s=False)
            objectList.sort()
            self.objectsQList.addItems(objectList)
            self.objectViewCheckbox.setEnabled(True)
        else:
            self.statusBar.setStyleSheet('background-color:' + red)
            self.statusBar.showMessage('No object selected', 4000)
        
        self.addItemsBtn.setEnabled(False)
        self.clearItemsBtn.setEnabled(True)
    
    '''

    def restoreLabels(self):
        self.sceneLabel.setText('Scene: ')
        self.sizeLabel.setText('Size: ')
        self.dateLabel.setText('Date: ')
    

    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      

    def objectUnload(self):
        self.objectsQList.clear()
        self.addItemsBtn.setEnabled(True)
        self.clearItemsBtn.setEnabled(False)
        self.objectViewCheckbox.setEnabled(False)
        
        if self.objectViewCheckbox.isChecked():
            self.hideViewer()
            self.objectViewCheckbox.setChecked(False)

        if cmds.objExists('___tmp___*'):
            cmds.delete('___tmp___*')

    
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
        
    
    # Prevent groupname as prefix of any node
    def removePrefix(self):
        groupname = cmds.ls(asset + '_*')
        for gn in groupname:
            new = gn.split(str(asset + '_model_v01_'))
            cmds.rename(gn, new[1])


    def closeEvent(self, event):
        self.objectUnload()
        self.cleanScene()
        #self.removePrefix()



if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = alembicExporter(parent=getMainWindow())
  win.show()
  win.raise_()
