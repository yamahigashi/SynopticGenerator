﻿[English](https://github.com/yamahigashi/SynopticGenerator/blob/master/README-en.md) / 
[Japanese](https://github.com/yamahigashi/SynopticGenerator/blob/master/README.md)


これは何？
======================

DCCツール(
[Autodesk Maya](http://www.autodesk.co.jp/products/autodesk-maya/overview) や 
[Autodesk Softimage](http://www.autodesk.co.jp/products/autodesk-softimage/overview))用
にシノプティックビューを作成するスクリプトです。  
複数の画像ファイル（下地、モデル、コントローラ）と設定ファイルからコントローラ領域を
抽出しシノプティック（イメージファイル、定義ファイル）に仕立て上げます。現在は
Softimage 用の書き出しに対応しています。

各種操作は python module として独立して実装しているので、機能の改変や追加、入れ替えを
容易に行うことができます。


Dependencies
------------
まず
+ python

が必要です。さらに以下を自前で用意するか
[Unoffcial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/ )
などからインストールしてください

### 必須 ###
+ opencv
+ numpy
+ Pillow
+ six
+ enum34
+ PyYAML

### 任意 ###
以下は必須ではないですがあると便利です。認識した輪郭線の確認などに使用できます。
+ matplotlib(optional)
+ pyparsing(optional)
+ pytz(optional)

導入
----
上記 Python 及びモジュール群をインストール後、SynopticGenerator をローカルに
クローンし、`synopticgenerator` フォルダを `PYTHON_PATH` の通った場所に配置すれば準備完了です。
`softimage_plugin` ォルダには下準備に必要な素材を用意する際、ビューポートキャプチャを
撮影＆ログに必要な情報を流すプラグインが入っています。 `synopticgenerator/sample` 以下には
xsi man を使用してのサンプルファイルがあります。`python make.py` を実行すると xsi man 用の
シノプティックファイルが生成されます。


使い方
------
より具体的な説明はサンプルの解説を参照してください。

## 画像の準備 ##
まずはDCCツールなどから画像を用意しましょう。

1. 下地画像を用意します
2. モデル画像を用意します（任意）
3. コントローラ画像を用意します

## 設定ファイルの編集 ##
記述例は sample.recipe を参照してください。

#### global ブロック ####
各種操作プラグインを横断し、参照するための設定を記述します。  
ログの設定や色名と色数値の対応表定義などができます

#### pipeline ブロック ####
具体的な処理内容を、処理順に記述してください

+ prepare: 画像の加工、準備
+ recognize: 画像からの領域抽出
+ filter: 領域データの加工
+ publish: 領域データからの最終画像描画、定義ファイル出力
+ finalize: 中間データ削除などの掃除処理

を一連の流れとして記述します。pipeline 名は任意です

## 作成スクリプト実行 ##
以下の python コードを実行

    import synopticgenerator
    synopticgenerator.create("sample.recipe")


プラグイン解説
----------------

### image ###
画像ファイルを操作するためのクラスです

+ `image.set_transparent_by_color`
+ `image.paste_with_transparent`

### recognizer ###
画像ファイルから領域データを抽出するためのクラスです

+ `recognizer.image_to_regions`

### filter ###
領域データを操作するためのクラスです

+ `filter.uniq_region`
+ `filter.set_color_region`
+ `filter.naming_region_by_position`
+ `filter.copy_region`
+ `filter.concatenate_region`

### drawer ###
領域データから画像を描画するためのクラスです

+ `drawer.draw_by_its_type`
+ `drawer.rectangle`
+ `drawer.polygon`
+ `drawer.circle`

### writer ###
領域データから定義ファイルを出力するためのクラスです

+ `writer.SoftimageHTML`

### utility ###
便利用です

+ `utility.remove_file`
+ `utility.html_character`
+ `utility.dump_region`

Enjoy!!

ライセンス
----------
Copyright &copy; 2014 yamahigashi
Distributed under the [MIT License][mit].  

[MIT]: http://www.opensource.org/licenses/mit-license.php
