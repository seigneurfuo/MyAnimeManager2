#!/bin/bash
cd archlinux
makepkg --cleanbuild --syncdeps --rmdeps --force --clean
rm -rf "MyAnimeManager 2"
rm -rf "src"
read _