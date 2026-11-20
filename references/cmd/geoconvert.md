# qsv geoconvert

<small>v29.0.0</small>

```text
Convert between various spatial formats and CSV/SVG including GeoJSON, SHP, and more.

For example to convert a GeoJSON file into CSV data:

  $ qsv geoconvert file.geojson geojson csv

To use stdin as input instead of a file path, use a dash "-":

  $ qsv prompt -m "Choose a GeoJSON file" -F geojson | qsv geoconvert - geojson csv

To convert a CSV file into GeoJSON data, specify the WKT geometry column with the --geometry flag:

  $ qsv geoconvert file.csv csv geojson --geometry geometry

Alternatively specify the latitude and longitude columns with the --latitude and --longitude flags:

  $ qsv geoconvert file.csv csv geojson --latitude lat --longitude lon

Convert latitude/longitude columns into a WKT geometry column, reading a TSV file:

  $ qsv geoconvert file.tsv csv csv --latitude lat --longitude lon

For CSV input, rows whose geometry cannot be used are skipped: an empty geometry, latitude
or longitude cell, WKT that does not parse, a latitude or longitude that is not a finite
number, or a latitude outside -90..90 or longitude outside -180..180. A warning on stderr
counts the skipped rows and gives the line of the first one. If EVERY row is skipped,
geoconvert fails instead, as the columns are then most likely wrong - swapped, or holding
projected coordinates such as State Plane feet. Latitude and longitude values may be
padded with spaces.

Swapped latitude/longitude columns are only caught when the swapped values fall out of
range (e.g. US West Coast longitudes near -122). Where both values are within +/-90
(e.g. New York: 40.7, -74), swapped columns are NOT detected - check a few rows on a map.

A shapefile needs its .shp, .shx and .dbf files side by side. If its .prj file describes a
projected coordinate system (e.g. NY State Plane), geoconvert warns: the coordinates are
output unchanged, so they are not the WGS-84 longitude/latitude that GeoJSON requires.
Reprojection is not done by geoconvert; reproject the shapefile first, e.g. with
ogr2ogr -t_srs EPSG:4326 out.shp in.shp

Coordinates are converted as 64-bit floating point numbers, which hold 15-17 significant
digits in all (whole and decimal digits together). A coordinate written with more digits
than that is output shortened, and its last digit may change: 40.123456789012345 becomes
40.123456789012344, and the longitude -122.123456789012345 becomes -122.12345678901235.
The difference is far below what GPS can measure; 7 decimal places is already about 1 cm.

See also https://github.com/dathere/qsv/wiki/Geospatial#geoconvert

Usage:
    qsv geoconvert [options] (<input>) (<input-format>) (<output-format>)
    qsv geoconvert --help

geoconvert REQUIRED arguments:
    <input>           The spatial file to convert. To use stdin instead, use a dash "-".
                      Note: SHP input must be a path to a .shp file and cannot use stdin.
    <input-format>    Valid values are "geojson", "shp", and "csv"
    <output-format>   Valid values are:
                      - For GeoJSON input: "csv", "svg", and "geojsonl"
                      - For SHP input: "csv", "geojson", "geojsonl", and "svg"
                      - For CSV input: "geojson", "geojsonl", "svg", and "csv"
                        (CSV output has the geometry as a WKT column)

geoconvert options:
                                 REQUIRED FOR CSV INPUT
    -g, --geometry <geometry>    The name of the column that has WKT geometry.
                                 Alternative to --latitude and --longitude.
    -y, --latitude <col>         The name of the column with northing values.
    -x, --longitude <col>        The name of the column with easting values.

    -l, --max-length <length>    The maximum column length in bytes when the output format
                                 is CSV. Oftentimes, the geometry column is too long to fit
                                 in a CSV file, causing other tools like Python & PostgreSQL
                                 to fail. If a column is too long, it will be truncated to
                                 the specified length and an ellipsis ("...") will be
                                 appended, so a truncated value is up to 3 bytes longer.

Common options:
    -h, --help                   Display this message
    -o, --output <file>          Write output to <file> instead of stdout.
    -d, --delimiter <arg>        The field delimiter for reading CSV input.
                                 Must be a single character. (default: ,)
```
