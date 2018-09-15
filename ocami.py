#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fontforge
import psMat
import os
import re
import sys
import math
import glob
from xml.dom import minidom
from logging import getLogger, StreamHandler, Formatter, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
formatter = Formatter('%(asctime)s [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(handler)

# ASCENT = 850
# DESCENT = 174
ASCENT = 1638
DESCENT = 410
#ASCENT = 819
#DESCENT = 205
SOURCE = './sourceFonts'
LICENSE = open('./LICENSE.font.txt').read()
LICENSE_URL = "http://scripts.sil.org/OFL"
COPYRIGHT = open('./COPYRIGHT.txt').read()
VERSION = '0.0.1'
FAMILY = 'Ocami'
ITALIC_ANGLE = -9
ITALIC_SKEW = psMat.skew(-ITALIC_ANGLE / 180.0 * math.pi)
ITALIC_SHIFT = math.tan(-ITALIC_ANGLE / 180.0 * math.pi) * 0.5

source_info = {
    "IBMPlexMono": {
        "base": "IBMPlexMono-",
        "weights": [
            "Thin",
            "ExtraLight",
            "Light",
            "Regular",
            "Text",
            "Medium",
            "SemiBold",
            "Bold",
        ],
        "have_italic": {
            "Thin": "ThinItalic",
            "ExtraLight": "ExtraLightItalic",
            "Light": "LightItalic",
            "Regular": "Italic",
            "Text": "TextItalic",
            "Medium": "MediumItalic",
            "SemiBold": "SemiBoldItalic",
            "Bold": "BoldItalic",
        },
        "format": ".ttf", # IBM also distributes OTF.
    },
    "AnonymousPro": {
        "base": "AnonymousPro-",
        "weights": [
            "Regular",
            "Bold",
        ],
        "have_italic": {
            "Regular": "Italic",
            "Bold": "BoldItalic",
        },
        "format": ".ttf",
    },
    "FiraMono": {
        "base": "FiraMono-",
        "weights": [
            "Regular",
            "Medium",
            "Bold",
        ],
        "have_italic": False,
        "format": ".ttf",
    },
    "SourceHanSans": {
        "base": "SourceHanSans-",
        "weights": [
            "ExtraLight",
            "Light",
            "Normal",
            "Regular",
            "Medium",
            "Bold",
            "Heavy",
        ],
        "have_italic": False,
        "format": ".otf",
    },
}

def font_fn(family, weight, italic):
    hsh = source_info[family]
    if not weight in hsh["weights"]:
        raise KeyError("Weight '%s' does not defined for %s" %
                       (weight, family))
    wn = weight
    if italic:
        if hsh["have_italic"]:
            wn = hsh["have_italic"][weight]
        else:
            raise KeyError("Italic for weight %s does not defined for %s" %
                           (weight, family))
    return hsh["base"] + wn + hsh["format"]

fonts = [
    {
        'family': FAMILY,
        'name': FAMILY + '-Regular',
        'filename': FAMILY + '-Regular.ttf',
        'weight': 400,
        'weight_name': 'Regular',
        'style_name': 'Regular',
        'src_fonts': {
            'ibm_plex': 'IBMPlexMono-Regular.ttf',
            'fira_mono': 'FiraMono-Regular.ttf',
            'source_han_sans': 'SourceHanSans-Regular.otf',
            'source_han_sans_subset': 'SourceHanSansJP-Regular.otf',
        },
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-Italic',
        'filename': FAMILY + '-Italic.ttf',
        'weight': 400,
        'weight_name': 'Regular',
        'style_name': 'Italic',
        'src_fonts': {
            'ibm_plex': 'IBMPlexMono-Italic.ttf',
            'fira_mono': 'FiraMono-Regular.ttf',
            'source_han_sans': 'SourceHanSans-Regular.otf',
            'source_han_sans_subset': 'SourceHanSansJP-Regular.otf',
        },
        'italic': True,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-Bold',
        'filename': FAMILY + '-Bold.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold',
        'src_fonts': {
            'ibm_plex': 'IBMPlexMono-Bold.ttf',
            'fira_mono': 'FiraMono-Bold.ttf',
            'source_han_sans': 'SourceHanSans-Bold.otf',
            'source_han_sans_subset': 'SourceHanSansJP-Bold.otf',
        },
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-BoldItalic',
        'filename': FAMILY + '-BoldItalic.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold Italic',
        'src_fonts': {
            'ibm_plex': 'IBMPlexMono-BoldItalic.ttf',
            'fira_mono': 'FiraMono-Bold.ttf',
            'source_han_sans': 'SourceHanSans-Bold.otf',
            'source_han_sans_subset': 'SourceHanSansJP-Bold.otf',
        },
        'italic': True,
    }
]

def log(str):
    logger.debug(str)

def set_os2_values(_font, _info):
    weight = _info.get('weight')
    style_name = _info.get('style_name')
    _font.os2_family_class = 2057
    _font.os2_weight = weight
    _font.os2_width = 5
    _font.os2_fstype = 0
    _font.os2_use_typo_metrics = 0
    if style_name == 'Regular':
        _font.os2_stylemap = 64
    elif style_name == 'Bold':
        _font.os2_stylemap = 32
    elif style_name == 'Italic':
        _font.os2_stylemap = 1
    elif style_name == 'Bold Italic':
        _font.os2_stylemap = 33
    _font.os2_vendor = 'misc'
    _font.os2_version = 1
    _font.os2_winascent = ASCENT
    _font.os2_winascent_add = False
    _font.os2_windescent = DESCENT
    _font.os2_windescent_add = False

    _font.os2_typoascent = -300
    _font.os2_typoascent_add = True
    _font.os2_typodescent = 200
    _font.os2_typodescent_add = True
    _font.os2_typolinegap = 0

    _font.hhea_ascent = ASCENT
    _font.hhea_ascent_add = False
    _font.hhea_descent = DESCENT
    _font.hhea_descent_add = False

    _font.hhea_linegap = 0
    _font.os2_panose = (2, 11, int(weight / 100), 9, 2, 2, 3, 2, 2, 7)
    return _font

def add_source_han_sans(target, source, italic):
    log("Reading %s..." % source["path"])
    srcfont = fontforge.open(source["path"])
    srcfont.cidFlatten()

    em = srcfont.em
    scale = float(DESCENT + ASCENT) / em

    srcfont.selection.all()
    if scale != 1.0:
        log("%s: Scaling %g%%..." % (srcfont.fontname, scale * 100.0))
        srcfont.transform(psMat.scale(scale,scale))

    #move = (srcfont.ascent - ASCENT) / scale
    #if move != 0.0:
    #    log("%s: Moving by %g..." % (srcfont.fontname, move))
    #    srcfont.transform(psMat.translate(0.0,move))

    scale = 0.85
    log("%s: Scaling %g%%..." % (srcfont.fontname, scale * 100.0))
    srcfont.transform(psMat.scale(scale,scale))

    log("%s: Adjusting width..." % (srcfont.fontname))
    for g in srcfont.glyphs():
        old_w = g.width
        if old_w > 0:
            if old_w < 1536:
                new_w = 1024
            else:
                new_w = 2048

            g.transform(psMat.translate(new_w / 2.0 - old_w / 2.0,0.0))
            g.width = new_w

    if italic:
        log("%s: Skewing %d degrees..." % (srcfont.fontname, ITALIC_ANGLE))
        move = ITALIC_SHIFT

        for g in srcfont.glyphs():
            old_w = g.width
            if old_w > 0:
                if old_w < 1536:
                    new_w = 1024
                else:
                    new_w = 2048

            g.transform(ITALIC_SKEW)
            g.transform(psMat.translate(-ITALIC_SHIFT,0.0))

            if old_w > 0:
                g.width = new_w

    srcfont.ascent = ASCENT
    srcfont.descent = DESCENT

    warned_list = [
        0x04e0d, 0x04e32, 0x04e39, 0x04e82, 0x04e86, 0x04eae, 0x04ec0,
        0x04ee4, 0x04f86, 0x04f8b, 0x04fbf, 0x0502b, 0x050da, 0x05169,
        0x0516d, 0x051b7, 0x051c9, 0x051cc, 0x051dc, 0x05207, 0x05217,
        0x05229, 0x0523a, 0x05289, 0x0529b, 0x052a3, 0x052d2, 0x052de,
        0x052f5, 0x05317, 0x0533f, 0x05375, 0x053c3, 0x053e5, 0x0540f,
        0x0541d, 0x05442, 0x054bd, 0x05587, 0x056f9, 0x0585e, 0x058d8,
        0x058df, 0x05948, 0x05973, 0x05b85, 0x05bee, 0x05c3f, 0x05c62,
        0x05c65, 0x05d19, 0x05d50, 0x05dba, 0x05e74, 0x05ea6, 0x05ed3,
        0x05eec, 0x05f04, 0x05f8b, 0x05fa9, 0x05ff5, 0x06012, 0x0601c,
        0x060e1, 0x06144, 0x06190, 0x061f6, 0x06200, 0x0622e, 0x062c9,
        0x062cf, 0x062d3, 0x062fe, 0x0637b, 0x063a0, 0x0649a, 0x064c4,
        0x06578, 0x06599, 0x06613, 0x06688, 0x066b4, 0x066c6, 0x066f4,
        0x0674e, 0x0677b, 0x06797, 0x067f3, 0x06817, 0x06881, 0x068a8,
        0x06a02, 0x06a13, 0x06ad3, 0x06adb, 0x06af8, 0x06b77, 0x06bae,
        0x06c88, 0x06ccc, 0x06ce5, 0x06d1b, 0x06d1e, 0x06d41, 0x06d6a,
        0x06dcb, 0x06dda, 0x06dea, 0x06e9c, 0x06ed1, 0x06f0f, 0x06f23,
        0x06feb, 0x06ffe, 0x07099, 0x070c8, 0x070d9, 0x07149, 0x071ce,
        0x071d0, 0x07210, 0x0721b, 0x07262, 0x072c0, 0x072fc, 0x07375,
        0x07387, 0x073b2, 0x073de, 0x07406, 0x07409, 0x07469, 0x07489,
        0x07498, 0x07559, 0x07565, 0x07570, 0x075e2, 0x07642, 0x07669,
        0x076e7, 0x07701, 0x0786b, 0x0788c, 0x078ca, 0x078fb, 0x0792a,
        0x0797f, 0x079ae, 0x079ca, 0x07a1c, 0x07acb, 0x07b20, 0x07c60,
        0x07c92, 0x07ce7, 0x07d10, 0x07d22, 0x07d2f, 0x07da0, 0x07dbe,
        0x07e37, 0x07f79, 0x07f85, 0x07f9a, 0x08001, 0x08046, 0x0806f,
        0x0807e, 0x0808b, 0x081d8, 0x081e8, 0x0826f, 0x082e5, 0x08336,
        0x083c9, 0x083f1, 0x0843d, 0x08449, 0x084fc, 0x085cd, 0x085fa,
        0x08606, 0x0863f, 0x087ba, 0x0881f, 0x0884c, 0x088c2, 0x088cf,
        0x088e1, 0x088f8, 0x08964, 0x0898b, 0x08aaa, 0x08ad2, 0x08ad6,
        0x08afe, 0x08b58, 0x08c48, 0x08cc2, 0x08cc8, 0x08def, 0x08eca,
        0x08f26, 0x08f2a, 0x08f3b, 0x08f62, 0x08fb0, 0x0908f, 0x090ce,
        0x090de, 0x0916a, 0x091b4, 0x091cc, 0x091cf, 0x091d1, 0x09234,
        0x09304, 0x0934a, 0x095ad, 0x0962e, 0x0964b, 0x09675, 0x09678,
        0x096b7, 0x096b8, 0x096e2, 0x096f6, 0x096f7, 0x09732, 0x09748,
        0x09818, 0x099f1, 0x09a6a, 0x09b6f, 0x09c57, 0x09dfa, 0x09e1e,
        0x09e7f, 0x09ece, 0x09f8d, 0x20984, 0x233cc, 0x29fce, 0x051a4,
        0x05be7, 0x05c60, 0x06753, 0x06eba, 0x07c3e,
    ]

    log("%s: Fixup codings..." % (srcfont.fontname))
    copytab = {}
    copyrev = {}

    #  "src": Source character in internal encoding of SouceHanSans.
    # "dest": Destination character in Unicode, or glyph name.
    # "copy": If True, copy the charctor (leave original).
    #         If False, move the charactor (delete original).
    #  "dup": Unicode charactor mapped by FontForge (informational)
    mis_encodes = [
        {"src":  1676, "dest": 0x3127, "copy": False, "dup":   None},
        {"src": 65353, "dest": "Identity.65353", "copy": False, "dup": 0x3127},

        {"src":  2877, "dest":  0x3588, "copy": True, "dup":  0x439b}, # 㖈
        {"src":  3084, "dest":  0x363d, "copy": True, "dup":  0x39b3}, # 㘽
        {"src": 11367, "dest":  0x51a4, "copy": True, "dup": 0x2f818}, # 冤
        {"src": 13071, "dest":  0x55c0, "copy": True, "dup":  0xfa0d}, # 嗀
        {"src": 16300, "dest":  0x5c60, "copy": True, "dup": 0x2f877}, # 屠
        {"src": 21218, "dest":  0x6753, "copy": True, "dup": 0x2f8dc}, # 杓
        {"src": 22784, "dest":  0x6adb, "copy": True, "dup": 0x2f8ed}, # 櫛
        {"src": 22838, "dest":  0x6af8, "copy": True, "dup":    None}, # 櫸
        {"src": 43439, "dest":  0x96b8, "copy": True, "dup":  0xf9b8}, # 隸
        {"src": 60176, "dest": 0x233cc, "copy": True, "dup":  0x675e}, # 杞
        {"src": 61476, "dest": 0x29fce, "copy": True, "dup": 0x29fd7}, # 𩿗
        {"src": 59577, "dest": 0x20984, "copy": True, "dup": 0x2f82c}, # 𠦄

        # KS X 1001 duplication list and ....
        {"src": 38815, "dest": 0x8c48, "copy": True, "dup": 0xf900}, # 豈
        {"src": 21055, "dest": 0x66f4, "copy": True, "dup": 0xf901}, # 更
        {"src": 39846, "dest": 0x8eca, "copy": True, "dup": 0xf902}, # 車
        {"src": 39036, "dest": 0x8cc8, "copy": True, "dup": 0xf903}, # 賈
        {"src": 24509, "dest": 0x6ed1, "copy": True, "dup": 0xf904}, # 滑
        {"src":  9902, "dest": 0x4e32, "copy": True, "dup": 0xf905}, # 串
        {"src": 12323, "dest": 0x53e5, "copy": True, "dup": 0xf906}, # 句
        {"src": 62984, "dest": 0x9f9c, "copy": True, "dup": 0xf908}, # 龜
        {"src": 62984, "dest": 0xf907, "copy": True, "dup": 0xf908}, # 龜
        {"src": 62984, "dest": 0xf908, "copy": True, "dup": 0xf908}, # 龜
        {"src": 58810, "dest": 0x5951, "copy": True, "dup": 0xf909}, # 契
        {"src": 41347, "dest": 0x91d1, "copy": True, "dup": 0xf90a}, # 金
        {"src": 12968, "dest": 0x5587, "copy": True, "dup": 0xf90b}, # 喇
        {"src": 14589, "dest": 0x5948, "copy": True, "dup": 0xf90c}, # 奈
        {"src": 18880, "dest": 0x61f6, "copy": True, "dup": 0xf90d}, # 懶
        {"src": 28042, "dest": 0x7669, "copy": True, "dup": 0xf90e}, # 癩
        {"src": 32334, "dest": 0x7f85, "copy": True, "dup": 0xf90f}, # 羅

        {"src": 36067, "dest": 0x863f, "copy": True, "dup": 0xf910}, # 蘿
        {"src": 36703, "dest": 0x87ba, "copy": True, "dup": 0xf911}, # 螺
        {"src": 37270, "dest": 0x88f8, "copy": True, "dup": 0xf912}, # 裸
        {"src": 40771, "dest": 0x908f, "copy": True, "dup": 0xf913}, # 邏
        {"src": 22397, "dest": 0xf914, "copy": True, "dup": 0xf9bf}, # 樂
        {"src": 23786, "dest": 0x6d1b, "copy": True, "dup": 0xf915}, # 洛
        {"src": 25465, "dest": 0x70d9, "copy": True, "dup": 0xf916}, # 烙
        {"src": 26844, "dest": 0x73de, "copy": True, "dup": 0xf917}, # 珞
        {"src": 34885, "dest": 0x843d, "copy": True, "dup": 0xf918}, # 落
        {"src": 41141, "dest": 0x916a, "copy": True, "dup": 0xf919}, # 酪
        {"src": 44928, "dest": 0x99f1, "copy": True, "dup": 0xf91a}, # 駱
        {"src": 10020, "dest": 0x4e82, "copy": True, "dup": 0xf91b}, # 亂
        {"src": 12147, "dest": 0x5375, "copy": True, "dup": 0xf91c}, # 卵
        {"src": 58811, "dest": 0x6b04, "copy": True, "dup": 0xf91d}, # 欄
        {"src": 26118, "dest": 0x721b, "copy": True, "dup": 0xf91e}, # 爛
        {"src": 58812, "dest": 0x862d, "copy": True, "dup": 0xf91f}, # 蘭

        {"src": 46719, "dest": 0x9e1e, "copy": True, "dup": 0xf920}, # 鸞
        {"src": 16768, "dest": 0x5d50, "copy": True, "dup": 0xf921}, # 嵐
        {"src": 25003, "dest": 0x6feb, "copy": True, "dup": 0xf922}, # 濫
        {"src": 35803, "dest": 0x85cd, "copy": True, "dup": 0xf923}, # 藍
        {"src": 37493, "dest": 0x8964, "copy": True, "dup": 0xf924}, # 襤
        {"src": 19223, "dest": 0x62c9, "copy": True, "dup": 0xf925}, # 拉
        {"src": 33569, "dest": 0x81d8, "copy": True, "dup": 0xf926}, # 臘
        {"src": 36883, "dest": 0x881f, "copy": True, "dup": 0xf927}, # 蠟
        {"src": 58813, "dest": 0x5eca, "copy": True, "dup": 0xf928}, # 廊
        {"src": 58814, "dest": 0x6717, "copy": True, "dup": 0xf929}, # 朗
        {"src": 23903, "dest": 0x6d6a, "copy": True, "dup": 0xf92a}, # 浪
        {"src": 26484, "dest": 0x72fc, "copy": True, "dup": 0xf92b}, # 狼
        {"src": 40868, "dest": 0x90de, "copy": True, "dup": 0xf92c}, # 郞
        {"src": 10421, "dest": 0x4f86, "copy": True, "dup": 0xf92d}, # 來
        {"src": 11398, "dest": 0x51b7, "copy": True, "dup": 0xf92e}, # 冷
        {"src": 11881, "dest": 0x52de, "copy": True, "dup": 0xf92f}, # 勞

        {"src": 20078, "dest": 0x64c4, "copy": True, "dup": 0xf930}, # 擄
        {"src": 22772, "dest": 0x6ad3, "copy": True, "dup": 0xf931}, # 櫓
        {"src": 26095, "dest": 0x7210, "copy": True, "dup": 0xf932}, # 爐
        {"src": 28245, "dest": 0x76e7, "copy": True, "dup": 0xf933}, # 盧
        {"src": 32584, "dest": 0x8001, "copy": True, "dup": 0xf934}, # 老
        {"src": 35937, "dest": 0x8606, "copy": True, "dup": 0xf935}, # 蘆
        {"src": 58815, "dest": 0x865c, "copy": True, "dup": 0xf936}, # 虜
        {"src": 39455, "dest": 0x8def, "copy": True, "dup": 0xf937}, # 路
        {"src": 43690, "dest": 0x9732, "copy": True, "dup": 0xf938}, # 露
        {"src": 45651, "dest": 0x9b6f, "copy": True, "dup": 0xf939}, # 魯
        {"src": 46656, "dest": 0x9dfa, "copy": True, "dup": 0xf93a}, # 鷺
        {"src": 28908, "dest": 0x788c, "copy": True, "dup": 0xf93b}, # 碌
        {"src": 29334, "dest": 0x797f, "copy": True, "dup": 0xf93c}, # 祿
        {"src": 31489, "dest": 0x7da0, "copy": True, "dup": 0xf93d}, # 綠
        {"src": 34634, "dest": 0x83c9, "copy": True, "dup": 0xf93e}, # 菉
        {"src": 41941, "dest": 0x9304, "copy": True, "dup": 0xf93f}, # 錄

        {"src": 46823, "dest": 0x9e7f, "copy": True, "dup": 0xf940}, # 鹿
        {"src": 38199, "dest": 0x8ad6, "copy": True, "dup": 0xf941}, # 論
        {"src": 14416, "dest": 0x58df, "copy": True, "dup": 0xf942}, # 壟
        {"src": 17562, "dest": 0x5f04, "copy": True, "dup": 0xf943}, # 弄
        {"src": 30831, "dest": 0x7c60, "copy": True, "dup": 0xf944}, # 籠
        {"src": 32836, "dest": 0x807e, "copy": True, "dup": 0xf945}, # 聾
        {"src": 26261, "dest": 0x7262, "copy": True, "dup": 0xf946}, # 牢
        {"src": 29011, "dest": 0x78ca, "copy": True, "dup": 0xf947}, # 磊
        {"src": 39024, "dest": 0x8cc2, "copy": True, "dup": 0xf948}, # 賂
        {"src": 43564, "dest": 0x96f7, "copy": True, "dup": 0xf949}, # 雷
        {"src": 14401, "dest": 0x58d8, "copy": True, "dup": 0xf94a}, # 壘
        {"src": 16304, "dest": 0x5c62, "copy": True, "dup": 0xf94b}, # 屢
        {"src": 22426, "dest": 0x6a13, "copy": True, "dup": 0xf94c}, # 樓
        {"src": 24080, "dest": 0x6dda, "copy": True, "dup": 0xf94d}, # 淚
        {"src": 24617, "dest": 0x6f0f, "copy": True, "dup": 0xf94e}, # 漏
        {"src": 31264, "dest": 0x7d2f, "copy": True, "dup": 0xf94f}, # 累

        {"src": 31806, "dest": 0x7e37, "copy": True, "dup": 0xf950}, # 縷
        {"src": 43241, "dest": 0x964b, "copy": True, "dup": 0xf951}, # 陋
        {"src": 11863, "dest": 0x52d2, "copy": True, "dup": 0xf952}, # 勒
        {"src": 32859, "dest": 0x808b, "copy": True, "dup": 0xf953}, # 肋
        {"src": 11473, "dest": 0x51dc, "copy": True, "dup": 0xf954}, # 凜
        {"src": 11442, "dest": 0x51cc, "copy": True, "dup": 0xf955}, # 凌
        {"src": 29615, "dest": 0x7a1c, "copy": True, "dup": 0xf956}, # 稜
        {"src": 31553, "dest": 0x7dbe, "copy": True, "dup": 0xf957}, # 綾
        {"src": 34724, "dest": 0x83f1, "copy": True, "dup": 0xf958}, # 菱
        {"src": 43310, "dest": 0x9675, "copy": True, "dup": 0xf959}, # 陵
        {"src": 38559, "dest": 0x8b80, "copy": True, "dup": 0xf95a}, # 讀
        {"src": 19233, "dest": 0x62cf, "copy": True, "dup": 0xf95b}, # 拏
        {"src": 22397, "dest": 0xf95c, "copy": True, "dup": 0xf9bf}, # 樂
        {"src": 38281, "dest": 0x8afe, "copy": True, "dup": 0xf95d}, # 諾
        {"src":  9912, "dest": 0x4e39, "copy": True, "dup": 0xf95e}, # 丹
        {"src": 16093, "dest": 0xf95f, "copy": True, "dup": 0xf9aa}, # 寧

        {"src": 18027, "dest": 0x6012, "copy": True, "dup": 0xf960}, # 怒
        {"src": 26726, "dest": 0xf961, "copy": True, "dup": 0xf9db}, # 率
        {"src": 27567, "dest": 0x7570, "copy": True, "dup": 0xf962}, # 異
        {"src": 11980, "dest": 0x5317, "copy": True, "dup": 0xf963}, # 北
        {"src": 29102, "dest": 0x78fb, "copy": True, "dup": 0xf964}, # 磻
        {"src": 10513, "dest": 0x4fbf, "copy": True, "dup": 0xf965}, # 便
        {"src": 17857, "dest": 0x5fa9, "copy": True, "dup": 0xf966}, # 復
        {"src":  9846, "dest": 0x4e0d, "copy": True, "dup": 0xf967}, # 不
        {"src": 23665, "dest": 0x6ccc, "copy": True, "dup": 0xf968}, # 泌
        {"src": 20406, "dest": 0x6578, "copy": True, "dup": 0xf969}, # 數
        {"src": 31242, "dest": 0x7d22, "copy": True, "dup": 0xf96a}, # 索
        {"src": 12269, "dest": 0x53c3, "copy": True, "dup": 0xf96b}, # 參
        {"src": 14192, "dest": 0x585e, "copy": True, "dup": 0xf96c}, # 塞
        {"src": 28288, "dest": 0x7701, "copy": True, "dup": 0xf96d}, # 省
        {"src": 34909, "dest": 0x8449, "copy": True, "dup": 0xf96e}, # 葉
        {"src": 38108, "dest": 0xf96f, "copy": True, "dup": 0xf9a1}, # 說

        {"src": 58816, "dest": 0x6bba, "copy": True, "dup": 0xf970}, # 殺
        {"src": 40197, "dest": 0x8fb0, "copy": True, "dup": 0xf971}, # 辰
        {"src": 23566, "dest": 0x6c88, "copy": True, "dup": 0xf972}, # 沈
        {"src": 19306, "dest": 0x62fe, "copy": True, "dup": 0xf973}, # 拾
        {"src": 34159, "dest": 0x82e5, "copy": True, "dup": 0xf974}, # 若
        {"src": 19566, "dest": 0x63a0, "copy": True, "dup": 0xf975}, # 掠
        {"src": 27547, "dest": 0x7565, "copy": True, "dup": 0xf976}, # 略
        {"src": 10092, "dest": 0x4eae, "copy": True, "dup": 0xf977}, # 亮
        {"src": 11277, "dest": 0x5169, "copy": True, "dup": 0xf978}, # 兩
        {"src": 11434, "dest": 0x51c9, "copy": True, "dup": 0xf979}, # 凉
        {"src": 21695, "dest": 0x6881, "copy": True, "dup": 0xf97a}, # 梁
        {"src": 31118, "dest": 0x7ce7, "copy": True, "dup": 0xf97b}, # 糧
        {"src": 33914, "dest": 0x826f, "copy": True, "dup": 0xf97c}, # 良
        {"src": 38190, "dest": 0x8ad2, "copy": True, "dup": 0xf97d}, # 諒
        {"src": 41344, "dest": 0x91cf, "copy": True, "dup": 0xf97e}, # 量
        {"src": 11920, "dest": 0x52f5, "copy": True, "dup": 0xf97f}, # 勵

        {"src": 12473, "dest": 0x5442, "copy": True, "dup": 0xf980}, # 呂
        {"src": 14669, "dest": 0x5973, "copy": True, "dup": 0xf981}, # 女
        {"src": 17517, "dest": 0x5eec, "copy": True, "dup": 0xf982}, # 廬
        {"src": 58817, "dest": 0x65c5, "copy": True, "dup": 0xf983}, # 旅
        {"src": 25038, "dest": 0x6ffe, "copy": True, "dup": 0xf984}, # 濾
        {"src": 29177, "dest": 0x792a, "copy": True, "dup": 0xf985}, # 礪
        {"src": 43024, "dest": 0x95ad, "copy": True, "dup": 0xf986}, # 閭
        {"src": 45157, "dest": 0x9a6a, "copy": True, "dup": 0xf987}, # 驪
        {"src": 62965, "dest": 0x9e97, "copy": True, "dup": 0xf988}, # 麗
        {"src": 47018, "dest": 0x9ece, "copy": True, "dup": 0xf989}, # 黎
        {"src": 11778, "dest": 0x529b, "copy": True, "dup": 0xf98a}, # 力
        {"src": 20975, "dest": 0x66c6, "copy": True, "dup": 0xf98b}, # 曆
        {"src": 23067, "dest": 0x6b77, "copy": True, "dup": 0xf98c}, # 歷
        {"src": 40095, "dest": 0x8f62, "copy": True, "dup": 0xf98d}, # 轢
        {"src": 17283, "dest": 0x5e74, "copy": True, "dup": 0xf98e}, # 年
        {"src": 18695, "dest": 0x6190, "copy": True, "dup": 0xf98f}, # 憐

        {"src": 18902, "dest": 0x6200, "copy": True, "dup": 0xf990}, # 戀
        {"src": 20003, "dest": 0x649a, "copy": True, "dup": 0xf991}, # 撚
        {"src": 24655, "dest": 0x6f23, "copy": True, "dup": 0xf992}, # 漣
        {"src": 25678, "dest": 0x7149, "copy": True, "dup": 0xf993}, # 煉
        {"src": 27136, "dest": 0x7489, "copy": True, "dup": 0xf994}, # 璉
        {"src": 29478, "dest": 0x79ca, "copy": True, "dup": 0xf995}, # 秊
        {"src": 58896, "dest": 0xf996, "copy": True, "dup": 0xfa57}, # 練
        {"src": 32800, "dest": 0x806f, "copy": True, "dup": 0xf997}, # 聯
        {"src": 39981, "dest": 0x8f26, "copy": True, "dup": 0xf998}, # 輦
        {"src": 58818, "dest": 0x84ee, "copy": True, "dup": 0xf999}, # 蓮
        {"src": 58819, "dest": 0x9023, "copy": True, "dup": 0xf99a}, # 連
        {"src": 42072, "dest": 0x934a, "copy": True, "dup": 0xf99b}, # 鍊
        {"src": 11560, "dest": 0x5217, "copy": True, "dup": 0xf99c}, # 列
        {"src": 11787, "dest": 0x52a3, "copy": True, "dup": 0xf99d}, # 劣
        {"src": 12656, "dest": 0x54bd, "copy": True, "dup": 0xf99e}, # 咽
        {"src": 25431, "dest": 0x70c8, "copy": True, "dup": 0xf99f}, # 烈

        {"src": 37163, "dest": 0x88c2, "copy": True, "dup": 0xf9a0}, # 裂
        {"src": 38108, "dest": 0x8aaa, "copy": True, "dup": 0xf9a1}, # 說
        {"src": 58820, "dest": 0x5ec9, "copy": True, "dup": 0xf9a2}, # 廉
        {"src": 17984, "dest": 0x5ff5, "copy": True, "dup": 0xf9a3}, # 念
        {"src": 19501, "dest": 0x637b, "copy": True, "dup": 0xf9a4}, # 捻
        {"src": 23196, "dest": 0x6bae, "copy": True, "dup": 0xf9a5}, # 殮
        {"src": 30751, "dest": 0x7c3e, "copy": True, "dup": 0xf9a6}, # 簾
        {"src": 26690, "dest": 0x7375, "copy": True, "dup": 0xf9a7}, # 獵
        {"src": 10176, "dest": 0x4ee4, "copy": True, "dup": 0xf9a8}, # 令
        {"src": 13628, "dest": 0x56f9, "copy": True, "dup": 0xf9a9}, # 囹
        {"src": 16093, "dest": 0x5be7, "copy": True, "dup": 0xf9aa}, # 寧
        {"src": 16984, "dest": 0x5dba, "copy": True, "dup": 0xf9ab}, # 嶺
        {"src": 18041, "dest": 0x601c, "copy": True, "dup": 0xf9ac}, # 怜
        {"src": 26787, "dest": 0x73b2, "copy": True, "dup": 0xf9ad}, # 玲
        {"src": 27078, "dest": 0x7469, "copy": True, "dup": 0xf9ae}, # 瑩
        {"src": 32372, "dest": 0x7f9a, "copy": True, "dup": 0xf9af}, # 羚

        {"src": 32723, "dest": 0x8046, "copy": True, "dup": 0xf9b0}, # 聆
        {"src": 41535, "dest": 0x9234, "copy": True, "dup": 0xf9b1}, # 鈴
        {"src": 43561, "dest": 0x96f6, "copy": True, "dup": 0xf9b2}, # 零
        {"src": 43736, "dest": 0x9748, "copy": True, "dup": 0xf9b3}, # 靈
        {"src": 44100, "dest": 0x9818, "copy": True, "dup": 0xf9b4}, # 領
        {"src": 10429, "dest": 0x4f8b, "copy": True, "dup": 0xf9b5}, # 例
        {"src": 29425, "dest": 0x79ae, "copy": True, "dup": 0xf9b6}, # 禮
        {"src": 41292, "dest": 0x91b4, "copy": True, "dup": 0xf9b7}, # 醴
        {"src": 43439, "dest": 0x96b7, "copy": True, "dup": 0xf9b8}, # 隷
        {"src": 18372, "dest": 0x60e1, "copy": True, "dup": 0xf9b9}, # 惡
        {"src": 10026, "dest": 0x4e86, "copy": True, "dup": 0xf9ba}, # 了
        {"src": 11020, "dest": 0x50da, "copy": True, "dup": 0xf9bb}, # 僚
        {"src": 16110, "dest": 0x5bee, "copy": True, "dup": 0xf9bc}, # 寮
        {"src": 16246, "dest": 0x5c3f, "copy": True, "dup": 0xf9bd}, # 尿
        {"src": 20465, "dest": 0x6599, "copy": True, "dup": 0xf9be}, # 料
        {"src": 22397, "dest": 0x6a02, "copy": True, "dup": 0xf9bf}, # 樂

        {"src": 25957, "dest": 0x71ce, "copy": True, "dup": 0xf9c0}, # 燎
        {"src": 27965, "dest": 0x7642, "copy": True, "dup": 0xf9c1}, # 療
        {"src": 35315, "dest": 0x84fc, "copy": True, "dup": 0xf9c2}, # 蓼
        {"src": 58821, "dest": 0x907c, "copy": True, "dup": 0xf9c3}, # 遼
        {"src": 47434, "dest": 0x9f8d, "copy": True, "dup": 0xf9c4}, # 龍
        {"src": 20870, "dest": 0x6688, "copy": True, "dup": 0xf9c5}, # 暈
        {"src": 43201, "dest": 0x962e, "copy": True, "dup": 0xf9c6}, # 阮
        {"src": 11743, "dest": 0x5289, "copy": True, "dup": 0xf9c7}, # 劉
        {"src": 21275, "dest": 0x677b, "copy": True, "dup": 0xf9c8}, # 杻
        {"src": 21467, "dest": 0x67f3, "copy": True, "dup": 0xf9c9}, # 柳
        {"src": 23847, "dest": 0x6d41, "copy": True, "dup": 0xf9ca}, # 流
        {"src": 24406, "dest": 0x6e9c, "copy": True, "dup": 0xf9cb}, # 溜
        {"src": 26911, "dest": 0x7409, "copy": True, "dup": 0xf9cc}, # 琉
        {"src": 27525, "dest": 0x7559, "copy": True, "dup": 0xf9cd}, # 留
        {"src": 28858, "dest": 0x786b, "copy": True, "dup": 0xf9ce}, # 硫
        {"src": 31201, "dest": 0x7d10, "copy": True, "dup": 0xf9cf}, # 紐

        {"src": 58822, "dest": 0x985e, "copy": True, "dup": 0xf9d0}, # 類
        {"src": 11288, "dest": 0x516d, "copy": True, "dup": 0xf9d1}, # 六
        {"src": 18970, "dest": 0x622e, "copy": True, "dup": 0xf9d2}, # 戮
        {"src": 43317, "dest": 0x9678, "copy": True, "dup": 0xf9d3}, # 陸
        {"src": 10700, "dest": 0x502b, "copy": True, "dup": 0xf9d4}, # 倫
        {"src": 16655, "dest": 0x5d19, "copy": True, "dup": 0xf9d5}, # 崙
        {"src": 24109, "dest": 0x6dea, "copy": True, "dup": 0xf9d6}, # 淪
        {"src": 39989, "dest": 0x8f2a, "copy": True, "dup": 0xf9d7}, # 輪
        {"src": 17810, "dest": 0x5f8b, "copy": True, "dup": 0xf9d8}, # 律
        {"src": 18542, "dest": 0x6144, "copy": True, "dup": 0xf9d9}, # 慄
        {"src": 21520, "dest": 0x6817, "copy": True, "dup": 0xf9da}, # 栗
        {"src": 26726, "dest": 0x7387, "copy": True, "dup": 0xf9db}, # 率
        {"src": 58823, "dest": 0x9686, "copy": True, "dup": 0xf9dc}, # 隆
        {"src": 11587, "dest": 0x5229, "copy": True, "dup": 0xf9dd}, # 利
        {"src": 12384, "dest": 0x540f, "copy": True, "dup": 0xf9de}, # 吏
        {"src": 16310, "dest": 0x5c65, "copy": True, "dup": 0xf9df}, # 履

        {"src": 20690, "dest": 0x6613, "copy": True, "dup": 0xf9e0}, # 易
        {"src": 21209, "dest": 0x674e, "copy": True, "dup": 0xf9e1}, # 李
        {"src": 21764, "dest": 0x68a8, "copy": True, "dup": 0xf9e2}, # 梨
        {"src": 23710, "dest": 0x6ce5, "copy": True, "dup": 0xf9e3}, # 泥
        {"src": 26906, "dest": 0x7406, "copy": True, "dup": 0xf9e4}, # 理
        {"src": 27767, "dest": 0x75e2, "copy": True, "dup": 0xf9e5}, # 痢
        {"src": 32311, "dest": 0x7f79, "copy": True, "dup": 0xf9e6}, # 罹
        {"src": 37189, "dest": 0x88cf, "copy": True, "dup": 0xf9e7}, # 裏
        {"src": 37228, "dest": 0x88e1, "copy": True, "dup": 0xf9e8}, # 裡
        {"src": 41341, "dest": 0x91cc, "copy": True, "dup": 0xf9e9}, # 里
        {"src": 43524, "dest": 0x96e2, "copy": True, "dup": 0xf9ea}, # 離
        {"src": 12065, "dest": 0x533f, "copy": True, "dup": 0xf9eb}, # 匿
        {"src": 24460, "dest": 0x6eba, "copy": True, "dup": 0xf9ec}, # 溺
        {"src": 12403, "dest": 0x541d, "copy": True, "dup": 0xf9ed}, # 吝
        {"src": 25961, "dest": 0x71d0, "copy": True, "dup": 0xf9ee}, # 燐
        {"src": 27159, "dest": 0x7498, "copy": True, "dup": 0xf9ef}, # 璘

        {"src": 35905, "dest": 0x85fa, "copy": True, "dup": 0xf9f0}, # 藺
        {"src": 62873, "dest": 0x96a3, "copy": True, "dup": 0xf9f1}, # 隣
        {"src": 46027, "dest": 0x9c57, "copy": True, "dup": 0xf9f2}, # 鱗
        {"src": 46909, "dest": 0x9e9f, "copy": True, "dup": 0xf9f3}, # 麟
        {"src": 21324, "dest": 0x6797, "copy": True, "dup": 0xf9f4}, # 林
        {"src": 24053, "dest": 0x6dcb, "copy": True, "dup": 0xf9f5}, # 淋
        {"src": 33605, "dest": 0x81e8, "copy": True, "dup": 0xf9f6}, # 臨
        {"src": 29991, "dest": 0x7acb, "copy": True, "dup": 0xf9f7}, # 立
        {"src": 30155, "dest": 0x7b20, "copy": True, "dup": 0xf9f8}, # 笠
        {"src": 30939, "dest": 0x7c92, "copy": True, "dup": 0xf9f9}, # 粒
        {"src": 26396, "dest": 0x72c0, "copy": True, "dup": 0xf9fa}, # 狀
        {"src": 25344, "dest": 0x7099, "copy": True, "dup": 0xf9fb}, # 炙
        {"src": 38478, "dest": 0x8b58, "copy": True, "dup": 0xf9fc}, # 識
        {"src": 10122, "dest": 0x4ec0, "copy": True, "dup": 0xf9fd}, # 什
        {"src": 34336, "dest": 0x8336, "copy": True, "dup": 0xf9fe}, # 茶
        {"src": 11613, "dest": 0x523a, "copy": True, "dup": 0xf9ff}, # 刺

        {"src": 11542, "dest": 0x5207, "copy": True, "dup": 0xfa00}, # 切
        {"src": 17373, "dest": 0x5ea6, "copy": True, "dup": 0xfa01}, # 度
        {"src": 19242, "dest": 0x62d3, "copy": True, "dup": 0xfa02}, # 拓
        {"src": 58824, "dest": 0x7cd6, "copy": True, "dup": 0xfa03}, # 糖
        {"src": 15891, "dest": 0x5b85, "copy": True, "dup": 0xfa04}, # 宅
        {"src": 23791, "dest": 0x6d1e, "copy": True, "dup": 0xfa05}, # 洞
        {"src": 20944, "dest": 0x66b4, "copy": True, "dup": 0xfa06}, # 暴
        {"src": 40022, "dest": 0x8f3b, "copy": True, "dup": 0xfa07}, # 輻
        {"src": 36964, "dest": 0x884c, "copy": True, "dup": 0xfa08}, # 行
        {"src": 62867, "dest": 0x964d, "copy": True, "dup": 0xfa09}, # 降
        {"src": 37573, "dest": 0x898b, "copy": True, "dup": 0xfa0a}, # 見
        {"src": 17463, "dest": 0x5ed3, "copy": True, "dup": 0xfa0b}, # 廓

        {"src": 40890, "dest": 0x90de, "copy": True, "dup": 0xfa2e}, # 郞
        {"src": 43437, "dest": 0x96b7, "copy": True, "dup": 0xfa2f}, # 隷
        # End of KS X 1001
    ]
    flg = False
    for h in mis_encodes:
        try:
            gs = srcfont[h["src"]]
            if h["dup"] and gs.unicode != h["dup"]:
                log("%s: .. %d (0x%04x) may not be a duplication of U+%04X." %
                    (srcfont.fontname, h["src"], h["src"], h["dup"]))
        except:
            log("%s: .. %d (0x%04x) does not found" %
                (srcfont.fontname, h["src"], h["src"]))
            continue

        if type(h["dest"]) is int:
            enc = srcfont.findEncodingSlot(h["dest"])
        else:
            enc = -1

        # If multiple glyphs has same unicode codepoint,
        # FontForge does not seem to copy to there.
        if enc < 0 or h["src"] != enc:
            if enc < 0:
                if type(h["dest"]) is int:
                    log("%s: .. U+%04x is not found" %
                        (srcfont.fontname, h["dest"]))
                else:
                    log("%s: .. Creating %s" % (srcfont.fontname, h["dest"]))
                    g = target.createChar(-1, h["dest"])
                    h["dest"] = g.encoding
            else:
                log("%s: .. U+%04x is at %d but gives %d" %
                    (srcfont.fontname, h["dest"], enc, h["src"]))

            uni = gs.unicode
            if uni < 0: uni = gs.glyphname
            copytab[h["dest"]] = uni
            if copyrev.get(uni) is None: copyrev[uni] = []
            copyrev[uni].append(h["dest"])

            srcfont.selection.select(("encoding",),h["src"])
            srcfont.copy()
            target.selection.select(("encoding",),h["dest"])
            target.paste()
            if not h["copy"]:
                g = srcfont[h["src"]]
                srcfont.removeGlyph(g)
        else:
            log("%s: .. U+%04x already exist at %d" %
                (srcfont.fontname, h["dest"], h["src"]))

    if flg:
        log("Errors found. Abort")
        exit(1)

    log("%s: Collecting informations of glyphs..." % (srcfont.fontname))
    lookup_remaps = {}
    not_in_unicode = {}
    gsubtables = {}
    gsub_tabs = srcfont.gsub_lookups
    subtables = {}
    contexts = {}
    for i in range(0,len(gsub_tabs)):
        tab = gsub_tabs[i]
        info = srcfont.getLookupInfo(tab)
        x = re.match(r"gsub_context(chain)?", info[0])
        if not x is None:
            before = None
            if i < len(gsub_tabs) - 1:
                before = tab[i + 1]
            contexts[tab] = before
        else:
            feat = info[2]
            if len(feat) == 0:
                log("%s: .. Skipped importing lookup \"%s\"" %
                    (srcfont.fontname, tab))
                continue

            liga = False
            for t in feat:
                if t[0] == "liga":
                    liga = True
                    break
            if liga:
                log("%s: .. Skipped standard liga (because mintty applies)" %
                    (srcfont.fontname))
                continue

            subtab = srcfont.getLookupSubtables(tab)
            m = []
            for t in subtab:
                m.append(t)
                subtables[t] = True
            gsubtables[tab] = m

    subtable_data = {}
    for g in srcfont.glyphs():
        uni = g.unicode
        enc = g.encoding
        subkey = uni
        if uni < 0:
            not_in_unicode[enc] = False
            subkey = g.glyphname

        lst = []
        subinfo = g.getPosSub("*")
        for info in subinfo:
            infol = []
            for i in info:
                infol.append(i)
            subtname = infol.pop(0)
            if not subtables.get(subtname):
                continue
            subttype = infol.pop(0)
            subtdata = infol
            m = subtable_data.get(subtname)
            if m is None:
                m = {}
            m[subkey] = subtdata
            subtable_data[subtname] = m

    flg = False
    for subtname in subtable_data:
        subtmap = subtable_data[subtname]
        for base in subtmap:
            data = subtmap[base]
            for i in range(0,len(data)):
                name = data[i]
                try:
                    g = srcfont[name]
                    uni = g.unicode
                    if uni < 0:
                        not_in_unicode[g.encoding] = True
                    else:
                        data[i] = uni
                except:
                    flg = True
                    log("%s: .. %s does not found" % (srcfont.fontname, name))

    log("%s: Creating glyphs for substitutions/ligatures..." %
        (srcfont.fontname))
    tgfst = None
    tglst = None
    srcfont.selection.none()
    for enc in not_in_unicode:
        if not not_in_unicode[enc]: continue
        g = srcfont[enc]
        nam = g.glyphname
        gu = target.createChar(-1,nam)
        uni = gu.encoding
        if tgfst is None: tgfst = uni
        tglst = uni
        #log("%s: .. Creating U+%x for %s" % (srcfont.fontname, uni, nam))
        srcfont.selection.select(("more",),enc)

    log("%s: Copying glyphs..." % (srcfont.fontname))
    srcfont.copy()
    target.selection.select(("ranges",),tgfst,tglst)
    target.paste()

    srcfont.encoding = "UnicodeFull"
    srcfont.selection.select(("ranges","unicode"),0x0000,0x10ffff)
    srcfont.copy()
    target.selection.select(("ranges","unicode"),0x0000,0x10ffff)
    target.paste()

    log("%s: Checking glyphs..." % (srcfont.fontname))
    flg = False
    for i in warned_list:
        try:
            m = target[i]
        except:
            flg = True
            log("Glyph U+%04x does not exist" % i)
    if flg:
        exit(1)

    subtab_map = {}
    subtable_info = {}
    log("%s: Importing Subtable maps..." % (srcfont.fontname))
    for m in gsubtables:
        target.importLookups(srcfont, m)
        info = target.getLookupInfo(m)
        tgtsub = target.getLookupSubtables(m)
        srcsub = gsubtables[m]
        for i in range(0,len(srcsub)):
            subtab_map[srcsub[i]] = tgtsub[i]
            subtable_info[tgtsub[i]] = info

    # Clear tables
    log("%s: .. Clearing all gsub maps..." % (srcfont.fontname))
    for g in target.glyphs():
        for tab in subtab_map.values():
            g.removePosSub(tab)

    log("%s: .. Rebuild gsub maps..." % (srcfont.fontname))
    for subsname in subtab_map:
        subtname = subtab_map[subsname]
        tabsrc = subtable_data.get(subsname)
        if tabsrc is None:
            log("%s: .. No data found for map \"%s\". Skipped." %
                (srcfont.fontname, subsname))
            continue

        subttype = subtable_info[subsname][0]

        unilst = []
        for uni in tabsrc:
            unilst.append((uni,uni))
            l = copyrev.get(uni)
            if not l is None:
                for x in l:
                    unilst.append((x,uni))

        for uni in unilst:
            tabuni = uni[1]
            uni = uni[0]

            g = None
            try:
                g = target[uni]
            except:
                "NOP"

            if g is None and type(uni) is str:
                gs = srcfont[uni]
                altuni = gs.altuni
                if not altuni is None:
                    for enc in altuni:
                        try:
                            g = target[enc[0]]
                            break
                        except:
                            "NOP"

                    if not g is None:
                        log("%s: .. U+%04x will be used instead of %s" %
                            (srcfont.fontname, g.unicode, uni))

            if g is None:
                if type(uni) is int:
                    uni = "U+%04x" % uni
                log("%s: .. %s were not copied." % (srcfont.fontname, uni))
                continue

            lst = tabsrc[tabuni]
            alst = []
            for i in lst:
                gx = target[i]
                alst.append(gx.glyphname)

            if subttype == "gsub_single":
                g.addPosSub(subtname, alst[0])
            elif subttype == "gsub_ligature" or subttype == "gsub_alternate":
                g.addPosSub(subtname, tuple(alst))
            else:
                log("%s: .. Subtable type %s is not supported." %
                    (srcfont.fontname, subttype))
                exit(1)

    srcfont.close()

    # Both IBM Plex and Fira Mono uses 600 width in 1000 em.
def add_ibm_plex_or_fira_mono(target, source, slant, ranges):
    log("Reading %s..." % source.get("path"))
    srcfont = fontforge.open(source.get("path"))

    # Unlink references because resize breaks position
    srcfont.selection.all()
    srcfont.unlinkReferences()

    srcfont.selection.none()
    target.selection.none()
    for m in ranges:
        if type(m) is tuple:
            f = m[0]
            t = m[1]
        elif type(m) is range:
            f = m.start
            t = m.stop - 1
        else:
            f = m
            t = m

        srcfont.selection.select(("ranges","more"),f,t)
        target.selection.select(("ranges","more"),f,t)

    log("%s: Remove not required glyphs..." % (srcfont.fontname))
    srcfont.selection.invert()
    for enc in srcfont.selection:
        try:
            g = srcfont[enc]
        except TypeError:
            continue
        srcfont.removeGlyph(g)

    srcfont.selection.invert()
    gpos_lookups = srcfont.gpos_lookups
    for lookup in gpos_lookups:
        subt = srcfont.getLookupSubtables(lookup)
        anch = []
        for tb in subt:
            l = srcfont.getLookupSubtableAnchorClasses(tb)
            for li in l:
                anch.append(li)
        if len(anch) > 0:
            target.importLookups(srcfont, lookup)

    ascent = srcfont.ascent
    scale = float(ASCENT) / ascent

    if scale != 1.0:
        log("%s: Scaling %g%%..." % (srcfont.fontname, scale * 100.0))
        mat = psMat.scale(scale,scale)
        srcfont.transform(mat)

    log("%s: Adjusting width and move anchors..." % (srcfont.fontname))
    for g in srcfont.glyphs():
        if g.width > 0.0:
            scale = (ASCENT + DESCENT) / 2 / g.width
            mat = psMat.scale(scale,scale)
            g.transform(mat)

    if slant:
        log("%s: Create slant font by skewing %d degrees" %
            (srcfont.fontname, ITALIC_ANGLE))
        for g in srcfont.glyphs():
            w = g.width
            tf = ITALIC_SKEW
            tf = psMat.compose(tf,psMat.translate(-ITALIC_SHIFT,0.0))
            g.transform(tf)
            g.width = w


    log("%s: Copying glyphs..." % (srcfont.fontname))
    srcfont.copy()
    target.paste()

    srcfont.close()

def add_own_symbols(target):
    log("Putting original symbols...")
    for svg in glob.glob("src/uni[0-9a-fA-F]*.svg"):
        svg_fn = os.path.basename(svg)
        m = re.match(r'uni([0-9a-fA-F]+)', svg_fn)
        if m is None: continue
        enc = int(m.group(1), 16)
        doc = minidom.parse(svg)
        svgroot = doc.documentElement
        width = float(svgroot.getAttribute("width"))
        height = float(svgroot.getAttribute("height"))
        doc.unlink()
        scale = (ASCENT + DESCENT) / height
        log("Adding U+%04x..." % enc)
        try:
            g = target[enc]
            g.clear()
        except:
            g = target.createChar(enc)
        g.importOutlines(svg)
        g.width = width
        g.transform(psMat.scale(scale,scale))


def build_font(_f, source_han_subset):
    log('Generating %s ...' % _f.get('weight_name'))
    sources = _f.get("src_fonts")
    for k in sources:
        val = sources.get(k)
        path = './sourceFonts/%s' % val
        sources[k] = {
            "base": val,
            "path": path,
        }

    build = fontforge.font()
    build.encoding = "UnicodeFull"
    build.ascent = ASCENT
    build.descent = DESCENT

    if source_han_subset:
        source_han = sources["source_han_sans_subset"]
    else:
        source_han = sources["source_han_sans"]

    add_source_han_sans(build, source_han, _f["italic"])
    add_ibm_plex_or_fira_mono(build, sources["ibm_plex"], False,
                              [
                                  (0x0020,0x007e), # Latin
                                  (0x00a0,0x036f), # Latin-Extended
                                   0x0e3f,         # Thai
                                  (0x1e80,0x1eff), # Latin-Extended-Additional
                                  (0x2000,0x20cf), # Puct, Sub/Sub, Currency
                                  (0x2100,0x215f), # Litter like, Number form
                                  (0x2190,0x21ff), # Arrows
                                  (0x2200,0x22ff), # Maths
                                   0xebe7,         # Fun
                                  (0xf6d7,0xf6d8), # ?
                                  (0xfb01,0xfb02), # Lig forms
                              ])

    add_ibm_plex_or_fira_mono(build, sources["fira_mono"], _f["italic"],
                              [
                                  (0x0370,0x03ff), # Greek
                                  (0x0400,0x052f), # Cyrillic
                                  (0x1f00,0x1fff), # Geek Extended
                                  (0x2300,0x23ff), # Misc Technical
                                  (0x25a0,0x267f), # Misc Symbols
                              ])

    add_own_symbols(build)

    if _f["italic"]:
        build.italicangle = ITALIC_ANGLE
    else:
        build.italicangle = 0
    build.ascent = ASCENT
    build.descent = DESCENT
    build.fontname = _f.get('family')
    build.familyname = _f.get('family')
    build.fullname = _f.get('name')
    build.weight = _f.get('weight_name')
    build = set_os2_values(build, _f)
    build.appendSFNTName(0x411,0, COPYRIGHT)
    build.appendSFNTName(0x411,1, _f.get('family'))
    build.appendSFNTName(0x411,2, _f.get('style_name'))
    # build.appendSFNTName(0x411,3, "")
    build.appendSFNTName(0x411,4, _f.get('name'))
    build.appendSFNTName(0x411,5, "Version " + VERSION)
    build.appendSFNTName(0x411,6, _f.get('family') + "-" + _f.get('weight_name'))
    # build.appendSFNTName(0x411,7, "")
    # build.appendSFNTName(0x411,8, "")
    # build.appendSFNTName(0x411,9, "")
    # build.appendSFNTName(0x411,10, "")
    # build.appendSFNTName(0x411,11, "")
    # build.appendSFNTName(0x411,12, "")
    build.appendSFNTName(0x411,13, LICENSE)
    build.appendSFNTName(0x411,14, LICENSE_URL)
    # build.appendSFNTName(0x411,15, "")
    build.appendSFNTName(0x411,16, _f.get('family'))
    build.appendSFNTName(0x411,17, _f.get('style_name'))
    build.appendSFNTName(0x409,0, COPYRIGHT)
    build.appendSFNTName(0x409,1, _f.get('family'))
    build.appendSFNTName(0x409,2, _f.get('style_name'))
    build.appendSFNTName(0x409,3, VERSION + ";" + _f.get('family') + "-" + _f.get('style_name'))
    build.appendSFNTName(0x409,4, _f.get('name'))
    build.appendSFNTName(0x409,5, "Version " + VERSION)
    build.appendSFNTName(0x409,6, _f.get('name'))
    # build.appendSFNTName(0x409,7, "")
    # build.appendSFNTName(0x409,8, "")
    # build.appendSFNTName(0x409,9, "")
    # build.appendSFNTName(0x409,10, "")
    # build.appendSFNTName(0x409,11, "")
    # build.appendSFNTName(0x409,12, "")
    build.appendSFNTName(0x409,13, LICENSE)
    build.appendSFNTName(0x409,14, LICENSE_URL)
    # build.appendSFNTName(0x409,15, "")
    build.appendSFNTName(0x409,16, _f.get('family'))
    build.appendSFNTName(0x409,17, _f.get('style_name'))

    fw = ASCENT + DESCENT
    for g in build.glyphs():
        w = g.width
        uni = g.unicode
        name = g.glyphname
        lb = g.left_side_bearing
        rb = g.right_side_bearing
        if uni >= 0:
            name = "%s (U+%04x)" % (name, uni)
        if w > fw:
            log("%s has width longer than %d, %d" % (name, fw, w))
        elif lb < 0 or rb < 0:
            log("%s is sticked out of the character width" % (name))
            if lb < 0:
                log(" ... about %d ticks left" % (-lb))
            else: lb = 0
            if rb < 0:
                log(" ... about %d ticks right" % (-rb))
            else: rb = 0
            d = w - lb - rb
            if d > fw:
                log(" ... total width longer than %d, %d" % (fw, d))


    fontpath = "dist/%s" % _f.get("filename")
    log("Writing %s..." % fontpath)
    build.generate(fontpath)
    build.close()

def main():
    args = sys.argv
    arg0 = args.pop(0)
    use_subset = False
    for m in args:
        if m == "-help" or m == "--help" or m == "-h":
            print("""
   fontforge -lang=py %s [Font File Names to generate]

   --help           Show this help
   --use-subset     Use subset Source Han Sans
            """ % arg0)
            exit(0)
        if m == "--use-subset":
            use_subset = True

    if len(sys.argv) > 1:
        lst = [x for x in fonts if x["filename"] in sys.argv]
    else:
        lst = fonts

    print('')
    print('### Generating %s started. ###' % FAMILY)

    for _f in lst:
        build_font(_f, use_subset)

    print('### Succeeded ###')


if __name__ == '__main__':
    main()
