# Nashville City Cemetery

The city of Nashville provides a dataset of known burials in city cemeteries from 1846 through 1979. https://docs.google.com/spreadsheets/d/13Nu6ScrK6FC1EnCaCeYddLTRbIc4S5JE/edit?usp=sharing&ouid=117851103307096970737&rtpof=true&sd=true

We are going to use the assistance of VSC + Github Copilot to help us clean and organize the data.  During this process we will pay close attention to the tasks in which Copilot can be used to save time but more importantly, we want to see tasks in which Claude falls short and will require oversight.

1. We want to use Claude to handle some of this tedious task.  Ask Claude if it can examine the Cause of Death column and fix some spelling errors and group some Cause of Deaths together.  (Example liver cancer and lung cancer can both be grouped as cancer and heart disease and heart attack can be grouped together.   However we don't want Scarlet Fever and Yellow Fever grouped because they are different diseases with a common symptom).  You can tell Claude to ask you for more details when you write your prompt. When Claude is done cleaning and grouping you can instruct it to add the updated Cause of Death into a new column named "Cause of Death Updated"

2. Use Copilot to help find the top 10 known causes of death from your updated column.  You can compare results with other students.  Differences could be due to chance or a slightly different prompt.

3. Use Copilot to find it there were any years that had a spike in the number of burials.  Ask Claude for an explanation for the results. Does the explanation make sense?  Do the number used as supporting evidence make sense?

4. There seems to be a spike during the Civil War, ask Claude if the Civil War had any impact of the age of those being buried.  Do the values and explanation make sense?

5. Use Copilot to make a new column named 'decade' next to the Year column.  Use this format - 1840's

6. Use Copilot to make a new column named 'age group' next to age.  You want children 5 or less listed as child, 6-17 listed as minors, 18-30 listed as young adults, 31-50 as middle aged, and older than 50 will be older adults.  If there is and blank for age fill in the age group value as unknown.

7. Use Copilot to make a visualization that shows the count of burials and most common burial decade for each age group.  Was there anything interesting in these results? What is Claude's interpretation?

8. Use Copilot to count for the number of burials by age group for each year of the 1860's.  Was there anything interesting in these results?  What is Claude's interpretation?

9. Finally, ask Claude to help build a PowerBI dashboard. You can either choose a focus or allow Claude to choose important metrics.  
