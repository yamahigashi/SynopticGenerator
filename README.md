[English](https://github.com/yamahigashi/SynopticGenerator/blob/master/README-en.md) / 
[Japanese](https://github.com/yamahigashi/SynopticGenerator/blob/master/README.md)


����͉��H
======================

DCC�c�[��(
[Autodesk Maya](http://www.autodesk.co.jp/products/autodesk-maya/overview) �� 
[Autodesk Softimage](http://www.autodesk.co.jp/products/autodesk-softimage/overview))�p
�ɃV�m�v�e�B�b�N�r���[���쐬����X�N���v�g�ł��B  
�����̉摜�t�@�C���i���n�A���f���A�R���g���[���j�Ɛݒ�t�@�C������R���g���[���̈��
���o���V�m�v�e�B�b�N�i�C���[�W�t�@�C���A��`�t�@�C���j�Ɏd���ďグ�܂��B���݂�
Softimage �p�̏����o���ɑΉ����Ă��܂��B

�e�푀��� python module �Ƃ��ēƗ����Ď������Ă���̂ŁA�@�\�̉��ς�ǉ��A����ւ���
�e�Ղɍs�����Ƃ��ł��܂��B


Dependencies
------------
�܂�
+ python

���K�v�ł��B����Ɉȉ������O�ŗp�ӂ��邩
[Unoffcial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/ )
�Ȃǂ���C���X�g�[�����Ă�������

### �K�{ ###
+ opencv
+ numpy
+ Pillow
+ six

### �C�� ###
�ȉ��͕K�{�ł͂Ȃ��ł�������ƕ֗��ł��B�F�������֊s���̊m�F�ȂǂɎg�p�ł��܂��B
+ matplotlib(optional)
+ pyparsing(optional)
+ pytz(optional)

����
----
��L Python �y�у��W���[���Q���C���X�g�[����ASynopticGenerator �����[�J����
�N���[�����A`synopticgenerator` �t�H���_�� `PYTHON_PATH` �̒ʂ����ꏊ�ɔz�u����Ώ��������ł��B
`softimage_plugin` �H���_�ɂ͉������ɕK�v�ȑf�ނ�p�ӂ���ہA�r���[�|�[�g�L���v�`����
�B�e�����O�ɕK�v�ȏ��𗬂��v���O�C���������Ă��܂��B `synopticgenerator/sample` �ȉ��ɂ�
xsi man ���g�p���ẴT���v���t�@�C��������܂��B`python make.py` �����s����� xsi man �p��
�V�m�v�e�B�b�N�t�@�C������������܂��B


�g����
------
����̓I�Ȑ����̓T���v���̉�����Q�Ƃ��Ă��������B

## �摜�̏��� ##
�܂���DCC�c�[���Ȃǂ���摜��p�ӂ��܂��傤�B

1. ���n�摜��p�ӂ��܂�
2. ���f���摜��p�ӂ��܂��i�C�Ӂj
3. �R���g���[���摜��p�ӂ��܂�

## �ݒ�t�@�C���̕ҏW ##
�L�q��� sample.recipe ���Q�Ƃ��Ă��������B

#### global �u���b�N ####
�e�푀��v���O�C�������f���A�Q�Ƃ��邽�߂̐ݒ���L�q���܂��B  
���O�̐ݒ��F���ƐF���l�̑Ή��\��`�Ȃǂ��ł��܂�

#### pipeline �u���b�N ####
��̓I�ȏ������e���A�������ɋL�q���Ă�������

+ prepare: �摜�̉��H�A����
+ recognize: �摜����̗̈撊�o
+ filter: �̈�f�[�^�̉��H
+ publish: �̈�f�[�^����̍ŏI�摜�`��A��`�t�@�C���o��
+ finalize: ���ԃf�[�^�폜�Ȃǂ̑|������

����A�̗���Ƃ��ċL�q���܂��Bpipeline ���͔C�ӂł�

## �쐬�X�N���v�g���s ##
�ȉ��� python �R�[�h�����s

    import synopticgenerator
    synopticgenerator.create("sample.recipe")


�v���O�C�����
----------------

### image ###
�摜�t�@�C���𑀍삷�邽�߂̃N���X�ł�

+ `image.set_transparent_by_color`
+ `image.paste_with_transparent`

### recognizer ###
�摜�t�@�C������̈�f�[�^�𒊏o���邽�߂̃N���X�ł�

+ `recognizer.image_to_regions`

### filter ###
�̈�f�[�^�𑀍삷�邽�߂̃N���X�ł�

+ `filter.uniq_region`
+ `filter.set_color_region`
+ `filter.naming_region_by_position`
+ `filter.copy_region`
+ `filter.concatenate_region`

### drawer ###
�̈�f�[�^����摜��`�悷�邽�߂̃N���X�ł�

+ `drawer.draw_by_its_type`
+ `drawer.rectangle`
+ `drawer.polygon`
+ `drawer.circle`

### writer ###
�̈�f�[�^�����`�t�@�C�����o�͂��邽�߂̃N���X�ł�

+ `writer.SoftimageHTML`

### utility ###
�֗��p�ł�

+ `utility.remove_file`
+ `utility.html_character`
+ `utility.dump_region`

Enjoy!!

���C�Z���X
----------
Copyright &copy; 2014 yamahigashi
Distributed under the [MIT License][mit].  

[MIT]: http://www.opensource.org/licenses/mit-license.php
