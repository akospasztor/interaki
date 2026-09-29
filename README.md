# Interaki

Interaki is a variation of the [Inter](https://rsms.me/inter/) font, focusing on
clarity and distinction. The name combines Inter with Aki, a Japanese name
associated with brightness and clarity.

## Modifications

Interaki has the following variations enabled by default:

| Feature | Description                     | Interaki                                                                                | Inter                                                                             |
| ------- | ------------------------------- | --------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `cv05`  | Lower-case `L` with tail        | <img src="img/illinois-interaki.png" alt="Illinois text with Interaki" height="50">     | <img src="img/illinois-inter.png" alt="Illinois text with Inter" height="50">     |
| `cv07`  | Alternate German double s (`ß`) | <img src="img/seestrasse-interaki.png" alt="Seestrasse text with Interaki" height="50"> | <img src="img/seestrasse-inter.png" alt="Seestrasse text with Inter" height="50"> |
| `ss03`  | Round quotes & commas           | <img src="img/quote-interaki.png" alt="Quote text with Interaki" height="100">          | <img src="img/quote-inter.png" alt="Quote text with Inter" height="100">          |

The features are frozen into the fonts, so they are active even in apps without
OpenType feature support.

## Usage

The fonts are built from the official Inter release with the `interaki.py`
script. It requires Python 3.10 or newer. Recommended usage is within a
virtualenv.

1. Install the dependencies:

   ```shell
   pip install -r requirements.txt
   ```

2. Download an official Inter release zip from the
   [Inter releases page](https://github.com/rsms/inter/releases) and unzip it,
   e.g. to `Inter-4.1/`.

3. Build the fonts:

   ```shell
   python interaki.py Inter-4.1
   ```

This converts the `Inter.ttc`, `InterVariable.ttf` and
`InterVariable-Italic.ttf`, and writes the `Interaki.ttc`,
`InterakiVariable.ttf` and `InterakiVariable-Italic.ttf` files to the `dist`
folder. Optionally, the fonts under the `extras` and `web` folders can also be
converted by specifying the `--extras` flag.

| Option            | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `-e`, `--extras`  | also convert the fonts in the `extras` and `web` folders |
| `-h`, `--help`    | show the help message of the script                      |
| `-o`, `--output`  | Output folder; if not specified defaults to: `dist`      |
| `-v`, `--verbose` | Show the full log, including every remapped glyph        |
| `--version`       | Show the Interaki version                                |

## Versioning

Interaki has its own `MAJOR.MINOR` version, independent of the Inter version it
is based on. The version is stored in the fonts with the minor version padded to
three digits, e.g. `1.0` as `1.000`. The version string of the fonts also
records the Inter version, e.g. `Version 1.000;Inter 4.001;git-9221beed3`.

| Interaki version | Based on Inter version | Changes                                               |
| ---------------- | ---------------------- | ----------------------------------------------------- |
| 1.0              | 4.1                    | Initial release with `cv05`, `cv07` and`ss03` enabled |

## Acknowledgements

Inter is a trademark of [Rasmus Andersson](https://rsms.me/)
([RSMS](https://learn.microsoft.com/en-us/typography/vendors/#r)).
