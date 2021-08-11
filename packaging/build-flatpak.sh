#!/bin/bash
cd "flatpak"
flatpak-builder --user --install build com.seigneurfuo.myanimemanager2.yml --force-clean

# flatpak run com.seigneurfuo.myanimemanager2