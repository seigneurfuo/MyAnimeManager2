#!/bin/bash

pkgname="myanimemanager2"
pkgver="2022.02.14-amd64"

cd debian

# Cration des dossiers
mkdir pkgdir
mkdir -p pkgdir/usr/share/applications/
mkdir -p pkgdir/opt/MyAnimeManager2/
mkdir output/

# Copie des fichiers depuis la source
cp ../../MyAnimeManager2.py pkgdir/opt/MyAnimeManager2/
cp -r ../../ressources pkgdir/opt/MyAnimeManager2/

# Copie des fichiers locaux
cp myanimemanager2.desktop pkgdir/usr/share/applications/

# Copie des fichiers du paquet
cp -r DEBIAN pkgdir/

# Supression des fichiers inutiles
rm -rf pkgdir/opt/MyAnimeManager2/ressources/__pycache__

# Creation du paquet
dpkg-deb --build --root-owner-group pkgdir "${pkgname}-${pkgver}.deb"

read _

# Nettoyage
rm -rf pkgdir/
