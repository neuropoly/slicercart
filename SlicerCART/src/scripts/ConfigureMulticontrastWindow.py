from utils import *

class ConfigureMulticontrastWindow(qt.QWidget):
    def __init__(self, segmenter, current_subject, subjects_to_all_contrasts, parent=None):
        super().__init__(parent)    # Call the constructor of the parent class

        self.segmenter = segmenter
        self.current_subject = current_subject
        self._initial_contrasts = subjects_to_all_contrasts[current_subject]
        
        Debug.print(self, "initial contrasts: "+ str(self._initial_contrasts))

        _main_layout = qt.QVBoxLayout()
        self.setLayout(_main_layout)

        self.list_widget = qt.QListWidget()
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragDropMode(qt.QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(qt.Qt.MoveAction)

        for i, (contrast_name, checked_state) in enumerate(list(self._initial_contrasts.items())):
            item = qt.QListWidgetItem(contrast_name)
            item.setFlags(item.flags() | qt.Qt.ItemIsUserCheckable | qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable | qt.Qt.ItemIsDragEnabled)
            item.setCheckState(qt.Qt.Checked if checked_state else qt.Qt.Unchecked)
            self.list_widget.addItem(item)

        _main_layout.addWidget(self.list_widget)
        
        # Number of rows displayed
        contrast_number_hbox = qt.QHBoxLayout()
        contrast_number_hbox.addWidget(qt.QLabel("Number of rows:"))
        
        self.multicontrast_layout_row_count_combobox = qt.QComboBox()
        contrast_number_hbox.addWidget(self.multicontrast_layout_row_count_combobox)
        
        for i in range(1, 5):
            self.multicontrast_layout_row_count_combobox.addItem(str(i + 1))
            
        self.multicontrast_layout_row_count_combobox.currentIndexChanged.connect(self.set_multicontrast_layout_rows)
        
        _main_layout.addWidget(self.multicontrast_layout_row_count_combobox)

        self.apply_button = qt.QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.push_apply)
        _main_layout.addWidget(self.apply_button)

        self.cancel_button = qt.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.push_cancel)
        _main_layout.addWidget(self.cancel_button)

        self.setWindowTitle(f"Configure Contrasts for {self.current_subject}")
        self.resize(350, 450)

    def set_multicontrast_layout_rows(self):
        row_count = int(self.multicontrast_layout_row_count_combobox.currentText)
        
        for i in range(row_count):
            requested_contrast = self.list_widget.item(i).text()
            self.segmenter.subjects_to_all_contrasts[self.current_subject][requested_contrast] = True
        
        self.segmenter.loadPatient()

    def push_apply(self):
        # final_ordered_contrasts = []
        # for i in range(self.list_widget.count()):
        #     item = self.list_widget.item(i)
        #     contrast_full_text = item.text()
        #     if ": " in contrast_full_text:
        #         contrast_name = contrast_full_text.split(": ", 1)[1]
        #     else:
        #         contrast_name = contrast_full_text

        #     is_checked = item.checkState() == qt.Qt.Checked
        #     final_ordered_contrasts.append((contrast_name, is_checked))

        # if (hasattr(self.SlicerCARTWidget_instance, 'subject_to_all_contrasts') and
        #         self.current_subject_id in self.SlicerCARTWidget_instance.subject_to_all_contrasts):
        #     self.SlicerCARTWidget_instance.subject_to_all_contrasts[self.current_subject_id] = final_ordered_contrasts
        self.close()

    def push_cancel(self):
        self.close()

