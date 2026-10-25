# Europe 1800 - spacing review, pass 1

## Scope and safeguards

- The **600-town master catalogue remains unchanged**.
- The existing playable scenario and five-city V2 calibration remain unchanged.
- This is a *test-only* import candidate and a *diagnostic-only* audit.
- **No town has been permanently deleted.**

## Provisional 13-town import candidate

The earlier 15-town local expansion had two uncomfortably crowded and ambiguous Paris satellites. This test candidate omits **VERSAILLES** and **BOULOGNE** from the *import file only*. Both remain in the 600-town master and 15-town comparison test. They can be reinstated if corrected geography and historical identity justify it. All other coordinates and populations are identical to the 15-town test. **Do not import into an existing populated scenario**; test in a fresh empty copy.

## Master catalogue proximity audit

Computed Euclidean distances from normalized x/y multiplied by 4096, for all 600 original entries. Flagged pairs: **27 under 15 tiles** and **113 between 15 and 30 tiles**. These coordinates are known to contain major geographic errors, so **these flags are not deletion decisions**. A pair may be falsely close, or two cities may be falsely far apart. The CSV provides a review queue only.

## Rules for future validated imports

1. Correct and verify positions against real geography first.
2. Under 15 tiles: normally keep the most important settlement; exception requires specific historic/gameplay justification.
3. 15–30 tiles: review individually for historic identity, industry, port function and regional importance.
4. 30+ tiles: generally retain, subject to geography.
5. Keep the master catalogue and previous tests untouched; only build new versioned candidate imports.

## Next calibration work

Independently calibrate Netherlands/Belgium, Channel ports, and Baltic coast using real map controls rather than applying the Paris or Berlin translation blindly. Validate screenshots before expanding further.
