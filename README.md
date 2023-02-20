# HAHKC League Table

The [Handball Association of Hong Kong](http://handball.org.hk/) provides match results and league tables on their website, but the match data is only available in PDF format and the league table is updated infrequently. So I wrote this script, which does the following:

- Scrapes the official Hong Kong Handball Association website to get the latest link to the fixture PDF.
- Extracts the match results from the PDF and cleans the data.
- Calculates the league table for each division based on the results.

## Example
### Input
[League Timetable](
http://handball.org.hk/2_Competition/2018-2019/%e8%81%af%e8%b3%bd/(190)%202018_LAEGUE_TIMETABLE_2020.08.15.pdf) (15 Aug 2020 version)

### Output
男甲 1 組
| Team | Matches Played | Goal Difference | Points |
|-----------|-----------|-----------|-----------|
| 南華 | 18 | 216 | 35 |
| EVOSA | 17 | 137 | 29 |
| 精薈體育 | 17 | 77 | 28 |
| SCAA | 16 | 69 | 22 |
| 元朗區體育會 | 17 | 13 | 19 |
| 威濤 | 17 | -76 | 14 |
| 東區 | 17 | -62 | 8 |
| 順利天主教 | 18 | -109 | 8 |
| MAGIC | 18 | -178 | 6 |
| HKG GIANTS | 17 | -197 | 3 |