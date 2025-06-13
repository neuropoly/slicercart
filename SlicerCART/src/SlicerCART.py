"""
This is the main file for SlicerCART.
That means the Slicer Python Interpreter always refer to the path of this
script when using SlicerCART.
"""

import os
import random
from datetime import datetime
from glob import glob
import colorsys

# KO: VTK isn't a standard Python lib, being loaded by Slicer post-init; as a result
#  it is not exposed as a library to IDEs. As such, we need to trust that slicer will
#  instantiate it before we reach this point; hence the error suppression.
import vtk  # noqa: F401

# ~KO: Both QT and Slicer are only initialized when slicer boots, and by extension when
#  some of their C++ code is imported. As a result, quite a few of their utilities are
#  not visible to IDEs, and may cause a "Cannot find reference 'xyz'" style warning in
#  our code base. For now, ignore it; will look into a workaround soon(tm)
import qt
import slicer

# Before importing our sub-modules, confirm we have everything installed
# TODO (KO): Refactor everything to make external packages locally imported instead
from utils.install_python_packages import check_and_install_python_packages
check_and_install_python_packages()

from scripts.CompareSegmentVersionsWindow import CompareSegmentVersionsWindow
from scripts.CustomInteractorStyle import CustomInteractorStyle
from scripts.InteractingClasses import SlicerCARTConfigurationInitialWindow
from scripts.InteractingClasses import SlicerCARTConfigurationSetupWindow
from scripts.LoadClassificationWindow import LoadClassificationWindow
from scripts.LoadSegmentationWindow import LoadSegmentationsWindow
from scripts.SlicerCARTLogic import SlicerCARTLogic
from scripts.ShowSegmentVersionLegendWindow import ShowSegmentVersionLegendWindow
from scripts.Timer import Timer
from scripts.WorkFiles import WorkFiles
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin, childWidgetVariables, loadUI
from utils.ConfigPath import ConfigPath
from utils.UITheme import Theme
from utils.UserPath import UserPath
from utils.constants import CLASSIFICATION_BOXES_LIST, TIMER_MUTEX
from utils.debugging_helpers import Debug, enter_function
from utils.development_helpers import Dev


###############################################################################

###############################################################################
# This main script contains the following classes:
#   SlicerCART --- main explanation script class
#   SlicerCARTWidget --- SlicerCART graphical user interface class (mainly use)
from ctk import ctkCollapsibleButton  

###############################################################################

class SlicerCART(ScriptedLoadableModule):
    """
    Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer
    /ScriptedLoadableModule.py
    
    This class is initialized when 3DSlicer starts
    """

    @enter_function
    def __init__(self, parent):
        """
        Initialize the SlicerCART module.
        
        Args:
        parent: Parent widget for the module.
        """
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "SlicerCART"  # TODO: make this more human
        # readable by adding spaces
        self.parent.categories = [
            "Examples"]  # TODO: set categories (folders where the module
        # shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names
        # that this module requires
        self.parent.contributors = [
            "Delphine Pilon, An Ni Wu, Emmanuel Montagnon, Maxime "
            "Bouthillier, Laurent Letourneau-Guillon"]  # TODO: replace with
        # "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to
        #  online module documentation
        self.parent.helpText = """
        This is an example of scripted loadable module bundled in an extension.
        See more information in 
        <a href="https://github.com/organization/projectname
        #SEGMENTER_v2">module documentation</a>.
        """

        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
        Module supported by funding from : 
        1. Fonds de Recherche du Québec en Santé and Fondation de 
        l’Association des Radiologistes du Québec Radiology Research funding 
        (299979) and Clinical Research Scholarship–Junior1 Salary Award (
        311203)
        2. Foundation of the Radiological Society of North America - Seed 
        Grant (RSD2122)
        3. Quebec Bio-Imaging Network, 2022 pilot project grant 
        (Project no 21.24)
        4. Support professoral du Département de radiologie, radio-oncologie et 
        médecine nucléaire de l’Université de Montréal, Radiology departement 
        Centre Hospitalier de l’Université de Montréal (CHUM) and CHUM Research 
        Center (CRCHUM) start-up funds
        Thanks to the Slicer community for the support and the development of 
        the software.
        """

class SlicerCARTWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """
    Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer
    /ScriptedLoadableModule.py
    """

    @enter_function
    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and initializes the module
        
        Args:
        parent: Parent widget for this widget.
        """
        # Run the initialization for this class's parents
        # KO: Initialization needs to be run this way to prevent the resulting
        #  modules becoming "isolated" from the main Slicer window. Thank
        #  Slicer for this jank!
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)

        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        # LLG CODE BELOW
        self.predictions_names = None

        # ----- ANW Addition  ----- : Initialize called var to False so the
        # timer only stops once
        self.called = False
        self.called_onLoadSegmentation = False

        # Create a temp file that serves as a flag to determine if output folder
        # has been selected or not.
        ConfigPath.create_temp_file()
        Debug.print(self, '*** temp file created. BE CAREFUL! ***')
        self.config_yaml = ConfigPath.open_project_config_file()
        self.DefaultDir = ConfigPath.DEFAULT_VOLUMES_DIRECTORY

        # Auto-Detect the Slicer theme, so specific foreground can be used
        self.theme = Theme.get_mode(self)
        self.foreground = Theme.set_foreground(self, self.theme)

    @enter_function
    def setup(self):
        """
        Called when the user opens the module the first time and the widget
        is initialized.
        """
        ### Segment editor widget
        self.layout.setContentsMargins(4, 0, 4, 0)

        super().setup()

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to
        # self.layout.
        uiWidget = loadUI(self.resourcePath('UI/SlicerCART.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the
        # top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each
        # MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should
        # be possible to run
        # in batch mode, without a graphical user interface. Only initialized once the SlicerCARTWidget class is initialized (when we enter the module)
        self.logic = SlicerCARTLogic()

        slicerCART_configuration_initial_window = (
            SlicerCARTConfigurationInitialWindow(
                self))
        slicerCART_configuration_initial_window.show()

        self.outputFolder = None
        self.currentCasePath = None
        self.CurrentFolder = None
        self.lineDetails = {}
        self.previousAction = None
        self.saved_selected = False  # Flag to load correctly the first case
        self.currentOutputPath = None
        self.currentVolumeFilename = None
        # Define colors to be used in the application
        self.color_active = "yellowgreen"
        self.color_inactive = "indianred"

        # To communicate classification version labels when loading
        # classification
        self.classification_version_labels = None

        # MB: code below added in the configuration setup since its absence
        # created issues when trying to load cases after selecting a volume
        # folder.
        self.config_yaml = ConfigPath.open_project_config_file()

        # ATTENTION! self.current_label_index refers to an index, but it is
        # getting its value based on the first label value (assumes it is always
        # 1): so, first index value = 1 -1 == 0
        self.current_label_index = (self.config_yaml['labels'][0]['value'] - 1)
        # self.current_label_index = self.config_yaml['labels'][0]['value']

        self.ui.PauseTimerButton.setText('Pause')
        self.ui.SelectVolumeFolder.connect(
            'clicked(bool)', self.onSelectVolumesFolderButton)
        self.ui.EditConfiguration.connect(
            'clicked(bool)', self.onEditConfiguration)
        self.ui.SlicerDirectoryListView.clicked.connect(
            self.getCurrentTableItem)
        self.ui.SaveSegmentationButton.connect(
            'clicked(bool)', self.onSaveSegmentationButton)
        self.ui.SelectOutputFolder.connect(
            'clicked(bool)', self.onSelectOutputFolder)
        self.ui.LoadSegmentation.connect(
            'clicked(bool)',  self.onLoadSegmentation)
        self.ui.ToggleSegmentation.connect(
            'clicked(bool)', self.toggle_segmentation_masks)
        self.ui.CompareSegmentVersions.connect(
            'clicked(bool)', self.onCompareSegmentVersions)
        self.ui.LoadClassification.connect(
            'clicked(bool)', self.onLoadClassification)
        self.ui.SaveClassificationButton.connect(
            'clicked(bool)', self.onSaveClassificationButton)
        self.ui.pushButton_Interpolate.connect(
            'clicked(bool)', self.onPushButton_Interpolate)
        self.ui.Previous.connect(
            'clicked(bool)', self.onPreviousButton)
        self.ui.Next.connect(
            'clicked(bool)', self.onNextButton)
        self.ui.Annotator_name.textChanged.connect(
            self.on_annotator_name_changed)
        self.ui.pushButton_Paint.connect(
            'clicked(bool)', self.onPushButton_Paint)
        self.ui.LassoPaintButton.connect(
            'clicked(bool)', self.onPushLassoPaint)
        self.ui.pushButton_ToggleVisibility.connect(
            'clicked(bool)', self.onPushButton_ToggleVisibility)
        self.ui.PushButton_segmeditor.connect(
            'clicked(bool)', self.onPushButton_segmeditor)
        self.ui.pushButton_Erase.connect(
            'clicked(bool)', self.onPushButton_Erase)
        self.ui.pushButton_Smooth.connect(
            'clicked(bool)', self.onPushButton_Smooth)
        self.ui.pushButton_Small_holes.connect(
            'clicked(bool)', self.onPushButton_Small_holes)
        self.ui.dropDownButton_label_select.currentIndexChanged.connect(
            self.onDropDownButton_label_select)
        self.ui.PauseTimerButton.connect(
            'clicked(bool)', self.togglePauseTimerButton)
        self.ui.StartTimerButton.connect(
            'clicked(bool)', self.toggleStartTimerButton)
        self.ui.pushButton_ToggleFill.connect(
            'clicked(bool)', self.toggleFillButton)

        self.ui.UB_HU.valueChanged.connect(self.onUB_HU)
        self.ui.LB_HU.valueChanged.connect(self.onLB_HU)
        self.ui.pushDefaultMin.connect('clicked(bool)', self.onPushDefaultMin)
        self.ui.pushDefaultMax.connect('clicked(bool)', self.onPushDefaultMax)
        self.ui.pushButton_undo.connect('clicked(bool)', self.onPushButton_undo)
        self.ui.ShowSegmentVersionLegendButton.connect(
            'clicked(bool)', self.onPush_ShowSegmentVersionLegendButton)

        self.ui.placeMeasurementLine.connect(
            'clicked(bool)', self.onPlacePointsAndConnect)

        self.ui.ShowSegmentVersionLegendButton.setVisible(False)

        self.disablePauseTimerButton()
        self.disableSegmentAndPaintButtons()
        self.ui.pushButton_Interpolate.setEnabled(False)
        self.adjust_interpolate_button_color(ConfigPath.INTERPOLATE_VALUE)
        self.ui.SaveSegmentationButton.setEnabled(False)

        self.enableStartTimerButton()

        self.ui.LoadClassification.setEnabled(False)
        self.ui.SaveClassificationButton.setEnabled(False)
        self.ui.LoadSegmentation.setEnabled(False)

        self.ui.ThresholdLabel.setStyleSheet("font-weight: bold")

        self.ui.UB_HU.setMinimum(-32000)
        self.ui.LB_HU.setMinimum(-32000)
        self.ui.UB_HU.setMaximum(29000)
        self.ui.LB_HU.setMaximum(29000)

        self.ui.pushButton_ToggleFill.setStyleSheet(
            f"background-color : {self.color_active}")
        self.ui.pushButton_ToggleFill.setText('Fill: ON')
        self.ui.pushButton_ToggleFill.setChecked(True)

        # By default, segments are visibles. So, the Segments visibles button is
        # setted to True and active.
        self.ui.pushButton_ToggleVisibility.setChecked(True)
        self.ui.pushButton_ToggleVisibility.setStyleSheet(
            f"background-color : {self.color_active}")
        
        # By default, load latest masks version button appears not selected.
        self.ui.ToggleSegmentation.setStyleSheet(
            f"background-color : {self.color_inactive}")

        self.ui.lcdNumber.setStyleSheet("background-color : black")

        self.MostRecentPausedCasePath = ""

        # Ensure keyboard shortcut (at least from the last configuration) work
        # at startup
        self.shortcut_objects = {}  # Maps shortcut key to QShortcut object
        self.shortcut_callbacks = {}
        self.set_keyboard_shortcuts()
        
        # Layout management on startup
        # Closes Data Probe upon landing in SlicerCART
        self.close_data_probe_on_startup()

    @enter_function
    def close_data_probe_on_startup(self):
        """
        Each time SlicerCARTWidget is loaded, this function is called to minimize Data Probe
        """
        mainWindow = slicer.util.mainWindow()
        for widget in mainWindow.findChildren(ctkCollapsibleButton):
            if widget.text == 'Data Probe':
                widget.collapsed = True

    @enter_function
    def set_classification_version_labels(self, classif_label):
        """
        Keep the classification labels depending on the classification 
        version to use and to save.
        """
        self.classification_version_labels = classif_label

    @enter_function
    def visibilityModifiedCallback(self, caller, event):
        """
        Each time segments visibility is changed, this function is called.
        caller: used to get segment visibility
        event: segment modified
        """
        toggle_to_set = False

        # Get the segmentIDs visibility one by one. Due to property of
        # SetAllSegments visibility used in ToggleVisibility (each segment is
        # settled one by one). This behavior allows to toogle segment
        # visibility and consider if the user modifies a segment while the
        # button segment visibiles is unselected.
        segmentIDs = vtk.vtkStringArray()
        self.segmentationNode.GetSegmentation().GetSegmentIDs(segmentIDs)

        # Check visibility for each segment
        for i in range(segmentIDs.GetNumberOfValues()):
            segmentID = segmentIDs.GetValue(i)
            isVisible = caller.GetSegmentVisibility(segmentID)
            Debug.print(self,
                        f"Segment '{segmentID}' visibility: {isVisible}")

            if isVisible:
                self.ui.pushButton_ToggleVisibility.setStyleSheet(
                    f"background-color : {self.color_active}")
                toggle_to_set = True

        Debug.print(
            self,f'Final state of toggle segments visibility button: '
                    f'{toggle_to_set}')

        self.ui.pushButton_ToggleVisibility.setChecked(toggle_to_set)

    @enter_function
    def setup_configuration(self):
        """
        Setup_configuration.
        
        Args:.
        """
        self.config_yaml = ConfigPath.open_project_config_file()
        # Warning: if incorrect config values that have been changed create
        # new errors around those line of codes. A solution is likely to add:
        # self.config_yaml = ConfigPath.set_config_value(self.config_yaml)
        # (This sets appropriate values for configuration; to insert after
        # open_project_config_file)

        if not ConfigPath.IS_DISPLAY_TIMER_REQUESTED:
            self.ui.PauseTimerButton.hide()
            self.ui.StartTimerButton.hide()

        if ConfigPath.IS_MOUSE_SHORTCUTS_REQUESTED:
            # MB
            self.interactor1 = slicer.app.layoutManager().sliceWidget(
                'Yellow').sliceView().interactor()
            self.interactor2 = slicer.app.layoutManager().sliceWidget(
                'Red').sliceView().interactor()

            # Apply the custom interactor style
            styleYellow = slicer.app.layoutManager().sliceWidget('Yellow')
            self.styleYellow = CustomInteractorStyle(sliceWidget=styleYellow)
            self.interactor1.SetInteractorStyle(self.styleYellow)

            styleRed = slicer.app.layoutManager().sliceWidget('Red')
            self.styleRed = CustomInteractorStyle(sliceWidget=styleRed)
            self.interactor2.SetInteractorStyle(self.styleRed)

        self.LB_HU = self.config_yaml["labels"][0]["lower_bound_HU"]
        self.UB_HU = self.config_yaml["labels"][0]["upper_bound_HU"]

        # Change the value of the upper and lower bound of the HU
        self.ui.UB_HU.setValue(self.UB_HU)
        self.ui.LB_HU.setValue(self.LB_HU)

        self.set_classification_config_ui()

        # Initialize timers
        self.timers = []
        timer_index = 0
        for label in self.config_yaml["labels"]:
            self.timers.append(Timer(number=timer_index))
            timer_index = timer_index + 1

        if not ConfigPath.IS_CLASSIFICATION_REQUESTED:
            self.ui.MRMLCollapsibleButton.setVisible(False)
        if not ConfigPath.IS_SEGMENTATION_REQUESTED:
            self.ui.MRMLCollapsibleButton_2.setVisible(False)

        if ConfigPath.MODALITY == 'MRI':
            self.ui.ThresholdLabel.setVisible(False)
            self.ui.MinimumLabel.setVisible(False)
            self.ui.MaximumLabel.setVisible(False)
            self.ui.LB_HU.setVisible(False)
            self.ui.UB_HU.setVisible(False)
            self.ui.pushDefaultMin.setVisible(False)
            self.ui.pushDefaultMax.setVisible(False)

        self.set_keyboard_shortcuts()

        if self.config_yaml['is_display_timer_requested']:
            self.ui.lcdNumber.setStyleSheet("background-color : black")
        else:
            self.ui.lcdNumber.setVisible(False)

        # Display the selected color view at module startup
        if self.config_yaml['slice_view_color'] == "Yellow":
            slicer.app.layoutManager().setLayout(
                slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
        if self.config_yaml['slice_view_color'] == "Red":
            slicer.app.layoutManager().setLayout(
                slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
        if self.config_yaml['slice_view_color'] == "Green":
            slicer.app.layoutManager().setLayout(
                slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)

        self.adjust_interpolate_button_color(ConfigPath.INTERPOLATE_VALUE)

    @enter_function
    def set_keyboard_shortcuts(self):
        """
        Set_keyboard_shortcuts.
        
        Args:.
        """
        # Initialize dictionaries if they don't exist yet
        if hasattr(self, 'shortcut_objects'):
            # Disconnect and delete all existing shortcuts
            for key, shortcut in self.shortcut_objects.items():
                print('deleitngshortcut key:', key, shortcut)
                shortcut.setParent(None)  # This will delete the shortcut
            self.shortcut_objects.clear()
            self.shortcut_callbacks.clear()
        else:
            self.shortcut_objects = {}
            self.shortcut_callbacks = {}

        if self.config_yaml.get('is_keyboard_shortcuts_requested', False):
            for entry in self.config_yaml.get("KEYBOARD_SHORTCUTS", []):
                shortcutKey = entry.get("shortcut")
                callback_name = entry.get("callback")
                button_name = entry.get("button")

                button = getattr(self.ui, button_name)
                callback = getattr(self, callback_name)

                # Create new shortcut and connect it
                shortcut = qt.QShortcut(qt.QKeySequence(shortcutKey), button)
                shortcut.connect("activated()", callback)

                self.shortcut_objects[shortcutKey] = shortcut
                self.shortcut_callbacks[shortcutKey] = callback

    @enter_function
    def set_segmentation_config_ui(self):
        """
        Set labels in the UI Drop Down Menu under Segmentation according to
        configuration.
        
        Args:.
        """
        self.ui.dropDownButton_label_select.clear()

        if self.ui.ToggleSegmentation.isChecked():
            segmentation_name = "Segmentation_1"
            segmentation_node = slicer.mrmlScene.GetNodesByName(
                segmentation_name)
            segmentation_node = segmentation_node.GetItemAsObject(0)

            segment_ids = segmentation_node.GetSegmentation().GetSegmentIDs()

            for segment_id in segment_ids:
                segment_name = self.segmentationNode.GetSegmentation(

                ).GetSegment(
                    segment_id).GetName()

                self.ui.dropDownButton_label_select.addItem(segment_name)

            self.segmentEditorWidget = (
                slicer.modules.segmenteditor.widgetRepresentation().self(

                ).editor)
            self.segmentEditorNode = (
                self.segmentEditorWidget.mrmlSegmentEditorNode())

            # Set the active segmentation node
            self.segmentEditorWidget.setSegmentationNode(segmentation_node)

        else:
            for label in self.config_yaml["labels"]:
                self.ui.dropDownButton_label_select.addItem(label["name"])

    @enter_function
    def set_classification_config_ui(self):

        # (Optional)) get the latest configuration if already exist in output
        # folder so if configuration has been changed from new configuration
        # but it already exists in the output folder, the classification labels
        # would be taken from the output folder. For now, it has been commented
        # since this would prevent to modify the classification and use it in
        # an already selected output folder. Uncomment to do above.
        # self.config_yaml = ConfigPath.open_project_config_file()

        # clear classification widgets
        for i in reversed(range(self.ui.ClassificationGridLayout.count())):
            if self.ui.ClassificationGridLayout.itemAt(i).widget() is not None:
                self.ui.ClassificationGridLayout.itemAt(i).widget().setParent(
                    None)

        comboboxesStartRow = (
            self.setupCheckboxes(3, self.config_yaml))
        freetextStartRow = self.setupComboboxes(comboboxesStartRow,
                                                self.config_yaml)
        self.setupFreeText(freetextStartRow, self.config_yaml["freetextboxes"])

    @enter_function
    def set_master_volume_intensity_mask_according_to_modality(self):
        """
        Set_master_volume_intensity_mask_according_to_modality.
        
        Args:.
        """
        if ConfigPath.MODALITY == 'CT':
            self.segmentEditorNode.SetMasterVolumeIntensityMask(True)
        elif ConfigPath.MODALITY == 'MRI':
            self.segmentEditorNode.SetMasterVolumeIntensityMask(False)

    @enter_function
    def setupCheckboxes(self, number_of_columns, classif_label, flag_use_csv=False):
        """
        SetupCheckboxes.

        Args:
        number_of_columns: Description of number_of_columns.
        classif_label: Description of classif_label.
        flag_use_csv: Flag to take values from csv file.
        """
        self.checkboxWidgets = {}

        row_index = 0

        if flag_use_csv:
            iteration_dict = self.get_label_iteration_dict(classif_label)
        else:
            iteration_dict = classif_label

        if classif_label["checkboxes"] != None:
            for i, (objectName, label) in (
                    enumerate(iteration_dict["checkboxes"].items())):
                checkbox = qt.QCheckBox()
                checkbox.setText(label)
                checkbox.setObjectName(objectName)

                row_index = i / number_of_columns + 1
                column_index = i % number_of_columns

                self.ui.ClassificationGridLayout.addWidget(
                    checkbox, row_index, column_index)
                self.checkboxWidgets[objectName] = checkbox

        return row_index + 1

    @enter_function
    def setupComboboxes(self, start_row, classif_label, combobox_version=None):
        """
        SetupComboboxes.
        
        Args:
        start_row: Description of start_row.
        classif_label: Description of classif_label.
        combobox_version: Description of combobox_version.
        """
        self.comboboxWidgets = {}

        if combobox_version == None:
            combobox_version = ConfigPath.get_latest_combobox_version(
                self.config_yaml)
        else:
            # Means that we need to read the comboboxes from the config yaml
            # Expand the classif_label using the full definitions
            full_definitions = self.config_yaml['comboboxes'][combobox_version]
            classif_label["comboboxes"][combobox_version] = {
                key: full_definitions[key]
                for key in sorted(classif_label["comboboxes"][combobox_version])
            }

        row_index = start_row
        if self.config_yaml['comboboxes'] != None:
            for i, (version, comboBoxes) in enumerate(
                    self.config_yaml["comboboxes"].items()):
                if version == combobox_version:
                    for comboBoxName, options in classif_label[
                        "comboboxes"][combobox_version].items():

                        comboboxLabel = qt.QLabel(
                            comboBoxName.replace("_", " ").capitalize() + " :")
                        comboboxLabel.setStyleSheet("font-weight: bold")
                        self.ui.ClassificationGridLayout.addWidget(
                            comboboxLabel, row_index, 0)

                        combobox = qt.QComboBox()
                        combobox.setObjectName(comboBoxName)

                        for optionKey, optionLabel in options.items():
                            combobox.addItem(optionLabel, optionKey)
                        self.ui.ClassificationGridLayout.addWidget(combobox,
                                                                   row_index, 1)
                        self.comboboxWidgets[comboBoxName] = combobox
                        row_index = row_index + 1

        return row_index + 1

    @enter_function
    def setupFreeText(self, start_row, columns_to_check=None):
        """
        SetupFreeText.
        
        Args:
        start_row: Description of start_row.
        columns_to_check: Description of columns_to_check.
        """
        self.freeTextBoxes = {}

        row_index = start_row

        if self.config_yaml["freetextboxes"] != None:

            for i, (freeTextObjectName, freeTextLabel) \
                    in enumerate(columns_to_check.items()):
                freeTextQLabel = qt.QLabel(freeTextLabel.capitalize() + " :")
                freeTextQLabel.setStyleSheet("font-weight: bold")
                self.ui.ClassificationGridLayout.addWidget(
                    freeTextQLabel, row_index, 0)
                lineEdit = qt.QLineEdit()
                self.freeTextBoxes[freeTextObjectName] = lineEdit
                self.ui.ClassificationGridLayout.addWidget(lineEdit, row_index,
                                                           1)
                row_index = row_index + 1

    @enter_function
    def connectShortcut(self, shortcutKey, button, callback):
        """
        ConnectShortcut.
        
        Args:
        shortcutKey: Description of shortcutKey.
        button: Description of button.
        callback: Description of callback.
        """
        shortcut = qt.QShortcut(slicer.util.mainWindow())
        shortcut.setKey(qt.QKeySequence(shortcutKey))
        shortcut.connect("activated()",
                         lambda: self.toggleKeyboardShortcut(button, callback))
        return shortcut

    @enter_function
    def toggleKeyboardShortcut(self, button, callback):
        """
        ToggleKeyboardShortcut.
        
        Args:
        button: Description of button.
        callback: Description of callback.
        """
        button.toggle()
        callback()

    @enter_function
    def setUpperAndLowerBoundHU(self, inputLB_HU, inputUB_HU):
        """
        SetUpperAndLowerBoundHU.
        
        Args:
        inputLB_HU: Description of inputLB_HU.
        inputUB_HU: Description of inputUB_HU.
        """
        self.LB_HU = inputLB_HU
        self.UB_HU = inputUB_HU
        self.ui.UB_HU.setValue(self.UB_HU)
        self.ui.LB_HU.setValue(self.LB_HU)

    # measurement line function set as a segment and paint functionality
    @enter_function
    def enableSegmentAndPaintButtons(self):
        """
        EnableSegmentAndPaintButtons.
        
        Args:.
        """
        self.ui.pushButton_Paint.setEnabled(True)
        self.ui.LassoPaintButton.setEnabled(True)
        self.ui.pushButton_Erase.setEnabled(True)
        self.ui.placeMeasurementLine.setEnabled(True)

    @enter_function
    def disableSegmentAndPaintButtons(self):
        """
        DisableSegmentAndPaintButtons.
        
        Args:.
        """
        self.ui.pushButton_Paint.setEnabled(False)
        self.ui.LassoPaintButton.setEnabled(False)
        self.ui.pushButton_Erase.setEnabled(False)
        self.ui.placeMeasurementLine.setEnabled(False)

    @enter_function
    def onEditConfiguration(self):
        """
        OnEditConfiguration.
        
        Args:.
        """
        slicerCARTConfigurationSetupWindow = SlicerCARTConfigurationSetupWindow(
            self, edit_conf=True)
        slicerCARTConfigurationSetupWindow.show()

    @enter_function
    def onSelectVolumesFolderButton(self):
        """
        OnSelectVolumesFolderButton.
        
        Args:.
        """

        Debug.print(self,
                    f'value of UserPath.get_selected_existing_folder: '
                    f'{UserPath.get_selected_existing_folder(self)}')

        self.config_yaml = ConfigPath.open_project_config_file()
        self.config_yaml = ConfigPath.set_config_values(self.config_yaml)

        if UserPath.get_selected_existing_folder(self):
            content = UserPath.get_selected_paths(self)
            for element in content:
                self.outputFolder = element
                self.CurrentFolder = content[self.outputFolder]
        else:
            self.CurrentFolder = (
                qt.QFileDialog.getExistingDirectory(
                    None,
                    "Open a folder",
                    self.DefaultDir,
                    qt.QFileDialog.ShowDirsOnly))

        # prevents crashing if no volume folder is selected
        if not self.CurrentFolder:
            return

        file_structure_valid = True
        if ConfigPath.REQUIRE_VOLUME_DATA_HIERARCHY_BIDS_FORMAT == True:
            file_structure_valid = self.validateBIDS(self.CurrentFolder)

        if file_structure_valid == False:
            return  # don't load any patient cases

        self.CasesPaths = sorted(glob(
            f'{self.CurrentFolder}{os.sep}**{os.sep}'
            f'{ConfigPath.INPUT_FILE_EXTENSION}',
            recursive=True))

        # Remove the volumes in the folder 'derivatives' (creates issues for
        # loading cases)
        self.CasesPaths = [item for item in self.CasesPaths if 'derivatives' not
                           in item]

        if not self.CasesPaths:
            message = ('No files found in the selected directory!'
                       f'\n\nCurrent file extension configuration: '
                       f'{ConfigPath.INPUT_FILE_EXTENSION}'
                       "\n\nMake sure the configured extension is "
                       "in the right format."
                       "\n\nFor example: check configuration_config.yml file "
                       "in "
                       "SlicerCART project or in output folder under _conf "
                       "folder."
                       "\n\nThen restart the module.")
            Dev.show_message_box(self, message, box_title='ATTENTION!')
            return

        self.Cases = sorted([os.path.split(i)[-1] for i in self.CasesPaths])

        self.reset_ui()

        self.ui.pushButton_Interpolate.setEnabled(True)

        # If output folder has already been selected from continue from
        # existing folder, this code updates the volume folders of output
        # folder.
        if self.outputFolder != None:
            UserPath.write_in_filepath(self, self.outputFolder,
                                       self.CurrentFolder)
            self.manage_workflow_and_classification()

    @enter_function
    def reset_ui(self):
        """
        Reset_ui.
        
        Args:.
        """
        self.ui.SlicerDirectoryListView.clear()
        self.ui.SlicerDirectoryListView.addItems(self.Cases)

        self.currentCase_index = 0  # THIS IS THE CENTRAL THING THAT HELPS
        # FOR CASE NAVIGATION
        self.update_ui()

    @enter_function
    def update_ui(self):
        """
        Update_ui.
        
        Args:.
        """
        self.updateCaseAll()
        self.loadPatient()

    @enter_function
    def set_patient(self, filename):
        """
        Set the patient to be displayed in UI case list and Slicer Viewer from
        filename.
        """
        index = self.WorkFiles.find_index_from_filename(filename,
                                                        self.Cases)
        currentCasePath = self.WorkFiles.find_path_from_filename(filename)

        self.currentCase = filename
        self.currentCase_index = index
        self.currentCasePath = currentCasePath

    @enter_function
    def manage_workflow(self):
        """
        Allows to work from appropriate working list and remaining list.
        """

        self.config_yaml = ConfigPath.open_project_config_file()
        # Instantiate a WorkFiles class object to facilitate cases lists
        # management.
        self.WorkFiles = WorkFiles(self.CurrentFolder, self.outputFolder)

        # Set up working list appropriateness compared to volumes folder
        # selected.
        if self.WorkFiles.check_working_list() == False:
            print(
                '\n\n INVALID WORKFLOW. CANNOT CONTINUE WITH CURRENT SELECTED '
                'VOLUMES AND OUTPUT FOLDERS.\n\n')
            # Output folder is inconsistent with Volumes Folder.
            # We should NEVER be able to save any other segmentations.
            message = ('The UI case list is now invalid. \n'
                       f'In the output folder {self.outputFolder}'
                       f'working_list and remaining_list, '
                       'files are inconsistent and corrupted.\n\n'
                       'Cannot continue with Slicer from now one.\n\n'
                       'Please restart SlicerCART if you want to continue.\n\n'
                       'Ensure you select appropriate volumes and output '
                       'folder, and reset working_list and remaining_list.\n'
                       '(For example, delete them).')
            Dev.show_message_box(self, message)
            return

        # Re-assignation of self.Cases and self.CasesPath based on working list.
        self.Cases = self.WorkFiles.get_working_list_filenames(self)
        self.CasesPaths = self.WorkFiles.get_working_list_filepaths(self.Cases)
        self.reset_ui()

        # Get the first case of remaining list (considers if empty).
        remaining_list_filenames = (
            self.WorkFiles.get_remaining_list_filenames(self))

        if self.WorkFiles.check_remaining_first_element(
                remaining_list_filenames):
            Debug.print(self, 'First case in remaining list ok.')
            remaining_list_first = self.WorkFiles.get_remaining_list_filenames(
                self)[0]
        else:
            Debug.print(self, 'Remaining list empty. Select case from working '
                              'list (working list should never be empty).')
            remaining_list_first = self.select_next_working_case()

        self.set_patient(remaining_list_first)

        # Assign segmentation labels in the segmentation UI
        self.set_segmentation_config_ui()

        self.update_ui()

    @enter_function
    def validateBIDS(self, path):
        """
        ValidateBIDS.
        
        Args:
        path: Description of path.
        """
        from bids_validator import BIDSValidator

        validator = BIDSValidator()
        is_structure_valid = True

        class InvalidBIDS(Exception):
            pass

        try:
            for subdir, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(
                            ConfigPath.INPUT_FILE_EXTENSION.split("*")[1]):
                        try:
                            path = "/sub" + \
                                   (subdir + "/" + file).split("/sub", 1)[1]
                            is_valid = validator.is_bids(path)
                        except:
                            raise InvalidBIDS

                        if is_valid == False:
                            raise InvalidBIDS
        except InvalidBIDS:
            msg_box = qt.QMessageBox()
            msg_box.setWindowTitle("BIDS Validation")
            msg_box.setText(
                "File hierarchy not in proper BIDS format. \n\nInformation : "
                "https://bids.neuroimaging.io \n\nTool : "
                "https://bids-standard.github.io/bids-validator")
            msg_box.exec()

            is_structure_valid = False

        return is_structure_valid

    @enter_function
    def updateCaseAll(self):
        """
        UpdateCaseAll.
        
        Args:.
        """
        # All below is dependent on self.currentCase_index updates,
        self.currentCase = self.Cases[self.currentCase_index]
        self.currentCasePath = self.CasesPaths[self.currentCase_index]

        if not ConfigPath.IS_DISPLAY_TIMER_REQUESTED:
            self.enableSegmentAndPaintButtons()

        self.updateCurrentPatient()
        # Highlight the current case in the list view (when pressing on next o)
        self.ui.SlicerDirectoryListView.setCurrentItem(
            self.ui.SlicerDirectoryListView.item(self.currentCase_index))
        self.update_current_segmentation_status()

    @enter_function
    def update_current_segmentation_status(self):
        """
        Update_current_segmentation_status.
        
        Args:.
        """
        current_color = self.ui.SlicerDirectoryListView.currentItem(

        ).foreground().color()
        if current_color == qt.QColor(self.foreground):
            self.ui.CurrentStatus.setText('Segmentation Status : Not done')
        elif current_color == qt.QColor('orange'):
            self.ui.CurrentStatus.setText(
                'Segmentation Status : Done by another annotator')
        elif current_color == qt.QColor('green'):
            self.ui.CurrentStatus.setText(
                'Segmentation Status : Done by this annotator')

    @enter_function
    def getCurrentTableItem(self):
        """
        GetCurrentTableItem.
        
        Args:.
        """
        # ----- ANW Addition ----- : Reset timer when change case and uncheck
        # all checkboxes
        self.resetTimer()
        self.resetClassificationInformation()

        # When an item in SlicerDirectroyListView is selected the case number
        # is printed
        # below we update the case index and we need to pass one parameter to
        # the methods since it takes 2 (1 in addition to self)
        self.updateCaseIndex(
            self.ui.SlicerDirectoryListView.currentRow)  # Index starts at 0
        # Update the case index
        self.currentCase_index = self.ui.SlicerDirectoryListView.currentRow
        # Same code in onBrowseFoldersButton, need to update self.currentCase
        # note that updateCaseAll() not implemented here - it is called when
        # a case is selected from the list view or next/previous button is
        # clicked
        self.currentCase = self.Cases[self.currentCase_index]
        self.currentCasePath = self.CasesPaths[self.currentCase_index]
        self.updateCurrentPatient()
        self.loadPatient()
        self.update_current_segmentation_status()

        # ----- ANW Addition ----- : Reset timer when change case, also reset
        # button status
        self.resetTimer()

    @enter_function
    def updateCaseIndex(self, index):
        """
        UpdateCaseIndex.
        
        Args:
        index: Description of index.
        """
        # ----- ANW Modification ----- : Numerator on UI should start at 1
        # instead of 0 for coherence
        self.ui.FileIndex.setText('{} / {}'.format(
            index + 1, len(self.Cases)))

    @enter_function
    def updateCurrentPatient(self):
        """
        UpdateCurrentPatient.
        
        Args:.
        """
        self.updateCaseIndex(self.currentCase_index)

    @enter_function
    def updateCurrentPath(self):
        """
        UpdateCurrentPath.
        
        Args:.
        """
        self.ui.CurrentPath.setReadOnly(True)
        self.ui.CurrentPath.setText(self.currentCasePath)

    @enter_function
    def loadPatient(self):
        """
        LoadPatient.
        
        Args:.
        """
        timer_index = 0
        self.timers = []
        for label in self.config_yaml["labels"]:
            self.timers.append(Timer(number=timer_index))
            timer_index = timer_index + 1

        # reset dropbox to index 0
        self.ui.dropDownButton_label_select.setCurrentIndex(0)

        # timer reset if we come back to same case
        self.called = False

        slicer.mrmlScene.Clear()
        slicer.util.loadVolume(self.currentCasePath)
        self.VolumeNode = \
            slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')[0]
        self.updateCaseAll()
        # Adjust windowing (no need to use self. since this is used locally)
        Vol_displayNode = self.VolumeNode.GetDisplayNode()
        # print('self volumenode get display node',
        # self.VolumeNode.GetDisplayNode())
        # print(' node', self.VolumeNode)

        Vol_displayNode.AutoWindowLevelOff()
        if ConfigPath.MODALITY == 'CT':
            Debug.print(self, 'MODALITY==CT')
            Vol_displayNode.SetWindow(ConfigPath.CT_WINDOW_WIDTH)
            Vol_displayNode.SetLevel(ConfigPath.CT_WINDOW_LEVEL)
        Vol_displayNode.SetInterpolate(ConfigPath.INTERPOLATE_VALUE)
        self.newSegmentation()

        self.updateCurrentOutputPathAndCurrentVolumeFilename()

        # If Load latest masks is checked, will load the latest version if
        # avaialable when loading a new patient
        if self.ui.ToggleSegmentation.isChecked():
            self.toggle_segmentation_masks()

    @enter_function
    def updateCurrentOutputPathAndCurrentVolumeFilename(self):
        """
        UpdateCurrentOutputPathAndCurrentVolumeFilename.
        
        Args:.
        """
        if (self.currentCasePath == None
                or self.CurrentFolder == None
                or self.outputFolder == None):
            return

        i = 0
        relativePath = ''
        for c in self.currentCasePath:
            if i >= len(self.CurrentFolder):
                relativePath = relativePath + c
            i = i + 1

        self.currentOutputPath = (
            os.path.split(self.outputFolder + relativePath))[0]
        self.currentVolumeFilename = (
            os.path.split(self.outputFolder + relativePath)[1].split("."))[0]

    # Getter method to get the segmentation node name
    # - Not sure if this is really useful here.
    @property
    @enter_function
    def segmentationNodeName(self):
        """
        SegmentationNodeName.
        
        Args:.
        """
        return (f"{os.path.split(self.currentCasePath)[1].split('.')[0]}"
            "_segmentation")

    @enter_function
    def newSegments(self):
        """
        NewSegments.
        
        Args:.
        """
        pass

    @enter_function
    def onPushButton_NewMask(self):
        """
        OnPushButton_NewMask.
        
        Args:.
        """
        self.newSegments()

    @enter_function
    def on_annotator_name_changed(self):
        """
        On_annotator_name_changed.
        
        Args:.
        """
        # self.update_case_list_colors()
        self.ui.SlicerDirectoryListView.setCurrentItem(
            self.ui.SlicerDirectoryListView.item(self.currentCase_index))
        self.update_current_segmentation_status()

    @enter_function
    def onPushButton_Interpolate(self):
        """
        OnPushButton_Interpolate.
        
        Args:.
        """

        INTERPOLATE_VALUE = not ConfigPath.INTERPOLATE_VALUE
        ConfigPath.set_interpolate_value(INTERPOLATE_VALUE)

        self.adjust_interpolate_button_color(INTERPOLATE_VALUE)
        self.VolumeNode.GetDisplayNode().SetInterpolate(INTERPOLATE_VALUE)

    @enter_function
    def adjust_interpolate_button_color(self, value):
        """
        Adjust the volume interpolation state to true or false

        Args:
            value: true (interpolated volume) or false (raw image)
        """
        if value:
            self.ui.pushButton_Interpolate.setStyleSheet(
                f"color: {self.color_active};")
        else:
            self.ui.pushButton_Interpolate.setStyleSheet(
                f"color: {self.color_inactive};")

    @enter_function
    def onPreviousButton(self):
        """
        OnPreviousButton.
        
        Args:.
        """
        # ----- ANW Addition ----- : Reset timer when change case and uncheck
        # all checkboxes
        self.resetTimer()
        self.resetClassificationInformation()

        # Code below avoid getting in negative values.
        self.currentCase_index = max(0, self.currentCase_index - 1)
        self.updateCaseAll()
        self.loadPatient()

    @enter_function
    def onNextButton(self):
        """
        OnNextButton.
        
        Args:.
        """
        # ----- ANW Addition ----- : Reset timer when change case and uncheck
        # all checkboxes
        self.resetTimer()
        self.resetClassificationInformation()

        # ----- ANW Modification ----- : Since index starts at 0, we need to
        # do len(cases)-1 (instead of len(cases)+1).
        # Ex. if we have 10 cases, then len(case)=10 and index goes from 0-9,
        # so we have to take the minimum between len(self.Cases)-1 and the
        # currentCase_index (which is incremented by 1 everytime we click the
        # button)
        self.currentCase_index = min(len(self.Cases) - 1,
                                     self.currentCase_index + 1)
        self.updateCaseAll()
        self.loadPatient()

        ConfigPath.set_latest_combobox_version(self.config_yaml)
        self.set_classification_version_labels(None)
        self.set_classification_config_ui()

    @enter_function
    def newSegmentation(self):
        """
        NewSegmentation.
        
        Args:.
        """
        # Create segment editor widget and node
        self.segmentEditorWidget = (
            slicer.modules.segmenteditor.widgetRepresentation().self().editor)
        self.segmentEditorNode = (
            self.segmentEditorWidget.mrmlSegmentEditorNode())
        # Create segmentation node (keep it local since we add a new
        # segmentation node)
        # Not for reference in other methods
        segmentationNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLSegmentationNode")
        # Set segmentation node name
        segmentationNode.SetName(self.segmentationNodeName)
        # Set segmentation node to segment editor
        self.segmentEditorWidget.setSegmentationNode(segmentationNode)
        # Set master volume node to segment editor
        self.segmentEditorWidget.setSourceVolumeNode(self.VolumeNode)
        # set refenrence geometry to Volume node (important for the
        # segmentation to be in the same space as the volume)
        segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(
            self.VolumeNode)
        self.createNewSegments()

        # Steps to add a visibility observer to the segmentation node created
        segmentationNode = slicer.mrmlScene.GetFirstNodeByClass(
            'vtkMRMLSegmentationNode')

        # Get the display node for the segmentation
        # (which controls the visibility of all segments)
        displayNode = segmentationNode.GetDisplayNode()

        # Add an observer to catch visibility changes
        displayNode.AddObserver(vtk.vtkCommand.ModifiedEvent,
                                self.visibilityModifiedCallback)

        # restart the current timer
        self.timers[self.current_label_index] = Timer(
            number=self.current_label_index)
        # reset tool
        self.segmentEditorWidget.setActiveEffectByName("No editing")

    # Load all segments at once
    @enter_function
    def createNewSegments(self):
        """
        CreateNewSegments.
        
        Args:.
        """
        for label in self.config_yaml["labels"]:
            self.onNewLabelSegm(label["name"], label["color_r"],
                                label["color_g"], label["color_b"],
                                label["lower_bound_HU"],
                                label["upper_bound_HU"])
            first_label_name = self.config_yaml["labels"][0]["name"]
            first_label_segment_name = first_label_name
            self.onPushButton_select_label(first_label_segment_name,
                                           self.config_yaml["labels"][0][
                                               "lower_bound_HU"],
                                           self.config_yaml["labels"][0][
                                               "upper_bound_HU"])

    @enter_function
    def newSegment(self, segment_name=None):
        """
        NewSegment.
        
        Args:
        segment_name: Description of segment_name.
        """

        self.segment_name = segment_name
        srcNode = slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
        self.srcSegmentation = srcNode.GetSegmentation()

        # Below will create a new segment if there are no segments in the
        # segmentation node, avoid overwriting existing segments
        if not self.srcSegmentation.GetSegmentIDs():  # if there are no
            # segments in the segmentation node
            self.segmentationNode = \
                slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
            self.segmentationNode.GetSegmentation().AddEmptySegment(
                self.segment_name)

        # if there are segments in the segmentation node, check if the
        # segment name is already in the segmentation node
        if any([self.segment_name in i for i in
                self.srcSegmentation.GetSegmentIDs()]):
            self.ensure_segment_id_matches_name(self.segment_name)
        else:
            self.segmentationNode = \
                slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
            self.segmentationNode.GetSegmentation().AddEmptySegment(
                self.segment_name)
            self.ensure_segment_id_matches_name(self.segment_name)

        return self.segment_name

    @enter_function
    def ensure_segment_id_matches_name(self, segment_name):
        """
        Ensure segment ID matches name when creating new segments.

        Args:
            segment_name: string that represents the wished segment name
        """
        # Check if name matches ID; if not, rename
        segment = self.srcSegmentation.GetSegment(segment_name)
        if segment.GetName() != segment_name:
            segment.SetName(segment_name)

    @enter_function
    def onNewLabelSegm(self, label_name, label_color_r, label_color_g,
                       label_color_b, label_LB_HU, label_UB_HU):
        """
        OnNewLabelSegm.
        
        Args:
        label_name: Description of label_name.
        label_color_r: Description of label_color_r.
        label_color_g: Description of label_color_g.
        label_color_b: Description of label_color_b.
        label_LB_HU: Description of label_LB_HU.
        label_UB_HU: Description of label_UB_HU.
        """
        segment_name = self.newSegment(label_name)
        self.segmentationNode = \
            slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
        self.segmentationNode.UndoEnabledOn()
        Segmentation = self.segmentationNode.GetSegmentation()

        # Prior to version 5.8.1, the below line worked. In version 5.8.1,
        # a segment id is settled by default and a generic name as well,
        # requiring a slightly different approach for managing segments.
        # self.SegmentID = Segmentation.GetSegmentIdBySegmentName(segment_name)
        self.SegmentID = self.get_segment_id_from_name(Segmentation,
                                                       segment_name)

        segment = Segmentation.GetSegment(self.SegmentID)
        segment.SetColor(label_color_r / 255, label_color_g / 255,
                         label_color_b / 255)
        self.onPushButton_select_label(segment_name, label_LB_HU, label_UB_HU)

    @enter_function
    def get_segment_id_from_name(self, segmentation, segment_name):
        """
        Get the segment id from the segment name

        Args:
            segmentation: segmentation node
            segment_name: string that is the segment name
        """
        num_segments = segmentation.GetNumberOfSegments()

        for i in range(num_segments):
            current_segment_id = segmentation.GetNthSegmentID(i)
            current_segment = segmentation.GetSegment(current_segment_id)
            current_name = current_segment.GetName()

            if current_name == segment_name:
                Debug.print(self, (f"Found match: Segment ID = "
                                   f"{current_segment_id}"))
                return current_segment_id

    @enter_function
    def onPushButton_select_label(self, segment_name, label_LB_HU, label_UB_HU):
        """
        OnPushButton_select_label.
        
        Args:
        segment_name: Description of segment_name.
        label_LB_HU: Description of label_LB_HU.
        label_UB_HU: Description of label_UB_HU.
        """
        self.segmentationNode = \
            slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
        Segmentation = self.segmentationNode.GetSegmentation()
        self.SegmentID = Segmentation.GetSegmentIdBySegmentName(segment_name)
        self.segmentEditorNode.SetSelectedSegmentID(self.SegmentID)
        self.updateCurrentPath()
        self.LB_HU = label_LB_HU
        self.UB_HU = label_UB_HU

        if (self.MostRecentPausedCasePath != self.currentCasePath
                and self.MostRecentPausedCasePath != ""):
            self.timers[self.current_label_index] = Timer(
                number=self.current_label_index)  # new path, new timer

        self.timer_router()

    @enter_function
    def startTimer(self):
        """
        StartTimer.
        
        Args:.
        """
        with TIMER_MUTEX:
            self.counter = 0
            # Add flag to avoid counting time when user clicks on save segm
            # button
            self.flag2 = True

            # ----- ANW Addition ----- : Code to keep track of time passed
            # with lcdNumber on UI
            # Create a timer
            self.timer = qt.QTimer()
            self.timer.timeout.connect(self.updatelcdNumber)

            # Start the timer and update every second
            self.timer.start(100)  # 1000 ms = 1 second

            # Call the updatelcdNumber function
            self.updatelcdNumber()

    # @enter_function ### THIS FUNCTION IS CALLED TOO OFTEN TO USE
    # ENTER_FUNCTION DECORATOR (too many prints in the python console)
    def updatelcdNumber(self):
        """
        UpdatelcdNumber.
        
        Args:.
        """
        # Get the time
        with TIMER_MUTEX:
            if self.flag2:  # add flag to avoid counting time when user
                # clicks on save segm button
                # the timer sends a signal every second (1000 ms). 
                self.counter += 1  # the self.timer.timeout.connect(
            # self.updatelcdNumber) function is called every second and
            # updates the counter

            self.ui.lcdNumber.display(self.counter / 10)

    @enter_function
    def stopTimer(self):
        """
        StopTimer.
        
        Args:.
        """
        with TIMER_MUTEX:
            # If already called once (i.e when user pressed save segm button
            # but forgot to annotator name), simply return the time
            if self.called:
                return self.total_time
            else:
                try:
                    self.total_time = self.counter / 10
                    self.timer.stop()
                    self.flag2 = False  # Flag is for the timer to stop counting
                    self.called = True
                    #   self.time_allocation()
                    return self.total_time
                except AttributeError as e:
                    print(f'!!! YOU DID NOT START THE COUNTER !!! :: {e}')
                    return None

    @enter_function
    def resetTimer(self):
        """
        ResetTimer.
        
        Args:.
        """
        with TIMER_MUTEX:
            # making flag to false : stops the timer
            self.flag2 = False  # For case after the first one the timer
            # stops until the user clicks on the
            self.counter = 0
            self.ui.lcdNumber.display(0)

            # reset button status
            self.enableStartTimerButton()
            self.disablePauseTimerButton()
            self.ui.PauseTimerButton.setText('Pause')
            if (self.ui.PauseTimerButton.isChecked()):
                self.ui.PauseTimerButton.toggle()

            if not ConfigPath.IS_DISPLAY_TIMER_REQUESTED:
                self.enableSegmentAndPaintButtons()
            else:
                self.disableSegmentAndPaintButtons()

    @enter_function
    def enableStartTimerButton(self):
        """
        EnableStartTimerButton.
        
        Args:.
        """
        self.ui.StartTimerButton.setEnabled(True)
        self.ui.StartTimerButton.setStyleSheet("background-color : yellowgreen")
        if (self.ui.StartTimerButton.isChecked()):
            self.ui.StartTimerButton.toggle()

    @enter_function
    def disablePauseTimerButton(self):
        """
        DisablePauseTimerButton.
        
        Args:.
        """
        self.ui.PauseTimerButton.setStyleSheet("background-color : silver")
        self.ui.PauseTimerButton.setEnabled(False)

    @enter_function
    def toggleStartTimerButton(self):
        """
        ToggleStartTimerButton.
        
        Args:.
        """
        # allow users to start the timer by clicking on any of the
        # segmentation-related buttons
        if (self.ui.SlicerDirectoryListView.count > 0):
            self.startTimer()
            self.timer_router()

            self.ui.StartTimerButton.setEnabled(False)
            self.ui.StartTimerButton.setStyleSheet("background-color : silver")

            self.ui.PauseTimerButton.setEnabled(True)
            self.ui.PauseTimerButton.setStyleSheet(
                "background-color : indianred")

            self.enableSegmentAndPaintButtons()
        else:
            self.ui.StartTimerButton.toggle()

    @enter_function
    def togglePauseTimerButton(self):
        """
        TogglePauseTimerButton.
        
        Args:.
        """
        # if button is checked - Time paused
        if self.ui.PauseTimerButton.isChecked():
            # setting background color to light-blue
            self.ui.PauseTimerButton.setStyleSheet(
                "background-color : lightblue")
            self.ui.PauseTimerButton.setText('Restart')
            self.timer.stop()
            for indiv_timer in self.timers:
                indiv_timer.stop()
            self.flag = False

            self.MostRecentPausedCasePath = self.currentCasePath

            self.disableSegmentAndPaintButtons()
            self.onPushButton_Erase()

        # if it is unchecked
        else:
            # set background color back to light-grey
            self.ui.PauseTimerButton.setStyleSheet(
                "background-color : indianred")
            self.ui.PauseTimerButton.setText('Pause')
            self.timer.start(100)
            self.timer_router()
            self.flag = True

            self.enableSegmentAndPaintButtons()

    # for the timer Class not the LCD one
    @enter_function
    def timer_router(self):
        """
        Timer_router.
        
        Args:.
        """
        self.timers[self.current_label_index].start()
        self.flag = True

        timer_index = 0
        for timer in self.timers:
            if timer_index != self.current_label_index:
                timer.stop()
            timer_index = timer_index + 1

    @enter_function
    def createFolders(self):
        """
        CreateFolders.
        
        Args:.
        """
        self.revision_step = self.ui.RevisionStep.currentText
        if len(self.revision_step) != 0:
            if os.path.exists(self.outputFolder) == False:
                msgboxtime = qt.QMessageBox()
                msgboxtime.setText(
                    "Segmentation not saved : output folder invalid!")
                msgboxtime.exec()
            else:
                self.updateCurrentOutputPathAndCurrentVolumeFilename()

                if os.path.exists(self.currentOutputPath) == False:
                    os.makedirs(self.currentOutputPath)

        else:
            msgboxtime = qt.QMessageBox()
            msgboxtime.setText(
                "Segmentation not saved : revision step is not defined!  \n "
                "Please save again with revision step!")
            msgboxtime.exec()

    @enter_function
    def startTimerForActions(self):
        """
        StartTimerForActions.
        
        Args:.
        """
        with TIMER_MUTEX:
            try:
                if not self.flag2:
                    self.toggleStartTimerButton()
            except AttributeError:
                self.toggleStartTimerButton()

    @enter_function
    def resetClassificationInformation(self):
        """
        ResetClassificationInformation.
        
        Args:.
        """
        # Try/Except to prevent crashing when selecting another file in the
        # UI case list if no classification_config_yaml file is already created.
        version = ConfigPath.get_combobox_version()
        try:
            self.config_yaml["checkboxes"]
            for i, (objectName, label) \
                    in enumerate(self.config_yaml["checkboxes"].items()):
                self.checkboxWidgets[objectName].setChecked(False)
            for i, (comboBoxName, options) \
                    in enumerate(
                self.config_yaml["comboboxes"][version].items()):
                self.comboboxWidgets[
                    comboBoxName].currentText = list(options.items())[0][1]
            for i, (freeTextBoxObjectName, label) \
                    in enumerate(self.config_yaml["freetextboxes"].items()):
                self.freeTextBoxes[freeTextBoxObjectName].setText("")
        except:
            pass

    @enter_function
    def getClassificationInformation(self):
        """
        Get all classification information available from both existing csv
        file and from the current SlicerCART module. Then, update all
        information available to an updated dataframe.
        return: dataframe with all previous and actual classification labels.
        """
        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        self.outputClassificationInformationFile = (
            os.path.join(self.currentOutputPath,
                         '{}_ClassificationInformation.csv'.format(
                             self.currentVolumeFilename)))
        df = None
        if (os.path.exists(
                self.outputClassificationInformationFile)
                and os.path.isfile(self.outputClassificationInformationFile)
        ):

            df = pd.read_csv(self.outputClassificationInformationFile)

        label_string_slicer = ""
        data_string_slicer = ""

        if df is not None:
            # Means that classification csv file already exists.
            Debug.print(
                self, 'Classification csv file already exists. To '
                              'update.')

            # Get Slicer Classification data only
            label_string_slicer, data_string_slicer = (
                self.get_classif_config_data())
            Debug.print(self,
                        'Got classification details from Slicer.')

            # Add Slicer Classification data header to csv df
            df = self.add_missing_columns_to_df(df, label_string_slicer)
            # Extract column names into a dictionary
            columns_dict = self.extract_header_from_df(df)

            # Extract previous data into a dictionary
            data_dict = {col: df[col].tolist() for col in df.columns}

            # Update classification data with annotation information (e.g.
            # annotator names, degree, revision step, etc.)
            data_string_slicer.update(self.build_current_classif_dictionary())

            # Check if any columns in actual classification labels has been
            # removed, and add -- if the column that has been removed
            data_string_slicer = (
                self.add_mark_for_removed_columns(df, data_string_slicer))

            # Ensure each element of the dictionary is ready to be converted
            # in df
            data_string_slicer = (
                self.convert_string_values_to_list_element(data_string_slicer))

            # At this point, previous dict and new dict should have the same
            # format: combine the dictionaries
            combined_df = self.combine_dict(data_dict, data_string_slicer)
            df = combined_df

        else:
            # Classification csv file does not exist already.
            label_string, data_string = self.get_classif_config_data()
            info_dict = self.build_current_classif_dictionary()

            data_dict = {}
            data_dict.update(info_dict)
            data_dict.update(data_string)

            # Ensure dictionary is ready to be converted to df
            data_dict = self.convert_string_values_to_list_element(data_dict)
            df = pd.DataFrame(data_dict)

        return df

    @enter_function
    def get_classif_config_data(self):
        """
        Get classification configuration data (both labels names and values)
        :return: 2 DICTIONARIES: one containing the label information; another
        containing the data for each labels.
        """
        label_string = {}
        data_string = {}

        # list_of_boxes = ["checkboxes", "comboboxes", "freetextboxes"]
        for element in CLASSIFICATION_BOXES_LIST:
            # label_string, data_string = self.build_classification_labels()
            label_temp, data_temp = self.build_classification_labels(element)

            label_string.update(label_temp)
            data_string.update(data_temp)

        return label_string, data_string

    @enter_function
    def get_all_classification_columns_csv(self, classif_label):
        """
        Get all classification columns name from csv file.
        """

        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        # Try except required since this function can be used initially or
        # after output folder has been selected. If initial, the output path is
        # not defined so it should return none (and not fail).

        if classif_label != None:
            try:
                self.outputClassificationInformationFile = (
                    os.path.join(self.currentOutputPath,
                                 '{}_ClassificationInformation.csv'.format(
                                     self.currentVolumeFilename)))
                df = None
                if (os.path.exists(
                        self.outputClassificationInformationFile)
                        and os.path.isfile(
                            self.outputClassificationInformationFile)):
                    df = pd.read_csv(self.outputClassificationInformationFile)

                if df is not None:
                    column_names = self.extract_header_from_df(df)

                    csv_columns_dict = {'checkboxes': {}, 'freetextboxes': {}}
                    for key, value in column_names.items():
                        if value == 'checkboxes':
                            tag = key.split(":")[0][2:-1]
                            if tag in classif_label['checkboxes']:
                                temp_dict = {}
                                temp_dict[tag] = (
                                    tag.replace("_", " ").capitalize())
                                csv_columns_dict[
                                    'checkboxes'][
                                    tag] = tag.replace("_", " ").capitalize()
                        # Not required to rebuild comboboxes here since already
                        # using a version control system.
                        # if value == 'comboboxes':
                        #     print('comboboxes', value)
                        if value == 'freetextboxes':
                            tag = key.split(":")[0][2:-1]
                            if tag in classif_label['freetextboxes']:
                                temp_dict = {}
                                temp_dict[tag] = (
                                    tag.replace("_", " ").capitalize())
                                csv_columns_dict[
                                    'freetextboxes'][
                                    tag] = tag.replace("_", " ").capitalize()

                    return csv_columns_dict
            except:
                pass

    @enter_function
    def build_classification_labels(self, classif_label):
        """
        Create a dictionary for both header (label names) and classification
        values.
        :param classif_label: string of name of type of labels (e.g.
        "checkboxes")
        :return: 2 DICTIONARIES one with names and types of columns; another
        with data values.
        """
        header_dict = {}
        value_dict = {}

        # Combobox version to use
        version = ConfigPath.get_combobox_version()

        # Get appropriate labeling and pass it in iteraction_dict
        iteration_dict = self.get_label_iteration_dict(
            self.classification_version_labels)

        for i, (objectName, label) in enumerate(
                iteration_dict[classif_label].items()):

            local_header_dict = {}

            # Adapt the format of label value saving depending of the type
            if classif_label == "checkboxes":
                local_header_dict[objectName] = classif_label

                try:
                    data = "No"
                    if self.checkboxWidgets[objectName].isChecked():
                        data = "Yes"

                except:
                    data = self.checkboxWidgets[objectName] = "--"
                    pass

            elif classif_label == "comboboxes":
                if objectName == version:
                    for key, value in label.items():
                        local_header_dict[key] = classif_label
                        data = self.comboboxWidgets[key].currentText
                        header_dict[f"{local_header_dict}"] = classif_label
                        value_dict[f"{local_header_dict}"] = data
                        local_header_dict = {}
                else:
                    continue

            elif classif_label == "freetextboxes":
                try:
                    local_header_dict[objectName] = classif_label
                    data = self.freeTextBoxes[objectName].text.replace(
                        "\n", " // ")
                except:
                    data = self.freeTextBoxes[objectName] = "--"
                    pass

            if not classif_label == "comboboxes":
                header_dict[f"{local_header_dict}"] = classif_label
                value_dict[f"{local_header_dict}"] = data

        return header_dict, value_dict

    @enter_function
    def get_label_iteration_dict(self, classif_label=None):
        """
        Get the configuration dictionary to iterate through (e.g. in
        classification ui versioning).
        """
        csv_columns_dict = self.get_all_classification_columns_csv(
            classif_label)
        if csv_columns_dict != None:
            iteration_dict = csv_columns_dict
            iteration_dict['comboboxes'] = self.config_yaml['comboboxes']
        else:
            iteration_dict = self.config_yaml

        return iteration_dict

    @enter_function
    def add_missing_columns_to_df(self, df, columns_dict):
        """
        Add columns to a dataframe if it is not in dictionary.
        :param df: dataframe to check if columns are present
        :columns_dict: dictionary of all columns needed.
        :return: dataframe with all required columns.
        If column is not already existing, all non-existing columns for existing
        rows are filled with '--' (this helps tracing back if classification
        configuration has changed).
        """
        # Add missing columns from the dictionary
        for column in columns_dict:
            if column not in df.columns:
                # df[column] = np.nan
                df[column] = '--'
        return df

    @enter_function
    def add_mark_for_removed_columns(self, dfcsv, slicer_dict):
        """
        Add '--' in the actual data for previously existing column that has
        been removed in the actual configuration.
        :param dfcsv: dataframe from previous csv file
        :param slicer_dict: dictionary of classification labels from slicer ui.
        :return: dictionary of data with all previously existing columns and
        actual columns (removed or added).
        """
        initial_columns = dfcsv.columns.tolist()
        for column in initial_columns:
            if column not in slicer_dict:
                slicer_dict[column] = '--'
        return slicer_dict

    @enter_function
    def convert_string_values_to_list_element(self, dict):
        """
        Ensure each value of a dictionary containing columns name as keys and
        values as column values are formatted to list to make it comptabile
        with using pandas functions.
        :param: dict: dictionary to make compatible.
        :return: dictionary compatible to be converted to dataframe.
        """
        # Ensure all values are lists
        for key in dict:
            if not isinstance(dict[key], list):
                dict[key] = [dict[key]]
        return dict

    @enter_function
    def combine_dict(self, dict1, dict2):
        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        """
        Combine 2 dictionaries into a dataframe
        :param dict1 first dictionary to combine
        :param dict2 second dictionary to combine
        :return: dataframe with both dictionary content
        """
        # Convert dictionaries to DataFrames
        df1 = pd.DataFrame(dict1)
        df2 = pd.DataFrame(dict2)

        # Concatenate the DataFrames
        result_df = pd.concat([df1, df2], ignore_index=True)
        return result_df

    @enter_function
    def extract_header_from_df(self, df):
        """
        Extract columns name from dataframe.
        :param: df: dataframe
        :return: dictionary of columns names as keys and type of
        classification label as values.
        """
        label_string = {}
        columns_name = list(df.columns.tolist())  # Get a list of column names

        for col in columns_name:
            try:
                # Attempt to evaluate the string as a dictionary
                col_dict = eval(col)
                if isinstance(col_dict, dict):
                    # Extract the single key-value pair from the dictionary
                    for key, value in col_dict.items():
                        label_string[col] = value
            except (SyntaxError, NameError, ValueError):
                # Handle cases where col is not a valid dictionary
                label_string[col] = col

        return label_string

    @enter_function
    def build_current_classif_dictionary(self):
        """
        Build dictionary with current demographic and general Slicer annotator
        information.
        :return: dictionary where keys are Column name for general information
        and values are corresponding data from actual configuration.
        """
        currentClassificationInformationVersion = (
            self.getClassificationInformationVersion())
        print('info current build', currentClassificationInformationVersion)
        info_dict = {}
        info_dict['Volume filename'] = self.currentCase
        info_dict[
            'Classification version'] = currentClassificationInformationVersion
        info_dict['Combobox version'] = self.combobox_version
        info_dict['Annotator Name'] = self.annotator_name
        info_dict['Annotator degree'] = self.annotator_degree
        info_dict['Revision step'] = self.ui.RevisionStep.currentText
        info_dict['Date and time'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        return info_dict

    @enter_function
    def onSaveSegmentationButton(self):
        """
        OnSaveSegmentationButton.
        
        Args:.
        """
        # By default creates a new folder in the volume directory
        # Stop the timer when the button is pressed
        self.time = self.stopTimer()
        # Stop timer of the Timer class
        for timer in self.timers:
            timer.stop()
        self.annotator_name = self.ui.Annotator_name.text
        self.annotator_degree = self.ui.AnnotatorDegree.currentText

        # Create folders if not exist
        self.createFolders()

        # Make sure to select the first segmentation node
        # (i.e. the one that was created when the module was loaded,
        # not the one created when the user clicked on the "Load mask" button)
        self.segmentationNode = (
            slicer.util.getNodesByClass('vtkMRMLSegmentationNode'))[0]

        currentSegmentationVersion = self.getCurrentSegmentationVersion()

        # quality control check (number of labels)
        is_valid = self.qualityControlOfLabels()
        if is_valid == False:
            return

        # Save if annotator_name is not empty and timer started:
        if self.annotator_name and self.time is not None:

            self.saveSegmentationInformation(currentSegmentationVersion)

            # If not working, the solution is likely to add here:
            # self.config_yaml = ConfigPath.open_project_config_file() # Get
            # latest/appropriate configuration
            # self.config_yaml = ConfigPath.set_config_value(
            # self.config_yaml) # Set appropriate values for configuration

            if 'nrrd' in ConfigPath.INPUT_FILE_EXTENSION:
                self.saveNrrdSegmentation(currentSegmentationVersion)

            if 'nii' in ConfigPath.INPUT_FILE_EXTENSION:
                self.saveNiiSegmentation(currentSegmentationVersion)

            msg_box = qt.QMessageBox()
            msg_box.setWindowTitle("Success")
            msg_box.setIcon(qt.QMessageBox.Information)
            msg_box.setText("Segmentation saved successfully!")
            msg_box.exec()

        # If annotator_name empty or timer not started.
        else:
            if not self.annotator_name:
                msgboxtime = qt.QMessageBox()
                msgboxtime.setText(
                    "Segmentation not saved : no annotator name !  "
                    "\n Please save again with your name!")
                msgboxtime.exec()
            elif self.time is None:
                print("Error: timer is not started for some unknown reason.")

        # self.update_case_list_colors()

        # One segment has been saved, which allows to load the next case from
        # now.
        self.saved_selected = True
        self.select_next_remaining_case()

    @enter_function
    def select_next_remaining_case(self):
        """
        Select_next_remaining_case.
        
        Args:.
        """
        Debug.print(self, f'self.currentCase_index: {self.currentCase_index}')
        Debug.print(self, f'self.currentCase: {self.currentCase}')
        Debug.print(self, f'self.currentCasePath: {self.currentCasePath}')
        Debug.print(self,
                    f'self.currentCase_index + 1 = '
                    f'{self.currentCase_index + 1}')

        remaining_list_filenames = self.WorkFiles.get_remaining_list_filenames()

        if ((remaining_list_filenames == [])
                or (remaining_list_filenames == None)
                or (len(remaining_list_filenames) == 0)):
            Debug.print(self, 'Remaining list empty!')
            next_case_name = self.select_next_working_case()

            # Update SlicerCART UI with the appropriate case.
            self.set_patient(next_case_name)
            self.update_ui()

            return

        if self.currentCase in remaining_list_filenames:
            current_case_index = self.WorkFiles.find_index_from_filename(
                self.currentCase, remaining_list_filenames)
            next_case_index = current_case_index + 1

            if next_case_index >= len(remaining_list_filenames):
                Debug.print(self, 'This is the last case!')
                next_case_name = self.currentCase  # So, remain on the last
                # case.

            else:
                next_case_name = remaining_list_filenames[next_case_index]

            self.WorkFiles.adjust_remaining_list(self.currentCase)

        else:
            # self.CurrentCase not in remaining list: going to the next case in
            # the working list.
            next_case_name = self.select_next_working_case()
            # define next case index

        self.set_patient(next_case_name)
        self.update_ui()

    @enter_function
    def select_next_working_case(self):
        """
        Select the next case to be displayed from the working list.
        """

        working_list_filenames = self.WorkFiles.get_working_list_filenames()
        index_in_working_list = self.WorkFiles.find_index_from_filename(
            self.currentCase, working_list_filenames)

        # Means that segmentation have already been saved.
        if self.saved_selected:
            next_case_index = index_in_working_list + 1

        else:
            next_case_index = index_in_working_list

        if next_case_index >= len(working_list_filenames):
            Debug.print(self, 'This is the last case of working list.')
            next_case_name = self.currentCase

        else:
            next_case_name = working_list_filenames[next_case_index]

        return next_case_name

    @enter_function
    def qualityControlOfLabels(self):
        """
        QualityControlOfLabels.
        
        Args:.
        """
        is_valid = True

        segment_names = self.getAllSegmentNames()
        if len(segment_names) != len(self.config_yaml["labels"]):
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Critical)
            msg.setText("ERROR : Incorrect number of labels")
            msg.setInformativeText(
                f'Expected {len(self.config_yaml["labels"])} labels but '
                f'obtained {len(segment_names)}. ')
            msg.setWindowTitle("ERROR : Incorrect number of labels")
            msg.exec()
            return False

        for i, segment_name in enumerate(segment_names):
            if segment_name != self.config_yaml["labels"][i]["name"]:
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("ERROR : Label mismatch")
                msg.setInformativeText(
                    f'Expected {self.config_yaml["labels"][i]["name"]} but '
                    f'obtained {segment_name}. ')
                msg.setWindowTitle("ERROR : Label mismatch")
                msg.exec()
                return False
        return is_valid

    @enter_function
    def re_order_segments(self, segmentation_node):
        """
        Re-order the segments when reloaded since previous version could have
        mistmatching number of non-empty segments (e.g. segment 1 and segment 3
        but not 2, while the newest version has segment 1,2, and 3.

        Args:
             segmentation_node: segmentation node displayed in the viewer
        """
        # Ensure final segment order matches the order in config_yaml["labels"]
        ordered_segment_ids = []
        segmentation = segmentation_node.GetSegmentation()

        # First, collect current ID for each name in the right order
        for label in self.config_yaml["labels"]:
            segment_id = segmentation.GetSegmentIdBySegmentName(label["name"])
            if segment_id:
                ordered_segment_ids.append(segment_id)

        # Apply reordering
        segmentation.ReorderSegments(ordered_segment_ids)

    @enter_function
    def saveNrrdSegmentation(self, currentSegmentationVersion):
        """
        Note that NRRD segmentation save in uint8 by default in contrast to
        .nii.gz format.
        """
        # Save .seg.nrrd file
        self.outputSegmFile = os.path.join(
            self.currentOutputPath,
            "{}_{}.seg.nrrd".format(
                self.currentVolumeFilename, currentSegmentationVersion))
        if not os.path.isfile(self.outputSegmFile):
            slicer.util.saveNode(self.segmentationNode, self.outputSegmFile)
        else:
            msg2 = qt.QMessageBox()
            msg2.setWindowTitle('Save As')
            msg2.setText(
                f'The file '
                f'{self.currentCase}_{self.annotator_name}_'
                f'{self.revision_step[0]}.seg.nrrd already exists '
                f'\n Do you want to replace the existing file?')
            msg2.setIcon(qt.QMessageBox.Warning)
            msg2.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
            msg2.buttonClicked.connect(self.msg2_clicked)
            msg2.exec()

    @enter_function
    def saveNiiSegmentation(self, currentSegmentationVersion):
        """
        Note that NRRD segmentations save in uint8 by default in contrast to
        .nii.gz format that saves by default in INT16. In that context,
        the flag SAVE_UINT8 (set to true by default in the config file),
        determines the type of the .nii.gz segmentation files.
        """
        # Export segmentation to labelmap (required step for .nii.gz files)
        self.labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass(
            'vtkMRMLLabelMapVolumeNode')
        slicer.modules.segmentations.logic(

        ).ExportVisibleSegmentsToLabelmapNode(
            self.segmentationNode, self.labelmapVolumeNode, self.VolumeNode
        )

        # Save to final path
        self.outputSegmFileNifti = os.path.join(
            self.currentOutputPath,
            f"{self.currentVolumeFilename}_{currentSegmentationVersion}.nii.gz"
        )
        if ConfigPath.SAVE_UINT8:
            Debug.print(self, "Save segmentation to UINT8.")
            # Save to a temporary file (optimal for uint8 type)
            temp_path = os.path.join(slicer.app.temporaryPath,
                                     "temp_seg.nii.gz")
            slicer.util.saveNode(self.labelmapVolumeNode, temp_path)

            # Step 3: Load and cast to UINT8 with nibabel
            import nibabel as nib
            import numpy as np
            nii = nib.load(temp_path)
            data = nii.get_fdata().astype(np.uint8)
            new_nii = nib.Nifti1Image(data, affine=nii.affine,
                                      header=nii.header)
            new_nii.set_data_dtype(np.uint8)

            if not os.path.isfile(self.outputSegmFileNifti):
                nib.save(new_nii, self.outputSegmFileNifti)
                Debug.print(self, f"Saved UINT8 segmentation to:"
                                  f" {self.outputSegmFileNifti}")

            # Remove temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        else:
            Debug.print(self, "Save segmentation to UINT16.")
            if not os.path.isfile(self.outputSegmFileNifti):
                slicer.util.saveNode(self.labelmapVolumeNode,
                                     self.outputSegmFileNifti)
                Debug.print(self, f"Saved INT16 segmentation to:"
                                  f" {self.outputSegmFileNifti}")

    @enter_function
    def saveSegmentationInformation(self, currentSegmentationVersion):
        """
        SaveSegmentationInformation.
        
        Args:
        currentSegmentationVersion: Description of currentSegmentationVersion.
        """
        # Header row
        self.previousAction = None
        tag_str = ("Volume filename,Segmentation version,Annotator Name,"
                   "Annotator degree,Revision step,Date and time,Duration")

        for label in self.config_yaml["labels"]:
            tag_str += "," + label["name"] + " duration"

        # Add line detail headers
        for line_key in self.lineDetails:
            tag_str += (f",{line_key} ControlPoint1,{line_key} ControlPoint2,"
                        f"{line_key} Length")

        data_str = self.currentCase
        data_str += "," + currentSegmentationVersion
        data_str += "," + self.annotator_name
        data_str += "," + self.annotator_degree
        data_str += "," + self.revision_step[0]
        data_str += "," + datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        data_str += "," + str(self.ui.lcdNumber.value)

        for timer in self.timers:
            data_str += "," + str(timer.total_time)

        # Add line details, ensuring control points are kept in one cell
        for line_key, line_data in self.lineDetails.items():
            control_point1 = ';'.join(
                map(str, line_data["ControlPoint1"]))  # Join with semicolon
            control_point2 = ';'.join(
                map(str, line_data["ControlPoint2"]))  # Join with semicolon
            length = line_data[
                "Length"]  # Length is a number, no need for conversion

            # Add control points and length to the data string
            data_str += f",{control_point1},{control_point2},{length}"

        self.outputSegmentationInformationFile = os.path.join(
            self.currentOutputPath,
            f'{self.currentVolumeFilename}_SegmentationInformation.csv')

        if os.path.isfile(self.outputSegmentationInformationFile):
            # Read existing contents
            with open(self.outputSegmentationInformationFile, 'r') as f:
                existing_content = f.readlines()
                existing_content = existing_content[1:] if len(
                    existing_content) > 1 else []

            # Rewrite the file with the new header and existing data
            with open(self.outputSegmentationInformationFile, 'w') as f:
                f.write(tag_str + "\n")  # Write the new header
                f.writelines(existing_content)  # Write the old content

            # Append the new data
            with open(self.outputSegmentationInformationFile, 'a') as f:
                f.write(data_str + "\n")
        else:
            # If the file doesn't exist, create it and write the header and data
            with open(self.outputSegmentationInformationFile, 'w') as f:
                f.write(tag_str + "\n")
                f.write(data_str + "\n")

    @enter_function
    def saveClassificationInformation(self, classification_df):
        """
        Save updated classification information to a csv file.
        :param: dataframe containing all updated classification data.
        """
        self.outputClassificationInformationFile = os.path.join(
            self.currentOutputPath,
            '{}_ClassificationInformation.csv'.format(
                self.currentVolumeFilename))

        classification_df.to_csv(self.outputClassificationInformationFile,
                                 index=False)

    @enter_function
    def getClassificationInformationVersion(self):
        """
        GetClassificationInformationVersion.
        
        Args:.
        """
        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        version = "v"
        classificationInformationPath = (f'{self.currentOutputPath}{os.sep}'
                                         f'{self.currentVolumeFilename}'
                                         f'_ClassificationInformation.csv')

        if os.path.exists(classificationInformationPath) == False:
            version = version + "01"

        else:
            csv_data = pd.read_csv(classificationInformationPath)
            existing_version_strings = csv_data[
                'Classification version'].to_list()
            existing_version_numbers = [(int)(version_string.split("v")[1]) for
                                        version_string in
                                        existing_version_strings]
            next_version_number = max(existing_version_numbers) + 1
            version = f'{version}{next_version_number:02d}'

        return version

    @enter_function
    def getCurrentSegmentationVersion(self):
        """
        GetCurrentSegmentationVersion.
        
        Args:.
        """
        # Adjust the version according to each individual file.
        list_of_segmentation_filenames = glob(
            f'{self.currentOutputPath}{os.sep}'
            f'{self.currentVolumeFilename}{ConfigPath.INPUT_FILE_EXTENSION}')

        version = 'v'
        if list_of_segmentation_filenames == []:
            version = version + "01"
        else:
            existing_versions = [(int)(filename.split('_v')[1].split(".")[0])
                                 for
                                 filename in list_of_segmentation_filenames]
            next_version_number = max(existing_versions) + 1
            next_version_number = min(next_version_number,
                                      99)  # max 99 versions
            version = f'{version}{next_version_number:02d}'
        return version

    @enter_function
    def msg2_clicked(self, msg2_button):
        """
        Msg2_clicked.
        
        Args:
        msg2_button: Description of msg2_button.
        """
        if msg2_button.text == 'OK':
            slicer.util.saveNode(self.segmentationNode, self.outputSegmFile)
        else:
            return

    @enter_function
    def msg3_clicked(self, msg3_button):
        """
        Msg3_clicked.
        
        Args:
        msg3_button: Description of msg3_button.
        """
        if msg3_button.text == 'OK':
            slicer.util.saveNode(self.labelmapVolumeNode,
                                 self.outputSegmFileNifti)
        else:
            return

    @enter_function
    def msg4_clicked(self, msg4_button):
        """
        Msg4_clicked.
        
        Args:
        msg4_button: Description of msg4_button.
        """
        if msg4_button.text == 'OK':
            slicer.util.saveNode(self.VolumeNode, self.outputVolfile)
        else:
            return

    @enter_function
    def check_volume_folder_selected(self):
        """
        Check_volume_folder_selected.
        
        Args:.
        """
        Debug.print(self, f'self.Currentfolder: {self.CurrentFolder}')
        if self.CurrentFolder != None:
            return True
        return False

    @enter_function
    def onSelectOutputFolder(self):
        """
        OnSelectOutputFolder.
        
        Args:.
        """

        if self.check_volume_folder_selected():
            self.outputFolder = (
                qt.QFileDialog.getExistingDirectory(
                    None,
                    "Open a folder",
                    self.DefaultDir,
                    qt.QFileDialog.ShowDirsOnly))
            ConfigPath.set_output_folder(self.outputFolder)
        else:
            Dev.show_message_box(self, 'Please select volumes folder first.',
                                 box_title='ATTENTION!')
            return

        # MB: Deactivated related to issue 112. To discuss in team (to remove).
        # if REQUIRE_EMPTY:
        #     self.verify_empty()

        ConfigPath.check_existing_configuration()
        ConfigPath.delete_temp_file()

        # Robust. If the next output folder selected (from a change) is empty,
        # ensure it will select the correct output folder path
        ConfigPath.write_correct_path()

        # Save the associated volume_folder_path with the output_folder
        # selected.
        UserPath.write_in_filepath(self, self.outputFolder, self.CurrentFolder)

        self.manage_workflow_and_classification()

        ConfigPath.write_config_file()

        self.set_ui_enabled_options()

    @enter_function
    def manage_workflow_and_classification(self):
        """
        Manage_workflow_and_classification.
        
        Args:.
        """
        # Update classification labels (part 1 of 2)
        initial_config_content = ConfigPath.get_initial_config_after_modif()
        temp_dict = ConfigPath.extract_config_classification(
            initial_config_content)

        self.manage_workflow()

        # Update classification labels (part 2 of 2)
        # To do after manage workflow because manage workflow looks for the
        # optimal configuration file to use.
        self.config_yaml = ConfigPath.compare_and_merge_classification(
            self.config_yaml, temp_dict)

        # Load classification parameters in the ui
        self.set_classification_config_ui()

    @enter_function
    def set_ui_enabled_options(self):
        """
        Set_ui_enabled_options.
        
        Args:.
        """
        if self.outputFolder is not None:
            self.ui.LoadClassification.setEnabled(True)
            self.ui.LoadSegmentation.setEnabled(True)

            self.ui.SaveSegmentationButton.setEnabled(True)
            self.ui.SaveClassificationButton.setEnabled(True)

            if self.CurrentFolder is not None:
                self.updateCurrentOutputPathAndCurrentVolumeFilename()

                # self.update_case_list_colors()

                self.ui.SlicerDirectoryListView.setCurrentItem(
                    self.ui.SlicerDirectoryListView.item(
                        self.currentCase_index))
                self.update_current_segmentation_status()

                self.predictions_paths = sorted(glob(
                    os.path.join(self.outputFolder,
                                 f'{ConfigPath.INPUT_FILE_EXTENSION}')))
        else:
            Debug.print(self, 'No output folder selected.')

    ### N.B. MB: All calling of the function belows have been disabled because
    # if there is a large UI case list (ex 1000 cases), the module becomes very
    # slow since it looks for the whole list each time. Function kept here to
    # addrees in the future in a more effective way of update UI case list
    # color.
    @enter_function
    def update_case_list_colors(self):
        """
        Update_case_list_colors.
        
        Args:.
        """
        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        if self.outputFolder is None or self.CurrentFolder is None:
            return

        self.ui.SlicerDirectoryListView.clear()
        for case in self.Cases:
            case_id = case.split('.')[0]
            item = qt.QListWidgetItem(case_id)
            segmentation_information_path = (f'{self.currentOutputPath}{os.sep}'
                                             f'{case_id}'
                                             f'_SegmentationInformation.csv')
            segmentation_information_df = None
            if os.path.exists(segmentation_information_path):
                segmentation_information_df = pd.read_csv(
                    segmentation_information_path)
                currentCaseSegmentationStatus = self.get_segmentation_status(
                    case, segmentation_information_df)
                if currentCaseSegmentationStatus == 0:
                    item.setForeground(qt.QColor(self.foreground))
                elif currentCaseSegmentationStatus == 1:
                    item.setForeground(qt.QColor('orange'))
                elif currentCaseSegmentationStatus == 2:
                    item.setForeground(qt.QColor('green'))

            self.ui.SlicerDirectoryListView.addItem(item)
        else:
            return

    @enter_function
    def get_segmentation_status(self, case, segmentation_information_df):
        """
        Get_segmentation_status.
        
        Args:
        case: Description of case.
        segmentation_information_df: Description of segmentation_information_df.
        """
        self.annotator_name = self.ui.Annotator_name.text

        found_case = 0
        if self.annotator_name is None:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText("No annotator name defined")
            msg.setInformativeText(
                'The annotator name is empty, therefore, the case list colors '
                'are not updated. ')
            msg.setWindowTitle("No annotator name defined")
            msg.exec()

        else:
            for _, row in segmentation_information_df.iterrows():
                if row['Volume filename'] == case and row[
                    'Annotator Name'] == self.annotator_name:
                    return 2
                elif row['Volume filename'] == case:
                    found_case = 1

        return found_case

    @enter_function
    def msg_warnig_delete_segm_node_clicked(self, msg_warnig_delete_segm_node_button):
        """
        Msg_warnig_delete_segm_node_clicked.

        Args:
        msg_warnig_delete_segm_node_button: Description of
        msg_warnig_delete_segm_node_button.
        """
        if msg_warnig_delete_segm_node_button.text == 'OK':
            srcNode = slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
            slicer.mrmlScene.RemoveNode(srcNode)
        else:
            return

    @enter_function
    def onLoadClassification(self):
        """
        OnLoadClassification.

        Args:.
        """
        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        classificationInformationPath = (f'{self.currentOutputPath}{os.sep}'
                                         f'{self.currentVolumeFilename}'
                                         f'_ClassificationInformation.csv')

        classificationInformation_df = None
        if os.path.exists(classificationInformationPath):
            classificationInformation_df = (
                pd.read_csv(classificationInformationPath))
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Information)
            msg.setText("No saved classifications")
            msg.setInformativeText(
                'There are no classifications saved in the '
                'ClassificationInformation.csv.')
            msg.setWindowTitle("No saved classifications")
            msg.exec()
            return

        loadClassificationWindow = LoadClassificationWindow(
            self, classificationInformation_df)
        loadClassificationWindow.show()


    @enter_function
    def onSaveClassificationButton(self):
        """
        OnSaveClassificationButton.
        
        Args:.
        """
        self.annotator_name = self.ui.Annotator_name.text
        self.annotator_degree = self.ui.AnnotatorDegree.currentText

        self.combobox_version = ConfigPath.get_combobox_version()
        classification_df = self.getClassificationInformation()

        # Create folders if don't exist
        self.createFolders()

        if self.annotator_name is not None:
            self.saveClassificationInformation(classification_df)
            # Those lines can be re-activated if wanted to display a success
            # message when saved.
            # msg_box = qt.QMessageBox()
            # msg_box.setWindowTitle("Success")
            # msg_box.setIcon(qt.QMessageBox.Information)
            # msg_box.setText("Classification saved successfully!")
            # msg_box.exec()

            # Go automatically to the next case in the UI list when
            # classification has been saved (if it<s the last case, it stays on
            # it)
            self.onNextButton()

        else:
            msgboxtime = qt.QMessageBox()
            msgboxtime.setText(
                "Classification not saved : no annotator name !  \n Please "
                "save again with your name!")
            msgboxtime.exec()


    @enter_function
    def onCompareSegmentVersions(self):
        """
        OnCompareSegmentVersions.
        
        Args:.
        """
        if 'Clear' in self.ui.CompareSegmentVersions.text:
            self.onClearCompareSegmentVersions()
        else:
            msg_warnig_delete_segm_node = (
                self.warnAgainstDeletingCurrentSegmentation())
            msg_warnig_delete_segm_node.buttonClicked.connect(
                self.onCompareSegmentVersionsWillEraseCurrentSegmentsWarningClicked)
            msg_warnig_delete_segm_node.exec()

    @enter_function
    def onCompareSegmentVersionsWillEraseCurrentSegmentsWarningClicked(
            self, msg_warnig_delete_segm_node_button):
        """
        OnCompareSegmentVersionsWillEraseCurrentSegmentsWarningClicked.
        
        Args:
        msg_warnig_delete_segm_node_button: Description of msg_warnig_delete_segm_node_button.
        """
        if msg_warnig_delete_segm_node_button.text == 'OK':
            srcNode = slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
            slicer.mrmlScene.RemoveNode(srcNode)

            self.openCompareSegmentVersionsWindow()
        else:
            return


    @enter_function
    def warnAgainstDeletingCurrentSegmentation(self):
        """
        WarnAgainstDeletingCurrentSegmentation.
        
        Args:.
        """
        msg_warnig_delete_segm_node = qt.QMessageBox()
        msg_warnig_delete_segm_node.setText(
            'This will delete the current segmentation. Do you want to '
            'continue?')
        msg_warnig_delete_segm_node.setIcon(qt.QMessageBox.Warning)
        msg_warnig_delete_segm_node.setStandardButtons(
            qt.QMessageBox.Ok | qt.QMessageBox.Cancel)

        return msg_warnig_delete_segm_node


    @enter_function
    def onLoadSegmentation(self):
        """
        OnLoadSegmentation.
        
        Args:.
        """
        msg_warnig_delete_segm_node = (
            self.warnAgainstDeletingCurrentSegmentation())
        msg_warnig_delete_segm_node.buttonClicked.connect(
            self.onLoadSegmentationWillEraseCurrentSegmentsWarningClicked)
        msg_warnig_delete_segm_node.exec()


    @enter_function
    def onLoadSegmentationWillEraseCurrentSegmentsWarningClicked(
            self, msg_warnig_delete_segm_node_button):
        """
        OnLoadSegmentationWillEraseCurrentSegmentsWarningClicked.
        
        Args:
        msg_warnig_delete_segm_node_button: Description of msg_warnig_delete_segm_node_button.
        """
        if msg_warnig_delete_segm_node_button.text == 'OK':
            srcNode = slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
            slicer.mrmlScene.RemoveNode(srcNode)
            self.openLoadSegmentationWindow()
        else:
            return

    @enter_function
    def toggle_segmentation_masks(self):
        """
        Load latest version of segmentation from output folder if available.
        """
        self.startTimerForActions()
        self.previousAction = 'segmentation'

        if self.ui.ToggleSegmentation.isChecked():

            self.ui.ToggleSegmentation.setStyleSheet(
                f"background-color : {self.color_active}")

            self.segmentationNode.GetDisplayNode().SetAllSegmentsVisibility(
                True)

            latest_version_path = self.get_latest_path()

            Debug.print(self, f'latest_version_path: {latest_version_path}')

            if latest_version_path is None:
                Debug.print(self, 'No segmentation found. Nothing to do.')
                return

            # Replace current segments in the segmentation node so they can be
            # edited
            self.replace_segments(latest_version_path)

        else:
            self.ui.ToggleSegmentation.setStyleSheet(
                f"background-color : {self.color_inactive}")
            self.segmentationNode.GetDisplayNode().SetAllSegmentsVisibility(
                False)

            segmentation_node = Dev.get_segmentation_node(self)
            segmentation = segmentation_node.GetSegmentation()
            segmentation.RemoveAllSegments()

            self.loadPatient()


    @enter_function
    def get_latest_path(self):
        """
        Get the latest path of most recent segmentation version if available.
        """
        latest_version = self.get_latest_existing_version()
        latest_path = os.path.join(
            self.currentOutputPath,
            "{}_{}"f"{ConfigPath.INPUT_FILE_EXTENSION[1:]}".format(
                self.currentVolumeFilename, latest_version))

        if os.path.exists(latest_path):
            return latest_path


    @enter_function
    def get_latest_existing_version(self):
        """
        Get the latest version available as a string.
        """
        version = self.getCurrentSegmentationVersion()
        version_int = self.parse_version_to_int(version)
        version_int -= 1
        if version_int == 0:
            version = version
        else:
            version = self.parse_version_int_to_str(version_int)
        Debug.print(self, f'version: {version}')
        return version


    @enter_function
    def parse_version_to_int(self, version_string):
        """
        Parse version as a string to corresponding integer.
        """
        version_formatted = version_string[1:]
        version = int(version_formatted)
        return version


    @enter_function
    def parse_version_int_to_str(self, version_int):
        """
        Parse an integer version to a string format
        """
        return f"v{version_int:02d}"


    @enter_function
    def openLoadSegmentationWindow(self):
        """
        OpenLoadSegmentationWindow.
        
        Args:.
        """
        # TMP: Import locally, because Slicer's external dependency management is nuts
        import pandas as pd

        segmentationInformationPath = (f'{self.currentOutputPath}{os.sep}'
                                       f'{self.currentVolumeFilename}'
                                       f'_SegmentationInformation.csv')

        segmentationInformation_df = None
        if os.path.exists(segmentationInformationPath):
            segmentationInformation_df = pd.read_csv(
                segmentationInformationPath)
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Information)
            msg.setText("No saved segmentations")
            msg.setInformativeText(
                'There are no segmentations saved in '
                'the SegmentationInformation.csv.')
            msg.setWindowTitle("No saved segmentations")
            msg.exec()
            return

        loadSegmentationWindow = LoadSegmentationsWindow(
            self, segmentationInformation_df)
        loadSegmentationWindow.show()


    @enter_function
    def openCompareSegmentVersionsWindow(self):
        """
        OpenCompareSegmentVersionsWindow.
        
        Args:.
        """
        import pandas as pd

        segmentationInformationPath = (f'{self.currentOutputPath}{os.sep}'
                                       f'{self.currentVolumeFilename}'
                                       f'_SegmentationInformation.csv')

        segmentationInformation_df = None
        if os.path.exists(segmentationInformationPath):
            segmentationInformation_df = pd.read_csv(
                segmentationInformationPath)
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Information)
            msg.setText("No saved segmentations")
            msg.setInformativeText(
                'There are no segmentations saved in '
                'the SegmentationInformation.csv.')
            msg.setWindowTitle("No saved segmentations")
            msg.exec()
            return

        compareSegmentVersionsWindow = CompareSegmentVersionsWindow(
            self, segmentationInformation_df)
        compareSegmentVersionsWindow.show()


    @enter_function
    def compareSegmentVersions(self,
                               selected_label,
                               selected_version_file_paths):
        """
        CompareSegmentVersions.
        
        Args:
        selected_label: Description of selected_label.
        selected_version_file_paths: Description of selected_version_file_paths.
        """
        self.labelOfCompareSegmentVersions = selected_label
        self.colorsSelectedVersionFilePathsForCompareSegmentVersions = {}

        selected_label_value = 0
        for label in self.config_yaml['labels']:
            if selected_label == label['name']:
                selected_label_value = label['value']

        slicer.mrmlScene.Clear()
        slicer.util.loadVolume(self.currentCasePath)
        self.VolumeNode = \
            slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')[0]

        Vol_displayNode = self.VolumeNode.GetDisplayNode()
        Vol_displayNode.AutoWindowLevelOff()
        if ConfigPath.MODALITY == 'CT':
            Debug.print(self, 'MODALITY==CT')
            Vol_displayNode.SetWindow(ConfigPath.CT_WINDOW_WIDTH)
            Vol_displayNode.SetLevel(ConfigPath.CT_WINDOW_LEVEL)
        Vol_displayNode.SetInterpolate(ConfigPath.INTERPOLATE_VALUE)

        self.segmentEditorWidget = (
            slicer.modules.segmenteditor.widgetRepresentation().self().editor)
        self.segmentEditorWidget.setActiveEffectByName("No editing")

        self.resetTimer()

        for (
                segment_name,
                version_file_path) in selected_version_file_paths.items():
            if 'nrrd' in ConfigPath.INPUT_FILE_EXTENSION:
                slicer.util.loadSegmentation(version_file_path)
                currentSegmentationNode = \
                    slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
            elif 'nii' in ConfigPath.INPUT_FILE_EXTENSION:
                labelmapVolumeNode = slicer.util.loadLabelVolume(
                    version_file_path)
                currentSegmentationNode = slicer.mrmlScene.AddNewNodeByClass(
                    "vtkMRMLSegmentationNode")
                slicer.modules.segmentations.logic(

                ).ImportLabelmapToSegmentationNode(
                    labelmapVolumeNode, currentSegmentationNode)

            self.segmentEditorWidget = (
                slicer.modules.segmenteditor.widgetRepresentation().self(

                ).editor)
            self.segmentEditorNode = (
                self.segmentEditorWidget.mrmlSegmentEditorNode())
            self.segmentEditorWidget.setSegmentationNode(
                currentSegmentationNode)
            self.segmentEditorWidget.setSourceVolumeNode(self.VolumeNode)
            (currentSegmentationNode
            .SetReferenceImageGeometryParameterFromVolumeNode(
                self.VolumeNode))
            segmentationDisplayNode = currentSegmentationNode.GetDisplayNode()
            segmentationDisplayNode.SetAllSegmentsVisibility(False)

            currentSegmentationNode.SetName(
                os.path.split(version_file_path)[1].split('.')[0])

            segment = currentSegmentationNode.GetSegmentation().GetSegment(
                str(selected_label_value))

            if segment is not None:
                segment.SetName(segment_name)

                # OBTAIN RANDOM BRIGHT COLOR :
                # https://stackoverflow.com/questions/43437309/get-a-bright
                # -random-colour-python
                h, s, l = (random.random(), 0.5 + random.random() / 2.0,
                           0.4 + random.random() / 5.0)
                r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
                self.colorsSelectedVersionFilePathsForCompareSegmentVersions[
                    segment_name] = [r, g, b]
                segment.SetColor(r / 255, g / 255, b / 255)

                segmentationDisplayNode.SetSegmentVisibility(
                    str(selected_label_value), True)

        self.disableSegmentAndPaintButtons()
        self.disablePauseTimerButton()
        self.ui.StartTimerButton.setEnabled(False)
        self.ui.StartTimerButton.setStyleSheet("background-color : light gray")
        self.ui.CompareSegmentVersions.setText(
            'Clear Read Only Segment Versions')
        self.ui.CompareSegmentVersions.setStyleSheet(
            "background-color : yellowgreen")
        self.ui.SaveSegmentationButton.setEnabled(False)

        self.ui.ShowSegmentVersionLegendButton.setVisible(True)


    @enter_function
    def onClearCompareSegmentVersions(self):
        """
        OnClearCompareSegmentVersions.
        
        Args:.
        """
        self.loadPatient()

        self.enableStartTimerButton()

        self.ui.CompareSegmentVersions.setText('Compare segment versions')
        self.ui.CompareSegmentVersions.setStyleSheet(
            "background-color : light gray")

        self.ui.SaveSegmentationButton.setEnabled(True)

        self.ui.ShowSegmentVersionLegendButton.setVisible(False)


    @enter_function
    def loadSegmentation(self, absolute_path_to_segmentation_file):
        """
        LoadSegmentation.
        
        Args:
        absolute_path_to_segmentation_file: Description of absolute_path_to_segmentation_file.
        """
        if 'nrrd' in ConfigPath.INPUT_FILE_EXTENSION:
            slicer.util.loadSegmentation(absolute_path_to_segmentation_file)
            self.segmentationNode = \
                slicer.util.getNodesByClass('vtkMRMLSegmentationNode')[0]
        elif 'nii' in ConfigPath.INPUT_FILE_EXTENSION:
            labelmapVolumeNode = slicer.util.loadLabelVolume(
                absolute_path_to_segmentation_file)
            self.segmentationNode = slicer.mrmlScene.AddNewNodeByClass(
                "vtkMRMLSegmentationNode")
            slicer.modules.segmentations.logic(

            ).ImportLabelmapToSegmentationNode(
                labelmapVolumeNode, self.segmentationNode)

        # Version 5.8.1 requires different handling of segment IDs than previous
        self.fix_segment_ids_and_names(self.segmentationNode,
                                        self.config_yaml["labels"])

        self.segmentEditorWidget = (
            slicer.modules.segmenteditor.widgetRepresentation().self().editor)

        self.segmentEditorNode = (
            self.segmentEditorWidget.mrmlSegmentEditorNode())

        self.segmentEditorWidget.setSegmentationNode(self.segmentationNode)
        self.segmentEditorWidget.setSourceVolumeNode(self.VolumeNode)

        # set refenrence geometry to Volume node
        self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(
            self.VolumeNode)

        nn = self.segmentationNode.GetDisplayNode()

        # set Segmentation visible:
        nn.SetAllSegmentsVisibility(True)

        loaded_segment_ids = (
            self.segmentationNode.GetSegmentation().GetSegmentIDs())


        list_of_segment_names = self.getAllSegmentNames()
        for label in self.config_yaml["labels"]:
            if label['name'] not in list_of_segment_names:
                self.onNewLabelSegm(label["name"], label["color_r"],
                                    label["color_g"], label["color_b"],
                                    label["lower_bound_HU"],
                                    label["upper_bound_HU"])

        for segment_id in loaded_segment_ids:
            for label in self.config_yaml["labels"]:
                if str(segment_id) == str(label['value']) or str(
                        segment_id) == str(label['name']):
                    self.segmentationNode.GetSegmentation().SetSegmentIndex(
                        str(segment_id), label['value'] - 1)

    @enter_function
    def fix_segment_ids_and_names(self, segmentationNode, config_labels):
        """
        Fix segment IDs and names based on the YAML config.
        Replaces UID-based segment IDs with label['value'] (as string).

        Args:
            segmentationNode = segmentation node that is displayed
            config_labels = labels in the config yaml file.

        """
        segmentation = segmentationNode.GetSegmentation()
        segments_to_add = []

        segment_ids = list(segmentation.GetSegmentIDs())
        for old_id in segment_ids:
            segment = segmentation.GetSegment(old_id)
            old_name = segment.GetName()

            for label in config_labels:
                # If the name or old ID matches a label value or name
                if old_name == str(label["value"]) or old_name == label["name"]:
                    # Deep copy the segment
                    new_segment = vtk.vtkSegment()
                    new_segment.DeepCopy(segment)

                    # Set correct name and color
                    new_segment.SetName(label["name"])
                    new_segment.SetColor(label["color_r"] / 255,
                                         label["color_g"] / 255,
                                         label["color_b"] / 255)

                    # Use the label value as the segment ID (string)
                    new_id = str(label["value"])
                    segments_to_add.append((new_id, new_segment))

                    # Remove the old segment
                    segmentation.RemoveSegment(old_id)
                    break  # stop checking labels once matched

        for new_id, segment in segments_to_add:
            segmentation.AddSegment(segment, new_id)
            segmentation.SetSegmentIndex(new_id, int(new_id) - 1)

    @enter_function
    def replace_segments(self, latest_version_path):
        """
        Set segments loaded from latest_version_available to current segment,
        enabling edition.
        :param latest_version_path: path of latest version available.
        """
        segmentation_node = Dev.get_segmentation_node(self)

        # Load the segmentation into a temporary node
        temporary_segmentation_node = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLSegmentationNode", "TemporarySegmentation")

        if latest_version_path.endswith(".nrrd"):
            slicer.util.loadSegmentation(latest_version_path,
                                         temporary_segmentation_node)

        elif (latest_version_path.endswith(".nii")
              or latest_version_path.endswith(".nii.gz")):
            labelmap_volume_node = (
                slicer.util.loadLabelVolume(latest_version_path))

            slicer.modules.segmentations.logic(

            ).ImportLabelmapToSegmentationNode(
                labelmap_volume_node, temporary_segmentation_node
            )

            slicer.mrmlScene.RemoveNode(
                labelmap_volume_node)  # Remove labelmap after import

        # Get the segmentation object from the nodes
        temp_segmentation = temporary_segmentation_node.GetSegmentation()
        target_segmentation = segmentation_node.GetSegmentation()

        # Clear existing segments in the target node
        segment_ids = [target_segmentation.GetNthSegmentID(i) for i in
                       range(target_segmentation.GetNumberOfSegments())]
        for segment_id in segment_ids:
            target_segmentation.RemoveSegment(segment_id)

        # Copy segments from the temporary node to the target node
        for i in range(temp_segmentation.GetNumberOfSegments()):
            segment = temp_segmentation.GetNthSegment(i)
            target_segmentation.AddSegment(segment)
            for label in self.config_yaml["labels"]:
                # Ensure that you compare the label value to the segment's
                # name correctly
                if str(label["value"]) == str(segment.GetName()):
                    # Get the segment ID using the segment's name
                    segment.SetName(label["name"])
                    rgb_r = label["color_r"] / 255
                    rgb_g = label["color_g"] / 255
                    rgb_b = label["color_b"] / 255
                    segment.SetColor(rgb_r, rgb_g, rgb_b)

        # Remove the temporary node
        slicer.mrmlScene.RemoveNode(temporary_segmentation_node)

        # Get current list of segment names in the active segmentation
        existing_segment_names = set()
        for sid in segmentation_node.GetSegmentation().GetSegmentIDs():
            existing_segment_names.add(
                segmentation_node.GetSegmentation().GetSegment(sid).GetName())

        # Loop over config labels, and if one is missing, add it as an empty segment
        for label in self.config_yaml["labels"]:
            if label["name"] not in existing_segment_names:
                self.onNewLabelSegm(label["name"],
                                    label["color_r"],
                                    label["color_g"],
                                    label["color_b"],
                                    label["lower_bound_HU"],
                                    label["upper_bound_HU"])

        self.re_order_segments(segmentation_node)

    @enter_function
    def getAllSegmentNames(self):
        """
        GetAllSegmentNames.

        Args:.
        """
        segment_ids = self.segmentationNode.GetSegmentation().GetSegmentIDs()
        segment_names = []
        for sid in segment_ids:
            segment = self.segmentationNode.GetSegmentation().GetSegment(sid)
            segment_names.append(segment.GetName())
        return segment_names

    @enter_function
    def onPushDefaultMin(self):
        """
        OnPushDefaultMin.
        
        Args:.
        """
        fresh_config = ConfigPath.open_project_config_file()
        self.config_yaml["labels"][self.current_label_index][
            "lower_bound_HU"] = \
            fresh_config["labels"][self.current_label_index]["lower_bound_HU"]
        self.setUpperAndLowerBoundHU(
            self.config_yaml["labels"][self.current_label_index][
                "lower_bound_HU"],
            self.config_yaml["labels"][self.current_label_index][
                "upper_bound_HU"])


    @enter_function
    def onPushDefaultMax(self):
        """
        OnPushDefaultMax.
        
        Args:.
        """
        fresh_config = ConfigPath.open_project_config_file()
        self.config_yaml["labels"][self.current_label_index][
            "upper_bound_HU"] = \
            fresh_config["labels"][self.current_label_index]["upper_bound_HU"]
        self.setUpperAndLowerBoundHU(
            self.config_yaml["labels"][self.current_label_index][
                "lower_bound_HU"],
            self.config_yaml["labels"][self.current_label_index][
                "upper_bound_HU"])

    @enter_function
    def onPush_ShowSegmentVersionLegendButton(self):
        """
        OnPush_ShowSegmentVersionLegendButton.
        
        Args:.
        """
        import pandas as pd

        segmentationInformationPath = (f'{self.currentOutputPath}{os.sep}'
                                       f'{self.currentVolumeFilename}'
                                       f'_SegmentationInformation.csv')

        segmentationInformation_df = None
        if os.path.exists(segmentationInformationPath):
            segmentationInformation_df = pd.read_csv(
                segmentationInformationPath)
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Information)
            msg.setText("No saved segmentations")
            msg.setInformativeText(
                'There are no segmentations saved in the '
                'SegmentationInformation.csv.')
            msg.setWindowTitle("No saved segmentations")
            msg.exec()
            return

        showSegmentVersionLegendWindow = (
            ShowSegmentVersionLegendWindow(self, segmentationInformation_df))
        showSegmentVersionLegendWindow.show()

    @enter_function
    def onPushButton_undo(self):
        """
        OnPushButton_undo.
        
        Args:.
        """
        if self.previousAction == 'segmentation':
            self.segmentEditorWidget.undo()

        elif self.previousAction == 'markups':
            # Get the last added markup node (or customize based on specific
            # markup type)
            markupsNodeList = slicer.mrmlScene.GetNodesByClass(
                "vtkMRMLMarkupsNode")
            markupsNodeList.InitTraversal()

            lastMarkupNode = None

            while True:
                markupNode = markupsNodeList.GetNextItemAsObject()
                if markupNode:
                    lastMarkupNode = markupNode  # Keep track of the last
                    # markup node
                else:
                    break

            # Remove the last control point from the markup node (or remove the
            # whole node if needed)
            if lastMarkupNode and lastMarkupNode.GetNumberOfControlPoints() > 0:
                lastMarkupNode.RemoveNthControlPoint(
                    lastMarkupNode.GetNumberOfControlPoints() - 1)
            else:
                slicer.mrmlScene.RemoveNode(
                    lastMarkupNode)  # Remove the whole markup node if no
                # points remain

            removedNode = self.lineDetails.pop(lastMarkupNode.GetName())


    @enter_function
    def onDropDownButton_label_select(self, value):
        """
        OnDropDownButton_label_select.
        
        Args:
        value: Description of value.
        """
        self.current_label_index = value
        label = self.config_yaml["labels"][value]
        self.setUpperAndLowerBoundHU(label["lower_bound_HU"],
                                     label["upper_bound_HU"])

        label_name = label["name"]
        try:
            segment_name = label_name
            self.onPushButton_select_label(segment_name,
                                           label["lower_bound_HU"],
                                           label["upper_bound_HU"])
        except:
            pass


    @enter_function
    def onPushLassoPaint(self):
        """
        OnPushLassoPaint.
        
        Args:.
        """
        self.startTimerForActions()
        self.previousAction = 'segmentation'
        self.ensure_active_segment_is_selected()
        self.segmentEditorWidget.setActiveEffectByName("Scissors")
        self.segmentEditorNode.SetMasterVolumeIntensityMask(False)
        effect = self.segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "FillInside")
        effect.setParameter("Shape", "FreeForm")
        effect.setSliceCutMode(3)

    @enter_function
    def onPushButton_Paint(self):
        """
        OnPushButton_Paint.
        
        Args:.
        """
        self.startTimerForActions()
        self.previousAction = 'segmentation'
        self.ensure_active_segment_is_selected()
        self.segmentEditorWidget.setActiveEffectByName("Paint")
        # Note it seems that sometimes you need to activate the effect first
        # with :
        # Assign effect to the segmentEditorWidget using the active effect
        self.effect = self.segmentEditorWidget.activeEffect()
        self.effect.activate()
        self.effect.setParameter('BrushSphere', 1)
        # Seems that you need to activate the effect to see it in Slicer
        # Set up the mask parameters (note that PaintAllowed...was changed to
        # EditAllowed)
        self.segmentEditorNode.SetMaskMode(
            slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)
        # Set if using Editable intensity range (the range is defined below
        # using object.setParameter)
        self.set_master_volume_intensity_mask_according_to_modality()
        self.segmentEditorNode.SetSourceVolumeIntensityMaskRange(self.LB_HU,
                                                                 self.UB_HU)
        self.segmentEditorNode.SetOverwriteMode(
            slicer.vtkMRMLSegmentEditorNode.OverwriteAllSegments)


    @enter_function
    def ensure_active_segment_is_selected(self):
        """
        Ensure_active_segment_is_selected.
        
        Args:.
        """
        # Make sure a valid segment is selected
        selected_segment_id = self.segmentationNode.GetSegmentation(

        ).GetSegmentIdBySegmentName(
            self.config_yaml["labels"][self.current_label_index]['name']
        )
        self.segmentEditorNode.SetSelectedSegmentID(selected_segment_id)


    @enter_function
    def toggleFillButton(self):
        """
        ToggleFillButton.
        
        Args:.
        """
        self.startTimerForActions()
        self.previousAction = 'segmentation'
        if self.ui.pushButton_ToggleFill.isChecked():
            self.ui.pushButton_ToggleFill.setStyleSheet(
                f"background-color : {self.color_active}")
            self.ui.pushButton_ToggleFill.setText('Fill: ON')
            self.segmentationNode.GetDisplayNode().SetOpacity2DFill(100)
        else:
            self.ui.pushButton_ToggleFill.setStyleSheet(
                f"background-color : {self.color_inactive}")
            self.ui.pushButton_ToggleFill.setText('Fill: OFF')
            self.segmentationNode.GetDisplayNode().SetOpacity2DFill(0)


    @enter_function
    def onPushButton_ToggleVisibility(self):
        """
        Toggle visibility of segments in the slicer viewer.
        """

        Debug.print(self, f'ToggleVisibility: '
                          f' {self.ui.pushButton_ToggleVisibility.isChecked()}')

        if self.ui.pushButton_ToggleVisibility.isChecked():
            self.segmentationNode.GetDisplayNode(

            ).SetAllSegmentsVisibility(True)
            self.ui.pushButton_ToggleVisibility.setStyleSheet(
                f"background-color : {self.color_active}")

        else:
            self.segmentationNode.GetDisplayNode(

            ).SetAllSegmentsVisibility(False)
            self.ui.pushButton_ToggleVisibility.setStyleSheet(
                f"background-color : {self.color_inactive}")
            self.mask_visible_flag_level2 = False


    @enter_function
    def togglePaintMask(self):
        """
        TogglePaintMask.
        
        Args:.
        """
        if self.ui.pushButton_TogglePaintMask.isChecked():
            self.ui.pushButton_TogglePaintMask.setStyleSheet(
                f"background-color : {self.color_active}")
            self.ui.pushButton_TogglePaintMask.setText('Paint Mask ON')
            self.segmentEditorNode.SetMaskMode(
                slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)


    @enter_function
    def onPushButton_segmeditor(self):
        """
        OnPushButton_segmeditor.
        
        Args:.
        """
        self.startTimerForActions()
        slicer.util.selectModule("SegmentEditor")


    @enter_function
    def onPushButton_Erase(self):
        """
        OnPushButton_Erase.
        
        Args:.
        """
        self.startTimerForActions()
        self.previousAction = 'segmentation'

        # Make sure a valid segment is selected
        self.ensure_active_segment_is_selected()

        self.segmentEditorWidget.setActiveEffectByName("Erase")
        # Note it seems that sometimes you need to activate the effect first
        # with : Assign effect to the segmentEditorWidget using the active
        # effect
        self.effect = self.segmentEditorWidget.activeEffect()
        # Seems that you need to activate the effect to see it in Slicer
        self.effect.activate()
        self.segmentEditorNode.SetMasterVolumeIntensityMask(False)


    @enter_function
    def onPushButton_Smooth(self):
        """
        OnPushButton_Smooth.
        
        Args:.
        """
        # pass
        # Smoothing
        self.startTimerForActions()
        self.previousAction = 'segmentation'
        self.ensure_active_segment_is_selected()
        self.segmentEditorWidget = (
            slicer.modules.segmenteditor.widgetRepresentation().self().editor)
        self.segmentEditorWidget.setActiveEffectByName("Smoothing")
        effect = self.segmentEditorWidget.activeEffect()
        effect.setParameter("SmoothingMethod", "MEDIAN")
        effect.setParameter("KernelSizeMm", 3)
        effect.self().onApply()


    @enter_function
    def onPlacePointsAndConnect(self):
        """
        OnPlacePointsAndConnect.
        
        Args:.
        """
        self.startTimerForActions()
        self.previousAction = 'markups'
        self.lineNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsLineNode")

        sht = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLMarkupsLineNode')

        lineName = f"Line_{sht}"
        self.lineNode.SetName(lineName)

        slicer.modules.markups.logic().SetActiveListID(self.lineNode)

        interactionNode = slicer.mrmlScene.GetNodeByID(
            "vtkMRMLInteractionNodeSingleton")
        interactionNode.SetCurrentInteractionMode(interactionNode.Place)

        self.lineNode.AddObserver(self.lineNode.PointModifiedEvent,
                                  self.onLinePlaced)


    @enter_function
    def onLinePlaced(self, caller, event):
        """
        OnLinePlaced.
        
        Args:
        caller: Description of caller.
        event: Description of event.
        """
        if caller.GetNumberOfControlPoints() < 2:
            return

        # Retrieve the control point coordinates after the user places the
        # points
        p1 = [0, 0, 0]
        p2 = [0, 0, 0]
        caller.GetNthControlPointPosition(0, p1)  # First control point
        caller.GetNthControlPointPosition(1, p2)  # Second control point

        lineLength = caller.GetLineLengthWorld()
        lineName = caller.GetName()

        self.lineDetails[lineName] = {
            "ControlPoint1": p1,
            "ControlPoint2": p2,
            "Length": lineLength
        }

    @enter_function
    def onPushButton_Small_holes(self):
        """
        OnPushButton_Small_holes.
        
        Args:.
        """
        # pass
        # Fill holes smoothing
        self.startTimerForActions()
        self.segmentEditorWidget = (
            slicer.modules.segmenteditor.widgetRepresentation().self().editor)
        self.segmentEditorWidget.setActiveEffectByName("Smoothing")
        effect = self.segmentEditorWidget.activeEffect()
        effect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
        effect.setParameter("KernelSizeMm", 3)
        effect.self().onApply()


    @enter_function
    def onLB_HU(self):
        """
        OnLB_HU.
        
        Args:.
        """
        try:
            self.LB_HU = self.ui.LB_HU.value
            self.set_master_volume_intensity_mask_according_to_modality()
            self.segmentEditorNode.SetSourceVolumeIntensityMaskRange(self.LB_HU,
                                                                     self.UB_HU)
            self.config_yaml["labels"][self.current_label_index][
                "lower_bound_HU"] = self.LB_HU
        except:
            pass


    @enter_function
    def onUB_HU(self):
        """
        OnUB_HU.
        
        Args:.
        """
        try:
            self.UB_HU = self.ui.UB_HU.value
            self.set_master_volume_intensity_mask_according_to_modality()
            self.segmentEditorNode.SetSourceVolumeIntensityMaskRange(self.LB_HU,
                                                                     self.UB_HU)
            self.config_yaml["labels"][self.current_label_index][
                "upper_bound_HU"] = self.UB_HU
        except:
            pass