# Scopus and Web of Science strings (ready to paste; not run - no login)

Scopus (TITLE-ABS-KEY):
```
TITLE-ABS-KEY ( ( bengaluru OR bangalore OR bangaluru ) AND ( lake OR lakes OR tank OR tanks OR wetland OR wetlands ) AND ( "water quality" OR pollution OR eutrophication OR "dissolved oxygen" OR bod OR physicochemical OR "physico-chemical" OR sewage OR nutrient OR coliform OR "heavy metal*" ) )
```
```
TITLE-ABS-KEY ( ( bellandur OR varthur OR ulsoor OR halasuru OR hebbal OR sankey OR lalbagh OR agara OR madiwala OR jakkur OR yelahanka OR puttenahalli OR kaikondrahalli OR nagawara OR hennur OR kengeri OR hesaraghatta ) AND ( lake OR tank OR wetland ) AND ( water OR pollut* OR foam* OR froth* ) )
```
```
TITLE-ABS-KEY ( ( bellandur OR varthur ) AND ( foam* OR froth* OR fire OR surfactant* OR "heavy metal*" ) )
```
Web of Science (Topic, TS=):
```
TS=((bengaluru OR bangalore OR bangaluru) AND (lake OR lakes OR tank OR tanks OR wetland*) AND ("water quality" OR pollut* OR eutrophic* OR "dissolved oxygen" OR BOD OR physicochemical OR "physico-chemical" OR sewage OR nutrient* OR coliform OR "heavy metal*"))
```
```
TS=((Bellandur OR Varthur OR Ulsoor OR Hebbal OR Sankey OR Lalbagh OR Agara OR Madiwala OR Jakkur OR Yelahanka OR Puttenahalli OR Kaikondrahalli OR Nagawara OR Kengeri OR Hesaraghatta) AND (lake* OR tank*) AND (water OR pollut* OR foam* OR froth*))
```
If exports are placed in `scopus-drop\` (CSV/BibTeX), `python/bib_analysis.py` can be extended to merge them (not implemented: folder empty).
