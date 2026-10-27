# Data

`nashville_city_cemetery_interments_1846_1979.csv` is the Nashville City Cemetery interment ledger, 1846–1979. The assignment README links to it as a Google Sheet ("The city of Nashville provides a dataset of known burials in city cemeteries from 1846 through 1979").

| | |
|---|---|
| Original file name | `Historic_Nashville_City_Cemetery_Interments__1846-1979.xlsx - Historic_Nashville_City_Cemeter.csv` (renamed here for convenience; contents unchanged) |
| Rows × columns | 19,745 × 14 |
| Burial years | 1846–1979 (2 rows have no year) |
| Size | 1.79 MB |
| md5 | `1fc59dc752d8c1ec10c0cff5aec09079` |

## Columns

| Column | What it holds |
|---|---|
| `Volume` | Source ledger. `4-1846` … `4-1860` and `5-1860` … `5-1881` are yearly ledgers. `6A` … `6Z` are later lettered volumes: 83% of their entries have a surname starting with the volume's letter, and 2,388 of their 2,389 entries date from 1879–1979 |
| `Name` | Name as written. Thousands of infants are recorded only as "Infant", "Inft.", "Infant Son", etc. |
| `Burial Month`, `Month No.`, `Burial Day`, `Burial Year` | Burial date (some parts blank) |
| `Sex` | Mostly `M` / `F`; a few other codes |
| `Race` | Mostly `W` / `B`; `D` appears only in 1869 and is not explained in the file |
| `Age` | Whole years as written; blank for 43.9% of rows |
| `Residence` | Mostly "City" |
| `Cause of Death/Burial` | Free text as written by the clerk: 2,210 distinct spellings |
| `Ave`, `Section/Lot` | Location in the cemetery |
| `Remarks` | Free text (family, lot owner, notes such as "f. m. c." = free man of color) |

Read it with `pd.read_csv(path, dtype=str, keep_default_na=False)` so that codes and blanks come through exactly as written; the notebook converts year and age to numbers itself.
