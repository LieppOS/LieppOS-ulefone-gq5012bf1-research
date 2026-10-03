# Remaining differences vs stock

There are **none at the function, data or ABI level.** Every function and
data object is byte-exact, and imports, modversions, modinfo, vermagic and
section sizes all match. See `parity/*.tsv`.

Out of scope for static closure, to be checked during runtime qualification:

- physical code→unit tables for raw fields that the driver only copies from
  DT;
- board wiring, which needs a schematic.

Neither affects the driver source.
