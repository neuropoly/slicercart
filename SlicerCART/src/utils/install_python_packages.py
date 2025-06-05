# TODO: There is probably a more elegant way to install pacakages through the
#  extension manager when the user installs the extension.
# TODO: check if the package installed with error

### MB: import qt can be done from here and will use the embedded Slicer qt
# version (which is great, since it removes the need for external download of
# Qt). Previously, when import qt was in requirements.py, SlicerCART failed
# to instantiate at fresh install since if a module was not found, a pop-up
# was generated to offer the option to install them (but the pop-up requires
# qt, without being improted and making the instanciation process failing).
# This is likely due because utils filders are imported like from utils
# import * in other .py files, so depending on the OS, all files can be
# imported at the same time and not in necessary order (e.g. requirements.py
# has not necessarily been imported before install_python_packages file: from
# discussion with Kalum Ost).
import qt
import slicer

# Dictionary of required python packages and their import names
# N.B. Some pip_name (like pandas) may require specific version
REQUIRED_PYTHON_PACKAGES = {
    "nibabel": "nibabel",
    "pandas==2.2.3": "pandas",
    "PyYAML": "yaml",
    "pynrrd": "nrrd",
    "slicerio": "slicerio",
    "bids_validator": "bids_validator"
}


def check_and_install_python_packages():
    """
    check_and_install_python_packages

    """
    missing_packages = []

    for pip_name, import_name in REQUIRED_PYTHON_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        msg = ("SlicerCART module: The following required python packages are "
               "missing:")
        msg += "\n" + "\n".join(missing_packages)
        msg += "\nWould you like to install them now?"
        response = qt.QMessageBox.question(slicer.util.mainWindow(),
                                           'Install Extensions', msg,
                                           qt.QMessageBox.Yes |
                                           qt.QMessageBox.No)
        if response == qt.QMessageBox.Yes:
            slicer.util.pip_install(missing_packages)
        else:
            qt.QMessageBox.warning(slicer.util.mainWindow(),
                                   'Missing Extensions',
                                   'The SlicerCART module cannot be loaded '
                                   'without the required extensions.')
