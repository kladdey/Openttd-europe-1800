# Modica / Pozzallo — population provenance investigation

**Outcome: historical administrative relationship confirmed; population scope
not settled. Keep this single master entry documented and deferred.**

The upstream `mdlincoln/europop` repository describes its extracted files as a
transcription of Jan de Vries, *European Urbanization 1500–1800* (1984),
Appendix I. At commit `ce0810c4de6affd9e62a3c003fb6dfdd295ea7e7`,
[`data-raw/extracted/de_vries6.csv`](https://github.com/mdlincoln/europop/blob/ce0810c4de6affd9e62a3c003fb6dfdd295ea7e7/data-raw/extracted/de_vries6.csv)
contains this row (values in thousands):

```csv
City,Code,1500,1550,1600,1650,1700,1750,1800
MODICA/POZZALLO,12,UNK,15,18,16,19,20,20
```

The tidy population CSV retains that combined label and the 1800 value of 20.
The separate `city_coords.csv` places the combined label at 36.726334 N,
14.844019 E, near coastal Pozzallo. Modern published reference points for Modica
and Pozzallo are distinct (see V8's coordinate reference audit). A slash label
and a coastal coordinate do not establish how the 20,000 were counted.

The Italian Ministry of Culture's
[*Archivio di Stato di Ragusa e Sezione di Modica* catalogue](https://dgagaeta.cultura.gov.it/public/uploads/documents/Archivi%20Italiani/634d031e69426.pdf),
PDF page 28 (zero-based page 27), captions a copy of a royal decree dated
**12 June 1829**, Naples: Pozzallo, previously dependent on Modica, was made a
separate commune. The archive reference is **Sezione di Modica, Comune di
Modica, b.57**. This establishes an administrative relationship relevant to 1800;
it does not define the population unit used by de Vries.

I inspected the upstream transcription and the archive catalogue's decree
caption, **not the original printed de Vries table and its footnotes**. The
municipal-history page found in search could not be retrieved reliably during
this pass, so its quoted population figures are not used as verified evidence.
The transcription could itself contain an editorial aggregation or label choice.

It is plausible that Modica should represent the historical principal centre,
with Pozzallo retained as a separately documented port role. That is a proposed
interpretation, not a completed source join. Moving all of the game's population
to Modica or creating two towns would prematurely resolve that ambiguity.

Required next evidence: the original Appendix I page containing this entry,
its explanatory notes and any population-unit definitions, or an independently
sourced historical town population series that explicitly disambiguates it.
Then choose one justified centre for this source record, preserve its master
population, re-sample terrain and re-run proximity against Ragusa and Scicli.
A separately added port would need its own justified population and policy review.

The machine-readable [source trace](../../../data/geography/modica_source_trace_v9.json)
records the pinned upstream commit/blob and unchanged master record. Neither the
master nor the full V8 comparison import has been edited.
