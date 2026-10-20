"""Stage-1 manual screening decisions on the 547-record pool (ids from data/clean/screen-pool.csv).
IFT = kept for full-text check (title/abstract suggests Bengaluru lake water-quality measurements). Everything else gets a reason code
assigned by keyword rules (documented below) -> data/clean/screening-log.csv"""
import pandas as pd, re
R = r"D:\Research-Publishing\13-bengaluru-lakes"
pool = pd.read_csv(R + r"\data\clean\screen-pool.csv")
IFT = set("""6 7 13 18 19 22 23 24 26 27 30 32 33 34 35 37 38 40 41 42 43 44 45 46 47 48 49 51 52 53 54 56 57 58 60 61 62 63 66 67 68 72 75 77 78 79 80 81 82 84 89 90 93 94 95 99 100 102 104 105 107 108 109 111 112 116 118 121 122 123 128 132 133 136 137 138 141 142 143 147 149 151 154 156 159 164 165
172 174 175 176 177 178 191 192 193 198 199 203 205 207 210 211 216 221 224 229 230 233 234 239 241 242 244 247 255 256 257 260 268 269 274 276 287 288 290 291 292 295 296 298 304 308 311 313 314 318 327 330 332 333 335 339 341 344 347 348 351 352 355 356 361 366 369 374 378 384 392 395 403 404 405 407 409 411 412 413 418 419 421 427 429 431 435 437 440 441 443 444 445 453 462 464 465 468 469 470 473 474 477 487 492 496 497 500 502 510 514 524 528 529 533 539 543 545 546 547
15 25 31 50 55 70 86 87 92 96 98 103 106 114 115 119 120 124 125 129 130 131 134 139 144 145 146 150 152 155 161 162 179 183 184 185 186 187 194 195 196 197 201 208 213 214 215 220 223 227 232 236 238 245 248 249 250 254 259 262 263 266 267 272 278 281 282 285 294 297 299 302 303 306 310 315 316 317 321 323 334 342 343 345 346 353 357 358 359 363 364 367 368 370 371 373 377 380 383 385 387 388 389 390 391 393 394 396 397 399 400 401 402 406 408 410 414 415 416 417 420 422 423 424 425 426 428 430 432 433 436 438 439 442 446 447 448 449 451 452 454 455 456 457 458 459 460 461 463 466 467 471 472 475 476 478 479 480 481 482 483 484 485 486 488 489 490 491 493 494 495 498 499 501 503 504 505 506 507 508 509 511 512 513 515 516 517 518 519 520 521 522 523 525 526 527 530 531 532 534 535 536 537 538 540 541 542 544""".split())
# Second block (ids after the first two lines) are lower-probability titles: kept ONLY IF the abstract/title still hits Bengaluru lake + measurement words (rule below)
FIRST = set("""6 7 13 18 19 22 23 24 26 27 30 32 33 34 35 37 38 40 41 42 43 44 45 46 47 48 49 51 52 53 54 56 57 58 60 61 62 63 66 67 68 72 75 77 78 79 80 81 82 84 89 90 93 94 95 99 100 102 104 105 107 108 109 111 112 116 118 121 122 123 128 132 133 136 137 138 141 142 143 147 149 151 154 156 159 164 165
172 174 175 176 177 178 191 192 193 198 199 203 205 207 210 211 216 221 224 229 230 233 234 239 241 242 244 247 255 256 257 260 268 269 274 276 287 288 290 291 292 295 296 298 304 308 311 313 314 318 327 330 332 333 335 339 341 344 347 348 351 352 355 356 361 366 369 374 378 384 392 395 403 404 405 407 409 411 412 413 418 419 421 427 429 431 435 437 440 441 443 444 445 453 462 464 465 468 469 470 473 474 477 487 492 496 497 500 502 510 514 524 528 529 533 539 543 545 546 547""".split())
SECOND = IFT - FIRST
MEAS = r"physico|physicochemical|water quality|\bbod\b|dissolved oxygen|nutrient|nitrate|phosph|heavy metal|metals|coliform|trophic|eutroph|wqi|water quality index|limnolog|pollution|sewage|toxic|uranium|surfactant|foam|hardness|alkalinity|conductiv|\bcod\b"
BLR = r"bengaluru|bangalore|bellandur|varthur|hebbal|ulsoor|sankey|lalbagh|madiwala|jakkur|yelahanka|kengeri|puttenahalli|byramangala|agara|nagawara|ullal|herohalli|anchepalya|kommaghatta|ramasandra|avalahalli|andrahalli|hosakote|dorekere|tattekere|mavathuru|bheemanakuppe|lingadheeranahalli|chikkabanavara"
rows = []
for _, r in pool.iterrows():
    rid = str(r.id); t = (str(r.title) + " " + str(r.abstract)).lower(); ti = str(r.title).lower()
    if rid in FIRST:
        dec, why = "full-text check", ""
    elif rid in SECOND and re.search(BLR, t) and re.search(MEAS, t) and not re.search(r"groundwater|ground water|vegetable|soil only|fish|endophyt|bacteri", ti):
        dec, why = "full-text check", ""
    else:
        dec = "exclude"
        if not re.search(BLR, t): why = "X1 not Bengaluru (no Bengaluru/lake name in title/abstract)"
        elif re.search(r"groundwater|ground water|borewell|tanker|household|potable|drinking", ti): why = "X3 groundwater/drinking-water only"
        elif re.search(r"fish|zooplankton|diatom|bird|spider|macrophyte|endophyt|bacteri|microb|cattle|erythrocyte|hematolog|labeo|tilapia|oreochromis|biodiversity|avifauna|nematode|algae|phytoplankton|biomarker|microplastic|vegetable|soil|crop", ti): why = "X3 biota/soil/other-matrix focus (no surface-water measurement evident in title)"
        elif re.search(r"remote sensing|sentinel|landsat|gis|land use|lulc|flood|satellite|geospatial|spatiotemporal|spatio-temporal", ti): why = "X2 remote sensing/land-use/hydrology (no in-situ water-quality values evident)"
        elif re.search(r"govern|polic|social|commons|stewardship|community|participat|political|politics|livelihood|gentrif|ecosystem services|perception|socio|esg|justice|inclusiv", ti): why = "X2 governance/social science (no measurements)"
        else: why = "X8 title/abstract screen: not a lake water-quality measurement study"
    rows.append(dict(id=r.id, key=r.key if "key" in r else "", title=r.title, year=r.year, doi=r.doi, venue=r.venue, decision=dec, reason=why, oa_url=r.oa_url, sources=r.sources))
out = pd.DataFrame(rows); out.to_csv(R + r"\data\clean\screening-pool-decisions.csv", index=False)
print(out.decision.value_counts()); print(out[out.decision == "exclude"].reason.str[:3].value_counts())
