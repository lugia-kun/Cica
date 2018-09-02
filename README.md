(工事中)

# プログラミング用日本語等幅フォント [TBD]

## ダウンロード

## 特徴

* 以下のフォントを合成後に調整した、プログラミング向けの等幅日本語フォントです
<!-- * 各種エディタで迷わずに設定できるフォント名にしました(ex. `Hoge Font`, `Hoge_Font` or `Hoge Font Regular`  ??? ARGGGG!!! )-->
<!-- * tmuxの画面分割に対応しています -->
<!-- * 非HiDPI（非Retina）のWindowsでも文字が欠けません -->
* Ambiguous Width の設定を Narrow で使うことを前提としています

フォントの大部分を占める「源ノ角ゴシック」が SIL OPEN FONT LICENSE 1.1 でライセンスされているため、SIL OPEN FONT LICENSE 1.1 以外でライセンスされたのフォントからのグリフは使用しないようにしています。

## バリエーション

| ファイル名              | 説明     |
| ----                    | ----     |
| [TBD]-Regular.ttf       | 通常     |
| [TBD]-RegularItalic.ttf | 斜体     |
| [TBD]-Bold.ttf          | 太字     |
| [TBD]-BoldItalic.ttf    | 太字斜体 |


## ビルド手順

2018-07-01時点、Ubuntu 16.04 にて

```sh
sudo apt-get update
sudo apt-get -y install apt-file
sudo apt-file update
sudo apt-file search add-apt-repository
sudo apt-get -y install software-properties-common
sudo apt-get -y install fontforge unar
git clone git@github.com:miiton/Cica.git
wget -O ubuntu-font-family-0.83.zip https://assets.ubuntu.com/v1/fad7939b-ubuntu-font-family-0.83.zip
unar ubuntu-font-family-0.83.zip
cp ubuntu-font-family-0.83/UbuntuMono-R.ttf ./sourceFonts/
cp ubuntu-font-family-0.83/UbuntuMono-B.ttf ./sourceFonts/
wget https://osdn.jp/downloads/users/8/8598/rounded-mgenplus-20150602.7z
unar rounded-mgenplus-20150602.7z
cp rounded-mgenplus-20150602/rounded-mgenplus-1m-regular.ttf ./sourceFonts
cp rounded-mgenplus-20150602/rounded-mgenplus-1m-bold.ttf ./sourceFonts
wget https://github.com/googlei18n/noto-emoji/raw/master/fonts/NotoEmoji-Regular.ttf -O sourceFonts/NotoEmoji-Regular.ttf
curl -LO http://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.zip
unar dejavu-fonts-ttf-2.37.zip
mv dejavu-fonts-ttf-2.37/ttf/DejaVuSansMono.ttf ./sourceFonts/
mv dejavu-fonts-ttf-2.37/ttf/DejaVuSansMono-Bold.ttf ./sourceFonts/
fontforge -lang=py -script cica.py
```

[fontforge のバージョンが古いと正常に動作しません #6](https://github.com/miiton/Cica/issues/6)

```
% fontforge --version

Copyright (c) 2000-2012 by George Williams.
 Executable based on sources from 14:57 GMT 31-Jul-2012-ML.
 Library based on sources from 14:57 GMT 31-Jul-2012.
fontforge 20120731
libfontforge 20120731-ML
```

# ライセンス

* 生成スクリプトは MIT License の元で使用許諾されます。
  - See [LICENSE.script.txt](LICENSE.script.txt)

* 生成スクリプトを用いて生成されたフォントは、SIL OPEN FONT LICENSE 1.1 の元で使用許諾されます。
  - See [LICENSE.font.txt](LICENSE.font.txt)

* 以下のグリフは自作です。これらのグリフのソース形態（つまり、SVG ファイル）は、CC0 1.0 Universal で提供（著作権を放棄）します。[src/COPYING](src/COPYING)

  - (まだない)

# 謝辞

[TBD] フォントの合成にあたり素晴らしいフォントを提供してくださっている製作者の方々に感謝いたします。

- 源の角ゴシック : [adobe\-fonts/source\-han\-sans: Source Han Sans \| 思源黑体 \| 思源黑體 \| 源ノ角ゴシック \| 본고딕](https://github.com/adobe-fonts/source-han-sans)
