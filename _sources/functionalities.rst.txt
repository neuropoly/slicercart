Functionalities
==========================
This section lists the functionalities of SlicerCART. If the function you
are looking for is not found below, it is likely that SlicerCART does not have
yet this feature: you are invited to open an issue on the `Github Repository <https://github.com/neuropoly/slicer-manual-annotation/issues>`_ to
request the functionality you are looking for.

**Details:**

This module has been adapted to perform several tasks. Among other things, it allows the user to:

- Customize configuration preferences for project-specific segmentation or classification tasks, including:

  - Task Selection (Segmentation and/or Classification)
  - Modality to be viewed/process/annotated (CT or MRI) [Must be one or the other for now. Does not currently take DICOM images.]
  - *Brain Imaging Data Structure* (BIDS) format imposition (test quickly if a dataset respects the BIDS convention through a BIDS-validator script:
    makes unable to load a dataset if it does not respect BIDS format)
  - View to display by default in the viewer (e.g. axial, sagittal, etc.) [only one at the time]
  - Interpolation of images (by default, Slicer images that are displayed
    get "interpolated" (i.e. smoother): with SlicerCART, you can toggle through this option)
  - For CT-Scans:

    - Specify the range of Hounsfield units for which a segmentation mask will be feasible (e.g. 45 to 90): otherwise, segmentation mask will not be created.
  - Customize keyboard shortcuts
  - Customize mouse button functions
  - Configure from the user interface the segmentation labels,
    including:

    - Label name
    - Label value
    - Color
    - Adding/Removal of labels (at least one is required for proper use)
  - Select if timer should be displayed during segmentation task
  - Configure from the GUI the classification labels,
    including adding/Removal of:

    - Labels
    - Checkbox
    - DropDown Menu (options)
    - Text field

- Identify the name, degree and revision step related to the human annotator
- Select folder of interest where volumes are saved

  - Display automatically the PATH of the loaded volume
- Select the output folder where processing and work is preferred to be saved
- Display in the user interface a case list of all the studies of interests for the segmentation task (from a site directory or a customized list)
- Select from the case list any volume of interest to display
- Navigate through case list from next and previous buttons
- Load automatically the first remaining case for segmentation in a customized list
- Create automatically all required segments that may be used according to the project configuration each time a volume is displayed
- From the Classification window:

  - Perform classification tasks e.g. checkbox, dropdown menu, textbox
  - Check and load a specific classification labels version for a given volume
  - Save a .csv file with classification statistics (e.g. subject, annotator's name and degree, revision step, date and time, checkboxes / dropdown / free text fields)
  - Go automatically to the next case in the UI

- From the Segmentation window:

  - Open directly the Segment Editor
  - Select the active segment to edit
  - Start Painting
  - Erase any part of visible masks
  - Select Lasso Paint (fills the space of a contour-based geometrical annotation)
  - Place a measurement line
  - Load the latest available segmentation mask versions available
  - Execute multiple automated functions when saving segmentation masks for a given volume. Indeed, the automated functions:

    - Save segmentation masks in the selected output folder with volume file hierarchy
    - Track the different versions (save the following version if previous version(s) already exist(s)) *N.B. limitation to 99 versions for a single volume*
    - Save a .csv file with segmentation statistics (e.g. subject, annotator's name and degree, revision step, date and time, total duration, duration of each label annotation)
    - Go to the next remaining case and make it ready to segment without any further action
  - Load a pre-existing segmentation for further modification (will be saved as a new version)

See :doc:`repository_organization` for the repository files and folders tree structure.

See :doc:`class_organization` for the class diagrams of the repository scripts.

This documentation was last updated on |today|.