#!/bin/bash

set -ex

LANG=en_US.utf-8

cd Ocami
pushd sourceFonts
# getfont archive ext source_url [alter]
function getfont() {
    local d="$1"
    local n="$d$2"
    if [ ! -r "$n" ]; then
        curl -L "$3" -o "$n";
    fi
    if [ -z "$4" ]; then
        rm -rf "$d"
        unar -q "$n"
    else
        rm -rf "$4"
        unar -q -o "$4" "$n"
    fi
}

getfont IBM_Plex-1.4.1 .zip \
        https://github.com/IBM/plex/releases/download/v1.4.1/TrueType.zip \
        IBM_Plex-1.4.1
getfont source-han-sans-2.001R .tar.gz \
        https://github.com/adobe-fonts/source-han-sans/archive/2.001R.tar.gz
getfont Fira-4.202 .tar.gz \
        https://github.com/mozilla/Fira/archive/4.202.tar.gz

for weight in Regular Italic Bold BoldItalic; do
    cp IBM_Plex-1.4.1/TrueType/IBM-Plex-Mono/IBMPlexMono-$weight.ttf .
done

for weight in Regular Bold; do
    cp source-han-sans-2.001R/OTF/Japanese/SourceHanSans-$weight.otf .
    cp source-han-sans-2.001R/SubsetOTF/JP/SourceHanSansJP-$weight.otf .
done
cp source-han-sans-2.001R/Resources/utf32-jp.map .

for weight in Regular Bold; do
    cp Fira-4.202/ttf/FiraMono-$weight.ttf .
done


popd

/opt/fontforge/bin/fontforge -lang=py -script ocami.py
