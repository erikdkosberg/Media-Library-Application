#! /usr/bin/env python3

import os
import datetime
import osxphotos
from osxphotos import ExportOptions
from tqdm import tqdm # progress bar
import tkinter as tk
from tkinter import ttk
import multiprocessing


class Exporter:
    def __init__(self):
        self.processes = []
        self.file_count = 0
        self.export_path = "Local.nosync"
        self.photosdb = osxphotos.PhotosDB()
        self.photos = self.photosdb.photos()
        self.albums = self.photosdb.albums

        print("#-------------------------------Python Exporting Tool-------------------------------#")
        print()
        print("Beginning Export...")
        print()
   
    def parse_dt(self, dt):
        year = int(dt.split("-")[0])
        month = int(dt.split("-")[1])
        day = int(dt.split("-")[2])

        return datetime.datetime(year, month, day)

    def dates(self, fd, td):
        self.photos = self.photosdb.photos(from_date=self.parse_dt(fd), to_date=self.parse_dt(td))

    def background_window(self, n):
        # Create the root window
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("400x200") # size of window

        # Create a label widget
        self.upper_label = tk.Label(self.root, text="Running Collection...\n\n")
        self.upper_label.pack()

        # Create a progress bar widget
        self.progress = ttk.Progressbar(self.root, length=350, mode="determinate", orient='horizontal')
        self.progress['value'] = 0
        self.progress.pack()

        # Create a label widget
        self.lower_label = tk.Label(self.root, text="Progress\n\n")
        self.lower_label.pack()

    def update_background(self, i, label):
        self.progress['value'] = (i+1)/len(self.photos)*100
        self.lower_label['text'] = (f"   {round((i+1)/len(self.photos)*100, 2)}" + "%")
        self.progress.update()
        self.root.update()   

    def export_photo(self, photo, dir_name, file_name, options):
        return osxphotos.PhotoExporter(photo).export(dir_name, file_name, options)

    def build_process(self):
        original_filename = p.original_filename

        ext = original_filename.split(".")[-1].upper()

        file_type = "Videos" if ext in ["MOV", "MP4"] else "Photos"

        dt = p.date
        str_dt = str(dt).replace(" ", "").replace("-", "").replace(":", "").replace("-", "").replace(".", "")[:14]
        
        year = str(dt.year)
        
        new_path = self.export_path + "/" + file_type + "/" + year

        if not os.path.exists(new_path):
            os.makedirs(new_path)

        if ext == "JPG":
            ext = "jpeg"

        self.check_path = new_path + "/" + str_dt + "." + ext
        check_dir = os.listdir(new_path)

        check1 = self.check_path.split("/")[-1].split(".")[0]
        check2 = [z.split("/")[-1].split(".")[0] for z in check_dir]

        if check1 not in check2:
            fobj = ExportOptions()
            fobj.download_missing = True
            fobj.use_photos_export = True
            fobj.overwrite = True
            #fobj.exiftool = True

            if ext == "PNG" or ext == "HEIC":
                fobj.convert_to_jpeg = True

            #fobj.sidecar = True
            self.export_photo(p, new_path, str_dt + "." + ext, options=fobj)

            #self.file_count += len(out.exported)

def export(object):
    object.background_window(len(object.photos))

    for i, p in enumerate(tqdm(object.photos)):
        proc = multiprocessing.Process(target=object.build_process, args=())
        object.processes.append(proc)
        proc.start()

        object.update_background(i, object.check_path.split("/")[-1])

    for p in object.processes:
        p.join()


if __name__ == "__main__":
    obj = Exporter()
    obj.dates("2022-12-20", "2030-12-31")
    export(obj)
    obj.root.destroy()
    obj.root.mainloop()

    with open("log.txt", "a") as f:
        f.write(f"{str(datetime.datetime.now())} {obj.file_count} exports\n")

print()
print(f"\n...Completed Export: {obj.file_count} file(s) exported - {len(obj.photos) - obj.file_count} skipped\n")
