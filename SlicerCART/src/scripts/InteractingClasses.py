"""
    This InteractingClasses file contains all classes that iteratively
    interact with each other. This is essential to avoid 'cirular imports'. It
    should be the only file in scripts folder that contains more than one class.
"""

###############################################################################
# This import needs to be done in each script file for appropriate use.
from utils import *

###############################################################################

###############################################################################
# This main script contains the following classes, used for configuration:
#   SlicerCARTConfigurationSetupWindow
#   SlicerCARTConfigurationInitialWindow
#   ConfigureSegmentationWindow
#   ConfigureSingleLabelWindow
#   ConfigureClassificationWindow
#   ConfigureSingleClassificationItemWindow

###############################################################################

class SlicerCARTConfigurationSetupWindow(qt.QWidget):
    @enter_function
    def __init__(self, segmenter, conf_folder_path=None, edit_conf=False,
                 parent=None):
        """
        __init__

        Args:
            segmenter: Description of segmenter.
            conf_folder_path: Description of conf_folder_path.
            edit_conf: Description of edit_conf.
            parent: Description of parent.
        """
        super(SlicerCARTConfigurationSetupWindow, self).__init__(parent)

        self.edit_conf = edit_conf

        if conf_folder_path is not None:
            shutil.copy(f'{conf_folder_path}{os.sep}{CONFIG_COPY_FILENAME}',
                        CONFIG_FILE_PATH)

        self.config_yaml = ConfigPath.open_project_config_file()

        self.set_default_values()

        self.segmenter = segmenter

        layout = qt.QVBoxLayout()

        task_button_hbox = qt.QHBoxLayout()

        task_button_hbox_label = qt.QLabel()
        task_button_hbox_label.setText('Task : ')
        task_button_hbox_label.setStyleSheet("font-weight: bold")

        self.segmentation_task_checkbox = qt.QCheckBox()
        self.segmentation_task_checkbox.setText('Segmentation')

        self.classification_task_checkbox = qt.QCheckBox()
        self.classification_task_checkbox.setText('Classification')

        task_button_hbox.addWidget(task_button_hbox_label)
        task_button_hbox.addWidget(self.segmentation_task_checkbox)
        task_button_hbox.addWidget(self.classification_task_checkbox)

        layout.addLayout(task_button_hbox)

        modality_hbox = qt.QHBoxLayout()

        modality_hbox_label = qt.QLabel()
        modality_hbox_label.setText('Modality : ')
        modality_hbox_label.setStyleSheet("font-weight: bold")

        self.ct_modality_radio_button = qt.QRadioButton('CT', self)
        self.mri_modality_radio_button = qt.QRadioButton('MRI', self)

        modality_hbox.addWidget(modality_hbox_label)
        modality_hbox.addWidget(self.ct_modality_radio_button)
        modality_hbox.addWidget(self.mri_modality_radio_button)

        layout.addLayout(modality_hbox)

        bids_hbox = qt.QHBoxLayout()

        self.bids_hbox_label = qt.QLabel()
        self.bids_hbox_label.setText('Impose BIDS ? ')
        self.bids_hbox_label.setStyleSheet("font-weight: bold")
        bids_hbox.addWidget(self.bids_hbox_label)

        self.bids_combobox = qt.QComboBox()
        self.bids_combobox.addItem('Yes')
        self.bids_combobox.addItem('No')

        bids_hbox.addWidget(self.bids_combobox)

        layout.addLayout(bids_hbox)

        file_extension_hbox = qt.QHBoxLayout()

        self.file_extension_label = qt.QLabel()
        self.file_extension_label.setText('Input File Extension : ')
        self.file_extension_label.setStyleSheet("font-weight: bold")
        file_extension_hbox.addWidget(self.file_extension_label)

        self.file_extension_combobox = qt.QComboBox()
        self.file_extension_combobox.addItem('*.nii.gz')
        self.file_extension_combobox.addItem('*.nrrd')

        file_extension_hbox.addWidget(self.file_extension_combobox)

        layout.addLayout(file_extension_hbox)

        initial_view_hbox = qt.QHBoxLayout()

        self.initial_view_label = qt.QLabel()
        self.initial_view_label.setText('Initial View : ')
        self.initial_view_label.setStyleSheet("font-weight: bold")
        initial_view_hbox.addWidget(self.initial_view_label)

        self.initial_view_combobox = qt.QComboBox()
        self.initial_view_combobox.addItem('Red (axial)')
        self.initial_view_combobox.addItem('Yellow (sagittal)')
        self.initial_view_combobox.addItem('Green (coronal)')

        initial_view_hbox.addWidget(self.initial_view_combobox)

        layout.addLayout(initial_view_hbox)

        interpolate_hbox = qt.QHBoxLayout()

        self.interpolate_label = qt.QLabel()
        self.interpolate_label.setText('Interpolate Image? ')
        self.interpolate_label.setStyleSheet("font-weight: bold")
        interpolate_hbox.addWidget(self.interpolate_label)

        self.interpolate_combobox = qt.QComboBox()
        self.interpolate_combobox.addItem('No')
        self.interpolate_combobox.addItem('Yes')

        interpolate_hbox.addWidget(self.interpolate_combobox)

        layout.addLayout(interpolate_hbox)

        ct_window_level_hbox = qt.QHBoxLayout()

        self.ct_window_level_label = qt.QLabel()
        self.ct_window_level_label.setText('Window Level : ')
        self.ct_window_level_label.setStyleSheet("font-weight: bold")
        ct_window_level_hbox.addWidget(self.ct_window_level_label)

        self.ct_window_level_line_edit = qt.QLineEdit(
            self.ct_window_level_selected)
        onlyInt = qt.QIntValidator()
        self.ct_window_level_line_edit.setValidator(onlyInt)
        self.ct_window_level_line_edit.setInputMask("0000")
        ct_window_level_hbox.addWidget(self.ct_window_level_line_edit)

        layout.addLayout(ct_window_level_hbox)

        ct_window_width_hbox = qt.QHBoxLayout()

        self.ct_window_width_label = qt.QLabel()
        self.ct_window_width_label.setText('Window Width : ')
        self.ct_window_width_label.setStyleSheet("font-weight: bold")
        ct_window_width_hbox.addWidget(self.ct_window_width_label)

        self.ct_window_width_line_edit = qt.QLineEdit(
            self.ct_window_width_selected)
        self.ct_window_width_line_edit.setValidator(onlyInt)
        self.ct_window_width_line_edit.setInputMask("0000")
        ct_window_width_hbox.addWidget(self.ct_window_width_line_edit)

        layout.addLayout(ct_window_width_hbox)

        keyboard_shortcuts_hbox = qt.QHBoxLayout()

        keyboard_shortcuts_label = qt.QLabel('Use Custom Keyboard Shortcuts? ')
        keyboard_shortcuts_label.setStyleSheet("font-weight: bold")
        keyboard_shortcuts_hbox.addWidget(keyboard_shortcuts_label)

        self.keyboard_shortcuts_checkbox = qt.QCheckBox()
        keyboard_shortcuts_hbox.addWidget(self.keyboard_shortcuts_checkbox)

        layout.addLayout(keyboard_shortcuts_hbox)

        toggle_fill_ks_hbox = qt.QHBoxLayout()

        self.toggle_fill_ks_label = qt.QLabel()
        self.toggle_fill_ks_label.setText('Toggle Fill Keyboard Shortcut : ')
        self.toggle_fill_ks_label.setStyleSheet("font-style: italic")
        toggle_fill_ks_hbox.addWidget(self.toggle_fill_ks_label)

        self.toggle_fill_ks_line_edit = qt.QLineEdit(
            self.toggle_fill_ks_selected)
        self.toggle_fill_ks_line_edit.setMaxLength(1)
        toggle_fill_ks_hbox.addWidget(self.toggle_fill_ks_line_edit)

        layout.addLayout(toggle_fill_ks_hbox)

        toggle_visibility_ks_hbox = qt.QHBoxLayout()

        self.toggle_visibility_ks_label = qt.QLabel()
        self.toggle_visibility_ks_label.setText(
            'Toggle Visibility Keyboard Shortcut : ')
        self.toggle_visibility_ks_label.setStyleSheet("font-style: italic")
        toggle_visibility_ks_hbox.addWidget(self.toggle_visibility_ks_label)

        self.toggle_visibility_ks_line_edit = qt.QLineEdit(
            self.toggle_visibility_ks_selected)
        self.toggle_visibility_ks_line_edit.setMaxLength(1)
        toggle_visibility_ks_hbox.addWidget(self.toggle_visibility_ks_line_edit)

        layout.addLayout(toggle_visibility_ks_hbox)

        undo_ks_hbox = qt.QHBoxLayout()

        self.undo_ks_label = qt.QLabel()
        self.undo_ks_label.setText('Undo Keyboard Shortcut : ')
        self.undo_ks_label.setStyleSheet("font-style: italic")
        undo_ks_hbox.addWidget(self.undo_ks_label)

        self.undo_ks_line_edit = qt.QLineEdit(self.undo_ks_selected)
        self.undo_ks_line_edit.setMaxLength(1)
        undo_ks_hbox.addWidget(self.undo_ks_line_edit)

        layout.addLayout(undo_ks_hbox)

        save_seg_ks_hbox = qt.QHBoxLayout()

        self.save_seg_ks_label = qt.QLabel()
        self.save_seg_ks_label.setText('Save Segmentation Keyboard Shortcut : ')
        self.save_seg_ks_label.setStyleSheet("font-style: italic")
        save_seg_ks_hbox.addWidget(self.save_seg_ks_label)

        self.save_seg_ks_line_edit = qt.QLineEdit(self.save_seg_ks_selected)
        self.save_seg_ks_line_edit.setMaxLength(1)
        save_seg_ks_hbox.addWidget(self.save_seg_ks_line_edit)

        layout.addLayout(save_seg_ks_hbox)

        smooth_ks_hbox = qt.QHBoxLayout()

        self.smooth_ks_label = qt.QLabel()
        self.smooth_ks_label.setText('Smooth Margins Keyboard Shortcut : ')
        self.smooth_ks_label.setStyleSheet("font-style: italic")
        smooth_ks_hbox.addWidget(self.smooth_ks_label)

        self.smooth_ks_line_edit = qt.QLineEdit(self.smooth_ks_selected)
        self.smooth_ks_line_edit.setMaxLength(1)
        smooth_ks_hbox.addWidget(self.smooth_ks_line_edit)

        layout.addLayout(smooth_ks_hbox)

        remove_small_holes_ks_hbox = qt.QHBoxLayout()

        self.remove_small_holes_ks_label = qt.QLabel()
        self.remove_small_holes_ks_label.setText(
            'Remove Small Holes Keyboard Shortcut : ')
        self.remove_small_holes_ks_label.setStyleSheet("font-style: italic")
        remove_small_holes_ks_hbox.addWidget(self.remove_small_holes_ks_label)

        self.remove_small_holes_ks_line_edit = qt.QLineEdit(
            self.remove_small_holes_ks_selected)
        self.remove_small_holes_ks_line_edit.setMaxLength(1)
        remove_small_holes_ks_hbox.addWidget(
            self.remove_small_holes_ks_line_edit)

        layout.addLayout(remove_small_holes_ks_hbox)

        interpolate_ks_hbox = qt.QHBoxLayout()

        self.interpolate_ks_label = qt.QLabel()
        self.interpolate_ks_label.setText(
            'Interpolate Image Keyboard Shortcut : ')
        self.interpolate_ks_label.setStyleSheet("font-style: italic")
        interpolate_ks_hbox.addWidget(self.interpolate_ks_label)

        self.interpolate_ks_line_edit = qt.QLineEdit(
            self.interpolate_ks_selected)
        self.interpolate_ks_line_edit.setMaxLength(1)
        interpolate_ks_hbox.addWidget(self.interpolate_ks_line_edit)

        layout.addLayout(interpolate_ks_hbox)

        mouse_shortcuts_hbox = qt.QHBoxLayout()

        mouse_shortcuts_label = qt.QLabel('Use Custom Mouse Shortcuts? ')
        mouse_shortcuts_label.setStyleSheet("font-weight: bold")
        mouse_shortcuts_hbox.addWidget(mouse_shortcuts_label)

        self.mouse_shortcuts_checkbox = qt.QCheckBox()
        mouse_shortcuts_hbox.addWidget(self.mouse_shortcuts_checkbox)

        layout.addLayout(mouse_shortcuts_hbox)
        self.configure_segmentation_button = qt.QPushButton(
            'Configure Segmentation...')
        self.configure_segmentation_button.setStyleSheet(
            "background-color : yellowgreen")
        layout.addWidget(self.configure_segmentation_button)

        self.configure_classification_button = qt.QPushButton(
            'Configure Classification...')
        self.configure_classification_button.setStyleSheet(
            "background-color : yellowgreen")
        layout.addWidget(self.configure_classification_button)

        self.previous_button = qt.QPushButton('Previous')
        layout.addWidget(self.previous_button)

        self.apply_button = qt.QPushButton('Apply')
        layout.addWidget(self.apply_button)

        self.cancel_button = qt.QPushButton('Cancel')
        layout.addWidget(self.cancel_button)

        self.connect_buttons_to_callbacks()

        if self.edit_conf:
            self.disableWidgetsForEditConfiguration()

        self.setLayout(layout)
        self.setWindowTitle("Configure SlicerCART")
        self.resize(800, 200)

    @enter_function
    def disableWidgetsForEditConfiguration(self):
        """
        disableWidgetsForEditConfiguration

        Args:
        """
        self.classification_task_checkbox.setEnabled(False)
        self.segmentation_task_checkbox.setEnabled(False)

        if self.bids_selected == False:
            self.bids_combobox.setEnabled(False)

        self.file_extension_combobox.setEnabled(False)
        self.ct_modality_radio_button.setEnabled(False)
        self.mri_modality_radio_button.setEnabled(False)
        self.previous_button.setVisible(False)

    @enter_function
    def connect_buttons_to_callbacks(self):
        """
        connect_buttons_to_callbacks

        Args:
        """
        self.segmentation_task_checkbox.stateChanged.connect(
            self.segmentation_checkbox_state_changed)
        self.classification_task_checkbox.stateChanged.connect(
            self.classification_checkbox_state_changed)
        self.keyboard_shortcuts_checkbox.stateChanged.connect(
            self.keyboard_shortcuts_checkbox_state_changed)
        self.ct_modality_radio_button.toggled.connect(
            lambda: self.update_selected_modality(
                self.ct_modality_radio_button.text))
        self.mri_modality_radio_button.toggled.connect(
            lambda: self.update_selected_modality(
                self.mri_modality_radio_button.text))
        self.bids_combobox.currentIndexChanged.connect(self.update_bids)
        self.file_extension_combobox.currentIndexChanged.connect(
            self.update_file_extension)
        self.initial_view_combobox.currentIndexChanged.connect(
            self.update_initial_view)
        self.interpolate_combobox.currentIndexChanged.connect(
            self.update_interpolate)
        self.ct_window_level_line_edit.textChanged.connect(
            self.update_ct_window_level)
        self.ct_window_width_line_edit.textChanged.connect(
            self.update_ct_window_width)
        self.toggle_fill_ks_line_edit.textChanged.connect(
            self.update_toggle_fill_ks)
        self.toggle_visibility_ks_line_edit.textChanged.connect(
            self.update_toggle_visibility_ks)

        self.undo_ks_line_edit.textChanged.connect(self.update_undo_ks)
        self.save_seg_ks_line_edit.textChanged.connect(self.update_save_seg_ks)
        self.smooth_ks_line_edit.textChanged.connect(self.update_smooth_ks)

        self.remove_small_holes_ks_line_edit.textChanged.connect(
            self.update_remove_small_holes_ks)
        self.interpolate_ks_line_edit.textChanged.connect(
            self.update_interpolate_ks)
        self.configure_classification_button.clicked.connect(
            self.push_configure_classification)
        self.previous_button.clicked.connect(self.push_previous)
        self.apply_button.clicked.connect(self.push_apply)
        self.cancel_button.clicked.connect(self.push_cancel)
        self.configure_segmentation_button.clicked.connect(
            self.push_configure_segmentation)

        if self.modality_selected == 'CT':
            self.ct_modality_radio_button.setChecked(True)
        elif self.modality_selected == 'MRI':
            self.mri_modality_radio_button.setChecked(True)

        if self.bids_selected:
            self.bids_combobox.setCurrentIndex(0)
        else:
            self.bids_combobox.setCurrentIndex(1)

        if 'Red' in self.initial_view_selected:
            self.initial_view_combobox.setCurrentIndex(0)
        elif 'Yellow' in self.initial_view_selected:
            self.initial_view_combobox.setCurrentIndex(1)
        elif 'Green' in self.initial_view_selected:
            self.initial_view_combobox.setCurrentIndex(2)

        if self.file_extension_selected == '*.nii.gz':
            self.file_extension_combobox.setCurrentIndex(0)
        elif self.file_extension_selected == '*.nrrd':
            self.file_extension_combobox.setCurrentIndex(1)

        self.interpolate_combobox.setCurrentIndex(self.interpolate_selected)

        self.segmentation_task_checkbox.setChecked(self.segmentation_selected)
        self.classification_task_checkbox.setChecked(
            self.classification_selected)
        self.mouse_shortcuts_checkbox.setChecked(self.mouse_shortcuts_selected)
        self.keyboard_shortcuts_checkbox.setChecked(
            self.keyboard_shortcuts_selected)

        self.segmentation_checkbox_state_changed()
        self.keyboard_shortcuts_checkbox_state_changed()

    @enter_function
    def set_default_values(self):
        """
        set_default_values

        Args:
        """
        ConfigPath.write_config_file()
        self.config_yaml = ConfigPath.open_project_config_file()

        self.segmentation_selected = (
            self.config_yaml)['is_segmentation_requested']
        self.classification_selected = (
            self.config_yaml)['is_classification_requested']
        self.mouse_shortcuts_selected = (
            self.config_yaml)['is_mouse_shortcuts_requested']
        self.keyboard_shortcuts_selected = (
            self.config_yaml)['is_keyboard_shortcuts_requested']

        self.modality_selected = self.config_yaml['modality']

        self.bids_selected = self.config_yaml['impose_bids_format']

        self.ct_window_level_selected = self.config_yaml['ct_window_level']
        self.ct_window_width_selected = self.config_yaml['ct_window_width']
        self.file_extension_selected = self.config_yaml['input_filetype']

        if self.config_yaml['slice_view_color'] == 'Red':
            self.initial_view_selected = 'Red (axial)'
        elif self.config_yaml['slice_view_color'] == 'Yellow':
            self.initial_view_selected = 'Yellow (sagittal)'
        elif self.config_yaml['slice_view_color'] == 'Green':
            self.initial_view_selected = 'Green (coronal)'

        self.interpolate_selected = self.config_yaml['interpolate_value']

        self.toggle_fill_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][0]['shortcut']
        self.toggle_visibility_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][1]['shortcut']
        self.undo_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][2]['shortcut']
        self.save_seg_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][3]['shortcut']
        self.smooth_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][4]['shortcut']
        self.remove_small_holes_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][5]['shortcut']
        self.interpolate_ks_selected = \
            self.config_yaml['KEYBOARD_SHORTCUTS'][6]['shortcut']

    @enter_function
    def classification_checkbox_state_changed(self):
        """
        classification_checkbox_state_changed

        Args:
        """
        self.classification_selected = (
            self.classification_task_checkbox.isChecked())
        self.configure_classification_button.setEnabled(
            self.classification_selected)

    @enter_function
    def keyboard_shortcuts_checkbox_state_changed(self):
        """
        keyboard_shortcuts_checkbox_state_changed

        Args:
        """
        self.keyboard_shortcuts_selected = (
            self.keyboard_shortcuts_checkbox.isChecked())

        self.toggle_fill_ks_label.setVisible(self.keyboard_shortcuts_selected)
        self.toggle_fill_ks_line_edit.setVisible(
            self.keyboard_shortcuts_selected)
        self.toggle_visibility_ks_label.setVisible(
            self.keyboard_shortcuts_selected)
        self.toggle_visibility_ks_line_edit.setVisible(
            self.keyboard_shortcuts_selected)
        self.undo_ks_label.setVisible(self.keyboard_shortcuts_selected)
        self.undo_ks_line_edit.setVisible(self.keyboard_shortcuts_selected)
        self.save_seg_ks_label.setVisible(self.keyboard_shortcuts_selected)
        self.save_seg_ks_line_edit.setVisible(self.keyboard_shortcuts_selected)
        self.smooth_ks_label.setVisible(self.keyboard_shortcuts_selected)
        self.smooth_ks_line_edit.setVisible(self.keyboard_shortcuts_selected)
        self.remove_small_holes_ks_label.setVisible(
            self.keyboard_shortcuts_selected)
        self.remove_small_holes_ks_line_edit.setVisible(
            self.keyboard_shortcuts_selected)
        self.interpolate_ks_label.setVisible(self.keyboard_shortcuts_selected)
        self.interpolate_ks_line_edit.setVisible(
            self.keyboard_shortcuts_selected)

    @enter_function
    def segmentation_checkbox_state_changed(self):
        """
        segmentation_checkbox_state_changed

        Args:
        """
        self.segmentation_selected = self.segmentation_task_checkbox.isChecked()
        self.configure_segmentation_button.setEnabled(
            self.segmentation_selected)

    @enter_function
    def update_interpolate_ks(self):
        """
        update_interpolate_ks

        Args:
        """
        self.interpolate_ks_selected = self.interpolate_ks_line_edit.text

    @enter_function
    def update_remove_small_holes_ks(self):
        """
        update_remove_small_holes_ks

        Args:
        """
        self.remove_small_holes_ks_selected = (
            self.remove_small_holes_ks_line_edit.text)

    @enter_function
    def update_smooth_ks(self):
        """
        update_smooth_ks

        Args:
        """
        self.smooth_ks_selected = self.smooth_ks_line_edit.text

    @enter_function
    def update_save_seg_ks(self):
        """
        update_save_seg_ks

        Args:
        """
        self.save_seg_ks_selected = self.save_seg_ks_line_edit.text

    @enter_function
    def update_undo_ks(self):
        """
        update_undo_ks

        Args:
        """
        self.undo_ks_selected = self.undo_ks_line_edit.text

    @enter_function
    def update_toggle_visibility_ks(self):
        """
        update_toggle_visibility_ks

        Args:
        """
        self.toggle_visibility_ks_selected = (
            self.toggle_visibility_ks_line_edit.text)

    @enter_function
    def update_toggle_fill_ks(self):
        """
        update_toggle_fill_ks

        Args:
        """
        self.toggle_fill_ks_selected = self.toggle_fill_ks_line_edit.text

    @enter_function
    def update_ct_window_width(self):
        """
        update_ct_window_width

        Args:
        """
        self.ct_window_width_selected = self.ct_window_width_line_edit.text

    @enter_function
    def update_ct_window_level(self):
        """
        update_ct_window_level

        Args:
        """
        self.ct_window_level_selected = self.ct_window_level_line_edit.text

    @enter_function
    def update_interpolate(self):
        """
        update_interpolate

        Args:
        """
        if self.interpolate_combobox.currentText == 'Yes':
            self.interpolate_selected = True
        else:
            self.interpolate_selected = False

    @enter_function
    def update_initial_view(self):
        """
        update_initial_view

        Args:
        """
        self.initial_view_selected = self.initial_view_combobox.currentText

    @enter_function
    def update_file_extension(self):
        """
        update_file_extension

        Args:
        """
        self.file_extension_selected = self.file_extension_combobox.currentText

    @enter_function
    def update_bids(self):
        """
        update_bids

        Args:
        """
        self.bids_selected = self.bids_combobox.currentText

    @enter_function
    def update_selected_modality(self, option):
        """
        update_selected_modality

        Args:
            option: Description of option.
        """
        self.modality_selected = option

        if self.modality_selected == 'CT':
            self.bids_combobox.setEnabled(False)

            self.ct_window_level_line_edit.setEnabled(True)
            self.ct_window_width_line_edit.setEnabled(True)

        else:
            self.bids_combobox.setEnabled(True)

            self.ct_window_level_line_edit.setEnabled(False)
            self.ct_window_width_line_edit.setEnabled(False)

    @enter_function
    def push_configure_segmentation(self):
        """
        push_configure_segmentation

        Args:
        """
        self.configureSegmentationWindow = ConfigureSegmentationWindow(
            self.segmenter, self.modality_selected, self.edit_conf)
        self.configureSegmentationWindow.show()
        self.close()

    @enter_function
    def push_configure_classification(self):
        """
        push_configure_classification

        Args:
        """
        configureClassificationWindow = ConfigureClassificationWindow(
            self.segmenter, self.edit_conf)
        configureClassificationWindow.show()
        self.close()

    @enter_function
    def push_previous(self):
        """
        push_previous

        Args:
        """
        self.close()
        slicerCART_configuration_initial_window = (
            SlicerCARTConfigurationInitialWindow(
            self.segmenter))
        slicerCART_configuration_initial_window.show()

    @enter_function  # Example that print the function name when you click on
    # apply in the Configuration Set Up Window
    def push_apply(self):
        """
        push_apply

        Args:
        """

        self.config_yaml[
            'is_segmentation_requested'] = (
            self.segmentation_task_checkbox.isChecked())

        self.config_yaml[
            'is_classification_requested'] = (
            self.classification_task_checkbox.isChecked())

        self.config_yaml[
            'is_mouse_shortcuts_requested'] = (
            self.mouse_shortcuts_checkbox.isChecked())

        self.config_yaml[
            'is_keyboard_shortcuts_requested'] = (
            self.keyboard_shortcuts_checkbox.isChecked())

        self.config_yaml['modality'] = self.modality_selected

        if self.bids_selected == 'Yes':
            self.config_yaml['impose_bids_format'] = True
        elif self.bids_selected == 'No':
            self.config_yaml['impose_bids_format'] = False

        self.config_yaml['input_filetype'] = self.file_extension_selected

        self.config_yaml['interpolate_value'] = self.interpolate_selected

        if 'Red' in self.initial_view_selected:
            self.config_yaml['slice_view_color'] = 'Red'
        elif 'Yellow' in self.initial_view_selected:
            self.config_yaml['slice_view_color'] = 'Yellow'
        elif 'Green' in self.initial_view_selected:
            self.config_yaml['slice_view_color'] = 'Green'

        self.config_yaml['ct_window_level'] = int(self.ct_window_level_selected)
        self.config_yaml['ct_window_width'] = int(self.ct_window_width_selected)

        self.config_yaml['KEYBOARD_SHORTCUTS'][0][
            'shortcut'] = self.toggle_fill_ks_selected
        self.config_yaml['KEYBOARD_SHORTCUTS'][1][
            'shortcut'] = self.toggle_visibility_ks_selected
        self.config_yaml['KEYBOARD_SHORTCUTS'][2][
            'shortcut'] = self.undo_ks_selected
        self.config_yaml['KEYBOARD_SHORTCUTS'][3][
            'shortcut'] = self.save_seg_ks_selected
        self.config_yaml['KEYBOARD_SHORTCUTS'][4][
            'shortcut'] = self.smooth_ks_selected
        self.config_yaml['KEYBOARD_SHORTCUTS'][5][
            'shortcut'] = self.remove_small_holes_ks_selected
        self.config_yaml['KEYBOARD_SHORTCUTS'][6][
            'shortcut'] = self.interpolate_ks_selected

        ConfigPath.write_config_file()
        self.config_yaml = ConfigPath.open_project_config_file()

        self.segmenter.setup_configuration()

        self.close()

    @enter_function
    def push_cancel(self):
        """
        push_cancel

        Args:
        """
        if self.edit_conf == False:
            msg = qt.QMessageBox()
            msg.setWindowTitle('Informative Message')
            msg.setText(
                'Using default configurations. To select a different '
                'configuration, restart the application. ')
            msg.exec()

        self.segmenter.setup_configuration()
        self.close()


class SlicerCARTConfigurationInitialWindow(qt.QWidget):
    @enter_function
    def __init__(self, segmenter, parent=None):
        """
        __init__

        Args:
            segmenter: Description of segmenter.
            parent: Description of parent.
        """
        super(SlicerCARTConfigurationInitialWindow, self).__init__(parent)

        # MB: Required for using the correct config file.
        self.config_yaml = ConfigPath.open_project_config_file()

        self.segmenter = segmenter

        layout = qt.QVBoxLayout()

        self.reuse_configuration_hbox = qt.QHBoxLayout()

        self.new_config_radio_button = qt.QRadioButton('New configuration',
                                                       self)
        self.reuse_config_radio_button = qt.QRadioButton(
            'Continue from existing output folder', self)
        self.use_template_config_radio_button = qt.QRadioButton(
            'Use template configuration', self)

        self.reuse_configuration_hbox.addWidget(self.new_config_radio_button)
        self.reuse_configuration_hbox.addWidget(self.reuse_config_radio_button)
        self.reuse_configuration_hbox.addWidget(
            self.use_template_config_radio_button)

        self.new_config_radio_button.toggled.connect(
            lambda: self.update_selected_reuse_config_option(
                self.new_config_radio_button.text))
        self.reuse_config_radio_button.toggled.connect(
            lambda: self.update_selected_reuse_config_option(
                self.reuse_config_radio_button.text))
        self.use_template_config_radio_button.toggled.connect(
            lambda: self.update_selected_reuse_config_option(
                self.use_template_config_radio_button.text))

        self.new_config_radio_button.setChecked(True)  # par défaut
        self.reuse_configuration_selected_option = (
            self.new_config_radio_button.text)

        layout.addLayout(self.reuse_configuration_hbox)

        self.next_button = qt.QPushButton('Next')
        self.next_button.clicked.connect(self.push_next)
        layout.addWidget(self.next_button)

        self.cancel_button = qt.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.push_cancel)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.setWindowTitle("Configure SlicerCART")
        self.resize(800, 100)

    @enter_function
    def update_selected_reuse_config_option(self, option):
        """
        update_selected_reuse_config_option

        Args:
            option: Description of option.
        """
        self.reuse_configuration_selected_option = option

    @enter_function
    def push_next(self):
        """
        push_next

        Args:
        """
        if (self.reuse_configuration_selected_option ==
                self.reuse_config_radio_button.text):
            msg = qt.QMessageBox()
            msg.setWindowTitle('Informative Message')
            msg.setText('Please select the output folder. ')
            msg.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
            msg.buttonClicked.connect(self.select_output_folder_clicked)
            msg.exec()
        elif (self.reuse_configuration_selected_option ==
              self.use_template_config_radio_button.text):
            msg = qt.QMessageBox()
            msg.setWindowTitle('Informative Message')
            msg.setText(
                'Please select the _conf folder containing the template '
                'configuration files. ')
            msg.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
            msg.buttonClicked.connect(self.select_template_folder_clicked)
            msg.exec()
        elif (self.reuse_configuration_selected_option ==
              self.new_config_radio_button.text):
            slicerCARTConfigurationSetupWindow = (
                SlicerCARTConfigurationSetupWindow(self.segmenter))
            slicerCARTConfigurationSetupWindow.show()
            self.segmenter.ui.SelectOutputFolder.setVisible(True)
            self.close()

    @enter_function
    def select_output_folder_clicked(self, button):
        """
        select_output_folder_clicked

        Args:
            button: Description of button.
        """
        if button.text == 'OK':
            self.outputFolder = (
                qt.QFileDialog.getExistingDirectory(
                    None,
                    "Open a folder",
                    ConfigPath.DEFAULT_VOLUMES_DIRECTORY,
                    qt.QFileDialog.ShowDirsOnly))
            content = UserPath.read_filepath(self)
            if self.outputFolder in content:
                self.CurrentFolder = content[self.outputFolder]
            else:
                Dev.show_message_box(self,
                                     'Please select volumes folder.',
                                     box_title='ATTENTION!')
                self.CurrentFolder = (
                    qt.QFileDialog.getExistingDirectory(
                        None, "Open a folder",
                        ConfigPath.DEFAULT_VOLUMES_DIRECTORY,
                        qt.QFileDialog.ShowDirsOnly))
                # Save the associated volume_folder_path with the output_folder
                # selected.
                UserPath.write_in_filepath(self, self.outputFolder,
                                           self.CurrentFolder)

            UserPath.save_selected_paths(self,
                                         self.outputFolder,
                                         self.CurrentFolder)
            UserPath.set_selected_existing_folder(self)

            # Ensure there is a config file in the output folder
            ConfigPath.set_output_folder(self.outputFolder)
            ConfigPath.check_existing_configuration()
            ConfigPath.delete_temp_file()

            # self.segmenter corresponds to SlicerCART UI in Slicer.
            self.segmenter.onSelectVolumesFolderButton()
            self.segmenter.set_ui_enabled_options()
            self.close()

            return

        else:
            slicerCART_configuration_initial_window = (
                SlicerCARTConfigurationInitialWindow(self.segmenter))
            slicerCART_configuration_initial_window.show()
            self.close()
            return

    @enter_function
    def error_msg_for_output_folder_selection_clicked(self, button):
        """
        error_msg_for_output_folder_selection_clicked

        Args:
            button: Description of button.
        """
        slicerCART_configuration_initial_window = (
            SlicerCARTConfigurationInitialWindow(
            self.segmenter))
        slicerCART_configuration_initial_window.show()
        self.close()

    @enter_function
    def select_template_folder_clicked(self, button):
        """
        select_template_folder_clicked

        Args:
            button: Description of button.
        """
        if button.text == 'OK':
            conf_folder_path = (
                qt.QFileDialog.getExistingDirectory(
                    None, "Open a folder", '', qt.QFileDialog.ShowDirsOnly))
            if (os.path.split(conf_folder_path)[1] == CONF_FOLDER_NAME
                    and os.path.exists(f'{conf_folder_path}'
                                       f'{os.sep}{CONFIG_COPY_FILENAME}')):
                slicerCARTConfigurationSetupWindow = (
                    SlicerCARTConfigurationSetupWindow(
                    self.segmenter, conf_folder_path))
                slicerCARTConfigurationSetupWindow.show()
                self.segmenter.ui.SelectOutputFolder.setVisible(True)
                self.close()

            else:
                msg = qt.QMessageBox()
                msg.setWindowTitle('Informative Message')
                msg.setText(
                    'The selected output folder does not contain the required '
                    'configuration files for SlicerCART. Please try again. ')
                msg.setStandardButtons(
                    qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
                msg.buttonClicked.connect(
                    self.error_msg_for_output_folder_selection_clicked)
                msg.exec()

        else:
            slicerCART_configuration_initial_window = (
                SlicerCARTConfigurationInitialWindow(
                self.segmenter))
            slicerCART_configuration_initial_window.show()
            self.close()
            return

    @enter_function
    def push_cancel(self):
        """
        push_cancel

        Args:
        """
        msg = qt.QMessageBox()
        msg.setWindowTitle('Informative Message')
        msg.setText(
            'Using default configurations. To select a different '
            'configuration, restart the application. ')
        msg.exec()

        self.segmenter.setup_configuration()
        self.close()


class ConfigureSegmentationWindow(qt.QWidget):
    @enter_function
    def __init__(self, segmenter, modality, edit_conf,
                 segmentation_config_yaml=None, label_config_yaml=None,
                 parent=None):
        """
            __init__

            Args:
                segmenter: Description of segmenter.
                modality: Description of modality.
                edit_conf: Description of edit_conf.
                segmentation_config_yaml: Description of segmentation_config_yaml.
                label_config_yaml: Description of label_config_yaml.
                parent: Description of parent.
            """
        super(ConfigureSegmentationWindow, self).__init__(parent)

        if label_config_yaml is None:
            Debug.print(self, 'label_config_yaml is None in '
                              'ConfigureSegmentationwindow')
            self.config_yaml = ConfigPath.open_project_config_file()
        else:
            Debug.print(self, 'else meaning label_config_yaml is NOT None in '
                              'ConfigureSegmentationwindow')
            self.config_yaml = label_config_yaml

        self.segmenter = segmenter
        self.modality = modality
        self.edit_conf = edit_conf

        layout = qt.QVBoxLayout()

        self.label_table_view = qt.QTableWidget()
        layout.addWidget(self.label_table_view)

        if self.config_yaml['labels'] != None:
            number_of_labels = len(self.config_yaml['labels'])

            self.label_table_view.setRowCount(number_of_labels)
            if self.modality == 'MRI':
                self.label_table_view.setColumnCount(
                    5)  # edit button, remove button, name, value, color
            elif self.modality == 'CT':
                self.label_table_view.setColumnCount(
                    7)  # edit button, remove button, name, value, color,
                # range HU min, range HU max
            self.label_table_view.horizontalHeader().setStretchLastSection(True)
            self.label_table_view.horizontalHeader().setSectionResizeMode(
                qt.QHeaderView.Stretch)

            for index, label in enumerate(self.config_yaml['labels']):
                edit_button = qt.QPushButton('Edit')
                edit_button.clicked.connect(
                    lambda state, label=label: self.push_edit_button(label))
                edit_button_hbox = qt.QHBoxLayout()
                edit_button_hbox.addWidget(edit_button)
                edit_button_hbox.setAlignment(qt.Qt.AlignCenter)
                edit_button_hbox.setContentsMargins(0, 0, 0, 0)
                edit_button_widget = qt.QWidget()
                edit_button_widget.setLayout(edit_button_hbox)
                self.label_table_view.setCellWidget(index, 0,
                                                    edit_button_widget)
                self.label_table_view.setHorizontalHeaderItem(
                    0, qt.QTableWidgetItem(''))

                remove_button = qt.QPushButton('Remove')
                remove_button.clicked.connect(
                    lambda state, label=label: self.push_remove_button(label))
                remove_button_hbox = qt.QHBoxLayout()
                remove_button_hbox.addWidget(remove_button)
                remove_button_hbox.setAlignment(qt.Qt.AlignCenter)
                remove_button_hbox.setContentsMargins(0, 0, 0, 0)
                remove_button_widget = qt.QWidget()
                remove_button_widget.setLayout(remove_button_hbox)

                self.label_table_view.setCellWidget(
                    index, 1, remove_button_widget)
                self.label_table_view.setHorizontalHeaderItem(
                    1, qt.QTableWidgetItem(''))

                if self.edit_conf:
                    remove_button.setEnabled(False)

                cell = qt.QTableWidgetItem(label['name'])
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(
                    qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.label_table_view.setItem(index, 2, cell)
                self.label_table_view.setHorizontalHeaderItem(
                    2, qt.QTableWidgetItem('Name'))

                cell = qt.QTableWidgetItem(str(label['value']))
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(
                    qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.label_table_view.setItem(index, 3, cell)
                self.label_table_view.setHorizontalHeaderItem(
                    3, qt.QTableWidgetItem('Value'))

                cell = qt.QTableWidgetItem('')
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setBackground(qt.QBrush(
                    qt.QColor(label['color_r'], label['color_g'],
                              label['color_b'])))
                self.label_table_view.setItem(index, 4, cell)
                self.label_table_view.setHorizontalHeaderItem(
                    4, qt.QTableWidgetItem('Colour'))

                if self.modality == 'CT':
                    cell = qt.QTableWidgetItem(str(label['lower_bound_HU']))
                    cell.setFlags(qt.Qt.NoItemFlags)
                    cell.setForeground(
                        qt.QBrush(qt.QColor(self.segmenter.foreground)))
                    self.label_table_view.setItem(index, 5, cell)
                    self.label_table_view.setHorizontalHeaderItem(
                        5, qt.QTableWidgetItem('Min. HU'))

                    cell = qt.QTableWidgetItem(str(label['upper_bound_HU']))
                    cell.setFlags(qt.Qt.NoItemFlags)
                    cell.setForeground(
                        qt.QBrush(qt.QColor(self.segmenter.foreground)))
                    self.label_table_view.setItem(index, 6, cell)
                    self.label_table_view.setHorizontalHeaderItem(
                        6, qt.QTableWidgetItem('Max. HU'))

        self.label_table_view.setSizePolicy(qt.QSizePolicy.Expanding,
                                            qt.QSizePolicy.Fixed)

        self.add_label_button = qt.QPushButton('Add Label')
        self.add_label_button.clicked.connect(self.push_add_label)
        layout.addWidget(self.add_label_button)

        display_timer_hbox = qt.QHBoxLayout()

        self.display_timer_label = qt.QLabel(
            'Display timer during segmentation? ')
        self.display_timer_label.setStyleSheet("font-weight: bold")
        display_timer_hbox.addWidget(self.display_timer_label)

        self.display_timer_checkbox = qt.QCheckBox()
        display_timer_hbox.addWidget(self.display_timer_checkbox)

        layout.addLayout(display_timer_hbox)

        self.apply_button = qt.QPushButton('Apply')
        layout.addWidget(self.apply_button)

        self.cancel_button = qt.QPushButton('Cancel')
        layout.addWidget(self.cancel_button)

        self.populate_default_values()
        self.connect_buttons_to_callbacks()

        self.setLayout(layout)
        self.setWindowTitle("Configure Segmentation")
        self.resize(500, 600)

    @enter_function
    def push_add_label(self):
        """
        push_add_label

        Args:
        """
        self.close()
        configureSingleLabelWindow = (
            ConfigureSingleLabelWindow(self.segmenter,
                                       self.modality,
                                       self.edit_conf,
                                       self.config_yaml))
        configureSingleLabelWindow.show()

    @enter_function
    def push_edit_button(self, label):
        """
        push_edit_button

        Args:
            label: Description of label.
        """
        self.close()

        configureSingleLabelWindow = (
            ConfigureSingleLabelWindow(self.segmenter,
                                       self.modality,
                                       self.edit_conf,
                                       self.config_yaml,
                                       label))
        configureSingleLabelWindow.show()

    @enter_function
    def push_remove_button(self, label):
        """
        push_remove_button

        Args:
            label: Description of label.
        """

        value_removed = -1
        for l in self.config_yaml['labels']:
            if l['name'] == label['name']:
                value_removed = l['value']
                self.config_yaml['labels'].remove(l)

        for l in self.config_yaml['labels']:
            if l['value'] > value_removed and value_removed != -1:
                l['value'] = l['value'] - 1

        # If there is no remaining button, the last segmentation label is not
        # remove
        if len(self.config_yaml['labels']) == 0:
            Debug.print(self, "len(self.config_yaml['labels']) == 0")
            msg = qt.QMessageBox()
            msg.setWindowTitle('ERROR : Label list is empty')
            msg.setText(
                'The label list cannot be empty. You need at least one '
                'segmentation label in the configuration. \n\nTo modify the '
                'last remaining label, '
                'you can:\n1) Add a new label and remove the current single '
                'label;\n2) Edit the current label color.\n\n Keeping for now '
                'the previous label configuration.')
            msg.setStandardButtons(qt.QMessageBox.Ok)
            # msg.buttonClicked.connect(self.push_error_label_list_empty)
            msg.exec()
        else:
            ConfigPath.write_config_file()
            self.close()

            configureSegmentationWindow = ConfigureSegmentationWindow(
                self.segmenter, self.modality, self.edit_conf, self.config_yaml)
            configureSegmentationWindow.show()

    @enter_function
    def set_default_values(self):
        """
        set_default_values

        Args:
        """
        self.config_yaml[
            'is_display_timer_requested'] = (
            self.display_timer_checkbox.isChecked())

    @enter_function
    def populate_default_values(self):
        """
        populate_default_values

        Args:
        """
        self.display_timer_selected = self.config_yaml[
            'is_display_timer_requested']
        self.display_timer_checkbox.setChecked(self.display_timer_selected)

    @enter_function
    def connect_buttons_to_callbacks(self):
        """
        connect_buttons_to_callbacks

        Args:
        """
        self.apply_button.clicked.connect(self.push_apply)
        self.cancel_button.clicked.connect(self.push_cancel)

    @enter_function
    def push_apply(self):
        """
        push_apply

        Args:
        """
        self.config_yaml[
            'is_display_timer_requested'] = (
            self.display_timer_checkbox.isChecked())

        Debug.print(self, 'in else push_apply in '
                          'ConfigureSegmentationWindow')
        ConfigPath.write_config_file()

        slicerCARTConfigurationSetupWindow = (
            SlicerCARTConfigurationSetupWindow(self.segmenter))
        slicerCARTConfigurationSetupWindow.show()
        self.close()

    @enter_function
    def push_error_label_list_empty(self):
        """
        push_error_label_list_empty

        Args:
        """
        self.push_cancel()

    @enter_function
    def push_cancel(self):
        """
        push_cancel

        Args:
        """
        slicerCARTConfigurationSetupWindow = (
            SlicerCARTConfigurationSetupWindow(self.segmenter))
        slicerCARTConfigurationSetupWindow.show()
        self.close()

    # combine the action of going back to configuration setup into one
    @enter_function
    def go_back_to_configuration_setup_window(self):
        """
        go_back_to_configuration_setup_window

        Args:
        """
        slicerCARTConfigurationSetupWindow = (
            SlicerCARTConfigurationSetupWindow(self.segmenter))
        slicerCARTConfigurationSetupWindow.show()


class ConfigureSingleLabelWindow(qt.QWidget):
    @enter_function
    def __init__(self, segmenter, modality, edit_conf, label_config_yaml,
                 label=None, parent=None):
        """
        __init__

           Args:
               segmenter: Description of segmenter.
               modality: Description of modality.
               edit_conf: Description of edit_conf.
               label_config_yaml: Description of label_config_yaml.
               label: Description of label.
               parent: Description of parent.
           """
        super(ConfigureSingleLabelWindow, self).__init__(parent)

        self.segmenter = segmenter
        self.modality = modality
        self.initial_label = label
        self.config_yaml = ConfigPath.open_project_config_file()
        self.edit_conf = edit_conf

        layout = qt.QVBoxLayout()  # Creates a vertical Box layout (Label Box)

        name_hbox = qt.QHBoxLayout()  # Creates a horizontal Box layout (line)
        name_label = qt.QLabel('Name : ')
        name_label.setStyleSheet("font-weight: bold")
        name_hbox.addWidget(name_label)
        self.name_line_edit = qt.QLineEdit('')
        name_hbox.addWidget(self.name_line_edit)
        layout.addLayout(name_hbox)

        value_hbox = qt.QHBoxLayout()  # Creates a horizontal Box layout (line)
        value_label = qt.QLabel('Value : ')
        value_label.setStyleSheet("font-weight: bold")
        value_hbox.addWidget(value_label)
        self.value_line_edit = qt.QLineEdit('')
        self.value_line_edit.setValidator(qt.QIntValidator())
        # To be changed at resolution of Issue #28
        self.value_line_edit.setEnabled(False)
        value_hbox.addWidget(self.value_line_edit)
        layout.addLayout(value_hbox)

        comment_hbox = qt.QHBoxLayout()
        # Create a QLabel to display a comment below the QLineEdit
        self.comment_label = qt.QLabel(
            'N.B. Label value is not editable and will be assigned '
            'automatically.\nEnter any integer between 0 and 255 in RGB to '
            'select label color.')
        comment_hbox.addWidget(self.comment_label)
        layout.addLayout(comment_hbox)

        color_hbox = qt.QHBoxLayout()  # Creates a horizontal Box layout (line)
        color_label = qt.QLabel('Colour : ')
        color_label.setStyleSheet("font-weight: bold")
        color_hbox.addWidget(color_label)

        colorValidator = qt.QIntValidator()
        colorValidator.setRange(0, 255)

        r_label = qt.QLabel('R')
        r_label.setStyleSheet("font-weight: bold")
        color_hbox.addWidget(r_label)
        self.color_r_line_edit = qt.QLineEdit('')
        self.color_r_line_edit.setMaxLength(3)
        self.color_r_line_edit.setValidator(colorValidator)
        self.color_r_line_edit.textChanged.connect(self.color_line_edit_changed)
        color_hbox.addWidget(self.color_r_line_edit)

        g_label = qt.QLabel('G')
        g_label.setStyleSheet("font-weight: bold")
        color_hbox.addWidget(g_label)
        self.color_g_line_edit = qt.QLineEdit('')
        self.color_g_line_edit.setMaxLength(3)
        self.color_g_line_edit.setValidator(colorValidator)
        self.color_g_line_edit.textChanged.connect(self.color_line_edit_changed)
        color_hbox.addWidget(self.color_g_line_edit)

        b_label = qt.QLabel('B')
        b_label.setStyleSheet("font-weight: bold")
        color_hbox.addWidget(b_label)
        self.color_b_line_edit = qt.QLineEdit('')
        self.color_b_line_edit.setMaxLength(3)
        self.color_b_line_edit.setValidator(colorValidator)
        self.color_b_line_edit.textChanged.connect(self.color_line_edit_changed)
        color_hbox.addWidget(self.color_b_line_edit)

        # Display the selected color from RGB
        self.color_display = qt.QLabel('        ')
        color_hbox.addWidget(self.color_display)
        layout.addLayout(color_hbox)

        validator_hbox = qt.QHBoxLayout()  # Creates a validator horizontal Box
        valided_result = ''
        self.validator_label_hbox = qt.QLineEdit(f'{valided_result}')
        validator_hbox.addWidget(self.validator_label_hbox)
        self.validator_label_hbox.setEnabled(False)  # Prevent user editing
        layout.addLayout(validator_hbox)

        @enter_function
        def validate_input(color_line_edit):
            """
            This functions validates if RGB value for a single color is valid.
            Display a comment if value is out of range.
            """
            input_text = color_line_edit.text
            result = colorValidator.validate(input_text, 0)
            if result == qt.QValidator.Acceptable:
                self.validator_label_hbox.setText('')
            else:
                if len(input_text) > 0:
                    self.validator_label_hbox.setText(
                        f'{input_text} is not valid.')
                else:
                    self.validator_label_hbox.setText('')

        # Connect each QLineEdit to validate_input using lambda
        self.color_r_line_edit.textChanged.connect(
            lambda: validate_input(self.color_r_line_edit))
        self.color_g_line_edit.textChanged.connect(
            lambda: validate_input(self.color_g_line_edit))
        self.color_b_line_edit.textChanged.connect(
            lambda: validate_input(self.color_b_line_edit))

        if self.modality == 'CT':
            min_hu_hbox = qt.QHBoxLayout()

            min_hu_label = qt.QLabel('Min. HU : ')
            min_hu_label.setStyleSheet("font-weight: bold")
            min_hu_hbox.addWidget(min_hu_label)

            self.min_hu_line_edit = qt.QLineEdit('')
            self.min_hu_line_edit.setValidator(qt.QIntValidator())
            self.min_hu_line_edit.setInputMask("0000")
            min_hu_hbox.addWidget(self.min_hu_line_edit)

            layout.addLayout(min_hu_hbox)

            max_hu_hbox = qt.QHBoxLayout()

            max_hu_label = qt.QLabel('Max. HU : ')
            max_hu_label.setStyleSheet("font-weight: bold")
            max_hu_hbox.addWidget(max_hu_label)

            self.max_hu_line_edit = qt.QLineEdit('')
            self.max_hu_line_edit.setValidator(qt.QIntValidator())
            self.max_hu_line_edit.setInputMask("0000")
            max_hu_hbox.addWidget(self.max_hu_line_edit)

            layout.addLayout(max_hu_hbox)

        if self.initial_label is not None:
            self.name_line_edit.setText(self.initial_label['name'])
            self.name_line_edit.setEnabled(False)
            self.value_line_edit.setText(self.initial_label['value'])
            self.color_r_line_edit.setText(label['color_r'])
            self.color_g_line_edit.setText(label['color_g'])
            self.color_b_line_edit.setText(label['color_b'])
            self.color_line_edit_changed()

            if self.modality == 'CT':
                self.min_hu_line_edit.setText(
                    self.initial_label['lower_bound_HU'])
                self.max_hu_line_edit.setText(
                    self.initial_label['upper_bound_HU'])

        self.save_button = qt.QPushButton('Save')
        self.save_button.clicked.connect(self.push_save)
        layout.addWidget(self.save_button)

        self.cancel_button = qt.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.push_cancel)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.setWindowTitle("Configure Label")
        self.resize(400, 200)

    @enter_function
    def color_line_edit_changed(self):
        """
        color_line_edit_changed

        Args:
        """
        # (R, G, B)
        color = (f'({self.color_r_line_edit.text},'
                 f'{self.color_g_line_edit.text},'
                 f'{self.color_b_line_edit.text})')
        self.color_display.setStyleSheet(f"background-color:rgb{color}")

    @enter_function
    def incorrect_rgb(self):
        """
        incorrect_rgb

        Args:
        """
        r = self.color_r_line_edit.text
        g = self.color_g_line_edit.text
        b = self.color_b_line_edit.text
        rgb_dict = {'R': r, 'G': g, 'B': b}

        # N.B. The line edit allows now only to enter integers, so we only
        # need to verify if values are not empty or between 0 and 255
        incorrect_values = []
        flag_incorrect_value = False

        for color in rgb_dict:
            try:
                rgb_dict[color] = int(rgb_dict[color])
                if 0 <= rgb_dict[color] <= 255:
                    continue
                else:
                    incorrect_values.append(f"{color}: {str(rgb_dict[color])}")
            except ValueError:
                incorrect_values.append(f"{color}: {str(rgb_dict[color])}")

        if len(incorrect_values) > 0:
            incorrect_values = ' '.join(incorrect_values)
            self.validator_label_hbox.setText(f'{incorrect_values} '
                                              f'is/are not valid value/s.')
            flag_incorrect_value = True

        return flag_incorrect_value

    @enter_function
    def incorrect_name(self):
        """
        incorrect_name

        Args:
        """
        name = self.name_line_edit.text
        flag_incorrect_name = False
        if name != None:
            name = name.strip()
        if name == "":
            self.validator_label_hbox.setText(f'Name cannot be empty.')
            flag_incorrect_name = True
        else:
            if " " in name:
                self.validator_label_hbox.setText(
                    f'Name {name} is invalid. '
                    f'No space accepted in label name.')
                flag_incorrect_name = True
            else:
                self.validator_label_hbox.setText('')
                self.name_line_edit.text = name

        return flag_incorrect_name

    @enter_function
    def push_save(self):
        """
        push_save

        Args:
        """
        label_found = False

        # Validate rgb and name
        if self.incorrect_rgb():
            return

        if self.incorrect_name():
            return

        current_label_name = self.name_line_edit.text
        Debug.print(self, f'currrent_label_name: {current_label_name}')

        for label in self.config_yaml['labels']:
            if label['name'] == current_label_name:
                # edit
                label_found = True
                label['color_r'] = int(self.color_r_line_edit.text)
                label['color_g'] = int(self.color_g_line_edit.text)
                label['color_b'] = int(self.color_b_line_edit.text)

                if self.modality == 'CT':
                    label['lower_bound_HU'] = int(self.min_hu_line_edit.text)
                    label['upper_bound_HU'] = int(self.max_hu_line_edit.text)

        if label_found == False:
            Debug.print(self, 'label_found==False')
            # append
            new_label = {'color_b': 10,
                         'color_g': 10,
                         'color_r': 255,
                         'lower_bound_HU': 30,
                         'name': 'ICH',
                         'upper_bound_HU': 90,
                         'value': 1}
            new_label['name'] = self.name_line_edit.text
            new_label['value'] = len(self.config_yaml['labels']) + 1
            new_label['color_r'] = int(self.color_r_line_edit.text)
            new_label['color_g'] = int(self.color_g_line_edit.text)
            new_label['color_b'] = int(self.color_b_line_edit.text)

            if self.modality == 'CT':
                new_label['lower_bound_HU'] = int(self.min_hu_line_edit.text)
                new_label['upper_bound_HU'] = int(self.max_hu_line_edit.text)
            self.config_yaml['labels'].append(new_label)

        ConfigPath.write_config_file()

        self.configureSegmentationWindow = ConfigureSegmentationWindow(
            self.segmenter, self.modality, self.edit_conf)
        self.configureSegmentationWindow.show()
        self.close()

    @enter_function
    def push_cancel(self):
        """
        push_cancel

        Args:
        """
        self.configureSegmentationWindow = ConfigureSegmentationWindow(
            self.segmenter, self.modality, self.edit_conf)
        self.configureSegmentationWindow.show()
        self.close()


class ConfigureClassificationWindow(qt.QWidget):
    @enter_function
    def __init__(self, segmenter, edit_conf, classification_config_yaml=None,
                 parent=None):
        """
        __init__

        Args:
            segmenter: Description of segmenter.
            edit_conf: Description of edit_conf.
            classification_config_yaml: Description of classification_config_yaml.
            parent: Description of parent.
        """
        super(ConfigureClassificationWindow, self).__init__(parent)

        self.segmenter = segmenter
        self.edit_conf = edit_conf

        if classification_config_yaml is None:
            self.config_yaml = ConfigPath.open_project_config_file()
        else:
            self.config_yaml = classification_config_yaml

        # This flag enables to track whether combobox options have been modified
        self.flag_all_combobox_versions = True

        layout = qt.QVBoxLayout()

        self.checkbox_table_view = qt.QTableWidget()
        layout.addWidget(self.checkbox_table_view)

        if self.config_yaml['checkboxes'] != None:
            number_of_checkboxes = len(self.config_yaml['checkboxes'])

            self.checkbox_table_view.setRowCount(number_of_checkboxes)
            self.checkbox_table_view.setColumnCount(2)
            self.checkbox_table_view.horizontalHeader().setStretchLastSection(
                True)
            self.checkbox_table_view.horizontalHeader().setSectionResizeMode(
                qt.QHeaderView.Stretch)

            for index, (objectName, checkbox_label) in enumerate(
                    self.config_yaml["checkboxes"].items()):
                remove_button = qt.QPushButton('Remove')
                remove_button.clicked.connect(
                    lambda state,
                           checkbox_label=
                           checkbox_label: self.push_remove_checkbox_button(
                        checkbox_label))
                remove_button_hbox = qt.QHBoxLayout()
                remove_button_hbox.addWidget(remove_button)
                remove_button_hbox.setAlignment(qt.Qt.AlignCenter)
                remove_button_hbox.setContentsMargins(0, 0, 0, 0)
                remove_button_widget = qt.QWidget()
                remove_button_widget.setLayout(remove_button_hbox)
                self.checkbox_table_view.setCellWidget(index, 0,
                                                       remove_button_widget)
                self.checkbox_table_view.setHorizontalHeaderItem(
                    0, qt.QTableWidgetItem(''))

                if self.edit_conf:
                    remove_button.setEnabled(False)

                cell = qt.QTableWidgetItem(checkbox_label)
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(
                    qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.checkbox_table_view.setItem(index, 1, cell)
                self.checkbox_table_view.setHorizontalHeaderItem(
                    1, qt.QTableWidgetItem('Label'))

        self.add_checkbox_button = qt.QPushButton('Add Checkbox')
        self.add_checkbox_button.clicked.connect(self.push_add_checkbox)
        layout.addWidget(self.add_checkbox_button)

        self.combobox_table_view = qt.QTableWidget()
        layout.addWidget(self.combobox_table_view)

        # Preparing comboboxes versioning
        dict_of_comboboxes = self.config_yaml['comboboxes']
        (latest_combobox_version,
         latest_combobox_dict) = (
            self.get_latest_combobox_version(dict_of_comboboxes))

        if latest_combobox_dict != None:
            number_of_comboboxes = len(
                self.config_yaml['comboboxes'][latest_combobox_version])

            self.combobox_table_view.setRowCount(number_of_comboboxes)
            self.combobox_table_view.setColumnCount(3)
            self.combobox_table_view.horizontalHeader().setStretchLastSection(
                True)
            self.combobox_table_view.horizontalHeader().setSectionResizeMode(
                qt.QHeaderView.Stretch)
            self.combobox_table_view.verticalHeader().setSectionResizeMode(
                qt.QHeaderView.Stretch)

            for index, (combo_box_name, combo_box_options) in enumerate(
                    latest_combobox_dict.items()):
                remove_button = qt.QPushButton('Remove')
                remove_button.clicked.connect(
                    lambda state,
                           combo_box_name=
                           combo_box_name: self.push_remove_combobox_button(
                        combo_box_name))
                remove_button_hbox = qt.QHBoxLayout()
                remove_button_hbox.addWidget(remove_button)
                remove_button_hbox.setAlignment(qt.Qt.AlignCenter)
                remove_button_hbox.setContentsMargins(0, 0, 0, 0)
                remove_button_widget = qt.QWidget()
                remove_button_widget.setLayout(remove_button_hbox)
                self.combobox_table_view.setCellWidget(index, 0,
                                                       remove_button_widget)
                self.combobox_table_view.setHorizontalHeaderItem(
                    0, qt.QTableWidgetItem(''))

                if self.edit_conf:
                    remove_button.setEnabled(False)

                cell = qt.QTableWidgetItem(
                    combo_box_name.replace('_', ' ').capitalize())
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(
                    qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.combobox_table_view.setItem(index, 1, cell)
                self.combobox_table_view.setHorizontalHeaderItem(
                    1, qt.QTableWidgetItem('Label'))

                combobox = qt.QComboBox()
                for i, (name, label) in enumerate(combo_box_options.items()):
                    combobox.addItem(label)

                combobox_hbox = qt.QHBoxLayout()
                combobox_hbox.addWidget(combobox)
                combobox_hbox.setAlignment(qt.Qt.AlignCenter)
                combobox_hbox.setContentsMargins(0, 0, 0, 0)
                widget = qt.QWidget()
                widget.setLayout(combobox_hbox)
                self.combobox_table_view.setCellWidget(index, 2, widget)
                self.combobox_table_view.setHorizontalHeaderItem(
                    2, qt.QTableWidgetItem(''))

        self.add_combobox_button = qt.QPushButton('Add Drop Down')
        self.add_combobox_button.clicked.connect(self.push_add_combobox)
        layout.addWidget(self.add_combobox_button)

        self.freetext_table_view = qt.QTableWidget()
        layout.addWidget(self.freetext_table_view)

        if self.config_yaml['freetextboxes'] != None:
            number_of_freetextboxes = len(self.config_yaml['freetextboxes'])

            self.freetext_table_view.setRowCount(number_of_freetextboxes)
            self.freetext_table_view.setColumnCount(2)
            self.freetext_table_view.horizontalHeader().setStretchLastSection(
                True)
            self.freetext_table_view.horizontalHeader().setSectionResizeMode(
                qt.QHeaderView.Stretch)

            for index, (objectName, freetextbox_label) in enumerate(
                    self.config_yaml["freetextboxes"].items()):
                remove_button = qt.QPushButton('Remove')
                remove_button.clicked.connect(
                    lambda state,
                           freetextbox_label=
                           freetextbox_label:
                    self.push_remove_freetextbox_button(freetextbox_label))
                remove_button_hbox = qt.QHBoxLayout()
                remove_button_hbox.addWidget(remove_button)
                remove_button_hbox.setAlignment(qt.Qt.AlignCenter)
                remove_button_hbox.setContentsMargins(0, 0, 0, 0)
                remove_button_widget = qt.QWidget()
                remove_button_widget.setLayout(remove_button_hbox)
                self.freetext_table_view.setCellWidget(index, 0,
                                                       remove_button_widget)
                self.freetext_table_view.setHorizontalHeaderItem(
                    0, qt.QTableWidgetItem(''))

                if self.edit_conf:
                    remove_button.setEnabled(False)

                cell = qt.QTableWidgetItem(freetextbox_label)
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(
                    qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.freetext_table_view.setItem(index, 1, cell)
                self.freetext_table_view.setHorizontalHeaderItem(
                    1, qt.QTableWidgetItem('Label'))

        self.add_freetextbox_button = qt.QPushButton('Add Text Field')
        self.add_freetextbox_button.clicked.connect(self.push_add_freetextbox)
        layout.addWidget(self.add_freetextbox_button)

        self.save_button = qt.QPushButton('Save')
        self.save_button.clicked.connect(self.push_save)
        layout.addWidget(self.save_button)

        self.cancel_button = qt.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.push_cancel)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.setWindowTitle("Configure Classification")
        self.resize(500, 600)

    @enter_function
    def get_latest_combobox_version(self, dict_of_comboboxes):
        """
        Get the latest combobox version
        :Param: dict_of_comboboxes: a dictionary that contains all the versions
        return: latest_combobox_version: string like v08 associated with the
        latest combobox version; latest_combobox_dict: dictionary that
        contains the combobox options for the latest version
        """
        search_latest_combobox_version = \
            lambda d: max(d.keys(), key=lambda k: int(k[1:])) if d else None

        latest_combobox_version = search_latest_combobox_version(
            dict_of_comboboxes)
        if dict_of_comboboxes != None:
            latest_combobox_dict = (dict_of_comboboxes[latest_combobox_version])
        else:
            latest_combobox_dict = None

        return latest_combobox_version, latest_combobox_dict

    @enter_function
    def push_remove_combobox_button(self, combo_box_name):
        """
        push_remove_combobox_button

        Args:
            combo_box_name: Description of combo_box_name.
        """
        self.close()

        # Flag that indicates that the remove combobox has been selected in
        # the ui
        ConfigPath.set_remove_combobox_flag()

        # Preparing comboboxes versioning
        dict_of_comboboxes = self.config_yaml['comboboxes']
        (latest_combobox_version,
         latest_combobox_dict) = (
            self.get_latest_combobox_version(dict_of_comboboxes))

        if ConfigPath.get_combobox_flag():
            # Means that a dropdown has not been added
            version_temp = int(latest_combobox_version[1:]) + 1
            latest_combobox_version = f"v{version_temp:02d}"
            # Deep copy to faciliate tracking of labels
            new_dict = copy.deepcopy(latest_combobox_dict)
            dict_of_comboboxes[latest_combobox_version] = new_dict

            # Set the flag to indicate that the comboboxes have been modified
            ConfigPath.set_combobox_flag()
            ConfigPath.set_remove_combobox_flag()

        dict_of_comboboxes[latest_combobox_version].pop(combo_box_name, None)

        configureClassificationWindow = ConfigureClassificationWindow(
            self.segmenter, self.edit_conf, self.config_yaml)
        configureClassificationWindow.show()

    @enter_function
    def push_remove_checkbox_button(self, checkbox_label):
        """
        push_remove_checkbox_button

        Args:
            checkbox_label: Description of checkbox_label.
        """
        self.close()

        object_name_to_remove = None

        for i, (object_name, label) in enumerate(
                self.config_yaml['checkboxes'].items()):
            if label == checkbox_label:
                object_name_to_remove = object_name

        if object_name_to_remove is not None:
            self.config_yaml['checkboxes'].pop(object_name_to_remove, None)

        configureClassificationWindow = ConfigureClassificationWindow(
            self.segmenter, self.edit_conf, self.config_yaml)
        configureClassificationWindow.show()

    @enter_function
    def push_remove_freetextbox_button(self, freetextbox_label):
        """
        push_remove_freetextbox_button

        Args:
            freetextbox_label: Description of freetextbox_label.
        """
        self.close()

        object_name_to_remove = None

        for i, (object_name, label) in enumerate(
                self.config_yaml['freetextboxes'].items()):
            if label == freetextbox_label:
                object_name_to_remove = object_name

        if object_name_to_remove is not None:
            self.config_yaml['freetextboxes'].pop(object_name_to_remove, None)

        configureClassificationWindow = ConfigureClassificationWindow(
            self.segmenter, self.edit_conf, self.config_yaml)
        configureClassificationWindow.show()

    @enter_function
    def push_add_freetextbox(self):
        """
        push_add_freetextbox

        Args:
        """
        self.close()

        configureSingleClassificationItemWindow = (
            ConfigureSingleClassificationItemWindow(
            self.segmenter, self.config_yaml, 'freetextbox', self.edit_conf))
        configureSingleClassificationItemWindow.show()

    @enter_function
    def push_add_combobox(self):
        """
        push_add_combobox

        Args:
        """
        self.close()

        configureSingleClassificationItemWindow = (
            ConfigureSingleClassificationItemWindow(
            self.segmenter, self.config_yaml, 'combobox', self.edit_conf))
        configureSingleClassificationItemWindow.show()

    @enter_function
    def push_add_checkbox(self):
        """
        push_add_checkbox

        Args:
        """
        self.close()

        configureSingleClassificationItemWindow = (
            ConfigureSingleClassificationItemWindow(
            self.segmenter, self.config_yaml, 'checkbox', self.edit_conf))
        configureSingleClassificationItemWindow.show()

    @enter_function
    def push_save(self):
        """
        push_save

        Args:
        """

        # Adjust latest combobox version
        # Extract the config file combobox latest version
        latest_combobox_version_file, latest_combobox_dict_file = (
            self.get_latest_combobox_version(self.config_yaml['comboboxes'])
        )

        # Reset combobox flag for enabling to track the correct combobox version
        ConfigPath.set_combobox_flag(True)
        ConfigPath.set_remove_combobox_flag(True)
        ConfigPath.set_combobox_version(latest_combobox_version_file)

        ConfigPath.write_config_file()

        if self.edit_conf:
            if self.segmenter.outputFolder is not None and os.path.exists(
                    self.segmenter.outputFolder):
                list_of_paths_to_classification_information_files = (
                    sorted(glob(f'{self.segmenter.outputFolder}'
                                f'{os.sep}**{os.sep}'
                                f'*ClassificationInformation.csv',
                                recursive=True)))

                for path in list_of_paths_to_classification_information_files:
                    with (open(path, 'r+') as file):
                        lines = file.readlines()

                        indices_to_populate_with_empty = []
                        total_number_of_items_in_new_setup = len(
                            self.config_yaml['checkboxes'].items()) + len(
                            self.config_yaml['comboboxes'].items()) + len(
                            self.config_yaml['freetextboxes'].items())

                        for i in range(len(lines)):
                            if i == 0:
                                header = lines[0]

                                header_items = header.split(',')

                                header_item_counter = 6  # start of the
                                # classification items
                                new_header = header_items[0] + ',' + \
                                             header_items[1] + ',' + \
                                             header_items[2] + ',' + \
                                             header_items[3] + ',' + \
                                             header_items[4] + ',' + \
                                             header_items[5]

                                for j, (_, label) in enumerate(
                                        self.config_yaml['checkboxes'].items()):
                                    if header_items[
                                        header_item_counter] == label:
                                        header_item_counter = \
                                        header_item_counter + 1
                                    else:
                                        indices_to_populate_with_empty.append(
                                            j + 6)
                                    new_header = new_header + ',' + label

                                for j, (combo_box_name, _) in enumerate(
                                        self.config_yaml["comboboxes"].items()):
                                    name = combo_box_name.replace('_',
                                                           ' ').capitalize()
                                    if header_items[
                                        header_item_counter] == name:
                                        header_item_counter = \
                                        header_item_counter + 1
                                    else:
                                        indices_to_populate_with_empty.append(
                                            j + 6 + len(
                                                self.config_yaml[
                                                    'checkboxes'].items()))
                                    new_header = new_header + ',' + name

                                for j, (_, label) in enumerate(
                                        self.config_yaml[
                                            'freetextboxes'].items()):
                                    if header_item_counter < len(
                                            header_items) and '\n' in \
                                            header_items[header_item_counter]:
                                        header_items[header_item_counter] = \
                                            header_items[
                                                header_item_counter].split(
                                                '\n')[0]

                                    if header_item_counter < len(
                                            header_items) and header_items[
                                        header_item_counter] == label:
                                        header_item_counter = \
                                        header_item_counter + 1
                                    else:
                                        indices_to_populate_with_empty.append(
                                            j + 6 + len(
                                                self.config_yaml[
                                                    'checkboxes'].items()) +
                                            len(self.config_yaml[
                                                    "comboboxes"].items()))
                                    new_header = new_header + ',' + label
                                lines[0] = new_header
                            else:
                                line = '\n' + lines[i]

                                line_items = line.split(',')

                                item_counter = 6  # start of the
                                # classification items
                                new_line = line_items[0] + ',' + line_items[
                                    1] + ',' + line_items[2] + ',' + line_items[
                                               3] + ',' + line_items[4] + ',' + \
                                           line_items[5]

                                for j in range(
                                        6, total_number_of_items_in_new_setup
                                           + 6):
                                    if j in indices_to_populate_with_empty:
                                        new_line = new_line + ','
                                    else:
                                        if '\n' in line_items[item_counter]:
                                            line_items[item_counter] = \
                                                line_items[
                                                    item_counter].replace(
                                                    '\n', '')
                                        new_line = new_line + ',' + line_items[
                                            item_counter]
                                        item_counter = item_counter + 1
                                lines[i] = new_line
                        file.truncate(0)
                        file.seek(0)
                        file.writelines(lines)
        slicerCARTConfigurationSetupWindow = SlicerCARTConfigurationSetupWindow(
            self.segmenter)
        slicerCARTConfigurationSetupWindow.show()
        self.close()

    @enter_function
    def push_cancel(self):
        """
        push_cancel

        Args:
        """
        slicerCARTConfigurationSetupWindow = SlicerCARTConfigurationSetupWindow(
            self.segmenter)
        slicerCARTConfigurationSetupWindow.show()
        self.close()


class ConfigureSingleClassificationItemWindow(qt.QWidget):
    @enter_function
    def __init__(self, segmenter, classification_config_yaml, item_added,
                 edit_conf, parent=None):
        """
        __init__

        Args:
            segmenter: Description of segmenter.
            classification_config_yaml: Description of classification_config_yaml.
            item_added: Description of item_added.
            edit_conf: Description of edit_conf.
            parent: Description of parent.
        """
        super(ConfigureSingleClassificationItemWindow, self).__init__(parent)

        self.segmenter = segmenter
        self.config_yaml = classification_config_yaml
        self.item_added = item_added
        self.edit_conf = edit_conf

        layout = qt.QVBoxLayout()

        name_hbox = qt.QHBoxLayout()

        name_label = qt.QLabel('Item Name : ')
        name_label.setStyleSheet("font-weight: bold")
        name_hbox.addWidget(name_label)

        self.name_line_edit = qt.QLineEdit('')
        name_hbox.addWidget(self.name_line_edit)

        layout.addLayout(name_hbox)

        self.edit_combobox(layout)

        self.save_button = qt.QPushButton('Save')
        self.save_button.clicked.connect(self.push_save)
        layout.addWidget(self.save_button)

        self.cancel_button = qt.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.push_cancel)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.setWindowTitle("Configure Classification Item")
        self.resize(200, 100)

    @enter_function
    def edit_combobox(self, layout):
        """
        edit_combobox

        Args:
            layout: Description of layout.
        """
        if self.item_added == 'combobox':

            # MB: Create a QHBox layout for the combo box information,
            # but do not show it yet in the pop-up. However, it has to be
            # created so it makes it easier to handle the adding of the
            # combobox later on.
            # Create a horizontal layout for the combo box and label
            options_hbox = qt.QHBoxLayout()
            # Label for the combo box
            options_label = qt.QLabel('Options : ')
            options_label.setStyleSheet("font-weight: bold")
            options_hbox.addWidget(options_label)
            # Create a combo box
            self.options_combobox = qt.QComboBox()
            self.options_combobox.setEditable(True)
            options_hbox.addWidget(self.options_combobox)
            # Do not add the Combobox to the layout (keep commented) unless
            # you want to see it in the pop-up.
            # layout.addLayout(options_hbox)

            # Create a horizontal layout for the explanations label
            info_hbox = qt.QHBoxLayout()

            message = ('\nAdjust the DropDown count.\n'
                       'Then, edit the option names.\n'
                       'If no text, option number will\n'
                       'be used as default.\n'
                       'N.B. Options will be saved sorted.\n')

            # Label for the combo box
            options_label_info = qt.QLabel(message)
            info_hbox.addWidget(options_label_info)
            layout.addLayout(info_hbox)

            # Create a horizontal layout for number of options input
            num_options_hbox = qt.QHBoxLayout()
            # Label for number of options
            num_options_label = qt.QLabel('Number of options: ')
            num_options_label.setStyleSheet("font-weight: bold")
            num_options_hbox.addWidget(num_options_label)
            # Spin box to specify the number of options
            self.num_options_spinbox = qt.QSpinBox()
            self.num_options_spinbox.setMinimum(1)  # At least 1 option
            self.num_options_spinbox.setMaximum(50)  # Arbitrary upper limit
            self.num_options_spinbox.setValue(5)  # Default value
            num_options_hbox.addWidget(self.num_options_spinbox)
            # Add the spin box layout to the main layout
            layout.addLayout(num_options_hbox)

            # Container for text fields to edit options
            self.options_edit_layout = qt.QVBoxLayout()
            layout.addLayout(self.options_edit_layout)

            @enter_function
            def clearLayout(layout):
                """
                Recursively clears all widgets and sublayouts from the given
                layout.
                :param layout: pop-up widget layout.
                """
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()  # Delete the widget
                    elif child.layout():
                        clearLayout(
                            child.layout())  # Recursively clear sublayouts

            # @enter_function ### THIS FUNCTION CANNOT USE ENTER_FUNCTION
            def updateOptionFields():
                """
                Dynamically adjust the number of options text field based on
                the number of options selected.
                """
                # Clear the text fields from the options layout
                clearLayout(self.options_edit_layout)
                # Clear all items from the combo box
                self.options_combobox.clear()

                # Create new text fields and populate the combo box
                for i in range(self.num_options_spinbox.value):
                    # Add text fields
                    option_hbox = qt.QHBoxLayout()
                    option_label = qt.QLabel(f"Option {i + 1}:")
                    option_line_edit = qt.QLineEdit()
                    option_line_edit.setText(f"")  # Default text

                    option_hbox.addWidget(option_label)
                    option_hbox.addWidget(option_line_edit)
                    self.options_edit_layout.addLayout(option_hbox)

                    # Add item to the combo box
                    self.options_combobox.addItem(option_line_edit.text)

                    # Define a function to update the combo box dynamically
                    @enter_function
                    def updateComboBoxItem(option_line_edit, index=i):
                        """
                        updateComboBoxItem

                        Args:
                            option_line_edit: Description of option_line_edit.
                            index: Description of index.
                        """
                        if index < self.options_combobox.count:
                            self.options_combobox.setItemText(
                                index, option_line_edit.text)
                        else:
                            self.options_combobox.addItem(option_line_edit.text)

                    # Use lambda with default argument to capture the current
                    # value of `i`
                    option_line_edit.textChanged.connect(
                        lambda _, le=option_line_edit,
                               idx=i: updateComboBoxItem(le, idx))

                # Populate the combo box with default values
                self.options_combobox.clear()
                for i in range(self.num_options_spinbox.value):
                    self.options_combobox.addItem(f"Option {i + 1}")

            # Connect spin box to update the option fields dynamically
            self.num_options_spinbox.valueChanged.connect(updateOptionFields)

    @enter_function
    def push_save(self):
        """
        push_save

        Args:
        """
        current_label_name = self.name_line_edit.text
        object_name = current_label_name.replace(' ', '_')

        if self.item_added == 'checkbox':
            label_found = False
            if self.config_yaml['checkboxes'] != None:
                for i, (_, label) in enumerate(
                        self.config_yaml['checkboxes'].items()):
                    if label == current_label_name:
                        label_found = True
            if label_found == False:
                # append
                if self.config_yaml['checkboxes'] == None:
                    self.config_yaml[
                        'checkboxes'] = \
                        {object_name: current_label_name.capitalize()}
                else:
                    self.config_yaml['checkboxes'].update(
                        {object_name: current_label_name.capitalize()})
        elif self.item_added == 'combobox':
            if self.options_combobox.count == 0:
                msg = qt.QMessageBox()
                msg.setWindowTitle('ERROR : No Drop Down Options Defined')
                msg.setText(
                    'At least one drop down option must be defined. '
                    'The previous classification configuration will be used. ')
                msg.setStandardButtons(
                    qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
                msg.buttonClicked.connect(
                    self.push_error_no_dropdown_option_defined)
                msg.exec()
            else:
                options_dict = {}
                combobox_option_items = [self.options_combobox.itemText(i) for i
                                         in range(self.options_combobox.count)]
                for option in combobox_option_items:
                    options_dict.update({option.replace(' ', '_'): option})

                item_found = False
                if self.config_yaml['comboboxes'] != None:
                    for i, (combobox_name, _) in enumerate(
                            self.config_yaml['comboboxes'].items()):
                        if combobox_name == object_name:
                            item_found = True
                else:
                    self.config_yaml['comboboxes'] = {}

                # Ensure 'comboboxes' key exists
                if 'comboboxes' not in self.config_yaml:
                    self.config_yaml['comboboxes'] = {}

                all_combobox_versions = self.config_yaml[
                    'comboboxes'].keys()

                latest_saved_version = (
                    self.get_latest_saved_combobox_version(
                        all_combobox_versions))

                # Get the existing version keys (e.g., v01, v02, ...)
                existing_versions = self.config_yaml['comboboxes'].keys()
                version_numbers = [int(k[1:]) for k in existing_versions if
                                   k.startswith('v') and k[1:].isdigit()]

                if ConfigPath.get_combobox_flag():
                    new_version_number = int(latest_saved_version) + 1
                    ConfigPath.set_combobox_flag()
                    ConfigPath.set_remove_combobox_flag()
                else:
                    new_version_number = latest_saved_version

                new_version_key = f"v{new_version_number:02d}"

                # If the latest version exists,
                # copy it and append new combobox to it
                if version_numbers:
                    latest_version_key = f"v{max(version_numbers):02d}"
                    new_version_data = self.config_yaml['comboboxes'][
                        latest_version_key].copy()
                else:
                    new_version_data = {}

                # Add the new combobox if not already present
                if object_name not in new_version_data:
                    new_version_data[object_name] = options_dict

                # Save the updated versioned comboboxes
                self.config_yaml['comboboxes'][
                    new_version_key] = new_version_data

        elif self.item_added == 'freetextbox':
            label_found = False

            if self.config_yaml['freetextboxes'] != None:
                for i, (_, label) in enumerate(
                        self.config_yaml['freetextboxes'].items()):
                    if label == current_label_name:
                        label_found = True

            if label_found == False:
                # append
                if self.config_yaml['freetextboxes'] == None:
                    self.config_yaml[
                        'freetextboxes'] = \
                        {object_name: current_label_name.capitalize()}

                else:
                    self.config_yaml['freetextboxes'].update(
                        {object_name: current_label_name.capitalize()})

        configureClassificationWindow = ConfigureClassificationWindow(
            self.segmenter, self.edit_conf, self.config_yaml)
        configureClassificationWindow.show()
        self.close()

    @enter_function
    def push_error_no_dropdown_option_defined(self):
        """
        push_error_no_dropdown_option_defined

        Args:
        """
        self.push_cancel()

    @enter_function
    def push_cancel(self):
        """
        push_cancel

        Args:
        """
        self.close()

    @enter_function
    def get_latest_saved_combobox_version(self, all_combobox_versions):
        """
        Get the latest saved (in configuration yaml file) version of combobox.
        :Param: all_combobox_version = dictionary that contains all combobox
        :return: integer indicating the version ex 8 (if 8 versions)
        """

        if (len(all_combobox_versions) > 0):

            existing_versions = all_combobox_versions
            version_numbers = max([int(k[1:]) for k in existing_versions if
                                   k.startswith('v') and k[1:].isdigit()])
        else:
            version_numbers = 0

        return version_numbers
