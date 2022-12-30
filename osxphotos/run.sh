#!/bin/bash

mkdir env
python3 -m venv env
source .env/bin/activate
python3 -m pip install osxphotos
python3 -m pip install tqdm
clear
cp osxphotos/exporter.py osxphotos/env/exporter.py
python3 osxphotos/env/exporter.py
rm osxphotos/env/exporter.py
exit