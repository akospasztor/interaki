#!/usr/bin/env python

"""Build the Interaki fonts from the original Inter release.

:author:    Akos Pasztor
:copyright: (c) 2026 Akos Pasztor, https://akospasztor.com
:license:   This software is licensed under terms that can be found in the
            LICENSE file in the root directory of this software component.
"""

import argparse
import logging
import os
from types import SimpleNamespace

from fontTools.ttLib import TTCollection, TTFont
from opentype_feature_freezer import RemapByOTL

# Interaki font version
VERSION = "1.0"

# Default output directory (if not specified)
DEFAULT_OUTPUT_DIR = "dist"

# Features to remap
FEATURES = [
    "cv05",  # Lower-case L with tail
    "cv07",  # Alternate German double s (ß)
    "ss03",  # Round quotes & commas
]

# Name IDs that carry the family name: family, unique ID, full name,
# PostScript name, typographic family, compatible full, PostScript CID
# findfont name, WWS family, variations PostScript name prefix.
RENAME_NAME_IDS = {1, 3, 4, 6, 16, 18, 20, 21, 25}

# Font files converted from the extras and web folders. Apart from CSS files,
# other files are skipped.
FONT_EXTENSIONS = (".ttf", ".otf", ".woff", ".woff2")


def remap_features(font: TTFont, features: list[str]) -> dict[str, str]:
    """Remap the font's cmap so the supplied features are on by default.

    .. note:: The font is modified in-place.

    :param font: Font to modify.
    :param features: OpenType feature tags to freeze.
    :return: The replaced glyphs, mapped to their alternates.
    :raises ValueError: If the font has no Unicode cmap, if any of the features
        is missing from the font, or if no glyphs were remapped.
    """
    font_name = font['name'].getDebugName(4)

    cmap = font.getBestCmap()
    if cmap is None:
        raise ValueError(f"{font_name} has no unicode cmap")
    before = dict(cmap)

    available = set()
    if "GSUB" in font:
        feature_records = font['GSUB'].table.FeatureList.FeatureRecord
        available = {record.FeatureTag for record in feature_records}
    missing = [feature for feature in features if feature not in available]
    if missing:
        raise ValueError(
            f"{font_name} is missing features: {', '.join(missing)}")

    # The font is handed over in memory, so the paths are never used for I/O.
    options = SimpleNamespace(
        inpath=font['name'].getDebugName(6),
        outpath="-",
        features=",".join(features),
        script=None,
        lang=None,
        names=False,
        report=False,
    )
    remapper = RemapByOTL(options)
    remapper.ttx = font
    remapper.remapByOTL()

    # remapByOTL() updates the cmap in place, so it now holds the new mapping.
    replaced = {}
    for u, glyph in before.items():
        if cmap[u] != glyph:
            replaced[glyph] = cmap[u]
    if not replaced:
        raise ValueError(
            f"{font_name} has the features, but no glyphs were remapped")
    return replaced


def set_font_name(font: TTFont, name: str) -> None:
    """Set the font name.

    This function updates the family, full and PostScript names in the name
    table (including the named instances of variable fonts), and in the CFF
    table of OTF fonts.

    .. note:: The font is modified in-place.

    :param font: Font to rename.
    :param name: New font family name to be set.
    """
    name_ids = set(RENAME_NAME_IDS)

    # Variable fonts also store a PostScript name for each named instance
    if "fvar" in font:
        name_ids |= {
            instance.postscriptNameID for instance in font['fvar'].instances
        }

    name_table = font['name']
    for record in name_table.names:
        if record.nameID in name_ids:
            name_table.setName(
                record.toUnicode().replace("Inter", name),
                record.nameID,
                record.platformID,
                record.platEncID,
                record.langID,
            )

    # OTF fonts keep a copy of the PostScript, family and full names in CFF.
    # Note: Table tags are always four characters, so the tag of the CFF table
    # is padded with a space: 'CFF '.
    if "CFF " in font:
        cff = font['CFF '].cff
        cff.fontNames = [n.replace("Inter", name) for n in cff.fontNames]
        top_dict = cff.topDictIndex[0]
        top_dict.FamilyName = top_dict.FamilyName.replace("Inter", name)
        top_dict.FullName = top_dict.FullName.replace("Inter", name)


def set_font_version(font: TTFont, version: str) -> None:
    """Set the font version.

    This function prepends the supplied version to the version string (name ID
    5) and the unique font identifier (name ID 3) and updates the font revision
    in the head table and the version in the CFF table of OTF fonts.

    .. note:: The font is modified in-place.

    :param font: Font to update.
    :param version: Version in the MAJOR.MINOR format.
    """
    # The minor version is padded to three digits, e.g. 1.2 -> 1.002, so the
    # font revision keeps increasing as a decimal number, e.g. 1.010 > 1.002.
    major, minor = version.split(".")
    revision = f"{major}.{int(minor):03d}"

    name = font['name']
    for record in name.names:
        if record.nameID == 5:
            original = record.toUnicode().removeprefix("Version ")
            text = f"Version {revision};Inter {original}"
        elif record.nameID == 3:
            text = f"{revision};{record.toUnicode()}"
        else:
            continue
        name.setName(text, record.nameID, record.platformID,
                     record.platEncID, record.langID)

    # The font revision is a 16.16 fixed-point number in the font file, but
    # fontTools takes the actual value and converts it: e.g. 1.500 is stored
    # as 0x00018000.
    font['head'].fontRevision = float(revision)  # type: ignore

    # OTF fonts keep a copy of the version in CFF
    # Note: Table tags are always four characters, so the tag of the CFF table
    # is padded with a space: 'CFF '.
    if "CFF " in font:
        top_dict = font['CFF '].cff.topDictIndex[0]
        if hasattr(top_dict, "version"):
            top_dict.version = version


def convert_font(font: TTFont) -> None:
    """Freeze the features, set the font name and set its version.

    .. note:: The font is modified in-place.

    :param font: Font to convert.
    :raises ValueError: If the features cannot be frozen, see
        :func:`remap_features`.
    """
    old_name = font['name'].getDebugName(4)
    remapped = remap_features(font, FEATURES)
    set_font_name(font, "Interaki")
    set_font_version(font, VERSION)
    print(f"  {old_name} -> {font['name'].getDebugName(4)} "
          f"({len(remapped)} glyphs remapped)")


def convert_file(file_path: str, output_dir: str) -> None:
    """Convert a single font file, e.g. Inter-Bold.otf to Interaki-Bold.otf.

    .. note:: The output keeps the format of the input file (TTF, OTF, WOFF or
        WOFF2).

    :param file_path: Path of the Inter font file.
    :param output_dir: Directory to write the converted file to. It is created
        if it does not exist.
    :raises ValueError: If the font cannot be converted, see
        :func:`convert_font`.
    """
    print(f"Processing {file_path} ...")
    filename = os.path.basename(file_path).replace("Inter", "Interaki")
    output = os.path.join(output_dir, filename)
    font = TTFont(file_path)
    convert_font(font)
    os.makedirs(output_dir, exist_ok=True)
    font.save(output)
    print(f"Saved {output}")


def convert_css(file_path: str, output_dir: str) -> None:
    """Convert a stylesheet, e.g. inter.css to interaki.css.

    This function renames the font families and the referenced font files to
    Interaki.

    :param file_path: Path of the Inter stylesheet.
    :param output_dir: Directory to write the converted stylesheet to. It is
        created if it does not exist.
    """
    print(f"Processing {file_path} ...")
    filename = os.path.basename(file_path).replace("inter", "interaki")
    output = os.path.join(output_dir, filename)
    with open(file_path, encoding="utf-8") as f:
        css = f.read()
    os.makedirs(output_dir, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(css.replace("Inter", "Interaki"))
    print(f"Saved {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inter_dir",
        help="path to the directory containing the original Inter font "
             "release files"
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help="output directory (if not specified, defaults to: "
             f"`{DEFAULT_OUTPUT_DIR}`)",
    )
    parser.add_argument(
        "-e",
        "--extras",
        action="store_true",
        help="convert the fonts and stylesheets in the `extras` and `web` "
             "folders",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show the full output log, including every remapped glyph",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=VERSION,
        help="show the version and exit",
    )
    args = parser.parse_args()

    # Only show errors by default. The opentype-feature-freezer  warns about
    # substitutions between glyphs without a codepoint (e.g. comma.numr ->
    # comma.numr.ss03), which cannot be frozen and are expected. In verbose
    # mode, the freezer's full log is shown.
    logging.basicConfig(level=logging.ERROR,
                        format="%(levelname)s: %(message)s")
    if args.verbose:
        logging.getLogger("opentype_feature_freezer").setLevel(logging.INFO)

    print(f"Building Interaki {VERSION}")
    print(f"Remapping features: {FEATURES}")
    os.makedirs(args.output, exist_ok=True)

    # Remap TTC font collection
    ttc_input = "Inter.ttc"
    ttc_output = os.path.join(args.output, "Interaki.ttc")
    collection = TTCollection(os.path.join(args.inter_dir, ttc_input))
    print(f"Processing {ttc_input} ...")
    for font in collection.fonts:
        convert_font(font)
    collection.save(ttc_output, shareTables=True)
    print(f"Saved {len(collection.fonts)} fonts to {ttc_output}")

    for filename in ("InterVariable.ttf", "InterVariable-Italic.ttf"):
        convert_file(os.path.join(args.inter_dir, filename), args.output)

    if args.extras:
        for folder in ("extras", "web"):
            for dirpath, dirnames, filenames in os.walk(
                os.path.join(args.inter_dir, folder)
            ):
                dirnames.sort()
                output_dir = os.path.join(
                    args.output, os.path.relpath(dirpath, args.inter_dir)
                )
                for filename in sorted(filenames):
                    file_path = os.path.join(dirpath, filename)
                    if filename.endswith(FONT_EXTENSIONS):
                        convert_file(file_path, output_dir)
                    elif filename.endswith(".css"):
                        convert_css(file_path, output_dir)
