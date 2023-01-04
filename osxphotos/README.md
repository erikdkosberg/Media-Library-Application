## OSXPHOTOS

This directory uses the 'osxphotos' API to talk to 'Photos.db'. It leverages the 'PhotoExporter' to export a photo with given filters.

    i.e. out = PhotoExporter(photo).export(new_path, new_file, options)

exporter.py has a class called 'Exporter' with a method called 'export' - it will skip already downloaded photos

### To make this script work

1. Install osxphotos, tdqm via pip

2. Modify the export path to your local path

3. Optionally call that 'dates' method before exporting to grab data from certain dates

### Weird Behaviors

If the export is backed up to the cloud - it skips the file thinking it already exists

    workaround 1: Store to a folder with '.nosync' at the end of the folder name

    workaround 2: Delete the files manually and try again

Unable to run multiprocessing - cannot Pickle sqlite.Connection object

    workaround 1: Use asyncio to create a queue of tasks

Random retry error when exporting

    workaround 1: Wait and run the collection again

When runnning from automator app, the terminal does not display

    workaround 1: Use a popup window with Tkinter to show the progress bar

Packages dont exist in automator app

    workaround 1: Start a virtual environment and install packages
