#!/bin/bash

# ----- Variables -----
EXTRACT_FOLDER="squashfs-root"

# ----- Sources -----
APPIMAGETOOL_APPIMAGE_URL="https://github.com/AppImage/AppImageKit/releases/download/13/"
APPIMAGETOOL_APPIMAGE_FILENAME="appimagetool-x86_64.AppImage"

PYTHON_APPIMAGE_URL="https://github.com/niess/python-appimage/releases/download/python3.10/"
PYTHON_APPIMAGE_FILENAME="python3.10.0-cp310-cp310-manylinux2014_x86_64.AppImage"



if [ ! -f "$APPIMAGETOOL_APPIMAGE_FILENAME" ]
then
    wget "${APPIMAGETOOL_APPIMAGE_URL}/${APPIMAGETOOL_APPIMAGE_FILENAME}"
    chmod +x ${APPIMAGETOOL_APPIMAGE_FILENAME}
fi

if [ ! -f "$PYTHON_APPIMAGE_FILENAME" ]
then
    wget "${PYTHON_APPIMAGE_URL}/${PYTHON_APPIMAGE_FILENAME}"
    chmod +x ${PYTHON_APPIMAGE_FILENAME}
fi



# Supression du dossier temporaire
if [ -d "$EXTRACT_FOLDER" ]; then
    rm -rf $EXTRACT_FOLDER
fi



# Extraction des fichiers
./${PYTHON_APPIMAGE_FILENAME} --appimage-extract



# On copie afin de corriger un bug
cp -v "${EXTRACT_FOLDER}/usr/share/applications/python3.10.0.desktop" "${EXTRACT_FOLDER}/usr/share/applications/python.desktop"



# Copie des dossiers du programme
mkdir "${EXTRACT_FOLDER}/opt/MyAnimeManager2"
cp -v "../../MyAnimeManager2.py" "${EXTRACT_FOLDER}/opt/MyAnimeManager2"
cp -rv "../../ressources" "${EXTRACT_FOLDER}/opt/MyAnimeManager2"
cp -v "../archlinux/myanimemanager2.desktop" "${EXTRACT_FOLDER}/usr/share/applications/"



# Copie des fichiers spéciaux
cp -fv "AppRun" "${EXTRACT_FOLDER}/AppRun"

rm "${EXTRACT_FOLDER}/usr/share/metainfo/python3.10.0.appdata.xml"
cp -fv "myanimemanager2.appdata.xml" "${EXTRACT_FOLDER}/usr/share/metainfo/"

rm "${EXTRACT_FOLDER}/python3.10.0.desktop"
ln -s "usr/share/applications/myanimemanager2.desktop" "${EXTRACT_FOLDER}/myanimemanager2.desktop"



# On se déplace dans le dossiers
export PATH="$(pwd)/${EXTRACT_FOLDER}/usr/bin:$PATH"



# On installe pip + les bibliothèques
pip install --upgrade pip
pip install -r ../../requirements.txt



# Build Appimage
ARCH=x86_64 "./${APPIMAGETOOL_APPIMAGE_FILENAME}" "./${EXTRACT_FOLDER}"
