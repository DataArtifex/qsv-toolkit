# qsv geocode

```text
Geocodes a location in CSV data against an updatable local copy of the Geonames cities index
and a local copy of the MaxMind GeoLite2 City database.

The Geonames cities index can be retrieved and updated using the `geocode index-*` subcommands.

The GeoLite2 City database will need to be MANUALLY downloaded from MaxMind. Though it is
free, you will need to create a MaxMind account to download the GeoIP2 Binary database (mmdb)
from https://www.maxmind.com/en/accounts/current/geoip/downloads.
Copy the GeoLite2-City.mmdb file to the ~/.qsv-cache/ directory or point to it using the
QSV_GEOIP2_FILENAME environment variable.

When you run the command for the first time, it will download a prebuilt Geonames cities
index from the qsv GitHub repo and use it going forward. You can operate on the local
index using the `geocode index-*` subcommands.

By default, the prebuilt index uses the Geonames Gazeteer cities15000.zip file using
English names. It contains cities with populations > 15,000 (about ~26k cities). 
See https://download.geonames.org/export/dump/ for more information.

It has seven major subcommands:
 * suggest        - given a partial City name, return the closest City's location metadata
                    per the local Geonames cities index (Jaro-Winkler distance)
 * suggestnow     - same as suggest, but using a partial City name from the command line,
                    instead of CSV data.
 * reverse        - given a WGS-84 location coordinate, return the closest City's location
                    metadata per the local Geonames cities index.
                    (Euclidean distance - shortest distance "as the crow flies")
 * reversenow     - sames as reverse, but using a coordinate from the command line,
                    instead of CSV data.
 * countryinfo    - returns the country information for the ISO-3166 2-letter country code
                    (e.g. US, CA, MX, etc.)
 * countryinfonow - same as countryinfo, but using a country code from the command line,
                    instead of CSV data.
 * iplookup       - given an IP address or URL, return the closest City's location metadata
                    per the local Maxmind GeoLite2 City database.
 * iplookupnow    - same as iplookup, but using an IP address or URL from the command line,
                    instead of CSV data.
 * index-*        - operations to update the local Geonames cities index.
                    (index-check, index-update, index-load & index-reset)
 
SUGGEST
Suggest a Geonames city based on a partial city name. It returns the closest Geonames
city record based on the Jaro-Winkler distance between the partial city name and the
Geonames city name.

The geocoded information is formatted based on --formatstr, returning it in 
'%location' format (i.e. "(lat, long)") if not specified.

Use the --new-column option if you want to keep the location column:

Examples:
Geocode file.csv city column and set the geocoded value to a new column named lat_long.

  $ qsv geocode suggest city --new-column lat_long file.csv

Limit suggestions to the US, Canada and Mexico.

  $ qsv geocode suggest city --country us,ca,mx file.csv

Limit suggestions to New York State and California, with matches in New York state
having higher priority as its listed first.

  $ qsv geocode suggest city --country us --admin1 "New York,US.CA" file.csv

If we use admin1 codes, we can omit --country as it will be inferred from the admin1 code prefix.

  $ qsv geocode suggest city --admin1 "US.NY,US.CA" file.csv

Geocode file.csv city column with --formatstr=%state and set the 
geocoded value a new column named state.

  $ qsv geocode suggest city --formatstr %state --new-column state file.csv

Use dynamic formatting to create a custom format.

  $ qsv geocode suggest city -f "{name}, {admin1}, {country} in {timezone}" file.csv
  # using French place names. You'll need to rebuild the index with the --languages option first
  $ qsv geocode suggest city -f "{name}, {admin1}, {country} in {timezone}" -l fr file.csv

SUGGESTNOW
Accepts the same options as suggest, but does not require an input file.
Its default format is more verbose - "{name}, {admin1} {country}: {latitude}, {longitude}"

  $ qsv geocode suggestnow "New York"
  $ qsv geocode suggestnow --country US -f %cityrecord "Paris"
  $ qsv geocode suggestnow --admin1 "US:OH" "Athens"

REVERSE
Reverse geocode a WGS 84 coordinate to the nearest City. It returns the closest Geonames
city record based on the Euclidean distance between the coordinate and the nearest city.
It accepts "lat, long" or "(lat, long)" format.

The geocoded information is formatted based on --formatstr, returning it in
'%city-admin1' format if not specified.

Examples:
Reverse geocode file.csv LatLong column. Set the geocoded value to a new column named City.

  $ qsv geocode reverse LatLong -c City file.csv

Reverse geocode file.csv LatLong column and set the geocoded value to a new column
named CityState, output to a file named file_with_citystate.csv.

  $ qsv geocode reverse LatLong -c CityState file.csv -o file_with_citystate.csv

The same as above, but get the timezone instead of the city and state.

  $ qsv geocode reverse LatLong -f %timezone -c tz file.csv -o file_with_tz.csv

REVERSENOW
Accepts the same options as reverse, but does not require an input file.

  $ qsv geocode reversenow "40.71427, -74.00597"
  $ qsv geocode reversenow --country US -f %cityrecord "40.71427, -74.00597"
  $ qsv geocode reversenow --admin1 "US:OH" "(39.32924, -82.10126)"

COUNTRYINFO
Returns the country information for the specified ISO-3166 2-letter country code.

  $ qsv geocode countryinfo country_col data.csv
  $ qsv geocode countryinfo --formatstr "%json" country_col data.csv
  $ qsv geocode countryinfo -f "%continent" country_col data.csv
  $ qsv geocode countryinfo -f "{country_name} ({fips}) in {continent}" country_col data.csv

COUNTRYINFONOW
Accepts the same options as countryinfo, but does not require an input file.

  $ qsv geocode countryinfonow US
  $ qsv geocode countryinfonow --formatstr "%pretty-json" US
  $ qsv geocode countryinfonow -f "%continent" US
  $ qsv geocode countryinfonow -f "{country_name} ({fips}) in {continent}" US

IPLOOKUP
Given an IP address or URL, return the closest City's location metadata per the
local Geonames cities index.

  $ qsv geocode iplookup IP_col data.csv
  $ qsv geocode iplookup --formatstr "%json" IP_col data.csv
  $ qsv geocode iplookup -f "%cityrecord" IP_col data.csv

IPLOOKUPNOW
Accepts the same options as iplookup, but does not require an input file.

  $ qsv geocode iplookupnow 140.174.222.253
  $ qsv geocode iplookupnow https://amazon.com
  $ qsv geocode iplookupnow --formatstr "%json" 140.174.222.253
  $ qsv geocode iplookupnow -f "%cityrecord" 140.174.222.253

INDEX-<operation>
Manage the local Geonames cities index used by the geocode command.

It has four operations:
 * check  - checks if the local Geonames index is up-to-date compared to the Geonames website.
            returns the index file's metadata JSON to stdout.
 * update - updates the local Geonames index with the latest changes from the Geonames website.
            use this command judiciously as it downloads about ~200mb of data from Geonames
            and rebuilds the index from scratch using the --languages option.
            If you don't need a language other than English, use the index-load subcommand instead
            as it's faster and will not download any data from Geonames.
 * reset  - resets the local Geonames index to the default prebuilt, English-only Geonames cities
            index (cities15000) - downloading it from the qsv GitHub repo for the current qsv version.
 * load   - load a Geonames cities index from a file, making it the default index going forward.
            If set to 500, 1000, 5000 or 15000, it will download the corresponding English-only
            Geonames index rkyv file from the qsv GitHub repo for the current qsv version.

Examples:
Update the Geonames cities index with the latest changes.

  $ qsv geocode index-update
  # or rebuild the index using the latest Geonames data
  # with English, French, German & Spanish place names
  $ qsv geocode index-update --languages en,fr,de,es

Load an alternative Geonames cities index from a file, making it the default index going forward.

  $ qsv geocode index-load my_geonames_index.rkyv

For more extensive examples, see https://github.com/dathere/qsv/blob/master/tests/test_geocode.rs.

Usage:
qsv geocode suggest [--formatstr=<string>] [options] <column> [<input>]
qsv geocode suggestnow [options] <location>
qsv geocode reverse [--formatstr=<string>] [options] <column> [<input>]
qsv geocode reversenow [options] <location>
qsv geocode countryinfo [options] <column> [<input>]
qsv geocode countryinfonow [options] <location>
qsv geocode iplookup [options] <column> [<input>]
qsv geocode iplookupnow [options] <location>
qsv geocode index-load <index-file>
qsv geocode index-check
qsv geocode index-update [--languages=<lang>] [--cities-url=<url>] [--force] [--timeout=<seconds>]
qsv geocode index-reset
qsv geocode --help

geocode arguments:
        
    <input>                     The input file to read from. If not specified, reads from stdin.

    <column>                    The column to geocode. Used by suggest, reverse & countryinfo subcommands.
                                For suggest, it must be a column with a City string pattern.
                                For reverse, it must be a column using WGS 84 coordinates in
                                "lat, long" or "(lat, long)" format.
                                For countryinfo, it must be a column with a ISO 3166-1 alpha-2 country code.
                                For iplookup, it must be a column with an IP address or a URL.
                                Note that you can use column selector syntax to select the column, but only
                                the first column will be used. See `select --help` for more information.

    <location>                  The location to geocode for suggestnow, reversenow, countryinfonow and
                                iplookupnow subcommands.
                                  For suggestnow, its a City string pattern.
                                  For reversenow, it must be a WGS 84 coordinate.
                                  For countryinfonow, it must be a ISO 3166-1 alpha-2 code.
                                  For iplookupnow, it must be an IP address or a URL.

    <index-file>                The alternate geonames index file to use. It must be a .rkyv file.
                                For convenience, if this is set to 500, 1000, 5000 or 15000, it will download
                                the corresponding English-only Geonames index rkyv file from the qsv GitHub repo
                                for the current qsv version and use it. Only used by the index-load subcommand.

geocode options:
    -c, --new-column <name>     Put the transformed values in a new column instead. Not valid when
                                using the '%dyncols:' --formatstr option.
    -r, --rename <name>         New name for the transformed column.
    --country <country_list>    The comma-delimited, case-insensitive list of countries to filter for.
                                Country is specified as a ISO 3166-1 alpha-2 (two-letter) country code.
                                https://en.wikipedia.org/wiki/ISO_3166-2

                                It is the topmost priority filter, and will be applied first. If multiple
                                countries are specified, they are matched in priority order.
                                
                                For suggest, this will limit the search to the specified countries.

                                For reverse, this ensures that the returned city is in the specified
                                countries (especially when geocoding coordinates near country borders).
                                If the coordinate is outside the specified countries, the returned city
                                will be the closest city as the crow flies in the specified countries.

                                SUGGEST only options:
    --min-score <score>         The minimum Jaro-Winkler distance score.
                                [default: 0.8]
    --admin1 <admin1_list>      The comma-delimited, case-insensitive list of admin1s to filter for.
    
                                If all uppercase, it will be treated as an admin1 code (e.g. US.NY, JP.40, CN.23).
                                Otherwise, it will be treated as an admin1 name (e.g New York, Tokyo, Shanghai).

                                Requires the --country option. However, if all admin1 codes have the same
                                prefix (e.g. US.TX, US.NJ, US.CA), the country can be inferred from the
                                admin1 code (in this example - US), and the --country option is not required.

                                If specifying multiple admin1 filters, you can mix admin1 codes and names,
                                and they are matched in priority order.

                                Matches are made using a starts_with() comparison (i.e. "US" will match "US.NY",
                                "US.NJ", etc. for admin1 code. "New" will match "New York", "New Jersey",
                                "Newfoundland", etc. for admin1 name.)

                                admin1 is the second priority filter, and will be applied after country filters.
                                See https://download.geonames.org/export/dump/admin1CodesASCII.txt for
                                recognized admin1 codes/names.

                                REVERSE only option:
    -k, --k_weight <weight>     Use population-weighted distance for reverse subcommand.
                                (i.e. nearest.distance - k * city.population)
                                Larger values will favor more populated cities.
                                If not set (default), the population is not used and the
                                nearest city is returned.

    -f, --formatstr=<string>    The place format to use. It has three options:
                                1. Use one of the predefined formats.
                                2. Use dynamic formatting to create a custom format.
                                3. Use the special format "%dyncols:" to dynamically add multiple
                                   columns to the output CSV using fields from a geocode result.
    
                                PREDEFINED FORMATS:
                                  - '%city-state' - e.g. Brooklyn, New York
                                  - '%city-country' - Brooklyn, US
                                  - '%city-state-country' | '%city-admin1-country' - Brooklyn, New York US
                                  - '%city-county-state' | '%city-admin2-admin1' - Brooklyn, Kings County, New York
                                  - '%city' - Brooklyn
                                  - '%state' | '%admin1' - New York
                                  - "%county' | '%admin2' - Kings County
                                  - '%country' - US
                                  - '%country_name' - United States
                                  - '%cityrecord' - returns the full city record as a string
                                  - '%admin1record' - returns the full admin1 record as a string
                                  - '%admin2record' - returns the full admin2 record as a string
                                  - '%lat-long' - <latitude>, <longitude>
                                  - '%location' - (<latitude>, <longitude>)
                                  - '%id' - the Geonames ID
                                  - '%capital' - the capital
                                  - '%continent' - the continent (only valid for countryinfo subcommand)
                                  - '%population' - the population
                                  - '%timezone' - the timezone
                                  - '%json' - the full city record as JSON
                                  - '%pretty-json' - the full city record as pretty JSON
                                  - '%+' - use the subcommand's default format. 
                                           suggest - '%location'
                                           suggestnow - '{name}, {admin1} {country}: {latitude}, {longitude}'
                                           reverse & reversenow - '%city-admin1-country'
                                           countryinfo - '%country_name'
                                           iplookup - '%cityrecord'
                                           iplookupnow - '{name}, {admin1} {country}: {latitude}, {longitude}'

                                
                                If an invalid format is specified, it will be treated as '%+'.

                                Note that when using the JSON predefined formats with the now subcommands,
                                the output will be valid JSON, as the "Location" header will be omitted.

                                DYNAMIC FORMATTING:
                                Alternatively, you can use dynamic formatting to create a custom format.
                                To do so, set the --formatstr to a dynfmt template, enclosing field names
                                in curly braces.
                                The following ten cityrecord fields are available:
                                  id, name, latitude, longitude, country, admin1, admin2, capital,
                                  timezone, population

                                Fifteen additional countryinfo field are also available:
                                  iso3, fips, area, country_population, continent, tld, currency_code,
                                  currency_name, phone, postal_code_format, postal_code_regex, languages,
                                  country_geonameid, neighbours, equivalent_fips_code

                                For US places, two additional fields are available:
                                  us_county_fips_code and us_state_fips_code
                                    
                                  e.g. "City: {name}, State: {admin1}, Country: {country} {continent} - {languages}"

                                If an invalid template is specified, "Invalid dynfmt template" is returned.

                                Both predefined and dynamic formatting are cached. Subsequent calls
                                with the same result will be faster as it will use the cached result instead
                                of searching the Geonames index.

                                DYNAMIC COLUMNS ("%dyncols:") FORMATTING:
                                Finally, you can use the special format "%dyncols:" to dynamically add multiple
                                columns to the output CSV using fields from a geocode result.
                                To do so, set --formatstr to "%dyncols:" followed by a comma-delimited list
                                of key:value pairs enclosed in curly braces.
                                The key is the desired column name and the value is one of the same fields
                                available for dynamic formatting.

                                 e.g. "%dyncols: {city_col:name}, {state_col:admin1}, {county_col:admin2}"

                                will add three columns to the output CSV named city_col, state_col & county_col.

                                Note that using "%dyncols:" will cause the the command to geocode EACH row without
                                using the cache, so it will be slower than predefined or dynamic formatting.
                                Also, countryinfo and countryinfonow subcommands currently do not support "%dyncols:".
                                [default: %+]
    -l, --language <lang>       The language to use when geocoding. The language is specified as a ISO 639-1 code.
                                Note that the Geonames index must have been built with the specified language
                                using the `index-update` subcommand with the --languages option.
                                If the language is not available, the first language in the index is used.
                                [default: en]

    --invalid-result <string>   The string to return when the geocode result is empty/invalid.
                                If not set, the original value is used.
    -j, --jobs <arg>            The number of jobs to run in parallel.
                                When not set, the number of jobs is set to the number of CPUs detected.
    -b, --batch <size>          The number of rows per batch to load into memory, before running in parallel.
                                Set to 0 to load all rows in one batch.
                                [default: 50000]
    --timeout <seconds>         Timeout for downloading Geonames cities index.
                                [default: 120]
    --cache-dir <dir>           The directory to use for caching the Geonames cities index.
                                If the directory does not exist, qsv will attempt to create it.
                                If the QSV_CACHE_DIR envvar is set, it will be used instead.
                                [default: ~/.qsv-cache]                                

                                INDEX-UPDATE only options:
    --languages <lang-list>     The comma-delimited, case-insensitive list of languages to use when building
                                the Geonames cities index.
                                The languages are specified as a comma-separated list of ISO 639-2 codes.
                                See https://download.geonames.org/export/dump/iso-languagecodes.txt to look up codes
                                and https://download.geonames.org/export/dump/alternatenames/ for the supported
                                language files. 253 languages are currently supported.
                                [default: en]
    --cities-url <url>          The URL to download the Geonames cities file from. There are several
                                available at https://download.geonames.org/export/dump/.
                                  cities500.zip   - cities with populations > 500; ~200k cities, 56mb
                                  cities1000.zip  - population > 1000; ~140k cities, 44mb
                                  cities5000.zip  - population > 5000; ~53k cities, 21mb
                                  cities15000.zip - population > 15000; ~26k cities, 13mb
                                Note that the more cities are included, the larger the local index file will be,
                                lookup times will be slower, and the search results will be different.
                                For convenience, if this is set to 500, 1000, 5000 or 15000, it will be 
                                converted to a geonames cities URL.
                                [default: https://download.geonames.org/export/dump/cities15000.zip]
    --force                     Force update the Geonames cities index. If not set, qsv will check if there
                                are updates available at Geonames.org before updating the index.

Common options:
    -h, --help                  Display this message
    -o, --output <file>         Write output to <file> instead of stdout.
    -d, --delimiter <arg>       The field delimiter for reading CSV data.
                                Must be a single character. (default: ,)
    -p, --progressbar           Show progress bars. Will also show the cache hit rate upon completion.
                                Not valid for stdin.
```
