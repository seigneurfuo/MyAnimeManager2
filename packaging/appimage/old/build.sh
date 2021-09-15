#!/bin/bash

# Doc: https://appimage-builder.readthedocs.io/en/latest/examples/pyqt.html

# region ----- Config -----
app_dir="AppDir"
app_name="MyAnimeManager2"
app_source="../../."
# endregion

# Clearn folder
rm -rf $app_dir

# Create folders
mkdir "$app_dir"
mkdir -p "$app_dir/usr/src"

# Copying application source to "$appdir/usr/src"
git clone "$app_source" "$app_dir/usr/src/$app_name"

# Removing unessesary folders and files
rm -rf "$app_dir/usr/src/$app_name/dist"
rm -rf "$app_dir/usr/src/$app_name/Tools"

# Installating Python TODO: Requirements.txt
python3 -m pip install --ignore-installed --root=$app_dir --prefix=/usr -r "$app_source/requirements.txt"
