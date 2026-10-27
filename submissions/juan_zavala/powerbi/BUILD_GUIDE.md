# Power BI build guide: Nashville City Cemetery, 1846–1979

This folder has everything needed to build the Question 9 dashboard in about 30–45 minutes. The design is already working in `../cemetery_dashboard.html`: open it in a browser first to see what the finished report should do.

**Focus:** who was buried, when, and of what. Two report pages:

1. **Overview:** burials per year with spikes, the top causes, and age groups by decade.
2. **The 1860's and the war:** the Question 4 and Question 8 views.

## What's in this folder

| File | What it is |
|---|---|
| `fact_burials.csv` | One row per burial (19,670 rows): year, decade, month, sex, race, age, age group, cause, cause family, era, ledger volume |
| `dim_year.csv` | Every year from 1846 to 1979 (134 rows, including the 6 years with no burials), with its decade and era |
| `dim_age_group.csv` | The six age groups in order, with their age ranges |
| `dim_cause.csv` | The 232 cleaned cause labels, each with its cause family and flags for "known" and "vague" |
| `measures.dax` | Every measure, written as one DAX query that also checks itself |
| `theme.json` | Colors and fonts that match the notebook charts |

All of these files are produced by `cemetery_analysis.ipynb` (Question 9), so they always match the notebook.

## Before you start: Mac or Windows?

Power BI Desktop runs only on Windows. On a Mac, use one of these:

- **A Windows computer** (a school lab PC, or a friend's), or Windows in a virtual machine such as Parallels. This is the easiest route, and the steps below assume it.
- **The Power BI service in a browser** (app.powerbi.com, with a school or work account). You can upload `fact_burials.csv` and build every visual from that one table. Relationships, sort-by-column and DAX measures need the data-model editor, which depends on your license and your school's settings. If it isn't available, use the built-in "Count of BurialID" instead of the `Burials` measure. You can still build every visual this way except the spike coloring.

## Step 1. Load the four CSV files (5 min)

1. **Home → Get data → Text/CSV**, then pick `fact_burials.csv` and click **Transform Data**.
2. Check the column types in Power Query. `Year`, `MonthNo`, `Age`, `AgeGroupOrder` and `BurialID` should be **Whole Number**, and every other column **Text**.
   - Watch `Volume`. Values like `4-1846` can be mistaken for dates, so it must stay **Text**.
   - Blank ages and years should load as `null`, not 0.
3. Repeat for `dim_year.csv`, `dim_age_group.csv` and `dim_cause.csv`. Their whole-number columns are `Year`, `DecadeStart` and `EraOrder` in `dim_year`, `SortOrder` in `dim_age_group`, and `Burials` in `dim_cause`. Everything else is **Text**.
4. Click **Close & Apply**.

## Step 2. Relationships and sort orders (5 min)

In **Model view**, make sure there are exactly these three relationships. Each one is many-to-one with single-direction filtering, from the dimension to the fact table. Power BI usually creates them by itself; delete any other relationship it adds.

| From (many) | To (one) |
|---|---|
| `fact_burials[Year]` | `dim_year[Year]` |
| `fact_burials[AgeGroup]` | `dim_age_group[AgeGroup]` |
| `fact_burials[Cause]` | `dim_cause[Cause]` |

Then set the sort orders. Select the column, then go to **Column tools → Sort by column**:

- `dim_age_group[AgeGroup]` by `SortOrder`. This gives child, minors, young adults, middle aged, older adults, unknown.
- `dim_year[Era]` by `EraOrder`.
- `dim_year[Decade]` by `DecadeStart`.

## Step 3. Measures, and the first check (5 min)

1. Open **DAX query view** (the `{ }` icon), paste all of `measures.dax`, and click **Run**.
2. Compare the results with the notebook:

   | Result | Should show |
   |---|---|
   | Spike years (tab 1) | 1849 (745), 1850 (809), 1863 (836), 1864 (1,372), 1865 (1,366), 1866 (1,354), 1873 (559) |
   | Headline numbers (tab 2) | 19,670 burials · 88.5% known cause · 44.0% no age recorded · peak year 1864 (1,372) · median recorded age 33 |

   If a number differs, check the relationships and column types before going on.
3. Click **Update model with changes**. All the measures are saved to `fact_burials`.
4. Format `% Known Cause`, `% No Age Recorded`, `% Cholera`, `% Young Adults`, `% Men Among Young Adults` and `Share of Age Group's Burials` as **Percentage, 1 decimal**.

## Step 4. Theme (1 min)

Go to **View → Themes → Browse for themes** and pick `theme.json`. The report background, fonts and default colors now match the notebook.

## Step 5. Page 1, "Overview" (15 min)

Use a 16:9 page. From top to bottom:

**Slicers** (one row across the top). Every slicer filters every visual on the page.

| Slicer | Field | Style |
|---|---|---|
| Decade | `dim_year[Decade]` | Dropdown |
| Age group | `dim_age_group[AgeGroup]` | Tile (buttons) |
| Sex | `fact_burials[Sex]` | Dropdown |
| Race | `fact_burials[Race]` | Dropdown |
| Cause family | `dim_cause[CauseFamily]` | Dropdown |

**KPI cards** (five, in a row): `Burials`, `% Known Cause`, `% No Age Recorded`, `Peak Year` and `Median Recorded Age`. Add `Peak Year Burials` as a second line on the peak-year card if you use the new card visual.

**Burials per year** (full width, column chart):
- X-axis: `dim_year[Year]`, type **Continuous**. Y-axis: `Burials`.
- Columns → Color → **fx** → Format style **Field value** → `Year Bar Color`. Spike years turn orange.
- Tooltips: `Baseline (5 prior years)`, `Excess Burials`, `Cholera Burials`.
- Title: "Burials per year (orange = spike: at least 1.5× and 50 more than the median of the 5 years before)".
- Optional: in the Filters pane, filter **this visual only** to `dim_year[Year]` 1846–1900. After 1900 no year has more than 41 burials, so the early years get more room.

**Top 10 known causes** (bar chart, left):
- Y-axis: `dim_cause[Cause]`. X-axis: `Known Cause Burials`.
- Filters on this visual: `dim_cause[IsKnown]` is `Yes`; `dim_cause[Cause]` **Top N = 10** by `Burials`.
- Bars → Color → **fx** → Field value → `Cause Bar Color`. Vague labels turn gray.

**Age group × decade** (matrix, right):
- Rows: `dim_age_group[AgeGroup]`. Columns: `dim_year[Decade]`. Values: `Share of Age Group's Burials`.
- Cell elements → **Background color** on, with a gradient from `#F4F8FE` (lowest) to `#184F95` (highest).
- Add a small table next to it with `dim_age_group[AgeGroup]`, `Burials` and `Most Common Decade`. This is Question 7's answer, and it changes with the slicers.

Age-group colors, if a visual is colored by age group (the same as the notebook):

| child | minors | young adults | middle aged | older adults | unknown |
|---|---|---|---|---|---|
| `#86B6EF` | `#5598E7` | `#2A78D6` | `#1C5CAB` | `#104281` | `#C9C7BF` |

## Step 6. Page 2, "The 1860's and the war" (10 min)

Duplicate page 1 so the slicers carry over, delete the visuals, then add:

**Burials by age group, 1860–1869** (Question 8):
- A column chart with X-axis `dim_year[Year]` (type **Categorical**) and Y-axis `Burials`. Put `dim_age_group[AgeGroup]` in **Small multiples**.
- Visual filter: `dim_year[Year]` between 1860 and 1869.
- Small multiples → **Y-axis scale: independent**, so the small groups stay readable.
- Tooltip: `Burials vs 1860`.

**Median recorded age before, during and after the war** (Question 4):
- A clustered bar chart with Y-axis `dim_year[Era]`, Legend `fact_burials[Race]` and X-axis `Median Recorded Age`.
- Visual filters:
  - `dim_year[Era]` is *Before the war (1856-60)*, *Civil War (1861-65)* or *After the war (1866-70)*.
  - `fact_burials[Race]` is *White* or *Black*.
- Next to it, add a table with `dim_year[Era]`, `fact_burials[Race]`, `Burials`, `Median Recorded Age`, `% Young Adults`, `% Men Among Young Adults` and `% No Age Recorded`. With no slicers set, the medians should match `results/civil_war_age.csv`:
  - White: 32, 32, 31
  - Black: 35, 27, 28

**A text box with the two cautions:**
- "Unknown" age is mostly infants (Question 6).
- 1869 comes from a single, likely incomplete ledger volume (Questions 3 and 8).

## Step 7. Check, save and share

- [ ] With no slicers set, the cards show 19,670 / 88.5% / 44.0% / 1864 / 33.
- [ ] Seven orange columns: 1849, 1850, 1863–1866 and 1873.
- [ ] The top 10 starts with Tuberculosis (consumption) at 1,843 and ends with Measles at 498, and Complications (unspecified) is gray.
- [ ] In the age group × decade table, child's most common decade is the 1850's and every other group's is the 1860's.
- [ ] Setting Race = Black recomputes the spikes for that group: 1849, 1850, 1863–1866, 1873 and 1874 turn orange. With Race = White, only 1849, 1850, 1863, 1864 and 1873 do.

Save as `cemetery_dashboard.pbix`. To share it, publish to the Power BI service (**Home → Publish**) or take a screenshot of each page for the README.

## Notes on the data (what a reader should know)

- **Blank age is "unknown", as the assignment asks, but 89.5% of those entries look like infants** ("Infant", "Still born", teething…). Read "unknown" as "mostly babies".
- **These are burials in one cemetery, not deaths in Nashville.** After 1870, other cemeteries took most burials.
- **1869 has only 209 rows, all from ledger volume 5-1869.** It looks like a partly transcribed volume, not a healthy year.
- **75 duplicate entries were removed.** They are lettered-book copies of 1879–1881 burials (see `results/duplicates_removed.csv`).
- **Cause labels come from `cause_of_death_rules.py`:** 2,209 spellings become 232 labels, and those are grouped here into 14 families plus Unknown.
