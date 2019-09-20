import os
import shutil
import pyqt5ac


# constants for various directory paths and file paths
SCRIPTS_DIR = os.path.realpath(os.path.dirname(__file__))
ROOT_DIR = os.path.realpath(os.path.join(SCRIPTS_DIR, '..'))
CORE_DIR = os.path.realpath(os.path.join(ROOT_DIR, 'openlp', 'core'))
RESOURCE_IMAGES_DIR = os.path.realpath(os.path.join(ROOT_DIR, 'resources', 'images'))

RESOURCES_PY_FILENAME = os.path.realpath(os.path.join(CORE_DIR, 'resources.py'))
RESOURCES_PY_OLD_FILENAME = os.path.realpath(os.path.join(CORE_DIR, 'resources.py.old'))
RESOURCES_PY_NEW_FILENAME = os.path.realpath(os.path.join(CORE_DIR, 'resources.py.new'))

OPENLP_2_QRC_FILENAME = os.path.realpath(os.path.join(RESOURCE_IMAGES_DIR, 'openlp-2.qrc'))


def generate_resources():
    # Back up the existing resources
    try:
        shutil.move(RESOURCES_PY_FILENAME, RESOURCES_PY_OLD_FILENAME)
    except FileNotFoundError:
        # there was no existing file to back up
        pass

    # Create the new data from the updated qrc
    pyqt5ac.main(force=True, ioPaths=[[OPENLP_2_QRC_FILENAME, RESOURCES_PY_NEW_FILENAME]])

    # Remove patch breaking lines
    with open(RESOURCES_PY_NEW_FILENAME, 'r') as infile, open(RESOURCES_PY_FILENAME, 'w') as outfile:
        for line in infile:
            if not line.startswith('# Created By:'):
                print(line, file=outfile, end='')

    # Patch resources.py to OpenLP coding style
    # couldn't find a good way to automate this in python

    # Remove temporary files
    try:
        os.remove(RESOURCES_PY_OLD_FILENAME)
    except FileNotFoundError:
        # don't care if the files don't exist because we are just deleting them anyway
        pass
    try:
        os.remove(RESOURCES_PY_NEW_FILENAME)
    except FileNotFoundError:
        # same as above
        pass


if __name__ == '__main__':
    generate_resources()
