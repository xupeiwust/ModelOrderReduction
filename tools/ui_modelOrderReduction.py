# -*- coding: utf-8 -*-
###############################################################################
#            Model Order Reduction plugin for SOFA                            #
#                         version 1.0                                         #
#                       Copyright © Inria                                     #
#                       All rights reserved                                   #
#                       2018                                                  #
#                                                                             #
# This software is under the GNU General Public License v2 (GPLv2)            #
#            https://www.gnu.org/licenses/licenses.en.html                    #
#                                                                             #
#                                                                             #
#                                                                             #
# Authors: Olivier Goury, Felix Vanneste                                      #
#                                                                             #
# Contact information: https://project.inria.fr/modelorderreduction/contact   #
###############################################################################
'''
    README

    to use this python script you need :

        - bla

        - & blabla
'''
#######################################################################
####################       IMPORT           ###########################
import os
import sys
import glob
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

# import ui_design  # This file holds our MainWindow and all design related things
import ui_design


import yaml
from collections import OrderedDict
from pydoc import locate


from launcher import *

# MOR IMPORT
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../python') # TO CHANGE

from mor.script import utility
from mor.script import ReduceModel
from mor.script import ObjToAnimate

from mor.gui import MyCompleter
from mor.gui import TreeModel
from mor.gui import GenericDialogForm
from mor.gui import utility as u

#######################################################################

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# var_float = "[\d{0,10}|\\.|\d{0,10}]"
var_int = '\d{1,10}'
var_float ="[0-9]{,10}.?[0-9]{,10}"
var_semantic = "[a-z|A-Z|\d|\\-|\\_]{1,20}" # string with max 20 char & min 1 with char from a to z/A to Z/-/_


existingAnimation = OrderedDict()
existingAnimation['defaultShaking'] = { 'incr':(var_float,locate('float')),
                                        'incrPeriod':(var_float,locate('float')),
                                        'rangeOfAction':(var_float,locate('float'))}
existingAnimation['shakingSofia'] = {'incr':var_float,
                                     'incrPeriod':var_float,
                                     'rangeOfAction':var_float}
existingAnimation['test'] = {'incr':var_float,
                             'incrPeriod':var_float,
                             'rangeOfAction':var_float}

green = '#c4df9b' 
yellow = '#fff79a'
red = '#f6989d'

col_path = 2
col_parameters = 1
col_animation = 0

class ExampleApp(QtGui.QMainWindow, ui_design.Ui_MainWindow):
    def __init__(self):

        # Init of inherited class 
        super(self.__class__, self).__init__()

        # Create each Object & Widget of the interface as an Derived Attribute of QMainWindow
        # to be able to display them
        self.setupUi(self)

        # Create some QRegExp that we will be used to create Validator
        # allowing us to block certain entry for the user
        var_semantic = "[a-z|A-Z|\d|\\-|\\_]{1,20}" # string with max 20 char & min 1 with char from a to z/A to Z/-/_
        var_entry = var_semantic+"\\="+var_semantic # string of 2 var_semantic separated by '='
        var_all = "[^\\*]"
        defaultShaking_mask = "(incr\\="+var_float+"){1}(incrPeriod\\="+var_float+"){1}(rangeOfAction\\="+var_float+"){1}"

        self.exp_var = QtCore.QRegExp("^("+var_semantic+")$")
        self.exp_path = QtCore.QRegExp("^("+var_semantic+"){1}(\\/"+var_semantic+")*$")
        self.exp_all = QtCore.QRegExp("^("+var_all+")+$")
        # self.exp_var_entry = QtCore.QRegExp("^("+var_entry_spe+"\\,)*("+var_entry_spe+")$")       

        # Add Signals
        # self.lineEdit_tolModes.textChanged.emit(self.lineEdit_tolModes.text())
        # self.lineEdit_tolGIE.textChanged.emit(self.lineEdit_tolGIE.text())
        # self.lineEdit_moduleName.textChanged.emit(self.lineEdit_moduleName.text())
        # self.lineEdit_NodeToReduce.textChanged.emit(self.lineEdit_NodeToReduce.text())
        # self.lineEdit_scene.textChanged.emit(self.lineEdit_scene.text())
        # self.lineEdit_output.textChanged.emit(self.lineEdit_output.text())
        
        # QLineEdit Action
        self.lineEdit_tolModes.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_tolGIE.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_moduleName.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_NodeToReduce.textChanged.connect(lambda: u.check_state(self.sender()))

        self.lineEdit_scene.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_scene.textChanged.connect(lambda: self.importScene(str(self.lineEdit_scene.text()) ) )
        self.lineEdit_output.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_output.textChanged.connect(self.checkPhases)

        # QTable Action
        self.tableWidget_animationParam.cellClicked.connect(self.showAnimationDialog)
        self.animationDialog = []

        # QPushButton Action
        self.btn_scene.clicked.connect(lambda: u.openFileName('Select the SOFA scene you want to reduce',display=self.lineEdit_scene))
        self.btn_output.clicked.connect(lambda: u.openDirName('Select the directory tha will contain all the results',display=self.lineEdit_output))
        self.btn_mesh.clicked.connect(lambda: u.openFilesNames('Select the meshes & visual of your scene',display=self.lineEdit_mesh))
        self.btn_addLine.clicked.connect(lambda: self.addLine(self.tableWidget_animationParam))
        self.btn_removeLine.clicked.connect(lambda: self.removeLine(self.tableWidget_animationParam,self.animationDialog))
        self.btn_launchReduction.clicked.connect(self.test) #self.execute)
        
        # QCheckBox Action
        # self.checkBox_mesh.stateChanged.connect(lambda: u.greyOut(self.checkBox_mesh,[self.lineEdit_mesh,self.btn_mesh]))
        # self.checkBox_executeAll.stateChanged.connect(lambda: self.executeAll(self.checkBox_executeAll,
        #                                                                     [   self.checkBox_phase1,
        #                                                                         self.checkBox_phase2,
        #                                                                         self.checkBox_phase3,
        #                                                                         self.checkBox_phase4],
        #                                                                     checked=False))
        
        # QAction Menu Action
        self.actionOpen.triggered.connect(lambda: self.open('Select Config File'))
        self.actionSave_as.triggered.connect(self.saveAs)
        self.actionSave.triggered.connect(self.save)
        self.actionReset.triggered.connect(self.reset)

        # Add frame_layout Action
        self.listLayout = [self.layout_path,self.layout_aniamationParam,self.layout_reductionParam,
                            self.layout_advancedParam,self.layout_execution]

        for layout in self.listLayout:
            QtCore.QObject.connect(layout._title_frame, QtCore.SIGNAL('clicked()'), self.resizeHeight)

        # Add Validator
        self.lineEdit_tolModes.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_tolGIE.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_moduleName.setValidator(QtGui.QRegExpValidator(self.exp_var))
        self.lineEdit_NodeToReduce.setValidator(QtGui.QRegExpValidator(self.exp_path))
        self.lineEdit_scene.setValidator(QtGui.QRegExpValidator(self.exp_all))
        self.lineEdit_output.setValidator(QtGui.QRegExpValidator(self.exp_all))

        # Set the different grpBoxes of our application
        # It will ease the way we iterate on them
        self.grpBoxes = [ self.grpBox_Path,
                          self.grpBox_AdvancedParam,
                          self.grpBox_ReductionParam,
                          self.grpBox_AnimationParam,
                          self.grpBox_Execution]

        # self.layouts = [self.layout_reductionParam,
        #                 self.layout_advancedParam,
        #                 self.layout_aniamationParam,
        #                 self.layout_execution]

        # Will be set to the current config we are working to avoid 
        # asking user each time is saving on which file he want to save it to
        self.saveFile = None

        # Dictionary containing a 'blank' configuration to be able to reset the application
        self.resetFileName = {
                'grpBox_Path':
                    {
                        'lineEdit_output': '',
                        'lineEdit_mesh': '',
                        'lineEdit_scene': '/home/felix/SOFA/plugin/ModelOrderReduction/tools/sofa_test_scene/diamondRobot.py',
                    },
                'grpBox_ReductionParam': 
                    {   'lineEdit_NodeToReduce': '',
                        'lineEdit_moduleName': 'myReducedModel',
                        'checkBox_AddTranslation': 'False'
                    },
                'grpBox_AdvancedParam': 
                    {   
                        'checkBox_addToLib': 'False', 
                        'lineEdit_tolModes': '0.001',
                        'lineEdit_tolGIE': '0.05',
                        'lineEdit_toKeep': ''
                    },
                'grpBox_AnimationParam':
                    {},
                'grpBox_Execution': 
                    {}
                }

       # 'checkBox_executeAll': 'False', 
       #                      'checkBox_phase2': 'False',
       #                      'checkBox_phase4': 'False',
       #                      'textEdit_preExecutionInfos': '',
       #                      'checkBox_phase3': 'False',
       #                      'checkBox_phase1': 'False'

        self.mandatoryFields = OrderedDict([
                                (self.lineEdit_scene,                self.label_scene),
                                (self.lineEdit_output,               self.label_output),
                                (self.lineEdit_NodeToReduce,         self.label_NodeToReduce),
                                (self.tableWidget_animationParam,    self.layout_aniamationParam),
                                (self.lineEdit_tolGIE,               self.label_tolGIE),
                                (self.lineEdit_tolModes,             self.label_tolModes)
                                ])


        self.phases = [self.phase1,self.phase2,self.phase3,self.phase4]
        self.phaseItem = []
        for phase in self.phases:
            self.phaseItem.append(self.addButton(phase))

        self.cfg = None

        self.reset(state=True)

    def test(self):
        newTxt = str(self.lineEdit_NodeToReduce.text())
        self.lineEdit_NodeToReduce.setText(newTxt+'/')

    def setPossiblePath(self):
        tmp = []
        for item in self.cfg['tree']:
            tmp.append(item)
            for obj in self.cfg['obj'][item]:
                tmp[-1] += '/' + obj

    def addButton(self,widget):

        # CheckBox
        checkBox = QtGui.QCheckBox()
        checkBox.setObjectName(_fromUtf8("checkBox"))
        checkBox.setFixedWidth(30)
        checkBox.setStyleSheet("border:0px")
        checkBox.setTristate(False)

        # Reset Button
        btn = QtGui.QPushButton(self.grpBox_Execution)
        btn.setObjectName(_fromUtf8("button"))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('icon.png'))
        btn.setIcon(icon)
        btn.setFixedWidth(30)
        btn.setStyleSheet("border:0px")
        btn.setDisabled(True)

        # Actions
        checkBox.stateChanged.connect(lambda: self.updatePhasesState((checkBox,btn)))
        btn.clicked.connect(lambda: u.greyOut(btn,[checkBox]))

        widget._title_frame._hlayout.addWidget(checkBox)
        widget._title_frame._hlayout.addWidget(btn)

        # checkBox.setParent(self.grpBox_Execution)
        # btn.setParent(self.grpBox_Execution)

        return (checkBox,btn)

    def updatePhasesState(self, items):
        checkBox , btn = items

        index = self.phaseItem.index(items)
        phase = self.phases[index]
        phase.blockSignals(True)

        if checkBox.isChecked() == True:
            # checkBox.setDisabled(False)

            for box,btn in self.phaseItem[:index]:
                box.setCheckState(True)
                box.setTristate(False)


        else:
            for box,btn in self.phaseItem[index:]:
                box.setCheckState(False)
                box.setTristate(False)
            for box,btn in self.phaseItem[index:]:
                box.setDisabled(False)
                box.setTristate(False)

        phase.blockSignals(False)

    def checkPhases(self):
        print("checkPhases")
        if str(self.lineEdit_output.text()) != '':
            print(self.lineEdit_output.text())
            path = self.lineEdit_output.text()
            phasesFile = [
                        ["/debug/debug_scene.py","/debug/stateFile.state"],
                        ["/data/modes.txt"],
                        ["/debug/HyperReducedFEMForceField_","/debug/elmts_"], #["/debug/step2_stateFile.state",
                        ["/data/RID_","/data/weight_","/data/conectivity_","/reduced_"] # ,"/mesh"
                    ]

            def check(file,item):
                checkBox , btn = item
                try:
                    f = open(file,'r')
                    if f:
                        print(file+" NOT EMPTY")
                        # item.setExpanded(True)
                        # print("isTristate ",checkBox.isTristate())

                        checkBox.setCheckState(True)
                        checkBox.setDisabled(True)
                        btn.setDisabled(False)
                        checkBox.setTristate(False)
                        # print("isTristate ",checkBox.isTristate())


                        # item.setText(1,"Done")
                    else:
                        print(file+" EMPTY")
                        # item.setExpanded(False)
                        checkBox.setCheckState(False)
                        checkBox.setDisabled(False)
                        # item.setText(1,"ToDo")
                        return

                except IOError as (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise

            def test(phase,item,globing=False):
                checkBox , btn = item
                for file in phase:
                    # print(item.text(0))
                    if globing:
                        files = glob.glob(str(path+file)+"*")
                        if files:
                            for file in files:
                                print(file)
                                check(file,item)
                        else:
                            print(path+file+" NONE")
                            # item.setExpanded(False)
                            checkBox.setCheckState(False)
                            checkBox.setDisabled(False)
                            # item.setText(1,"ToDo")

                            return False

                    else:
                        if os.path.exists(path+file):
                            check(path+file,item)
                        else:
                            print(path+file+" NONE")
                            # item.setExpanded(False)
                            checkBox.setCheckState(False)
                            checkBox.setDisabled(False)
                            # item.setText(1,"ToDo")
                            return False

            def checkExecution(phases,phaseItem,globing=False):
                for phase in phases :
                    item = phaseItem[phases.index(phase)]
                    state = test(phase,item,globing) 
                    if not state:
                        return

            checkExecution(phasesFile[:2],self.phaseItem[:2])
            checkExecution(phasesFile[2:],self.phaseItem[2:],globing=True)

    def resizeEvent(self, event):
        # print("EVENT")

        # height = 145
        # for layout in self.listLayout:
        #     # print(str(layout._title_frame._title.text())+" HEIGHT = "+str(layout.height())+' Collapse : '+str(layout._is_collasped))
        #     if layout._is_collasped:
        #         height += 30
        #     else:
        #         height += layout.height()
        #     # print(str(layout._title_frame._title.text())+" HEIGHT = "+str(layout.height())+" WIDTH = "+str(self.width())+' Collapse : '+str(layout._is_collasped))

        # if height > 600:
        #     height += 65
        # else:
        #     height += 20

        height = 600+65

        self.setMaximumSize(800,height)
        self.setMinimumSize(600, 320) #290)
        QtGui.QMainWindow.resizeEvent(self, event)

    def resizeHeight(self,offset=145):
        # print("resizeHeight ------------------>")

        height = offset
        for layout in self.listLayout:
            # print(str(layout._title_frame._title.text())+" HEIGHT = "+str(layout.height())+' Collapse : '+str(layout._is_collasped))
            if layout._is_collasped:
                if layout.height() > 30 :
                    layout.resize(layout.width(),30)
                height += 30
            else:
                height += layout.height()
            # print(str(layout._title_frame._title.text())+" HEIGHT = "+str(layout.height())+" WIDTH = "+str(self.width())+' Collapse : '+str(layout._is_collasped))

        self.scrollArea.resize(self.scrollArea.width(),height)
        if height > 600:
            self.resize(self.width(),600+65)
        else:
            self.resize(self.width(),height+20)

    def setEnabled(self,state=True):

        for layout in self.listLayout[1:]:
            if not state and layout.collapsed:
                layout.toggleCollapsed()
            layout.setEnabled(state)

        self.btn_launchReduction.setEnabled(state)

    def showAnimationDialog(self, row, column):
        if column == col_parameters :
            dialog = self.animationDialog[row]
            if dialog.exec_():
                u.setAnimationParamStr(self.tableWidget_animationParam.item(row,column),dialog.currentValues.iteritems())
                u.setCellColor(self.tableWidget_animationParam,dialog,row,column)

    def reset(self,state=False):
        '''
        Reset (with ctrl+R) application to a 'blank' state
        '''
        for page in self.grpBoxes:
            pageName = str(page.objectName())
            self.loadPage(page,self.resetFileName[pageName])
        self.saveFile = None
        self.setEnabled(state)

    def save(self):
        '''
        Save (with ctrl+S) application current state as an YAML file
        '''
        if not self.saveFile:
            self.saveAs()

        data = {}
        for page in self.grpBoxes:
            if str(page.objectName()) == 'grpBox_Execution':
                data[str(page.objectName())] = {}
                for phase in self.phases:
                    self.buildDic(phase._title_frame,data[str(page.objectName())],str(phase.objectName()))
            else:
                self.buildDic(page,data)

        with open(self.saveFile, 'w') as ymlfile:
            yaml.dump(data,ymlfile, default_flow_style=False)

    def saveAs(self):
        '''
        Save As, ask user .yml file to save & correct name if need be 
        '''
        self.saveFile = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Configuration',filter="yaml file *.yml"))

        if self.saveFile.find('.') == -1 :
            self.saveFile = self.saveFile+'.yml'
        if self.saveFile.split('.')[-1] != 'yml':
            self.saveFile = self.saveFile+'.yml'

        self.save()

    def open(self,hdialog,filter='(*.yml)'):
        '''
        Open (with ctrl+O) ask user to choose a file then load it
        '''
        name = u.openFileName(hdialog,filter)
        self.load(name)
        self.saveFile = name

    def importScene(self,filePath):
        print('importScene : '+str(self.lineEdit_scene.text()))
        if str(self.lineEdit_scene.text()) != '':
            numiterations = 1
            filename = "importScene.py"
            path = os.path.dirname(os.path.abspath(__file__))+'/'
            filesandtemplates = [ (open(path+filename).read(), filename)]

            listSofaScene = [
                                {"ORIGINALSCENE": filePath,
                                 "nbIterations":numiterations}
                            ]

            results = startSofa(listSofaScene, filesandtemplates, launcher=SerialLauncher())

            with open(results[0]["directory"]+'/graphScene.yml', 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)
            
            model = TreeModel(self.cfg)
            # print(model.rootItem.itemData)

            completer = MyCompleter(self.lineEdit_NodeToReduce)
            completer.setModel(model)
            completer.setCompletionColumn(0)
            completer.setCompletionRole(QtCore.Qt.DisplayRole)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            # print(model.dumpObjectTree())
            self.lineEdit_NodeToReduce.setCompleter(completer)
            self.lineEdit_NodeToReduce.clicked.connect(completer.complete)
            self.lineEdit_NodeToReduce.focused.connect(completer.complete)
            completer.activated.connect(lambda: self.display(completer,self.lineEdit_NodeToReduce))

            # self.lineEdit_NodeToReduce.selectionChanged.connect(completer.complete)
            self.setEnabled()

    def display(self,completer,lineEdit):
        # lineEdit.blockSignals(True)
        print('display')
        if completer.asChild:
            completer.complete()
            # print("Previous "+str(lineEdit.text()))
            # newTxt = str(lineEdit.text())
            # lineEdit.setText(newTxt+'/')
            # print("New "+str(lineEdit.text()))
        # lineEdit.blockSignals(False)

    def load(self,name):
        '''
        Load will, from a cfg file, set all the values of the datafields application
        It will iterate on each 'page' our application contains & load it 
        '''
        with open(name, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        for page in self.grpBoxes:
            # print('PAGE : '+str(page.objectName()))
            pageName = str(page.objectName())
            self.loadPage(page,cfg[pageName])

    def loadPage(self,page,cfg):
        '''
        LoadPage will set all coresponding widget value
        For each key in our cfg file (which are the obj names) it will search the coresponding widget
        '''
        for child in page.children():
            objectName = str(child.objectName())
            # print('CHILD : '+objectName)
            if objectName in cfg:
                if cfg[objectName]:
                    if type(child).__name__ == 'FrameLayout':
                        index = self.phases.index(child)
                        if cfg[objectName]['checkBox'] == 'True':
                            self.phaseItem[index][0].setCheckState(True)
                        elif cfg[objectName]['checkBox'] == 'False':
                            self.phaseItem[index][0].setCheckState(False)
                    if type(child).__name__ == 'QLineEdit':
                        # print('----------------->'+objectName)
                        child.setText(cfg[objectName])
                    if type(child).__name__ == 'QTextEdit':
                        # print('----------------->'+objectName)
                        child.setText(cfg[objectName])
                    if type(child).__name__ == 'QCheckBox':
                        # print('----------------->'+objectName)
                        if cfg[objectName] == 'True':
                            child.setCheckState(True)
                        elif cfg[objectName] == 'False':
                            child.setCheckState(False)
                    if type(child).__name__ == 'QSpinBox':
                        child.setValue(cfg[objectName])
                    if type(child).__name__ == 'QTableWidget':
                        # print('----------------->'+objectName)
                        color = str(self.lineEdit_scene.palette().color(QtGui.QPalette.Background).name())
                        if color != yellow and color != red:
                            for row in range(child.rowCount()):
                                child.removeRow(0)
                            self.addLine(child,len(cfg[objectName]))

                            for row in cfg[objectName]:
                                for column in cfg[objectName][row]:
                                    # print(cfg[objectName][row][column])
                                    if column == 2:
                                        if cfg[objectName][row][column]:
                                            child.cellWidget(row,column).setText(cfg[objectName][row][column])
                                        else :
                                            child.cellWidget(row,column).setText('')
                                            u.setBackColor(child.cellWidget(row,column))
                                    elif column == 0:
                                        child.cellWidget(row,column).setCurrentIndex(existingAnimation.keys().index(cfg[objectName][row][column]))
                                    elif column == 1:
                                        self.animationDialog[row].load(cfg[objectName][row][column])
                                        u.setAnimationParamStr(self.tableWidget_animationParam.item(row,column),self.animationDialog[row].currentValues.iteritems())
                                        u.setCellColor(self.tableWidget_animationParam,self.animationDialog[row],row,column)

                elif child in self.mandatoryFields.keys():
                    u.setBackColor(child)
                    if type(child).__name__ == 'QTableWidget':
                        pass
                    else:
                        child.setText('')
                else:
                    child.setText('')

    def buildDic(self,page,data,pageName=None):
        '''
        BuildDic will build a Dictionnary that will describe the state of a 'page' of our application
        '''
        toSave = ['QLineEdit','QTextEdit','QCheckBox','QTableWidget','QSpinBox']
        if not pageName:
            pageName=str(page.objectName())
        data[pageName] = {}
        # print('pageName : '+pageName)
        for child in page.children():
            objectName = str(child.objectName())
            # print(objectName)
            # print(type(child).__name__)
            if type(child).__name__ in toSave:
                # print('--------------->'+child.objectName())
                if type(child).__name__ == 'QLineEdit':
                    data[pageName][objectName] = str(child.text())
                    # print('----------------->'+str(child.text()))
                if type(child).__name__ == 'QTextEdit':
                    data[pageName][objectName] = str(child.toPlainText())
                    # print('----------------->'+str(child.toPlainText()))
                if type(child).__name__ == 'QCheckBox':
                    data[pageName][objectName] = str(child.isChecked())
                    # print('----------------->'+str(child.isChecked()))
                if type(child).__name__ == 'QSpinBox':
                    data[pageName][objectName] = child.value()
                if type(child).__name__ == 'QTableWidget':
                    # data[pageName][child.objectName()] = child.text()
                    # print('----------------->'+objectName)
                    data[pageName][objectName] = {}
                    for row in range(child.rowCount()):
                        rowdata = []
                        data[pageName][objectName][row] = {}
                        for column in range(child.columnCount()):
                            item = child.cellWidget(row,column)
                            if column == 0:
                                data[pageName][objectName][row][column] = str(item.currentText())
                            elif column == 1:
                                item = child.item(row,column)
                                if item.text():
                                    dicParam = {}
                                    params = str(item.text()).replace(' ','').split(',')
                                    for param in params:
                                        tmp = param.split('=')
                                        dicParam[tmp[0]] = tmp[1]
                                    data[pageName][objectName][row][column] = dicParam
                                else:
                                    data[pageName][objectName][row][column] = None
                            elif item.text() != '':
                                data[pageName][objectName][row][column] = str(item.text())
                            else:
                                data[pageName][objectName][row][column] = None
        return data

    def execute(self):
        '''
        execute will gather all the argument necessary for the execution
        verify there validity than execute the reduction process based on them
        '''
        data = {}
        for page in self.grpBoxes:
            self.buildDic(page,data)

        arguments = {}
        
        # msg = []
        # for field in self.mandatoryFields.keys():
        #     color = str(field.palette().color(QtGui.QPalette.Background).name())
        #     if type(field).__name__ == 'QTableWidget':
        #         for row in range(field.rowCount()):
        #             for column in range(field.columnCount()):
        #                 item = field.cellWidget(row,column)
        #                 if item:
        #                     if str(item.palette().color(QtGui.QPalette.Background).name()) in [yellow,red]:
        #                         color = str(item.palette().color(QtGui.QPalette.Background).name())
        #                 elif str(field.item(row,column).backgroundColor().name()) in [yellow,red]:
        #                     color = str(field.item(row,column).backgroundColor().name())
        #     if color == yellow or color == red:
        #         msg.append(field)

        # if msg:
        #     tmp = 'ERROR:\n'
        #     for field in msg:
        #         if type(self.mandatoryFields[field]).__name__ == 'FrameLayout':
        #             tmp += 'Wrong/Missing Entry    ----------->    '+self.mandatoryFields[field].title()+'\n'
        #         else:
        #             tmp += 'Wrong/Missing Entry    ----------->    '+self.mandatoryFields[field].text()+'\n'
        #     # self.textEdit_preExecutionInfos.setText(tmp)
        #     print(tmp)
        # else:

        self.grpBoxes = [ self.grpBox_Path,
                          self.grpBox_AdvancedParam,
                          self.grpBox_ReductionParam,
                          self.grpBox_AnimationParam,
                          self.grpBox_Execution]
        msg =[]

        # Path Arguments
        pageName = str(self.grpBox_Path.objectName())

        arguments['originalScene'] = data[pageName]['lineEdit_scene']
        arguments['outputDir'] = data[pageName]['lineEdit_output']

        if data[pageName]['lineEdit_mesh']:
            arguments['meshes'] = data[pageName]['lineEdit_mesh'].split('\n')
        else: u.msg_warning(msg,'No Mesh specified')

        # ReductionParam Arguments
        pageName = str(self.grpBox_ReductionParam.objectName())

        arguments['nodesToReduce'] = [data[pageName]['lineEdit_NodeToReduce']]

        if data[pageName]['lineEdit_moduleName']:
            arguments['packageName'] = data[pageName]['lineEdit_moduleName']
        else: u.msg_info(msg,'No Module Name, take defaul')

        if data[pageName]['checkBox_AddTranslation'] == 'True' :
            arguments['addRigidBodyModes'] = [1,1,1]
        else: 
            u.msg_info(msg,'No Translation')
            arguments['addRigidBodyModes'] = [0,0,0]

        # AnimationParam Arguments
        pageName = str(self.grpBox_AnimationParam.objectName())

        arguments['listObjToAnimate'] = []
        for row in data[pageName]['tableWidget_animationParam']:
            animation = data[pageName]['tableWidget_animationParam'][row][0]
            for key,value in data[pageName]['tableWidget_animationParam'][row][1].iteritems():
                typ = existingAnimation[animation][key][1]
                data[pageName]['tableWidget_animationParam'][row][1][key] = typ(value)
            arguments['listObjToAnimate'].append(ObjToAnimate(  location = data[pageName]['tableWidget_animationParam'][row][2],
                                                                animFct = data[pageName]['tableWidget_animationParam'][row][0],
                                                                **data[pageName]['tableWidget_animationParam'][row][1]) )

        # Advanced Arguments
        pageName = str(self.grpBox_AdvancedParam.objectName())

        arguments['tolModes'] = float(data[pageName]['lineEdit_tolModes'])
        arguments['tolGIE'] = float(data[pageName]['lineEdit_tolGIE'])

        if data[pageName]['lineEdit_toKeep']:
            arguments['toKeep'] = data[pageName]['lineEdit_toKeep']
        else: u.msg_info(msg,'No To Keep Specified, take default')

        if data[pageName]['checkBox_addToLib'] == 'True':
            arguments['addToLib'] = True
        else:
            u.msg_info(msg,"The Reduced Model won't be added to the library")
        

        # Preference Arguments
        # !!!!  add preference  !!!!
        # if data[pageName]['checkBox_verbose'] == 'True':
        #     arguments['verbose'] = True
        # else:
        #     u.msg_info(msg,'Verbose Set to False')

        # if data[pageName]['spinBox_numberCPU']:
        #     arguments['nbrCPU'] = data[pageName]['spinBox_numberCPU']
        # !!!!  add preference  !!!!


        # Execution Arguments
        pageName = str(self.grpBox_Execution.objectName())


        msg = '\n'.join(msg)
        # self.textEdit_preExecutionInfos.setText(msg)
        separator = "---------------------\n\n"

        print(msg)

        if msg.find('ERROR') != -1:
            pass
            # self.textEdit_preExecutionInfos.append(separator+'Execution Stopped')
        else:
            for arg in arguments:
                print(arg)
            reduceMyModel = ReduceModel(**arguments)

            steps = []
            for checkBox , btn in self.phaseItem:
                index = self.phaseItem.index((checkBox,btn))
                if checkBox.checkState() == QtCore.Qt.Checked or checkBox.checkState() == QtCore.Qt.PartiallyChecked:
                    if checkBox.isEnabled() == True:
                        steps.append(index)

            print("STEP : "+str(steps))
            if len(steps) == 4:
                reduceMyModel.performReduction()
            else:
                for step in steps:
                    if step == 0:
                        reduceMyModel.phase1()
                    elif step == 1:
                        reduceMyModel.phase2()
                    elif step == 2:
                        reduceMyModel.phase3()
                    elif step == 3:
                        reduceMyModel.phase4()

            # if data[pageName]['checkBox_executeAll'] == 'True':
            #     self.textEdit_preExecutionInfos.append(separator+'Execute All')
            #     reduceMyModel.performReduction()
            # else:
            #     self.textEdit_preExecutionInfos.setText(msg)
            #     if data[pageName]['checkBox_phase1'] == 'True':
            #         self.textEdit_preExecutionInfos.append(separator+'Execute Phase 1')
            #         reduceMyModel.phase1()
            #     if data[pageName]['checkBox_phase2'] == 'True':
            #         self.textEdit_preExecutionInfos.append(separator+'Execute Phase 2')
            #         reduceMyModel.phase2()
            #     if data[pageName]['checkBox_phase3'] == 'True':
            #         self.textEdit_preExecutionInfos.append(separator+'Execute Phase 3')
            #         reduceMyModel.phase3()
            #     if data[pageName]['checkBox_phase4'] == 'True': 
            #         self.textEdit_preExecutionInfos.append(separator+'Execute Phase 4')
            #         reduceMyModel.phase4()

            # self.textEdit_preExecutionInfos.append(separator+'Execution Finished')

    def executeAll(self,checkBox,items,checked=True):
        '''
        executeAll is the action associated with checkBox_executeAll
        it will check all the steps while greying them out
        '''
        u.checkedBoxes(checkBox,items,checked)
        u.greyOut(checkBox,items,checked)

    def addLine(self,tab,number=1):

        for new in range(number):
            tab.insertRow(tab.rowCount())
            row = tab.rowCount()-1

            tmp = ui_v1proposition.MyLineEdit(tab)
            model = TreeModel(self.cfg,obj=True)

            completer = MyCompleter(tmp)
            completer.setModel(model)
            completer.setCompletionColumn(0)
            completer.setCompletionRole(QtCore.Qt.DisplayRole)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)  
            tmp.setCompleter(completer)

            tmp.textChanged.emit(tmp.text())
            tmp.textChanged.connect(lambda: u.check_state(self.sender()))
            tmp.setValidator(QtGui.QRegExpValidator(self.exp_path))

            tmp.clicked.connect(completer.complete)
            tmp.focused.connect(completer.complete)

            u.setBackColor(tmp)
            tab.setCellWidget(row,2,tmp)

            item = QTableWidgetItem()
            tab.setItem(row,1,item)
            backgrdColor = QColor()
            backgrdColor.setNamedColor(yellow)
            tab.item(row,1).setBackgroundColor(backgrdColor)
            
            self.animationDialog.append(GenericDialogForm('defaultShaking',existingAnimation['defaultShaking']))
            self.addComboToTab(tab,existingAnimation.keys(),row,0)

    def addComboToTab(self,tab,values,row,column):
        '''
        addComboToTab will add a QComboBox to an QTableWidget[row][column] and fill it with different value 
        '''
        combo = QtGui.QComboBox()
        combo.setObjectName(_fromUtf8("combo"+str(row)+str(column)))
        combo.activated.connect(lambda: self.addAnimationDialog(tab,row,column,column+1))
        for value in values:
            combo.addItem(value)
        tab.setCellWidget(row,column,combo)

    def addAnimationDialog(self,tab,row,column,dialogColumn):
        previousAnimation = self.animationDialog[row].animation
        currentAnimation = str(tab.cellWidget(row,column).currentText())

        if previousAnimation != currentAnimation:
            self.animationDialog[row] = GenericDialogForm(currentAnimation,existingAnimation[currentAnimation])
            tab.item(row,dialogColumn).setText('')

    def removeLine(self,tab,dialogs,rm=False):
        '''
        removeLine remove the current selected row or the last one created and also the associated dialog box object 
        '''
        row = u.removeLine(tab)
        if row:
            dialogs.remove(dialogs[row])

###################################################################################################

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function