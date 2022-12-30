#! /usr/bin/env python3

import os
import datetime
import time
import osxphotos
from osxphotos import ExportOptions
from tqdm import tqdm  # progress bar
import tkinter as tk
from tkinter import ttk


class Exporter:
    """Uses the 'osxphotos' library to connect to 'Photos.db' and access all photos from current user on Mac OS.

    Can be used to backup all media to an external disk - as well as process the data coming in.

    You can change the obj.date() call to modify the collection period. Will skip files that already exist."""

    # Connect to the database and define some key attributes
    def __init__(self):
        self.file_count = 0
        self.export_path = "/Volumes/External Backup/Media"
        self.photosdb = osxphotos.PhotosDB()
        self.photos = self.photosdb.photos()
        self.albums = self.photosdb.albums

        print(
            "#-------------------------------Python Exporting Tool-------------------------------#"
        )
        print("\nBeginning Export...\n")

    # Reads in Y-M-D as string and converts it to a datetime object
    def parse_dt(self, dt) -> datetime:
        year = int(dt.split("-")[0])
        month = int(dt.split("-")[1])
        day = int(dt.split("-")[2])

        return datetime.datetime(year, month, day)

    # Sets the date filter for the database connection
    def dates(self, fd, td) -> None:
        self.photos = self.photosdb.photos(
            from_date=self.parse_dt(fd), to_date=self.parse_dt(td)
        )

    # So we can view the process when running the script from something like Mac OS terminal
    def background_window(self, n) -> None:

        # Create the root window
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("400x200")  # size of window

        # Upper label
        self.upper_label = tk.Label(self.root, text="Running Collection...\n\n")
        self.upper_label.pack()

        # Create a progress bar widget
        self.progress = ttk.Progressbar(
            self.root, length=350, mode="determinate", orient="horizontal"
        )
        self.progress["value"] = 0
        self.progress.pack()

        # Lower label - display the progress of the collection to a pop up window
        self.lower_label = tk.Label(self.root, text="Progress\n\n")
        self.lower_label.pack()

    # Update the window after processing each photo
    def update_background(self, i, label) -> None:
        self.progress["value"] = (i + 1) / len(self.photos) * 100
        self.lower_label["text"] = f"   {round((i+1)/len(self.photos)*100, 2)}" + "%"
        self.progress.update()
        self.root.update()

    # Main function - call internal methods and run the export
    def export(self) -> None:

        # Initialize the pop-up window
        self.background_window(len(self.photos))

        # Loop through each photo - assumes we've already modified self.photos at this point
        total_time = 0
        for i, p in enumerate(tqdm(self.photos)):
            original_filename = p.original_filename

            # Get the file extension from the original filename
            ext = original_filename.split(".")[-1].upper()

            # We want to split up the media into either "Videos" or "Photos"
            file_type = "Videos" if ext in ["MOV", "MP4"] else "Photos"

            # Get the datetime information from the photo
            dt = p.date

            # This is what we will use to name the files - so we can easily search them by datetime
            str_dt = (
                str(dt)
                .replace(" ", "")
                .replace("-", "")
                .replace(":", "")
                .replace("-", "")
                .replace(".", "")[:14]
            )

            # Make a new folder for each year
            year = str(dt.year)
            new_path = self.export_path + "/" + file_type + "/" + year
            if not os.path.exists(new_path):
                os.makedirs(new_path)

            # Just to have consistent spelling
            if ext == "JPG":
                ext = "jpeg"

            # To check if the file is already there
            check_path = new_path + "/" + str_dt + "." + ext
            check_dir = os.listdir(new_path)

            check1 = check_path.split("/")[-1].split(".")[0]
            check2 = [z.split("/")[-1].split(".")[0] for z in check_dir]

            # If file doesnt exist, export it
            if check1 not in check2:

                # Customize these options to configure the export
                fobj = ExportOptions()
                fobj.download_missing = True
                fobj.use_photos_export = True
                fobj.overwrite = True

                # Exiftool must be installed for this to work
                # fobj.exiftool = True

                # Make everything .jpeg just to make things easier
                if ext == "PNG" or ext == "HEIC":
                    fobj.convert_to_jpeg = True

                # Attach a duplicate .json file with associated metadata
                # fobj.sidecar = True

                start_time = time.perf_counter_ns()
                try:
                    # Run the export
                    out = osxphotos.PhotoExporter(p).export(
                        new_path, str_dt + "." + ext, options=fobj
                    )
                    self.file_count += len(out.exported)
                except:
                    # Unable to parse that file; log it to investigate later
                    with open("log.txt", "a") as f:
                        f.write(
                            f"Had trouble writing {original_filename} at {str(datetime.datetime.now())}\n"
                        )
                total_time += time.perf_counter_ns() - start_time

            # Update the window after each photo
            self.update_background(i, check_path.split("/")[-1])

        print(f"Total time: {total_time/10**9}")


if __name__ == "__main__":
    obj = Exporter()
    obj.dates("2022-10-20", "2030-12-22")
    obj.export()
    obj.root.destroy()
    obj.root.mainloop()

    with open("log.txt", "a") as f:
        f.write(f"{str(datetime.datetime.now())} {obj.file_count}   exports\n")


print(
    f"\n...Completed Export: {obj.file_count} file(s) exported - {len(obj.photos) - obj.file_count} skipped\n"
)
