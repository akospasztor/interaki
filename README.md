# Interaki

Interaki is a variation of the [Inter](https://rsms.me/inter/) font, focusing on
clarity and distinction. The name combines Inter with Aki, a Japanese name
associated with brightness and clarity.

## Modifications

Interaki has the following variations enabled by default:

| Feature | Description                     |
| ------- | ------------------------------- |
| `cv05`  | Lower-case `L` with tail        |
| `cv07`  | Alternate German double s (`ß`) |
| `ss03`  | Round quotes & commas           |

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
| `--extras`        | also convert the fonts in the `extras` and `web` folders |
| `-h`, `--help`    | show the help message of the script                      |
| `-o`, `--output`  | Output folder; if not specified defaults to: `dist`      |
| `-v`, `--verbose` | Show the full log, including every remapped glyph        |

### Prebuilt fonts

Every push to this repository builds the fonts, including the extras, with
GitHub Actions. The results can be downloaded as the `Interaki-v<version>`
artifact of a workflow run on the
[Actions page](https://github.com/akospasztor/interaki/actions).

Inter is a trademark of [Rasmus Andersson](https://rsms.me/)
([RSMS](https://learn.microsoft.com/en-us/typography/vendors/#r)).
