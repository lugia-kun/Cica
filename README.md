# プログラミング用日本語等幅フォント Ocami

## ダウンロード

## 特徴

* 以下のフォントを合成後に調整した、プログラミング向けの等幅日本語フォントです
  * 英数字・記号類に IBM Plex Mono
  * ギリシャ文字・キリル文字に Fira Mono
  * それ以外の文字に Source Han Sans (源ノ角ゴシック)
* Ambiguous Width の設定を Narrow で使うことを想定しています
  * Ambigious Width の設定は、Wide にできないこともあること、[OS標準のままだと必要なデータが無いことが多く](https://github.com/hamano/locale-eaw)、リモート等での使用に向かないため。

## バリエーション

| ファイル名           | 説明     |
| ----                 | ----     |
| Ocami-Regular.ttf    | 通常     |
| Ocami-Italic.ttf     | 斜体     |
| Ocami-Bold.ttf       | 太字     |
| Ocami-BoldItalic.ttf | 太字斜体 |


## ビルド手順

ビルドには、最新の fontforge が必要（手元では [e688b8c](https://github.com/fontforge/fontforge/commit/e688b8c4dc634dcc128709f84b98f2407294f3fb) を使用）で、かつ[パッチ](https://github.com/fontforge/fontforge/issues/3300)を当てる必要があります。

# ライセンス

* 生成スクリプトは MIT License の元で使用許諾されます。
  - See [LICENSE.script.txt](LICENSE.script.txt)

* 生成スクリプトを用いて生成されたフォントは、SIL OPEN FONT LICENSE 1.1 の元で使用許諾されます。
  - See [LICENSE.font.txt](LICENSE.font.txt)
  - このファイルにはソースフォントの著作権表示は含まないため、実際のフォントの著作権表示とは異なります。

* [src](src/) ディレクトリ以下のグリフは自作です。これらのグリフのソース形態（つまり、SVG ファイル）は、CC0 1.0 Universal で提供（著作権を放棄）します。フォントにかかわらずご自由にお使いいただけます。
  - See [src/COPYING](src/COPYING)

# TODO

* ~~tmuxの画面分割~~
* 非HiDPI（非Retina）のWindows (作者はなぜ確認が必要なのかわかっていません)
* Powerline シンボルの作成
  * OFL でバンドル出来るライセンスになっていないため。
* 罫線文字の修正
* 記号の半角化
  * macOS の Homebrew が使う絵文字のように、フォントが全角幅でデザインされていながらカーソルが半角分しか進まないことをすでに想定していると考えられるものは全角のままとします（が、端末によっては表示が切れたりします）。
  * Emacs (GTK) などのようにフォントの幅をそのまま使われるときに、全角のほうが都合が良い文字も全角のままにする・・・と思います。
  * 数学記号は全角である意味が無いので、半角化すると思います。

# 謝辞

Ocami フォントの合成にあたり素晴らしいフォントを提供してくださっている製作者の方々に感謝いたします。

- 源ノ角ゴシック : [adobe\-fonts/source\-han\-sans: Source Han Sans \| 思源黑体 \| 思源黑體 \| 源ノ角ゴシック \| 본고딕](https://github.com/adobe-fonts/source-han-sans)
- IBM Plex Mono : [Introduction \| IBM Plex](https://www.ibm.com/plex/)
- Fira Mono : [Fira Sans](https://mozilla.github.io/Fira/)

