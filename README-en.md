[English](https://github.com/yamahigashi/SynopticGenerator/blob/master/README-en.md) / 
[Japanese](https://github.com/yamahigashi/SynopticGenerator/blob/master/README.md)


What is this?
======================

For DCC tool(
[Autodesk maya](http://www.autodesk.co.jp/products/autodesk-maya/overview)  or
[Autodesk Softimage](http://www.autodesk.co.jp/products/autodesk-softimage/overview)),
generate synoptic image and view. From some image file (background, model and controllers)
and config file, detect controller's contours, synthesize them. Currently worknig for softimage.

Each operation is separated for python module, you can easyly modify, add new features.

Dependencies
------------
At first
+ python

addition, prepare below modules by youself or you can download binaries from
[Unoffcial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/ )


### require ###
+ opencv
+ numpy
+ Pillow
+ six

### optional ###
Useful modules, you can check contours with this.
+ matplotlib(optional)
+ pyparsing(optional)
+ pytz(optional)

install
-------
After preparation of Python and some modules、you clone this SynopticGenerator repositry,
deploy `synopticgenerator` folder into `PYTHON_PATH` environment variable.
in `softimage_plugin` folder, you can see some plugin for softimage, that enable ViewPort Capture
at hand and logging useful info. `synopticgenerator/sample` you can found two samples using XSI-man.
in sample folder run `python make.py` you get xsi man's synoptic files.


How to use?
------
See sample for more informations.

## Preparation ##
from 

1. background image
2. model view image
3. controllers images

## Edit Configuration ##
See `sample/xsi_man/xsi_man.recipe` for more informations.


#### global block ####
You can set here configuration over modules,
for example, logging level and color table.

#### pipeline block ####
You descript here, each operations sequencially.

+ prepare: preparation for images
+ recognize: detect contours into region data
+ filter: filter regions data
+ publish: output synthesized image, view text file.
+ finalize: clean up

You can name pipeline's name as you want.

## Execution your script ##
Simply run this python code

    import synopticgenerator
    synopticgenerator.create("sample.recipe")


Plugin manual
----------------

### image ###
画像ファイルを操作するためのクラスです

+ `image.set_transparent_by_color`
+ `image.paste_with_transparent`

### recognizer ###
画像ファイルから領域データを抽出するためのクラスです

+ `recognizer.image_to_shapes`

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
