Quick Start
======================

Follow the steps below to use SlicerCART.

Important Note
--------------

The current version **IS NOT** able to:

- Load multiple MRI contrasts at the same time for a given subject (`issue 8 <https://github.com/neuropoly/slicercart/issues/8>`__)
- Load automatically the latest classification version (`issue 184 <https://github.com/neuropoly/slicercart/issues/184>`__)
- Compare multiple segments to revise them (`issue 180 <https://github.com/neuropoly/slicercart/issues/180>`__)

Start Segmentation and Classification
---------------

1. Open 3D Slicer
2. Launch SlicerCART
3. Select "New configuration" or "Continue from existing output folder", and click on Next


   New configuration -> Start a new project and define its specific configuration (clicking on Next will show a pop-up window that allows the user to customize SlicerCART settings)



   Continue from existing output folder -> Resume previous tasks for a given project (clicking on Next will resume the specific project-folder configuration)


   Use template configuration -> Not available (for now).

   .. image:: /_static/images/select_configuration_popup.png

4. Edit the SlicerCART configuration interface to define project-specific configuration

   *N.B. Only if "New Configuration" has been selected (otherwise, go to* `7
   <#display-volume-to-segment>`_ *).*



   Select if you will complete segmentation and/or classification tasks, the modality  (takes only one), if you impose BIDS (will pass a BIDS validator test before loading volumes), input volumes file extensions, etc.



   By default, at least one segmentation label is required. Classification labels can be modified as wanted (no minimum required).

   .. image:: /_static/images/select_configuration_module.png

5. Select volumes folder, and specify annotator information

   * Select the folder that contains the images that you want to process (BIDS folder, will not consider images in derivatives)


   * Specify the annotator name, degree and revision step (all are mandatory for saving)

   .. image:: /_static/images/folder_and_name_to_use.png
   .. image:: /_static/images/example_loading_cases_ui.png

   .. note::

      If loading cases in the UI fails, please open an issue on the `GitHub
      Issues page <https://github.com/neuropoly/slicercart/issues>`_, or ask a team member. If this step has not succeeded, you will not be able to use SlicerCART.

6. Select output folder

   Select the folder where output data (e.g. segmentation masks, statistics) will be saved. If there is already an existing configuration in that folder, note that this folder configuration will we considered for the current project tasks.

   .. image:: /_static/images/select_output_folder.png

.. _display-volume-to-segment:
7. Display Volume to Segment

   Click on the case in Case list you want to display.
   Perform classification or segmentation from the appropriate window.

   .. image:: /_static/images/select_volume_to_segment.png

8. Classification

   Click on the Classification window. Select the appropriate labels depending on your configuration, for each case.

   .. image:: /_static/images/classification_example.png

9. Segmentation

   Click on the Segmentation window, then on the case you want to start segmentation. Click on:

   - SegmentEditor: opens the default segment editor of 3D Slicer
   - Paint: enables the user to paint the **first** mask label
   - Erase Mode: enables the user to erase the current segment label

   .. image:: /_static/images/perform_segmentation.png

10. Save Classification OR Segmentation

   *N.B. You can only save segmentation OR classification labels separately (you cannot save both at the same time, for the moment).*



   Once segmentation is completed, click on *Save segmentation* (or *Save classification*) [or keyboard shortcut if defined] to save the segmentation mask or classification labels in the output folder.



   Note that a `.csv` file will be generated for basic segmentation statistics (e.g. time of segmentation, annotator information, etc.). Classification data is saved in a separate `.csv` file per volume. Each `.csv` file can have multiple version (up to 99 is supported).

   .. image:: /_static/images/save_segmentation.png

10. Go to the Next Case

    After a save (whether classification or segmentation), the viewer loads automatically the next case (in the UI case list for classification; in the remaining_list.yaml file for segmentation). A pop-up appears if it is the last case in the remaining_list.yaml (or in the UI case list).

    .. image:: /_static/images/continue_segmentation.png

Feedback
--------------------

If you have any question and/or inquiry, please open a new issue on `SlicerCART Github <https://github
.com/neuropoly/slicer-manual-annotation/issues>`__.

Thank you!

The SlicerCART Team

----