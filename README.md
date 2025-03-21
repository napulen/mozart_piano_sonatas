![GitHub repo size](https://img.shields.io/github/repo-size/DCMLab/mozart_piano_sonatas)
![GitHub all releases](https://img.shields.io/github/downloads/DCMLab/mozart_piano_sonatas/total?color=%252300&label=Downloaded%20ZIPs)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-9cf)


# The Annotated Mozart Sonatas: Score, Harmony, and Cadence
Scores, chord labels and cadence labels for Mozart's 18 piano sonatas, following the [Neue Mozart Ausgabe](https://dme.mozarteum.at/DME/nma).

This dataset is accompanied by the data report `Hentschel, J., Neuwirth, M. and Rohrmeier, M., 2021. The Annotated Mozart Sonatas: Score, Harmony, and Cadence. Transactions of the International Society for Music Information Retrieval, 4(1), pp.67–80. DOI:` [http://doi.org/10.5334/tismir.63](http://doi.org/10.5334/tismir.63)

_An updated version of the dataset and the Python script are in preparation and will be released a couple of days from here (May 19th). The folder `scores` will be renamed to `MS3`. The column `onset` will be renamed to `mc_onset`. The annotation labels will appear under the left hand and in MuseScore's Roman Numeral Layer. The `mozart_loader.py` will be using the Python library [ms3](https://pypi.org/project/ms3) and appear with a couple of bugs corrected._

## TOC

- [Data Formats](#data-formats)
  - [Opening TSV files](#opening-tsv-files)
- [Accessing the Data](#accessing-the-data)
  - [Raw Data](#raw-data)
  - [Accessing Harmony Features](#accessing-harmony-features)
  - [Repetitions](#repetitions)
  - [Transposing everything to C](#transposing-everything-to-c)
- [How to correctly load the TSV files into pandas](#how-to-correctly-load-the-tsv-files-into-pandas)
- [How to get to different representations of chord tones](#how-to-get-to-different-representations-of-chord-tones)
  - [Scale Degrees & Roman Numerals](#scale-degrees--roman-numerals)
  - [Intervals & Relative Chromatic Pitch Classes](#intervals--relative-chromatic-pitch-classes)
  - [Note Names](#note-names)
    - [Tonal Pitch Classes in the note lists](#tonal-pitch-classes-in-the-note-lists)
  - [Storing and Retrieving Pitch-Based String Representations](#storing-and-retrieving-pitch-based-string-representations)
  - [Data types for parsing the data](#data-types-for-parsing-the-data)
    - [Data types](#data-types)
    - [Converters/Parsers](#convertersparsers)
- [Creating master table](#creating-master-table)
- [Creating all TSV files](#creating-all-tsv-files)
- [Questions, Suggestions, Corrections, Bug Reports](#questions-suggestions-corrections-bug-reports)
- [Licenses](#licenses)


## Data Formats

Every sonata movement is represented by five files with identical filenames in five different folders. For example, the first movement of the first sonata K. 279 has the following files:

* `scores/K279-1.mscx`: Uncompressed MuseScore file including the music and harmony labels.
* `notes/K279-1.tsv`: A table of all notes contained in the score and their relevant features.
* `measures/K279-1.tsv`: A table with relevant information about the measures in the score.
* `harmonies/K279-1.tsv`: A list of the included harmony labels with their positions in the score.
* `cadences/K279-1.tsv`: A list of cadence labels and their positions.

The README in each folder contains information about the respective files.

### Opening TSV files

Tab-separated value (TSV) files are like Comma-separated value (CSV) files and can be opened with most modern text editors. However, for correctly displaying the columns, you might want to use a spreadsheet or an addon for your favourite text editor. When you use an spreadsheet such as Excel, it might annoy you by interpreting fractions as dates. This can be circumvented by using `Data --> From Text/CSV` or the free alternative [LibreOffice Calc](https://www.libreoffice.org/download/download/). Other than that, TSV data can be loaded with every modern programming language.

## Accessing the Data

The included script `mozart_loader.py` lets you conveniently create an augmented representation of the data. First, create a local copy of this repository, either by using the command `git clone https://github.com/DCMLab/mozart_piano_sonatas.git` or by unpacking this [ZIP file](https://github.com/DCMLab/mozart_piano_sonatas/archive/master.zip). After navigating to your local copy, you can simply run the script by typing `python mozart_loader.py`. The script requires Python >= 3.6 with `pandas` >=  0.24.0 installed.

### Raw Data

> Run `python mozart_loader.py -h` to see the overview of available options.

The script's most simple functionality concatenates all TSV files from the folders and stores them as single files:

* `-N` concatenates the note matrices
    * `-NT` merges notes that are being tied together, leaving only those representing an onset, with merged durations aggregated
* `-M` concatenates the measure matrices
* `-H` concatenates the harmony labels
* `-C` concatenates the cadence labels

In case you want to join harmony labels with notes and/or cadence labels in a single file, add `-j` for joining. The basic representation of all data in a single file is yielded by `python mozart_loader.py -NHCMj`.

When joining the notes with labels, the latter often appear duplicated, namely once for every note with the identical onset. All notes that do not coincide with a label have NULL values in the concerning columns. This can be circumvented using the parameter `-p` which propagates the labels (and their features), thus identifying all notes that fall in their range.

### Accessing Harmony Features

The harmony labels follow the [DCML standard for harmonic annotation](https://github.com/DCMLab/standards) and can be split into feature columns.

* Using the option `-e` on the script will perform this expansion for you and spread the encoded information over the DataFrame, e.g. information about global and local keys.
* If you want to transpose all labels to the global tonic, thus eliminating the information about local keys, use `-g`.
* The chord tones expressed by the labels can be additionally computed by using `-E` instead of `-e`. They are expressed as integer intervals representing the number of stacked perfect fifths over the tonic, i.e., `0` is the tonic, `1` the dominant, `2` the supertonic, `-1` the subdominant, etc.
  * If the parameter `-g` is set, all chord tones are expressed as intervals (stacks of fifths) over the *global* tonic.
  * Otherwise, they represent intervals (stacks of fifths) over the chord's *local* tonic.
  * Or you can have all chord tones represent absolute pitches, based on the global key. In that case they display intervals (stacks of fifths) over the tone C = `0`, making G = `1`, F = `-1` etc.

All options can be combined with the above-mentioned functionality for data joining. The thickest data representation would be yielded using `python mozart_loader.py NHCEpj`. Except if you add:

### Repetitions

By default, all data is being returned as though playing every section only once, i.e. without first endings (without *prima volta*). Instead, you may choose the 'unfolded' version that duplicates notes and labels depending on the piece's repeat structure. Simply add `-u` to the parameters. This puts first and second endings in their correct positions, thus creating correct transitions and event counts that are closer to what is actually being performed. This option adds the column `playthrough` which counts complete measures in `mn` style but counting "through" instead of repeating measure numbers.

### Transposing everything to C

The option `-A` lets you rebase all pitches on C which corresponds to a transposition of every piece to C major or C minor. It is a special case of the (maximal) parameter combination `-CHNEpj`: The result is a DataFrame that represents the note list of all pieces merged with cadence labels and fully expanded chord labels which both have been propagated over the note lists. The difference is that all global keys are changed to `C` or `c` with the columns `tpc` (tonal pitch class) and `midi` transposed accordingly. The chord tones correspond to the representation of parameter `-g` but without transposing the chord labels (unless you add `-g`).

## How to correctly load the TSV files into pandas

Since the TSV files contain null values, lists, fractions, and numbers that are to be treated as strings, you may want to use this code to load any TSV files related to this repository, processed or not:

```python
from utils.feature_matrices import load_tsv

############################################################################
# For a file created using `python mozart_loader.py -CHNjuE`
############################################################################
tsv = './formatted/-CHNMjpuE_joined.tsv'

############################################################################
# If you have pandas >= 1.0.0 installed and want to use the new nullable
# string type, set stringtype=True.
############################################################################
df = load_tsv(tsv, stringtype=False)
```

## How to get to different representations of chord tones

For convenience a function for converting the chord tones into other representations
is available. Here are a couple of examples. They show different representations for
this small segment of the Adagio from K. 280:
![mozart score example from K280-2](https://www.epfl.ch/labs/dcml/wp-content/uploads/2020/04/280-2.png)

The function `transform_note_columns()` receives a TSV file created by `mozart_loader.py [-E][-g][-a]`
and outputs it with an altered representation of the chord tones.

### Scale Degrees & Roman Numerals

The first showcase begins with the "normal" chord tones, i.e., those expressed relative
to the respective local tonic as output by `mozart_loader.py -E`. The parameter `sd`
converts them to scale degrees, `rn` to Roman numerals. In both cases, `transform_note_columns()`
automatically uses the boolean column `localkey_is_minor` to compute mode-dependent
scale degrees.

```python
from utils.feature_matrices import load_tsv
from utils.expand_labels import transform_note_columns

df = load_tsv('./formatted/-E_harmonies.tsv')
transform_note_columns(df, 'sd')
```

This example output shows only the most relevant columns:

|globalkey|localkey|chord |     chord_tones     |root|bass_note|
|---------|--------|------|---------------------|----|---------|
|f        |III     |I     |(1, 3, 5)            |   1|        1|
|f        |III     |V65/vi|(5#, 7, 2, 3)        |   3|       5#|
|f        |III     |vi    |(6, 1, 3)            |   6|        6|
|f        |III     |ii6   |(4, 6, 2)            |   2|        4|
|f        |III     |V(64) |(5, 1, 3)            |   5|        5|
|f        |III     |V7    |(5, 7, 2, 4)         |   5|        5|

When the same chords are expressed relative to the global tonic by using
`mozart_loader.py -Eg`, the local keys are eliminated. In order to compute correct
scale degrees or Roman numerals for the chord tones, the boolean column `globalkey_is_minor`
needs to be used:

```python
df = load_tsv('./formatted/-Eg_harmonies.tsv')
transform_note_columns(df, 'sd', minor_col='globalkey_is_minor')
```

|globalkey| chord |     chord_tones     |root|bass_note|
|---------|-------|---------------------|----|---------|
|f        |III    |(3, 5, 7)            |   3|        3|
|f        |V65    |(7#, 2, 4, 5)        |   5|       7#|
|f        |i      |(1, 3, 5)            |   1|        1|
|f        |iv6    |(6, 1, 4)            |   4|        6|
|f        |VII(64)|(7, 3, 5)            |   7|        7|
|f        |VII7   |(7, 2, 4, 6)         |   7|        7|

Instead, we could decide to view all chord tones as scale degrees of a major mode
by using the keyword argument `minor=False`. Additionally, the next example uses
the `note_cols` argument to transform only the `chord_tones` to Roman numerals,
leaving the other columns untouched (as stacks of fifths over the global tonic).

```python
df = load_tsv('./formatted/-Eg_harmonies.tsv')
transform_note_columns(df, 'rn', note_cols=['chord_tones'], minor=False)
```

|globalkey| chord |        chord_tones        |root|bass_note|
|---------|-------|---------------------------|----|---------|
|f        |III    |(IIIb, V, VIIb)      |  -3|       -3|
|f        |V65    |(VII, II, IV, V)   |   1|        5|
|f        |i      |(I, IIIb, V)         |   0|        0|
|f        |iv6    |(VIb, I, IV)         |  -1|       -4|
|f        |VII(64)|(VIIb, IIIb, V)      |  -2|       -2|
|f        |VII7   |(VIIb, II, IV, VIb)|  -2|       -2|

### Intervals & Relative Chromatic Pitch Classes

This representation simply converts the 'stacks of fifths' intervals to specific
interval names or to relative chromatic pitch classes where 0 is the tonic. In the
two examples, the local keys have once again been preserved:

```python
df = load_tsv('./formatted/-E_harmonies.tsv')
transform_note_columns(df, 'iv')
```

|globalkey|localkey|chord |      chord_tones       |root|bass_note|
|---------|--------|------|------------------------|----|---------|
|f        |III     |I     |(P1, M3, P5)      |P1  |P1       |
|f        |III     |V65/vi|(A5, M7, M2, M3)|M3  |A5       |
|f        |III     |vi    |(M6, P1, M3)      |M6  |M6       |
|f        |III     |ii6   |(P4, M6, M2)      |M2  |P4       |
|f        |III     |V(64) |(P5, P1, M3)      |P5  |P5       |
|f        |III     |V7    |(P5, M7, M2, P4)|P5  |P5       |

```python
transform_note_columns(df, 'pc')
```

|globalkey|localkey|chord | chord_tones |root|bass_note|
|---------|--------|------|-------------|---:|--------:|
|f        |III     |I     |(0, 4, 7)    |   0|        0|
|f        |III     |V65/vi|(8, 11, 2, 4)|   4|        8|
|f        |III     |vi    |(9, 0, 4)    |   9|        9|
|f        |III     |ii6   |(5, 9, 2)    |   2|        5|
|f        |III     |V(64) |(7, 0, 4)    |   7|        7|
|f        |III     |V7    |(7, 11, 2, 5)|   7|        7|

### Note Names

In order to express the chords as absolute pitches, the chord tones first need
to be transposed to the absolute key which can be done using `mozart_loader.py -a`.

```python
df = load_tsv('./formatted/-a_harmonies.tsv')
transform_note_columns(df, 'name')
```

|globalkey|localkey|chord |      chord_tones      |root|bass_note|
|---------|--------|------|-----------------------|----|---------|
|f        |III     |I     |(Ab, C, Eb)      |Ab  |Ab       |
|f        |III     |V65/vi|(E, G, Bb, C)  |C   |E        |
|f        |III     |vi    |(F, Ab, C)       |F   |F        |
|f        |III     |ii6   |(Db, F, Bb)      |Bb  |Db       |
|f        |III     |V(64) |(Eb, Ab, C)      |Eb  |Eb       |
|f        |III     |V7    |(Eb, G, Bb, Db)|Eb  |Eb       |

If, instead, you use the globalkey chord labels for a note name representation,
this would correspond to a transposition of the whole piece to the key of C (major
or minor), as output as well using `mozart_loader.py -A`.

```python
df = load_tsv('./formatted/-Eg_harmonies.tsv')
transform_note_columns(df, 'name')
```

|globalkey| chord |     chord_tones      |root|bass_note|
|---------|-------|----------------------|----|---------|
|f        |III    |(Eb, G, Bb)     |Eb  |Eb       |
|f        |V65    |(B, D, F, G)  |G   |B        |
|f        |i      |(C, Eb, G)      |C   |C        |
|f        |iv6    |(Ab, C, F)      |F   |Ab       |
|f        |VII(64)|(Bb, Eb, G)     |Bb  |Bb       |
|f        |VII7   |(Bb, D, F, Ab)|Bb  |Bb       |

Using the original labels and chord tones (`mozart_loader.py -E`) would correspond to a transposition to
C (major or minor) of each segment in a particular local key. In other words,
all `I` chords will appear as `(C, E, G)` (in major and minor keys) but all `III`
chords, for example, will appear as `(Eb, G, Bb)` for local minor keys and as
`(E, G#, B)` for local major keys.

|globalkey|localkey|chord |     chord_tones     |root|bass_note|
|---------|--------|------|---------------------|----|---------|
|f        |III     |I     |(C, E, G)      |C   |C        |
|f        |III     |V65/vi|(G#, B, D, E)|E   |G#       |
|f        |III     |vi    |(A, C, E)      |A   |A        |
|f        |III     |ii6   |(F, A, D)      |D   |F        |
|f        |III     |V(64) |(G, C, E)      |G   |G        |
|f        |III     |V7    |(G, B, D, F) |G   |G        |

#### Tonal Pitch Classes in the note lists

Naturally, you can also represent the pitches of the note lists of the actual scores
as note names, e.g. the simple note list of all sonatas created using `mozart_loader.py -N`:

```python
df = load_tsv('./formatted/-N_notes.tsv')
transform_note_columns(df, 'name', note_cols=['tpc'])
```

The first five notes in the first sonata `K279-1` with their note names:

|mc |mn |onset|duration|tpc|midi|
|--:|--:|----:|-------:|--:|---:|
|  1|  1|    0|1/16    |C  |  48|
|  1|  1|    0|1/4     |E  |  64|
|  1|  1|    0|1/4     |G  |  67|
|  1|  1|    0|1/4     |C  |  72|
|  1|  1|1/16 |1/16    |C  |  60|

### Storing and Retrieving Pitch-Based String Representations

The convenience function `load_tsv()` is hard-coded to the data types that `mozart_loader.py`
produces. This would cause an error if you tried to use it on a TSV file where the
chord tones have been converted to a pitch based representation (note names, scale
degrees, roman numerals, or interval names). This small example shows how the converters
and datatypes that the function uses can be updated. It uses a note list with joined
harmonies and chord tones produced by `mozart_loader.py -Naj`.

```python
from utils.feature_matrices import load_tsv, str2strtuple, iterable2str
from utils.expand_labels import transform_note_columns

df = load_tsv('./formatted/-Naj_joined.tsv')

# Converting the (absolute) chord tones and the pitches of the notes to note names
absolute_chord_tones = transform_note_columns(df, 'name')
absolute_pitches = transform_note_columns(absolute_chord_tones, 'name', note_cols=['tpc'])

# Converting the tone tuples to strings before saving the DataFrame to TSV
tone_tuples = ['chord_tones', 'added_tones']
absolute_pitches.loc[:, tone_tuples] = absolute_pitches.loc[:, tone_tuples].applymap(iterable2str)
absolute_pitches.to_csv('absolute_pitches.tsv', sep='\t')

# re-loading the stored TSV while updating the converters and data types for the altered columns
reloaded = load_tsv('absolute_pitches.tsv', converters={'chord_tones': str2strtuple, 'added_tones': str2strtuple}, dtypes={'root': str, 'bass_note': str, 'tpc': str}, )
```

### Data types for parsing the data

The function `load_tsv` uses the following data types and converters to load the individual columns.

#### Data types

The data type `Int64` designates columns that contain integers *and* NULL values. The column `function` serves as a quick reminder for the meaning of column names which are not self-evident. The column `occurrence`
shows which of the individual TSV files the columns can occur and, consequently, in which README you
find information about the column (**N**otes, **H**armonies, **C**adences, **M**easures)

| column           | function                                             | type    | occurrence |
|------------------|------------------------------------------------------|---------|------------|
| alt_label        | alternative chord label                              | string  | H          |
| barline          |                                                      | string  | M          |
| bass_note        |                                                      | Int64   | H          |
| cadence          |                                                      | string  | C          |
| cadences_id      |                                                      | Int64   | C          |
| changes          | chord alterations, suspensions, additions etc.       | string  | H          |
| chord            | part of the chord label that defines the chord tones | string  | H          |
| chord_type       |                                                      | string  | H          |
| dont_count       | concerns measure numbering                           | Int64   | M          |
| figbass          | chord inversion                                      | string  | H          |
| form             | chord form                                           | string  | H          |
| globalkey        | global reference key of a piece                      | string  | H          |
| gracenote        |                                                      | string  | N          |
| harmonies_id     |                                                      | Int64   | H          |
| keysig           | key signature of a measure                           | integer | M          |
| label            | complete chord label                                 | string  | H          |
| localkey         | local reference key                                  | string  | H          |
| mc               | measure count                                        | integer | NHM        |
| midi             |                                                      | integer | H          |
| mn               | measure number                                       | integer | NHCM       |
| notes_id         |                                                      | Int64   | N          |
| numbering_offset | concerns measure numbering                           | Int64   | M          |
| numeral          | Roman numeral (chord root)                           | string  | H          |
| pedal            |                                                      | string  | H          |
| phraseend        |                                                      | string  | H          |
| playthrough      | unique measure numbers for unfolded scores           | integer | NHCM       |
| relativeroot     | lower-reference key from which a chord is borrowed   | string  | H          |
| repeats          |                                                      | string  | M          |
| root             | root expressed as interval                           | Int64   | H          |
| special          | shorthand chord symbols                              | string  | H          |
| staff            |                                                      | integer | N          |
| tied             |                                                      | Int64   | N          |
| timesig          | time signature                                       | string  | NHCM       |
| tpc              | tonal pitch class                                    | integer | N          |
| voice            | in which notational layer a note occurs              | integer | N          |
| voices           | number of notational layers in a measure             | integer | M          |
| volta            | for identifying first and second endings             | Int64   | M          |

#### Converters/Parsers

The collections are stored in the TSV files as strings in which the different elements
are separated by the string `, ` (comma and space). The boolean values are stored as
0 or 1. The fractions are stored either as integers or in the format `3/4`.

| column             | converter  | occurrence |
|--------------------|------------|------------|
| added_tones        | collection | H          |
| act_dur            | fraction   | M          |
| chord_tones        | collection | H          |
| globalkey_is_minor | boolean    | H          |
| localkey_is_minor  | boolean    | H          |
| next               | collection | M          |
| nominal_duration   | fraction   | N          |
| offset             | fraction   | M          |
| onset              | fraction   | NHC        |
| duration           | fraction   | N          |
| scalar             | fraction   | N          |

## Creating master table

    python mozart_loader.py -NECMjp


## Creating all TSV files

    ms3 extract -N ../notes -M ../measures -L ../harmonies -e ambig

## Questions, Suggestions, Corrections, Bug Reports

Please create an issue and feel free to fork and submit pull requests.

## Licenses

* **Data**: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/))
* **Software**: [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.txt)
