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
VERSION = '0.4.0'
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

    _font.os2_typoascent = ASCENT
    _font.os2_typoascent_add = False
    _font.os2_typodescent = -DESCENT
    _font.os2_typodescent_add = False
    _font.os2_typolinegap = 0

    _font.hhea_ascent = ASCENT
    _font.hhea_ascent_add = False
    _font.hhea_descent = -DESCENT
    _font.hhea_descent_add = False

    _font.hhea_linegap = 0
    _font.os2_panose = (2, 11, int(weight / 100), 9, 2, 2, 3, 2, 2, 7)
    return _font

def get_SFNTtag(font, name, lang = "English (US)"):
    m = font.sfnt_names
    h = {}
    for x in m:
        if x[1] != name: continue
        h[x[0]] = x[2]

    data = h.get(lang)
    if data is None:
        data = h.get(0x409)

    return data

def merge_SFNT(srcfont, target, name, lang = "English (US)"):
    src = get_SFNTtag(srcfont, name, lang)
    tgt = get_SFNTtag(target, name, lang)

    if src:
        if tgt is None:
            tgt = ""
        elif len(tgt) > 0:
            if tgt[-1] != "\n":
               tgt += "\n"
            tgt += "\n"
        tgt += "[%s]\n%s" % (srcfont.fontname, src)

        target.appendSFNTName(0x409, name, tgt)

def merge_designer(srcfont, target):
    merge_SFNT(srcfont, target, "Designer")

def merge_copyright(srcfont, target):
    merge_SFNT(srcfont, target, "Copyright")

def merge_description(srcfont, target):
    merge_SFNT(srcfont, target, "Descriptor")

def merge_trademark(srcfont, target):
    merge_SFNT(srcfont, target, "Trademark")

def _(uni_or_glyphname):
    if type(uni_or_glyphname) is int:
        if uni_or_glyphname > 0xffff:
            return "U+%06X" % uni_or_glyphname
        else:
            return "U+%04X" % uni_or_glyphname
    else:
        return "'%s'" % uni_or_glyphname

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

    copy_map = {}
    copy_map_reverse = {}
    umap = open("sourceFonts/utf32-jp.map", "r")
    l = umap.readline()
    while l != "":
        a = l.split("\t")
        mat = re.match(r"<([0-9a-fA-f]+)>", a[0])
        uni = int(mat.group(1), 16)
        enc = int(a[1])
        copy_map[uni] = enc
        x = copy_map_reverse.get(enc)
        if x is None:
            x = []
        x.append(uni)
        copy_map_reverse[enc] = x
        l = umap.readline()
    umap.close()

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
            locl = False
            for t in feat:
                if t[0] == "liga":
                    liga = True
                    break
                if t[0] == "locl":
                    locl = True
                    break
            if liga:
                log("%s: .. Skipped standard liga (because mintty applies)" %
                    (srcfont.fontname))
                continue
            if locl:
                log("%s: .. Skipped local form (have no much meaning)" %
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
        enc = g.encoding
        uni = copy_map_reverse.get(enc)
        subkey = uni
        if uni is None:
            not_in_unicode[enc] = False
            subkey = [g.glyphname]

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
            for key in subkey:
                m[key] = subtdata
            subtable_data[subtname] = m

    flg = False
    for subtname in subtable_data:
        subtmap = subtable_data[subtname]
        for base in subtmap:
            data = subtmap[base]
            x = data.copy()
            x.append(base)
            for i in range(0,len(x)):
                name = x[i]
                if type(name) is str:
                    try:
                        g = srcfont[name]
                        uni = copy_map_reverse.get(g.encoding)
                        if uni is None:
                            not_in_unicode[g.encoding] = True
                        else:
                            data[i] = uni[0]
                    except TypeError:
                        flg = True
                        log("%s: .. %s does not found" %
                            (srcfont.fontname, nane))

    if flg:
        exit(1)

    fp = open("ocami-subt.log", "w")
    for subtname in subtable_data:
        subtmap = subtable_data.get(subtname)
        if subtmap is None: continue
        print("%s:" % subtname, file = fp)
        for base in subtmap:
            s = "  %s: " % _(base)
            x = None
            data = subtmap[base]
            for i in range(0,len(data)):
                gid = data[i]
                if x is None:
                    x = ""
                else:
                    x += ", "
                x = "%s" % _(gid)
            if not x is None:
                s += "[" + x + "]"
            print(s, file = fp)
    fp.close()

    log("%s: Creating glyphs for substitutions/ligatures..." %
        (srcfont.fontname))
    tgfst = None
    tglst = None
    lenc = None
    srcfont.selection.none()
    for enc in not_in_unicode:
        if not not_in_unicode[enc]: continue
        if not lenc is None and lenc >= enc:
            srcfont.copy()
            target.selection.select(("ranges",),tgfst,tglst)
            target.paste()
            srcfont.selection.none()
            tgfst = None
            tglst = None

        g = srcfont[enc]
        nam = g.glyphname
        gu = target.createChar(-1,nam)
        uni = gu.encoding
        if tgfst is None: tgfst = uni
        tglst = uni
        log("%s: .. Creating U+%x for %s" % (srcfont.fontname, uni, nam))
        srcfont.selection.select(("more",),enc)
        lenc = enc

    log("%s: Copying glyphs..." % (srcfont.fontname))
    srcfont.copy()
    target.selection.select(("ranges",),tgfst,tglst)
    target.paste()

    lenc = None
    luni = None
    n = 0
    ns = 0
    srcfont.selection.none()
    target.selection.none()
    for uni in copy_map:
        enc = copy_map[uni]
        try:
            g = srcfont["Identity.%d" % (enc)]
        except TypeError:
            log("%s: .. %d is not found" % (srcfont.fontname, enc))
            continue

        if lenc:
            if lenc >= enc or luni >= uni:
                lenc = None
                luni = None
                srcfont.copy()
                target.paste()
                ns = ns + n
                log("%s: .. Copying %d glyphs..." % (srcfont.fontname, n))
                srcfont.selection.none()
                target.selection.none()
                n = 0;

        lenc = enc
        luni = uni
        srcfont.selection.select(("more",),enc)
        target.selection.select(("more","unicode"),uni)
        n = n + 1

    if n > 0:
        log("%s: .. Copying %d glyphs..." % (srcfont.fontname, n))
        srcfont.copy()
        target.paste()
        ns = ns + n

    log("%s: .. %d glyphs copied" % (srcfont.fontname, ns))

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
            l = copy_map_reverse.get(uni)
            if not l is None:
                for x in l:
                    unilst.append((x,uni))

        for uni in tabsrc:
            g = None
            try:
                g = target[uni]
            except:
                log("%s: .. %s were not copied" % (srcfont.fontname, _(uni)))
                continue

            lst = tabsrc[uni]
            alst = []
            inf = None
            for li in lst:
                gx = target[li]
                alst.append(gx.glyphname)
                if inf is None:
                    inf = _(li)
                else:
                    inf += ", " + _(li)

            log("%s: sub %s -> [%s]" % (srcfont.fontname, _(uni), inf))

            if subttype == "gsub_single":
                g.addPosSub(subtname, alst[0])
            elif subttype == "gsub_ligature" or subttype == "gsub_alternate":
                g.addPosSub(subtname, tuple(alst))
            else:
                log("%s: .. Subtable type %s is not supported." %
                    (srcfont.fontname, subttype))
                exit(1)

    merge_designer(srcfont, target)
    merge_copyright(srcfont, target)
    merge_trademark(srcfont, target)
    merge_description(srcfont, target)
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

    merge_designer(srcfont, target)
    merge_copyright(srcfont, target)
    merge_trademark(srcfont, target)
    merge_description(srcfont, target)
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

def check_font(target):
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

    log("Checking glyphs...")
    flg = False
    for i in warned_list:
        try:
            m = target[i]
        except:
            flg = True
            log("Glyph U+%04x does not exist" % i)
    if flg:
        exit(1)

    fw = ASCENT + DESCENT
    for g in target.glyphs():
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

    # Clear copyright field (new font has been set copyright from username)
    build.appendSFNTName(0x409, 0, "")
    build.appendSFNTName(0x411, 0, "")

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
                                  (0x2000,0x20cf), # Puct, Sup/Sub, Currency
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

    # https://docs.microsoft.com/en-us/typography/opentype/spec/name
    tag = {
        "Copyright": 0,
        "Family": 1,
        "Styles": 2,
        "UniqueID": 3,
        "Fullname": 4,
        "Version": 5,
        "PostscriptName": 6,
        "Trademark": 7,
        "Manufacturer": 8,
        "Designer": 9,
        "Descriptor": 10,
        "Vendor URL": 11,
        "Designer URL": 12,
        "License": 13,
        "License URL": 14,
        # "Reserved": 15,
        "Preferred Family": 16,
        "Preferred Styles": 17,
        "Compatible Full": 18,
        "Sample Text": 19,
        "CID findfont name": 20,
        "WWS Family": 21,
        "WWS Subfamily": 22,
        "Light Background": 23,
        "Dark Background": 24,
        "Variations PostScript Prefix": 25
    }

    cpl = get_SFNTtag(build, "Copyright")
    lic = re.sub(r"@@.*@@", cpl, LICENSE)

    cpl = COPYRIGHT + "\n" + cpl

    fp = open("dist/OFL.txt", "w", encoding = "utf-8")
    fp.write(lic)
    fp.close()

    # build.appendSFNTName(0x411,0, COPYRIGHT)
    # build.appendSFNTName(0x411,1, _f.get('family'))
    # build.appendSFNTName(0x411,2, _f.get('style_name'))
    # build.appendSFNTName(0x411,3, "")
    # build.appendSFNTName(0x411,4, _f.get('name'))
    # build.appendSFNTName(0x411,5, "Version " + VERSION)
    # build.appendSFNTName(0x411,6, _f.get('family') + "-" + _f.get('weight_name'))
    # build.appendSFNTName(0x411,7, "")
    # build.appendSFNTName(0x411,8, "")
    # build.appendSFNTName(0x411,9, "")
    # build.appendSFNTName(0x411,10, "")
    # build.appendSFNTName(0x411,11, "")
    # build.appendSFNTName(0x411,12, "")
    # build.appendSFNTName(0x411,13, LICENSE)
    # build.appendSFNTName(0x411,14, LICENSE_URL)
    # build.appendSFNTName(0x411,15, "")
    # build.appendSFNTName(0x411,16, _f.get('family'))
    # build.appendSFNTName(0x411,17, _f.get('style_name'))
    build.appendSFNTName(0x409,0, cpl)
    build.appendSFNTName(0x409,1, _f.get('family'))
    build.appendSFNTName(0x409,2, _f.get('style_name'))
    build.appendSFNTName(0x409,3, VERSION + ";misc;" + _f.get('family') + "-" + _f.get('style_name'))
    build.appendSFNTName(0x409,4, _f.get('name'))
    build.appendSFNTName(0x409,5, "Version " + VERSION)
    build.appendSFNTName(0x409,6, _f.get('name'))
    # build.appendSFNTName(0x409,7, "")
    # build.appendSFNTName(0x409,8, "")
    # build.appendSFNTName(0x409,9, "")
    # build.appendSFNTName(0x409,10, "")
    # build.appendSFNTName(0x409,11, "")
    # build.appendSFNTName(0x409,12, "")
    build.appendSFNTName(0x409,13, lic)
    build.appendSFNTName(0x409,14, LICENSE_URL)
    # build.appendSFNTName(0x409,15, "")
    # build.appendSFNTName(0x409,16, _f.get('family'))
    # build.appendSFNTName(0x409,17, _f.get('style_name'))

    check_font(build)

    fontpath = "dist/%s" % _f.get("filename")
    log("Writing %s..." % fontpath)
    build.generate(fontpath)
    # build.save(fontpath + ".sfd")
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

    if len(args) > 0:
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
