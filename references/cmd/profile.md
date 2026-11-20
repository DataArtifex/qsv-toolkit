# qsv profile

<small>v29.0.0</small>

```text
Profile a CSV (local path or URL) and emit a `.metadata.json` file carrying
five top-level blocks:

  `dpp`        — inferred dataset signals: lat/lon/date columns, file size,
                 row count, encoding, etc. (the legacy datapusher-plus
                 inference block).
  `stats`      — per-column summary statistics from `qsv stats`.
  `frequency`  — per-column value counts from `qsv frequency`.
  `ckan`       — a CKAN-shaped block (package + resources) that
                 datapusher-plus consumes to prepopulate CKAN packages.
  `projection` — the dataset re-expressed in the active profile's metadata
                 vocabulary. Default is DCAT-US v3, emitted in its canonical
                 form: plain JSON with unprefixed keys and no `@context`,
                 validating against the schemas data.gov's own validator at
                 https://harvest.data.gov/validate/ runs. Bundled alternates are
                 dcat-ap-v3 (EU portals), croissant (ML/AI registries) and
                 geoconnex (water-data federations). Consumable directly by
                 data.gov harvesters, EU DCAT-AP catalogs, mlcommons /
                 Hugging Face / Kaggle, and Internet of Water tooling.

Behind the scenes qsv runs the same statistical + frequency analysis
datapusher-plus (DP+) runs in CKAN, builds a Jinja2 evaluation context from
the results, and — when an optional CKAN scheming YAML spec is supplied —
evaluates the spec's `formula` / `suggestion_formula` templates against that
context. Jinja2 helpers and filters are a native Rust port of DP+'s
`jinja2_helpers.py`, built on `minijinja`.

For DCAT-US v3 the projection also COMPUTES properties that are tedious to
author by hand, from the same statistics: temporal coverage and resolution
(an exact xsd:duration: a regular series' step, else recording precision),
spatial bounding box (excluding out-of-range and (0, 0) placeholder
coordinates) and resolution - from latitude/longitude columns or, without
them, a WKT `POINT (longitude latitude)` column - an update schedule (only for
a regular calendar series), the content language, DQV quality measurements
(completeness, plus duplicate rows and CSV/UTF-8 validity with `--validate`),
and a CSVW table schema with per-column constraints (required, ranges,
lengths, enumerations, primary key). Values
that are generated, detected or estimated rather than measured (a
description, the language, the schedule, the temporal and spatial resolution)
form an "inferred" tier that the publisher's own metadata replaces;
`projection_provenance` lists them (and LLM column annotations, which only an
override replaces). A generated
description carries a disclosure and a review warning, so it never passes
for a human-authored one.

When the input is a URL whose response carries DCAT markup (HTTP
`Link: rel=describedBy`), qsv discovers the publisher's stated metadata and
merges it as a base layer beneath the inferred projection.

For an example CKAN scheming YAML spec, see:
  https://github.com/dathere/datapusher-plus/blob/main/ckanext/datapusher_plus/dataset-druf.yaml

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_profile.rs.
See also https://github.com/dathere/qsv/wiki/Metadata-Profiling

Examples:

  # Quick: dpp/stats/frequency + default DCAT-US v3 projection.
  $ qsv profile data.csv

  # Pipe stdin; output defaults to `stdin.metadata.json`.
  $ cat data.csv | qsv profile

  # URL input: discover the publisher's DCAT markup and merge it as a base layer.
  $ qsv profile https://data.example.gov/datasets/sample.csv

  # Seed publisher/contact info from a JSON file; write to a chosen output path.
  $ qsv profile data.csv --initial-context publisher.json -o data.metadata.json

  # data.gov-style harvest: validate against DCAT-US v3 JSON Schema, abort on
  # mandatory-field violations, wrap in a Catalog envelope.
  $ qsv profile data.csv --validate --strict --catalog -o data.metadata.json

  # DCAT-AP v3 for EU data portals; `pyshacl` validates the bundled SHACL shapes.
  $ qsv profile open-data.csv --profile dcat-ap-v3 --validate --strict

  # Croissant JSON-LD for an ML dataset; `mlcroissant` validates the output.
  $ qsv profile train.csv --profile croissant --validate -o train.croissant.json

  # Geoconnex JSON-LD for hydrologic data (qsv built with the `geoconnex` feature).
  $ qsv profile gages.csv --profile geoconnex --validate --strict

  # Evaluate a CKAN scheming spec: Jinja2 formulas compute spatial/temporal
  # extents, accrual periodicity, and other derived fields.
  $ qsv profile data.csv --spec dataset-druf.yaml -o data.metadata.json

  # CKAN-only output: drop the `projection` block, keep dpp/stats/frequency/ckan.
  $ qsv profile data.csv --no-projection --spec dataset-druf.yaml

  # Custom YAML profile from disk (embedded names always win over same-named
  # files, so use a non-clashing name for custom profiles).
  $ qsv profile data.csv --profile ./my-org-dcat.yaml --validate

Usage:
    qsv profile [options] [<input>]
    qsv profile --help

profile argument:
    <input>                   Path or URL to the CSV to profile. When `-` or
                              omitted, reads from stdin.
                              When the URL has DCAT markup, qsv will attempt to
                              discover and ingest it as a base layer of metadata
                              (unless --no-dcat-discovery is set). See --no-dcat-discovery
                              and --dcat-discovery-timeout for details and opt-out.

profile options:
    --spec <yaml>             CKAN scheming YAML spec file. If omitted, only the
                              inferred `dpp` block (lat/lon/date columns, dataset
                              stats) is emitted; no formulas are evaluated.
    --initial-context <json>  JSON file providing seed values for the package /
                              resource dicts plus optional JSON-Pointer
                              overrides for the final projection block. Replaces
                              the older --package-meta / --resource-meta
                              flags. Top-level keys: `package`, `resource`,
                              `dataset_info`. Each leaf value may be wrapped
                              as {"value": ..., "force": true} to mark it as
                              overriding any value discovered from URL DCAT
                              markup AND any value qsv inferred. Force is
                              honored across all three subtrees: dataset_info
                              entries override their target path verbatim;
                              package / resource entries route through the
                              active profile's `field_mappings:` table (e.g.
                              `package.title force=true` lands at
                              `/projection/title`, beating inference and
                              discovery). Forced values for slots the profile
                              does not surface are silently dropped (no-op).
                              `dataset_info` keys are JSON Pointers into the
                              output (e.g. `/projection/title`): the value
                              replaces what is there, and missing objects
                              are created. Inside an array, use an existing
                              index, or a final `-` to append (e.g.
                              `/projection/hasQualityMeasurement/-` adds a
                              measurement after the computed ones). An
                              override that cannot be applied (not a
                              pointer, an index out of range, `-` with no
                              array to append to) is reported in
                              projection_warnings (or, with --no-projection,
                              on stderr) and fails --strict.
                              See tests/resources/profile/dcat-init-context.README.md
                              for a fully-populated example.
    --no-projection           Skip the metadata projection block (dcat/croissant/
                              geoconnex, depending on the active profile).
    --no-ckan                 Skip the CKAN-shape block.
    --croissant-frequency     Embed per-column value-frequency distributions in
                              the metadata projection. The croissant profile
                              renders them as inline cr:RecordSets (one
                              `<col>-frequency` RecordSet of {value, count,
                              percentage} rows per column), per the spec's
                              "distribution of values is a statistic on the
                              field" guidance. Off by default (keeps the
                              projection compact); the raw counts always remain
                              in the top-level `frequency` block regardless.
                              Other bundled profiles ignore this flag.
    --locate <mode>           Name the places the data covers, as DCAT-US v3
                              `spatial` Locations, by looking up the densest
                              coordinate cells (up to 40, row-weighted) with
                              `qsv geocode`. <mode> is one of:
                                geonames - label the bounding box with the
                                           place, admin1 or country that 80%
                                           of the sampled rows share (offline
                                           Geonames index).
                                census   - add each US state and county
                                           holding at least 5% of the sampled
                                           rows (the heaviest state always;
                                           up to 10 counties), keyed by
                                           Census GEOID (US
                                           Census Geocoder: online, keyless,
                                           cached). State and county
                                           columns, when they resolve, supply
                                           these instead, with or without
                                           coordinates, as they name every
                                           row exactly: states as USPS, FIPS
                                           or names; counties as names or
                                           GEOIDs, matched exactly within each
                                           row's state (TIGERweb county
                                           names). A name several counties
                                           share is noted, not guessed.
                                           A state column lists states only
                                           when at least 90% of its values
                                           are US states.
                                both     - geonames and census.
                              Also adds the coordinates' centroid. A lookup
                              that cannot run is noted in projection_warnings;
                              the bounding box is kept. Default: off.
    --describegpt <json>      Use a `qsv describegpt --format json` result as
                              LLM-inferred metadata (see also --infer). Its
                              Description becomes the description, its Tags
                              the keywords and its Dictionary labels and
                              descriptions annotate the CSVW columns - all as
                              inferred values, which supplied or discovered
                              metadata replaces. describegpt's attribution
                              footer moves to the `llm_attribution` block and
                              the description gets a one-line disclosure.
    --infer                   Run `qsv describegpt --all` on the input and use
                              its result as with --describegpt. The LLM is
                              configured through describegpt's QSV_LLM_*
                              environment variables. If it cannot run, a
                              warning is added and the statistics-based
                              description is used.
    --tag-vocab <file>        With --describegpt or --infer: a local
                              `tag,description` CSV (the format describegpt
                              uses for its own tag vocabulary). Only tags in it are
                              kept - describegpt only asks the LLM to keep to
                              the vocabulary - and they also become `theme`
                              Concepts carrying the vocabulary's description.
    --dcat-legacy-license     Also emit `license` on the Dataset, alongside
                              the Distribution-level copy. Both are valid
                              DCAT-US v3 (the Dataset-level property was
                              added upstream), but the migration guide
                              directs publishers to put license on each
                              Distribution, so that is what qsv emits by
                              default. Default: off.
    --no-dcat-discovery       Skip DCAT-markup discovery on URL inputs.
                              Discovery sniffs HTTP Link: rel=describedBy
                              (and, in future, sibling .metadata.json /
                              JSON-LD <script> blocks) to use the
                              publisher's stated metadata as a base layer.
    --dcat-discovery-timeout <secs>  Per-request timeout for DCAT-markup
                              discovery probes. Default: 5.
    --validate                Validate the emitted projection block against
                              the active profile's declared validators. For
                              dcat-us-v3 that's the vendored GSA JSON Schema
                              bundle (see resources/dcat-us-v3/); for
                              dcat-ap-v3 / geoconnex it's pyshacl over the
                              bundled SHACL shapes; for croissant it's
                              mlcroissant. Catches missing mandatory fields,
                              cardinality issues, and shape violations.
                              Violations append to projection_warnings by
                              default. Also runs `qsv validate` over the
                              input (CSV structure + UTF-8), so a passing
                              file is declared UTF-8 encoded and its
                              syntactic validity is recorded as a
                              quality measurement. A file that fails it
                              (or a pass that cannot run) also gets a
                              Required `syntacticValidity` warning.
                              Ignored, with a warning on stderr, when
                              combined with --no-projection.
    --strict                  Fail the command, instead of just warning,
                              when an --initial-context override cannot
                              be applied, and, with --validate, when the
                              input fails `qsv validate`, on
                              Required-severity schema violations or on
                              non-Info external-validator findings.
                              Severity comes
                              from the DCAT-US v3 schema's own
                              requirementLevel annotations, so a missing
                              mandatory property aborts while a
                              recommended-field advisory does not.
                              Note:
                              RFC4180 structural failures from
                              `qsv validate` (emitted when a spec
                              declares `validators`) are always
                              appended as warnings, regardless of this
                              flag.
    --allow-external-validator
                              Opt in to spawning the validator binary
                              declared by `validation.external` when the
                              profile was loaded from an arbitrary YAML
                              file. Bundled profiles (dcat-us-v3,
                              dcat-ap-v3, croissant, geoconnex) always run
                              their declared external validators because
                              the profile content is vetted at qsv release
                              time. Without this flag, file-loaded
                              profiles emit a Recommended-severity
                              warning instead of running the binary, so
                              an untrusted YAML can't silently execute
                              arbitrary commands. Default: off.
    --catalog                 Wrap the emitted DCAT-US v3 Dataset inside a
                              Catalog envelope (Catalog{dataset:[...]}).
                              Useful for federation harvesters (data.gov,
                              CKAN ingest) that expect Catalog-shaped
                              top-level metadata. Default: off
                              (Dataset-only, backwards-compatible).
    --profile <name|path>     Metadata projection profile to use. Embedded
                              names: dcat-us-v3 (default), dcat-ap-v3,
                              croissant; geoconnex (when built with the
                              `geoconnex` feature, which no prebuilt binary
                              includes: build qsv with
                              `-F feature_capable,geoconnex`, or qsvdp
                              with `-F datapusher_plus,geoconnex`).
                              A path to a custom YAML profile is also
                              accepted; embedded names always win over
                              same-named files. See
                              resources/profiles/README.md for the schema
                              and authoring guide.
    --force                   Force recomputing cardinality and unique values
                              even if a stats cache file exists.
    -j, --jobs <arg>          The number of jobs to run in parallel for the
                              underlying stats/frequency passes. When not set,
                              the number of jobs is set to the number of CPUs
                              detected.
    -o, --output <file>       Output JSON path. Default: <input>.metadata.json.

Common options:
    -h, --help                Display this message
    -n, --no-headers          When set, the first row will not be interpreted
                              as headers. Namely, it will be processed with the
                              rest of the rows. Otherwise, the first row will
                              always appear as the header row in the output.
    -d, --delimiter <arg>     The field delimiter for reading CSV data.
                              Must be a single character.
    --memcheck                Check if there is enough memory to load the entire
                              CSV into memory using CONSERVATIVE heuristics.
```
