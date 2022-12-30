#! /usr/bin/env python3

import os
import datetime
import osxphotos
from osxphotos import ExportOptions
from tqdm import tqdm # progress bar
import tkinter as tk
from tkinter import ttk
import multiprocessing
import sqlite3


file_count = 0
export_path = "/Volumes/External Backup/Media/Test"
photosdb = osxphotos.PhotosDB()
photos = photosdb.photos()
uuids = [photo.uuid for photo in photos]
fobj = ExportOptions()
fobj.download_missing = True
#fobj.use_photos_export = True
#fobj.overwrite = True
for i, photo in enumerate(photos):
    # Export the photo to the desired location
    original_filename = photo.original_filename

    # Get the file extension from the original filename
    ext = original_filename.split(".")[-1].upper()

    # We want to split up the media into either "Videos" or "Photos"
    file_type = "Videos" if ext in ["MOV", "MP4"] else "Photos"

    new_path = export_path + "/" + file_type

    out = osxphotos.PhotoExporter(photo).export(new_path, photo.original_filename, options=fobj)
    if len(out.exported) == 0:
        print(photo.original_filename)

    print(f"export {i}")

