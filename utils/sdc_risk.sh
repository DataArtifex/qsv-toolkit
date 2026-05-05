#!/usr/bin/env bash
#=============================================================================
# sdc_risk.sh — Statistical Disclosure Control (SDC) Risk Assessment
#=============================================================================
#
# A QSV-based utility that computes compound key frequencies and individual
# re-identification risk for statistical disclosure control.
#
#-----------------------------------------------------------------------------
# CORE CONCEPTS
#-----------------------------------------------------------------------------
#
# Quasi-Identifiers
#   A quasi-identifier is a piece of information — such as age, gender, or
#   ZIP code — that does not uniquely identify an individual on its own but
#   can be combined with other similar variables or linked to external
#   databases to re-identify a specific person in an anonymised dataset.
#
# k-Anonymity
#   k-anonymity is a privacy property ensuring each record in a dataset is
#   indistinguishable from at least k-1 others based on its quasi-identifiers.
#   The metric k_sample counts how many records share the same equivalence
#   class in the sample, while K_pop_est estimates that count in the
#   population using sampling weights.
#
# Equivalence Classes
#   An equivalence class is the group of records that share identical values
#   for all selected quasi-identifiers. Each class is identified by a
#   compound key built from the quasi-identifier values.
#
# l-Diversity
#   l-diversity is a privacy model that requires each equivalence class to
#   contain at least l "well-represented" values for a sensitive attribute.
#   A sensitive attribute is the private, confidential information (such as
#   a medical diagnosis or income) that must be protected from disclosure.
#   l-diversity is only computed when sensitive attributes are provided.
#
# Individual Risk
#   The individual re-identification risk is estimated as the inverse of the
#   population-weighted equivalence class size: ind_risk = 1 / K_pop_est.
#
#-----------------------------------------------------------------------------
# PREREQUISITES
#-----------------------------------------------------------------------------
#
# - QSV CLI must be installed and available in PATH.
# - The input CSV should be prepared for SDC analysis, containing only the
#   relevant variables (quasi-identifiers, sensitive attributes, weight).
# - If no sampling weight column is provided, a uniform weight of 1.0 is
#   automatically created.
#
#-----------------------------------------------------------------------------
# OUTPUT
#-----------------------------------------------------------------------------
#
# The script produces:
#   {SDC_BASENAME}.csv       — Input data augmented with the equivalence class
#   {SDC_BASENAME}.risk.csv  — Risk table with k-anonymity, l-diversity (if
#                              applicable), and individual risk per class
#
#-----------------------------------------------------------------------------
# EXAMPLES
#-----------------------------------------------------------------------------
#
# Minimal — only required arguments (uniform weight auto-created):
#   ./sdc_risk.sh sdcMicro.csv -q "relat,sex,hhcivil"
#
# With sampling weight and sensitive attributes:
#   ./sdc_risk.sh sdcMicro.csv -q "relat,sex,hhcivil" -w sampling_weight \
#       -s "income,expend,savings"
#
# Full customisation:
#   ./sdc_risk.sh sdcMicro.csv -q "relat,sex,hhcivil,urbrur" \
#       -w sampling_weight -s "income,expend" \
#       -k 3 -l 2 -e "eq_class" -o "micro_sdc"
#

#=============================================================================
# USAGE
#=============================================================================

usage() {
    cat <<USAGE
Usage: $(basename "$0") [DATA_FILE] -q QUASI_IDS [OPTIONS]

Arguments:
  DATA_FILE                    Input CSV file (default: data.csv)

Required:
  -q, --quasi-ids COLS         Comma-separated quasi-identifiers

Options:
  -o, --output BASENAME        Base name for SDC output files (default: sdc)
  -w, --weight COLUMN          Sampling weight column name (auto-created if omitted)
  -k, --k-anonymity N          k-anonymity threshold (default: 5)
  -e, --equiv-id NAME          Equivalence class column name (default: equivalence_class)
  -l, --l-diversity N          l-diversity threshold (default: 5)
  -s, --sensitive-attrs COLS   Comma-separated sensitive attributes
  -h, --help                   Show this help message
USAGE
    exit 0
}

#=============================================================================
# DEFAULTS
#=============================================================================

DATA_FILE="data.csv"
SDC_BASENAME="sdc"
WEIGHT=""
QUASI_IDS=""
K_ANONYMITY=5
EQUIV_ID="equivalence_class"
L_DIVERSITY=5
SENSITIVE_ATTRS=""

#=============================================================================
# PARSE ARGUMENTS
#=============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)           SDC_BASENAME="$2";     shift 2 ;;
        -w|--weight)           WEIGHT="$2";           shift 2 ;;
        -q|--quasi-ids)        QUASI_IDS="$2";        shift 2 ;;
        -k|--k-anonymity)      K_ANONYMITY="$2";      shift 2 ;;
        -e|--equiv-id)         EQUIV_ID="$2";         shift 2 ;;
        -l|--l-diversity)      L_DIVERSITY="$2";      shift 2 ;;
        -s|--sensitive-attrs)  SENSITIVE_ATTRS="$2";   shift 2 ;;
        -h|--help)             usage ;;
        -*)  echo "Error: Unknown option: $1" >&2; usage ;;
        *)   DATA_FILE="$1";   shift ;;
    esac
done

# Validate required parameters

if [[ -z "$QUASI_IDS" ]]; then
    echo "Error: --quasi-ids (-q) is required." >&2
    usage
fi

# Derived: equivalence class format string (built from QUASI_IDS)
EQUIV_FORMATSTR="{$(echo $QUASI_IDS | tr -d ' ' | sed 's/,/}|{/g')}"

#=============================================================================
# CLEANUP
#=============================================================================

# Remove output files from previous runs
rm -f "${SDC_BASENAME}.csv" "${SDC_BASENAME}.tmp.csv" "${SDC_BASENAME}.risk.csv" "${SDC_BASENAME}.risk.tmp.csv"

# Millisecond timer helpers — detect best available method once
if perl -MTime::HiRes -e '1' 2>/dev/null; then
    now_ms() { perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }
elif command -v python3 &>/dev/null; then
    now_ms() { python3 -c 'import time; print(int(time.time()*1000))'; }
else
    now_ms() { echo $(( $(date +%s) * 1000 )); }
fi
elapsed() { local ms=$(( $2 - $1 )); printf "%d.%03ds" $((ms / 1000)) $((ms % 1000)); }

TOTAL_START=$(now_ms)


#=============================================================================
# PREPARE DATASET
#=============================================================================

STEP_START=$(now_ms)

# create new dataset with equivalence class variable
qsv apply dynfmt --formatstr "$EQUIV_FORMATSTR" --new-column "$EQUIV_ID" --output "${SDC_BASENAME}.csv" "$DATA_FILE" > /dev/null

# if WEIGHT is not set, create a default weight column
if [[ -z "${WEIGHT// }" ]]; then
    qsv apply dynfmt --formatstr "1" --new-column "weight" --output "${SDC_BASENAME}.tmp.csv" "${SDC_BASENAME}.csv" > /dev/null
    mv "${SDC_BASENAME}.tmp.csv" "${SDC_BASENAME}.csv"
    WEIGHT="weight"
fi

echo "  Prepare dataset .......... $(elapsed $STEP_START $(now_ms))"


#=============================================================================
# compute k-anonymity, l-diversity, and risk metric
#=============================================================================
#
# Based on
# SELECT
#   equivalence_id,
#    -- k-Anonymity Metrics
#    COUNT(*) AS k_sample,                   -- f_k: How many in your file
#    SUM(sampling_weight) AS K_pop_est,      -- F_k: Estimated real-world frequency
#
#    -- l-Diversity Metrics (Distinct Count)
#    COUNT(DISTINCT income_bin) AS l_income,
#    COUNT(DISTINCT savings_bin) AS l_savings,
#    COUNT(DISTINCT expend_bin) AS l_expend,
#
#    -- Risk Metric
#    (1.0 / SUM(sampling_weight)) AS ind_risk -- Individual risk calculation
# FROM self
# GROUP BY equivalence_id
# ORDER BY K_pop_est ASC;
#

STEP_START=$(now_ms)

# only compute l-diversity if sensitive variables are specified
SQL_L_DIVERSITY=$(echo $SENSITIVE_ATTRS | sed 's/ //g; s/,/ /g' | awk 'NF {for(i=1;i<=NF;i++) printf "    COUNT(DISTINCT %s) AS l_%s,\n", $i, $i}')

# generate the SQL query
SQL_QUERY=$(cat <<EOF
SELECT ${QUASI_IDS}, ${EQUIV_ID},
    COUNT(*) AS k_sample,
    SUM(${WEIGHT}) AS K_pop_est,
    ${SQL_L_DIVERSITY}
    (1.0 / SUM(${WEIGHT})) AS ind_risk
FROM _t_1
GROUP BY ${QUASI_IDS}, ${EQUIV_ID}
ORDER BY k_sample ASC;
EOF
)

# run query
qsv sqlp "${SDC_BASENAME}.csv" "$SQL_QUERY" --output "${SDC_BASENAME}.risk.csv" > /dev/null

echo "  Compute risk metrics ..... $(elapsed $STEP_START $(now_ms))"


#=============================================================================
# ADD PASS / FAIL FLAGS
#=============================================================================

STEP_START=$(now_ms)

# k-anonymity pass/fail
SQL_K_PASS="SELECT *, CASE WHEN k_sample >= ${K_ANONYMITY} THEN 'PASS' ELSE 'FAIL' END AS k_pass FROM _t_1"
qsv sqlp "${SDC_BASENAME}.risk.csv" "$SQL_K_PASS" --output "${SDC_BASENAME}.risk.tmp.csv" > /dev/null
mv "${SDC_BASENAME}.risk.tmp.csv" "${SDC_BASENAME}.risk.csv"

# l-diversity pass/fail (only when sensitive attributes were provided)
if [[ -n "$SENSITIVE_ATTRS" ]]; then
    # build LEAST(l_attr1, l_attr2, ...) from the sensitive attribute names
    L_COLS=$(echo "$SENSITIVE_ATTRS" | sed 's/ //g; s/,/\n/g' | sed 's/^/l_/' | paste -sd ',' -)
    SQL_L_PASS="SELECT *, CASE WHEN LEAST(${L_COLS}) >= ${L_DIVERSITY} THEN 'PASS' ELSE 'FAIL' END AS l_pass FROM _t_1"
    qsv sqlp "${SDC_BASENAME}.risk.csv" "$SQL_L_PASS" --output "${SDC_BASENAME}.risk.tmp.csv" > /dev/null
    mv "${SDC_BASENAME}.risk.tmp.csv" "${SDC_BASENAME}.risk.csv"
fi

echo "  Add pass/fail flags ...... $(elapsed $STEP_START $(now_ms))"


#=============================================================================
# SUMMARY
#=============================================================================

echo ""
echo "Output: ${SDC_BASENAME}.risk.csv"
echo "Total elapsed time: $(elapsed $TOTAL_START $(now_ms))"
