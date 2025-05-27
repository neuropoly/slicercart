import copy

from utils import *
class LoadClassificationWindow(qt.QWidget):
   @enter_function
   def __init__(self, segmenter, classificationInformation_df, parent = None):
      super(LoadClassificationWindow, self).__init__(parent)

      self.classificationInformation_df = classificationInformation_df
      self.segmenter = segmenter

      layout = qt.QVBoxLayout()
      self.versionTableView = qt.QTableWidget()
      layout.addWidget(self.versionTableView)

      buttonLayout = qt.QHBoxLayout()

      versionLabel = qt.QLabel()
      versionLabel.setText('Classification version to load: ')
      versionLabel.setStyleSheet("font-weight: bold")
      buttonLayout.addWidget(versionLabel)

      self.versionDropdown = qt.QComboBox()
      buttonLayout.addWidget(self.versionDropdown)

      layout.addLayout(buttonLayout)

      if classificationInformation_df.shape[0] > 0:
          available_versions = classificationInformation_df['Classification version'].to_list()
          for v in available_versions:
              self.versionDropdown.addItem(v)

          self.versionTableView.setRowCount(len(available_versions))
          self.versionTableView.setColumnCount(4)
          self.versionTableView.horizontalHeader().setStretchLastSection(True)
          self.versionTableView.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

          for index, row in classificationInformation_df.iterrows():
                cell = qt.QTableWidgetItem(row['Classification version'])
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.versionTableView.setItem(index, 0, cell)
                self.versionTableView.setHorizontalHeaderItem(0, qt.QTableWidgetItem('Version'))

                cell = qt.QTableWidgetItem(row['Annotator Name'])
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.versionTableView.setItem(index, 1, cell)
                self.versionTableView.setHorizontalHeaderItem(1, qt.QTableWidgetItem('Annotator'))

                cell = qt.QTableWidgetItem(row['Annotator degree'])
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.versionTableView.setItem(index, 2, cell)
                self.versionTableView.setHorizontalHeaderItem(2, qt.QTableWidgetItem('Degree'))

                cell = qt.QTableWidgetItem(row['Date and time'])
                cell.setFlags(qt.Qt.NoItemFlags)
                cell.setForeground(qt.QBrush(qt.QColor(self.segmenter.foreground)))
                self.versionTableView.setItem(index, 3, cell)
                self.versionTableView.setHorizontalHeaderItem(3, qt.QTableWidgetItem('Date and Time'))

      self.loadButton = qt.QPushButton('Load')
      self.loadButton.clicked.connect(self.pushLoad)
      layout.addWidget(self.loadButton)

      self.cancelButton = qt.QPushButton('Cancel')
      self.cancelButton.clicked.connect(self.pushCancel)
      layout.addWidget(self.cancelButton)

      self.setLayout(layout)
      self.setWindowTitle("Load Classification")
      self.resize(800, 400)

   @enter_function
   def pushLoad(self):
       selected_version = self.versionDropdown.currentText
       print('selected_version', selected_version)
       print('self classif df', self.classificationInformation_df)



       selected_version_df = (
           self.classificationInformation_df[
               self.classificationInformation_df[
                   'Classification version'
               ]==selected_version].reset_index(drop = True))

       print('selected_version_df', selected_version_df)
       print('segmemter config yaml', self.segmenter.config_yaml["checkboxes"].items())

       columns_names = self.get_csv_all_classification_labels(self.classificationInformation_df)
       print('\n\ncolumns name in push load', columns_names)

       selected_version_df = (
                                 selected_version_df.loc)[:,
                             ~selected_version_df.isin(['--']).any()]
       print('selected_version_df', selected_version_df)




       intersection = set(selected_version_df.columns).intersection(
           columns_names.keys())

       print('intersection', intersection)
       print('len intersection', len(intersection))
       classif_label = self.get_label_names_to_show(intersection,
                                                    columns_names)
       # Final output (for checking)
       # print(classif_label)

       print('\n\n\nclassif checkboxes !!!!!', classif_label)

       self.clean_classification_grid(self.segmenter)



       comboboxesStartRow = self.segmenter.setupCheckboxes(3, classif_label,
                                                           flag_use_csv=True)
       print('checkboxes added')

       combobox_version = selected_version_df['Combobox version'].iloc[0]
       version_combobox_label_dict = {}
       version_combobox_label_dict[combobox_version] = classif_label[
           'comboboxes']
       total_dict_combobox = {}
       total_dict_combobox['comboboxes'] = version_combobox_label_dict
       # self.segmenter.setupComboboxes(comboboxesStartRow, classif_label, combobox_version)
       start_row = self.segmenter.setupComboboxes(comboboxesStartRow,
                                       total_dict_combobox, combobox_version)
       print('comboboxes added')


       print('classif label freetextbozxese', classif_label['freetextboxes'])
       self.segmenter.setupFreeText(start_row, classif_label['freetextboxes'])

       # Attribute the correct classification labels to the SlicerCART widget
       export_to_slicercart = copy.deepcopy(classif_label)
       self.segmenter.set_classification_version_labels(export_to_slicercart)
       print('export to slicer cart')




       iteration_dict = self.segmenter.get_label_iteration_dict()
       print('iteration_dict%%%%%*******', iteration_dict)

       # for i, (objectName, label) in enumerate(self.segmenter.config_yaml["checkboxes"].items()):
       # for i, (objectName, label) in enumerate(iteration_dict["checkboxes"].items()):
       for i, (objectName, label) in enumerate(classif_label["checkboxes"].items()):

           print('columns names', list(selected_version_df.columns))
           print('adding i', i)
           print(' objectName adding', objectName)
           print('label adding', label)
           print('module checbokex', iteration_dict["checkboxes"].items())

           # config_file_dict = self.segmenter.config_yaml["checkboxes"]
           config_file_dict = classif_label['checkboxes']

           # column_name = f'"{{\'{config_file_dict[objectName]}\': \'checkboxes\'}}"'
           # column_name = f"'{config_file_dict[objectName]}': 'checkboxes'"

           print('testing correct name', config_file_dict)
           print('testinc 2 corre anem ', config_file_dict[objectName])

           column_name = self.recreate_column_name(objectName,
                                                   'checkboxes')


           print('column name', column_name)

           try:
               print('in try column')

               if selected_version_df.at[0, column_name] == 'Yes':
                   self.segmenter.checkboxWidgets[objectName].setChecked(True)
               elif selected_version_df.at[0, column_name] == 'No' or str(selected_version_df.at[0, column_name]) == 'nan':
                   self.segmenter.checkboxWidgets[objectName].setChecked(False)

           except:
               print(' means that the column name does not exist in the '
                     f'loaded classificatoin version {column_name}')
               pass

       for i, (comboBoxName, options) in enumerate(
               self.segmenter.config_yaml["comboboxes"][
                   combobox_version].items()):
           print('columns names', list(selected_version_df.columns))
           print('adding i', i)
           print(' combobox name adding', comboBoxName)
           print('label adding', options)



           config_file_dict = self.segmenter.config_yaml["comboboxes"][
               combobox_version]

           print('module combobox', config_file_dict)

           label = config_file_dict[comboBoxName]
           print('label combo', label)

           column_name = self.recreate_column_name(comboBoxName,
                                                   'comboboxes')
           print('column_name combobo', column_name)
           # self.segmenter.comboboxWidgets[comboBoxName].setCurrentText(selected_version_df.at[0, comboBoxName.replace("_", " ").capitalize()])
           # self.segmenter.comboboxWidgets[comboBoxName].setCurrentText(
           #     selected_version_df.at[0, column_name])
           self.segmenter.comboboxWidgets[comboBoxName].setCurrentText(
                   selected_version_df.at[0, column_name])


       # Ensure to save using the correct combobox version if later
       # classificaitno
       ConfigPath.set_combobox_version(combobox_version)




       print('now about to do freetextboxes')

       print('iteration dict before free textbox', iteration_dict)
       print('classif label free textboxes', classif_label)

       for i, (freeTextBoxObjectName, label) in enumerate(classif_label['freetextboxes'].items()):

           print('label', label)

           # saved_text = selected_version_df.at[0, label.capitalize()]



           # config_file_dict = self.segmenter.config_yaml["freetextboxes"]
           # config_file_dict = classif_label['freetextboxes']

           print('config file dict freetextbox', config_file_dict)
           print(' freetextboxe object name adding', freeTextBoxObjectName)
           # print(' saved text', saved_text)



           # column_name = f'"{{\'{config_file_dict[objectName]}\': \'checkboxes\'}}"'
           # column_name = f"'{config_file_dict[objectName]}': 'checkboxes'"
           column_name = self.recreate_column_name(freeTextBoxObjectName,
                                                   'freetextboxes')
           print('columns names', list(selected_version_df.columns))
           print('adding i', i)
           print('label adding', label)
           print('label capitalize', label.capitalize())
           print('module checbokex freetextbox', config_file_dict.items())
           print('')


           try:
               print(' in try column freetext')

               saved_text = selected_version_df.at[0, column_name]
               print('saved_text', saved_text)

               if str(saved_text) != 'nan':
                   self.segmenter.freeTextBoxes[freeTextBoxObjectName].setText(saved_text)
               else:
                   self.segmenter.freeTextBoxes[freeTextBoxObjectName].setText("")

           except:
               print(' means that the column name does not exist in the '
                     'current version ')
               pass



       self.close()

   def pushCancel(self):
       self.close()


   @enter_function
   def get_csv_all_classification_labels(self, csv_df):
       # Extract column names as a list
       column_names = csv_df.columns.tolist()
       print('column_names', column_names)
       # info_dict = self.segmenter.build_current_classif_dictionary()
       classification_labels = []
       for element in column_names:
           try:
               # Convert string to dictionary
               result_dict = eval(element)
               if isinstance(result_dict,
                             dict):  # Ensure the result is a dictionary
                   print("Conversion successful:", result_dict)
                   classification_labels.append(element)
               else:
                   print("The string did not evaluate to a dictionary.")
           except (SyntaxError, NameError) as e:
               print("Failed to convert string to dictionary:", e)
       print('list up to date', classification_labels)
       # classification_labels = {key: value for d in classification_labels for key, value in
       #                d.items()}
       # Convert strings to dictionaries and combine them
       result_dict = {}
       for d in classification_labels:
           try:
               # Safely evaluate the string to a dictionary
               parsed_dict = eval(d)  # Use with caution if input is untrusted
               if isinstance(parsed_dict, dict):
                   for key, value in parsed_dict.items():
                       result_dict[d] = value
           except Exception as e:
               print(f"Failed to parse '{d}': {e}")

       return result_dict


   @enter_function
   def get_label_names_to_show(self, intersection, columns_names):
       """
       :param intersection: set of all values in the specified version
       :param columns_names: list of column names with data from csv file
       :return: classif label, a dictionary with keys corresponding to the
       types of classification labels and values corresponding to dictionary
       where values of each element are the name of the label in the UI
       e.g. {'checkboxes': {'SDH': 'SDH',
       """
       # Initialize the classif_label dictionary
       classif_label = {}

       # Assuming CLASSIFICATION_BOXES_LIST and intersection are already defined
       for element in CLASSIFICATION_BOXES_LIST:
           # Initialize an empty dictionary for each classification type
           classif_label[element] = {}

       # Iterate through the intersection (assuming it's already defined)
       for element in intersection:
           print('element', element)

           if element in columns_names:
               label_type = columns_names[
                   element]  # Get the label type (e.g., 'checkboxes')
               print('label type', label_type)

               # Parse the element (extract the key)
               parsed_value = element.strip("{}").split(":")[0].strip(" '")
               print('parsed value', parsed_value)

               # Initialize the dictionary for the label type if it doesn't exist
               if label_type not in classif_label:
                   classif_label[
                       label_type] = {}  # Create an empty dictionary for this label_type

               # Add the parsed value to the appropriate label type in the classif_label dictionary
               classif_label[label_type][parsed_value] = parsed_value
               print('classif label', classif_label[label_type][parsed_value])

       return classif_label


   @enter_function
   def clean_classification_grid(self, segmenter):
       # Loop through all items in the layout and remove them
       for i in reversed(range(segmenter.ui.ClassificationGridLayout.count(

       ))):
           widget = segmenter.ui.ClassificationGridLayout.itemAt(
               i).widget()
           if widget is not None:
               widget.deleteLater()

   @enter_function
   def recreate_column_name(self, name, type):
       return f"{{'{name}': '{type}'}}"

   @enter_function
   def valiate_classification_ui_config(self, segmenter):
       for i in reversed(range(segmenter.ui.ClassificationGridLayout.count(

       ))):
           widget = segmenter.ui.ClassificationGridLayout.itemAt(
               i).widget()
           print('widget', widget)




