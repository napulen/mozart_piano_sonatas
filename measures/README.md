## Columns

The TSVs in this folder each hold information about every measure of one movement. This information is necessary for keeping track of the different numberings `mc` and `mn`, for computing the repeat structure, and for knowing about special bar lines such as `double`.

The data type `Int64` stands for integer columns containing NULL values.

The column `presence` shows with which parameters of `mozart_loader.py` the column is present, where `raw` means that the column is present in the raw data and will be output with `-M`.


| column | type | presence | description |
|----------------------|-----------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **mc** | integer | raw | Measure count, identifier for the measure units in the XML encoding. Always starts with 1 for correspondence to MuseScore's status bar. |
| **mn** | integer | raw | Measure number, continuous count of complete measures as used in printed editions. Starts with 1 except for pieces beginning with a pickup measure, numbered as 0. |
| **playthrough** | integer | u | For the unfolded representations, a running count of complete measures disambiguating repeated MNs. |
| **keysig** | integer | raw | Key signature as the amount of accidentals. Sharps as positive, flats as negative integers. `1` = G major / E minor; `-1` = F major / D minor. |
| **timesig** | string | raw | Time signature of the measure. |
| **act_dur** | fraction | raw | Actual duration of the `mc` expressed as fraction of a whole note (`1/4` = quarter note). |
| **offset** | fraction | raw | Distance of `mc` from beat 1 of the corresponding complete measure `mn`, expressed as fraction of a whole note. |
| **voices** | integer | raw | Number of notational layers occurring in this `mc`. |
| **repeats** | string | raw | Repeat signs and/or indicators for the first and the last measure. Serves to compute the repeat structure. |
| **volta** | Int64 | raw | Disambiguates endings: `1` for first endings, `2` for second endings. |
| **barline** | string | raw | Barline style on the right of the `mc`, as encoded by MuseScore. |
| **numbering_offset** | Int64 | raw | Number to be added to this and all subsequent `mn`s, determined by the "Add to bar number" functionality in MuseScore. |
| **dont_count** | Int64 | raw | If `1`, this `mc` is not counted as the next `mn`. Otherwise NULL. Determined by the "Exclude from bar count" functionality in MuseScore and used for upbeat measures (also within the piece), second endings, cadencas spanning several bars etc. |
| **next** | collection or integer | raw | One or several `mc`s that can follow this `mc`. If there are several measures that may follow (in the case of repetions), the integers are separated by `, ` (comma + space). In case the unfolded parameter `-u` is being used, this column holds integers only because repetitions are disambiguated. |
