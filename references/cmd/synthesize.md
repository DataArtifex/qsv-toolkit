# qsv synthesize

<small>v20.1.0</small>

```text
Generates a synthetic CSV that is statistically faithful to a source CSV.

`synthesize` analyzes <input> with `stats` and `frequency`, then emits N rows of
fake data that reproduce the source's per-column attributes:

  * Categorical / low-cardinality columns are reproduced by frequency-weighted
    sampling of their *real* value set — cardinality, weights and repetition
    structure are preserved exactly.
  * Numeric and date/datetime columns are reproduced with quartile buckets, so
    the shape of the distribution (not just its [min,max] range) is preserved.
  * Null ratios are reproduced per column.

When a Data Dictionary is supplied (via --dictionary, or generated on the fly
with --infer-content-type), each column's semantic Content Type picks a
realistic faker (names, emails, addresses, UUIDs, etc.) for columns that are
NOT fully enumerated by `frequency`. For bounded-cardinality faker columns
(cardinality < requested rows and below an internal cap of 100,000), a fixed
pool of distinct fake values is pre-generated and sampled from, so the column's
cardinality is preserved. For very high cardinality columns above this cap, a
fresh fake value is generated per row instead — distinct count is approximate
in that case.

When `stats` provides string-length statistics (min_length / max_length /
avg_length / stddev_length) AND the column is routed to an unstructured text
generator (lorem_*, free_text, or the no-faker fallback), synthesized values
are truncated so their character lengths follow Normal(avg_length,
stddev_length) clamped to [min_length, max_length]. This applies to unstructured
pooled values as well — a low-cardinality free-text column still gets its
generated pool entries truncated. Structured semantic fakers (email, name,
uuid, phone, address parts, etc.) ignore these stats — truncating them would
corrupt their format, so their pools are reproduced verbatim. Frequency-
enumerated values are always reproduced verbatim and are never truncated.

When the Data Dictionary declares `relationships`, the named columns are
generated *jointly* so inter-column structure survives into each output row:

  * joint      — categorical / functional-dependency groups (e.g.
                 city/state/zip). Whole value-tuples are sampled from the
                 source by frequency, so only real co-occurring combinations
                 are emitted.
  * ordered    — columns that must keep a monotonic order within a row (e.g.
                 created_date <= closed_date). The anchor column is generated
                 from its own distribution; each later column is the anchor
                 plus a non-negative gap drawn from the gap distribution
                 learned from the source.
  * correlated — numeric columns whose correlation should be preserved. A
                 Gaussian copula couples the columns while leaving each
                 column's own distribution unchanged.

Relationships are read from the dictionary's `relationships` array — inferred
by `describegpt` or hand-authored. Columns not named by any relationship are
still generated independently. Pass --no-relationships to disable relationship
modeling entirely.

With --seed, output is fully reproducible.

Examples:

  # Pure statistical synthesis — no dictionary needed
  $ qsv synthesize data.csv -n 1000 --seed 42 > synthetic.csv

  # First, generate the Data Dictionary with describegpt
  $ qsv describegpt data.csv --dictionary --infer-content-type --format JSON -o dict.json
  # Then layer in semantic fakers from the dictionary
  $ qsv synthesize data.csv --dictionary dict.json -n 1000 > synthetic.csv

  # Let synthesize build the dictionary itself (needs an LLM API key)
  $ qsv synthesize data.csv --infer-content-type -n 1000 > synthetic.csv

  # Preserve inter-column relationships declared in the dictionary
  # (e.g. city/state/zip, created_date <= closed_date)
  $ qsv synthesize data.csv --dictionary dict.json -n 1000 > synthetic.csv

For more examples, see https://github.com/dathere/qsv/blob/master/tests/test_synthesize.rs.

Usage:
    qsv synthesize [options] <input>
    qsv synthesize --help

synthesize options:
    --dictionary <file>    Data Dictionary JSON file produced by
                           `describegpt --dictionary --infer-content-type --format JSON`.
                           Layers semantic Content Types onto generation. If
                           omitted, generation is purely type/frequency-based.
    --infer-content-type   Generate the Data Dictionary on the fly by invoking
                           `describegpt --dictionary --infer-content-type` on
                           <input>. Requires an LLM API key (QSV_LLM_APIKEY).
                           Ignored if --dictionary is given.
    -n, --rows <n>         Number of synthetic rows to generate. [default: 100]
    --seed <n>             RNG seed for fully reproducible output.
    --locale <loc>         Locale for faker-backed columns. Case-insensitive.
                           Supported: en, fr_fr, de_de, it_it, pt_br, pt_pt,
                           ja_jp, zh_cn, zh_tw, ar_sa, cy_gb, fa_ir, nl_nl,
                           tr_tr. Sparse locales (those without per-category
                           data in fake-rs) silently fall back to en data for
                           the missing categories — e.g. lorem text under a
                           non-en locale is still English, since only zh_cn
                           has localized lorem data. [default: en]
    --freq-limit <n>       Frequency pool depth passed to the internal `frequency`
                           run as --limit. A column is reproduced via exact
                           frequency-weighted sampling only when its cardinality
                           is fully captured within this limit; higher values
                           reproduce more columns verbatim. 0 means unlimited.
                           [default: 100]
    --stats-options <arg>  Extra options appended to the internal `stats` run.
                           Note: cardinality, quartiles and date inference are
                           always enabled — do not re-specify them here.
    --consistent-fakes     For structured-faker columns with bounded cardinality
                           (cardinality fully captured by `frequency`), build a
                           stable source-value -> fake-value mapping so the same
                           source value always produces the same fake in the
                           output. Preserves the source frequency distribution
                           and overrides the default "emit real values when
                           frequency-enumerated" behavior for structured fakers
                           (names, emails, addresses, etc.). Has no effect on
                           unstructured columns (lorem_*, free_text, unknown),
                           all-unique columns, or non-faker columns. Useful for
                           deidentified synthesis where you want stable joins
                           on the faked columns.
    --no-relationships     Disable inter-column relationship modeling. Every
                           column is generated independently even when the
                           dictionary declares a `relationships` array.
    --joint-cardinality-cap <n>  Maximum number of distinct value-tuples a
                           `joint` relationship may have. A joint group above
                           this cap falls back to independent generation (or
                           aborts under --strict-relationships). 0 means
                           unlimited. [default: 100000]
    --correlation-threshold <f>  Minimum absolute Spearman correlation for a
                           pair of columns to stay in a `correlated`
                           relationship. Weakly-correlated members are dropped.
                           [default: 0.3]
    --strict-relationships  Abort instead of warning-and-degrading when a
                           declared relationship fails validation.
    -j, --jobs <arg>       Number of jobs to use for the internal `stats` and
                           `frequency` runs.

Common options:
    -h, --help             Display this message
    -o, --output <file>    Write output to <file> instead of stdout.
    -d, --delimiter <arg>  The field delimiter for reading the input CSV.
                           Must be a single character. (default: ,)
```
