"""
Venturine handoff validator, for the venturine-handoff/v1 format.

Usage (run by file path):
python3 scripts/validate_handoff.py handoff.json

Checks the structure of a handoff document and the evidence rules that tie
labels to sources, calculations and reviews. See docs/handoff-v1.md.

Reads only the one .json file named on the command line. It never writes
files, uses the network, or runs other programs, and it never prints the
contents of the file it reads: messages name a field and a rule, not a value.
Requires only the Python standard library.
"""

import argparse
import json
import re

VALIDATOR_VERSION = "0.1.0"
SCHEMA_ID = "venturine-handoff/v1"

MAX_FILE_BYTES = 1000000
MAX_DEPTH = 12
MAX_NODES = 20000
MAX_ITEMS = 500
MAX_STRING = 5000
MAX_MESSAGES = 100

# The shared evidence vocabulary, defined in docs/evidence-terminology.md.
LABELS = (
    "VERIFIED", "PARTIALLY_SUPPORTED", "UNVERIFIED", "CONTRADICTED",
    "FOUNDER_PROVIDED", "DERIVED", "ASSUMPTION", "UNKNOWN",
)
STAGES = ("idea", "validating", "pre-launch", "launched")
SOURCE_TYPES = (
    "vendor_page", "official_statistic", "regulator", "filing", "news",
    "academic", "third_party_analysis", "search_summary", "founder",
    "calculation", "other",
)
# Source types that can never make a claim VERIFIED by themselves.
NON_VERIFYING_SOURCE_TYPES = ("search_summary", "third_party_analysis",
                              "founder")
PRODUCER_KINDS = ("skill", "agent", "user", "other")

# Calculator operations and their input counts. A test keeps this table in
# step with scripts/calculate.py.
ENGINE_OPERATIONS = {
    "revenue": 2,
    "gross-margin": 2,
    "contribution-margin": 2,
    "break-even": 3,
    "break-even-loaded": 4,
    "operating-profit": 5,
    "cac": 2,
    "runway": 2,
    "subscription-ltv": 2,
}
# Operations of scripts/forecast.py, with the allowed range of input counts.
# Each takes named inputs, and engine-validated results carry a receipt.
FORECAST_OPERATIONS = {
    "monthly-forecast": (8, 8),
    "scenario-compare": (16, 40),
    "sensitivity": (9, 13),
    "price-compare": (5, 12),
}
MANUAL_OPERATION = "manual"
# Operations where acquisition spending must be counted exactly once.
ACQUISITION_SENSITIVE = (
    "break-even-loaded", "operating-profit",
) + tuple(FORECAST_OPERATIONS)

DECISION_LABELS = (
    "PROCEED TO VALIDATION", "REVISE THE CONCEPT", "INSUFFICIENT EVIDENCE",
    "NOT VIABLE UNDER STATED CONSTRAINTS",
)
HIGH_CONFIDENCE_DECISIONS = (
    "PROCEED TO VALIDATION", "NOT VIABLE UNDER STATED CONSTRAINTS",
)
CONFIDENCE_LEVELS = ("PRELIMINARY", "AUDITED")
REVIEWERS = ("evidence-auditor", "red-team-reviewer")
AUDITOR_RESULTS = (
    "PASS", "PASS WITH LIMITATIONS", "REVISION REQUIRED",
    "INSUFFICIENT EVIDENCE",
)
RED_TEAM_VERDICTS = (
    "STANDS", "STANDS WITH WEAKNESSES", "DOES NOT STAND",
    "NOT ENOUGH INFORMATION",
)
REVIEW_RESULTS = {
    "evidence-auditor": AUDITOR_RESULTS,
    "red-team-reviewer": RED_TEAM_VERDICTS,
}
# A decision this strong needs an auditor result of at least this quality.
PASSING_AUDITOR_RESULTS = ("PASS", "PASS WITH LIMITATIONS")

TOP_REQUIRED = ("schema", "created", "producer", "venture", "evidence_ledger")
TOP_OPTIONAL = (
    "id", "calculations", "decision", "reviews", "open_questions",
    "next_steps", "notes",
)
PRODUCER_KEYS = ("component", "kind", "version")
VENTURE_KEYS = (
    "name", "summary", "stage", "customer", "problem", "solution",
    "business_model", "geography", "currency", "hypothetical",
)
LEDGER_KEYS = (
    "id", "claim", "label", "value", "unit", "source", "derived_from",
    "calculation", "limitations", "validation",
)
SOURCE_KEYS = ("type", "title", "url", "published", "accessed", "examined")
CALCULATION_KEYS = (
    "id", "operation", "inputs", "result", "unrounded_result",
    "engine_validated", "engine_version", "method",
    "acquisition_counted_once", "receipt",
)
INPUT_KEYS = ("name", "value", "evidence")
DECISION_KEYS = ("label", "confidence", "rationale")
REVIEW_KEYS = ("reviewer", "result", "date", "summary")

KNOWN_KEYS = None  # filled in below, once every key table exists
ID_PATTERN = re.compile(r"^[A-Z][0-9]{1,4}$", re.ASCII)
COMPONENT_PATTERN = re.compile(r"^[a-z][a-z0-9-]{1,40}$", re.ASCII)
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$", re.ASCII)
DATE_PATTERN = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$", re.ASCII)
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$", re.ASCII)
NUMBER_PATTERN = re.compile(
    r"^[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$", re.ASCII
)
RECEIPT_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$", re.ASCII)
URL_PATTERN = re.compile(r"^https?://[^\s]+$", re.ASCII)
EXTENSION_PREFIX = "x_"

# High-confidence secret formats. A match is an error, and the value is
# never printed.
SECRET_PATTERNS = (
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}")),
    ("GitHub token",
     re.compile(r"(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{30,}")),
    ("Slack token", re.compile(r"(?<![A-Za-z0-9])xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("API key", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}")),
    ("Google API key",
     re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_-]{35}")),
    ("credentials in a URL", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")),
)
# Every quantifier is bounded so that a long run of ordinary characters is
# scanned in linear time. An unbounded local part backtracked quadratically
# and let one 1 MB string hang the validator.
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63})+"
)


KNOWN_KEYS = frozenset(
    TOP_REQUIRED + TOP_OPTIONAL + PRODUCER_KEYS + VENTURE_KEYS + LEDGER_KEYS
    + SOURCE_KEYS + CALCULATION_KEYS + INPUT_KEYS + DECISION_KEYS
    + REVIEW_KEYS
)


def key_label(key):
    """
    Text for a key in a message. Only the format's own field names are ever
    shown. Any other key could be a secret or personal data, so it is not
    echoed.
    """
    if key in KNOWN_KEYS:
        return key
    if key.startswith(EXTENSION_PREFIX):
        return "<custom field>"
    return "<unrecognized field>"


class Report:
    """Collects messages, capped so a hostile file cannot flood output."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, message):
        if len(self.errors) < MAX_MESSAGES:
            self.errors.append(f"{path}: {message}")
        elif len(self.errors) == MAX_MESSAGES:
            self.errors.append("too many errors; further errors omitted")

    def warn(self, path, message):
        if len(self.warnings) < MAX_MESSAGES:
            self.warnings.append(f"{path}: {message}")


def valid_date(text):
    match = DATE_PATTERN.match(text)
    if not match:
        return False
    year, month, day = (int(part) for part in match.groups())
    if not 1 <= month <= 12 or year < 1:
        return False
    days = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
            else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return 1 <= day <= days[month - 1]


class DuplicateKey(ValueError):
    pass


def _reject_constant(name):
    raise ValueError("NaN and Infinity are not allowed")


def _no_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise DuplicateKey("duplicate object key")
        seen[key] = value
    return seen


def parse_document(text):
    """Parse JSON text strictly. Returns (document, error_message)."""
    try:
        return json.loads(
            text, object_pairs_hook=_no_duplicates,
            parse_constant=_reject_constant,
        ), None
    except DuplicateKey:
        return None, "the file has a duplicate object key"
    except RecursionError:
        return None, "the file is nested too deeply"
    except ValueError as error:
        # JSONDecodeError messages name a position, never file content.
        if isinstance(error, json.JSONDecodeError):
            return None, (
                f"not valid JSON (line {error.lineno}, column {error.colno})"
            )
        return None, str(error)


def measure(document):
    """Iteratively compute (depth, node_count) without recursion."""
    deepest, nodes = 0, 0
    stack = [(document, 1)]
    while stack:
        value, depth = stack.pop()
        nodes += 1
        deepest = max(deepest, depth)
        if nodes > MAX_NODES or depth > MAX_DEPTH + 1:
            return deepest, nodes
        if isinstance(value, dict):
            stack.extend((v, depth + 1) for v in value.values())
        elif isinstance(value, list):
            stack.extend((v, depth + 1) for v in value)
    return deepest, nodes


def iter_strings(document):
    """Yield (path, text) for every string value and key, iteratively."""
    stack = [("$", document)]
    while stack:
        path, value = stack.pop()
        if isinstance(value, str):
            yield path, value
        elif isinstance(value, dict):
            for key, item in value.items():
                yield f"{path}.<key>", key
                stack.append((f"{path}.{key_label(key)}", item))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                stack.append((f"{path}[{index}]", item))


def scan_for_sensitive_text(document, report):
    for path, text in iter_strings(document):
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                report.error(path, f"contains what looks like a {name}; "
                                   "remove it")
        if EMAIL_PATTERN.search(text):
            report.warn(path, "contains an email address; handoffs are "
                              "meant to be shared, so remove personal data")


# ---------------------------------------------------------------- field checks


def check_object(value, path, report, allowed, required=()):
    """Return True when value is an object with only known keys."""
    if not isinstance(value, dict):
        report.error(path, "must be an object")
        return False
    for key in required:
        if key not in value:
            report.error(path, f"missing required field '{key}'")
    for key in value:
        if key in allowed or key.startswith(EXTENSION_PREFIX):
            continue
        report.error(path, "unknown field (its name is not shown); allowed "
                           "fields here: " + ", ".join(sorted(allowed))
                           + f"; custom fields must start with "
                             f"'{EXTENSION_PREFIX}'")
    return True


def check_text(obj, key, path, report, max_len=MAX_STRING, required=False):
    if key not in obj:
        if required:
            report.error(path, f"missing required field '{key}'")
        return None
    value = obj[key]
    if not isinstance(value, str):
        report.error(f"{path}.{key}", "must be a string")
        return None
    if required and not value.strip():
        report.error(f"{path}.{key}", "must not be empty")
    if len(value) > max_len:
        report.error(f"{path}.{key}", f"must be at most {max_len} characters")
    return value


def check_choice(obj, key, path, report, choices, required=False):
    value = check_text(obj, key, path, report, 100, required)
    if value is not None and value not in choices:
        report.error(f"{path}.{key}", "must be one of: " + ", ".join(choices))
        return None
    return value


def check_date(obj, key, path, report, required=False):
    value = check_text(obj, key, path, report, 10, required)
    if value is not None and not valid_date(value):
        report.error(f"{path}.{key}", "must be a real date as YYYY-MM-DD")
        return None
    return value


def check_text_list(obj, key, path, report, max_len=1000):
    if key not in obj:
        return
    value = obj[key]
    if not isinstance(value, list):
        report.error(f"{path}.{key}", "must be an array of strings")
        return
    if len(value) > MAX_ITEMS:
        report.error(f"{path}.{key}", f"at most {MAX_ITEMS} items")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            report.error(f"{path}.{key}[{index}]",
                         "must be a non-empty string")
        elif len(item) > max_len:
            report.error(f"{path}.{key}[{index}]",
                         f"must be at most {max_len} characters")


def check_producer(value, report):
    path = "producer"
    if not check_object(value, path, report, PRODUCER_KEYS,
                        ("component", "kind")):
        return
    component = check_text(value, "component", path, report, 41)
    if component is not None and not COMPONENT_PATTERN.match(component):
        report.error(f"{path}.component",
                     "must be lowercase letters, digits and hyphens")
    check_choice(value, "kind", path, report, PRODUCER_KINDS)
    version = check_text(value, "version", path, report, 20)
    if version is not None and not SEMVER_PATTERN.match(version):
        report.error(f"{path}.version", "must look like 1.2.3")


def check_venture(value, report):
    path = "venture"
    if not check_object(value, path, report, VENTURE_KEYS, ("name",)):
        return
    check_text(value, "name", path, report, 120, required=True)
    for key in ("summary", "customer", "problem", "solution",
                "business_model", "geography"):
        check_text(value, key, path, report, 2000)
    check_choice(value, "stage", path, report, STAGES)
    currency = check_text(value, "currency", path, report, 3)
    if currency is not None and not CURRENCY_PATTERN.match(currency):
        report.error(f"{path}.currency", "must be a 3-letter code such as USD")
    if "hypothetical" in value and not isinstance(value["hypothetical"],
                                                  bool):
        report.error(f"{path}.hypothetical", "must be true or false")


def check_source(source, path, report):
    """Validate a source object. Returns the dict when usable, else None."""
    if not check_object(source, path, report, SOURCE_KEYS, ("type",)):
        return None
    check_choice(source, "type", path, report, SOURCE_TYPES)
    check_text(source, "title", path, report, 300)
    url = check_text(source, "url", path, report, 2000)
    if url is not None and not URL_PATTERN.match(url):
        report.error(f"{path}.url", "must be an http or https URL")
    check_date(source, "published", path, report)
    check_date(source, "accessed", path, report)
    if "examined" in source and not isinstance(source["examined"], bool):
        report.error(f"{path}.examined", "must be true or false")
    return source


def has_locator(source):
    return bool(source.get("url") or source.get("title"))


def check_label_rules(entry, path, source, report):
    label = entry.get("label")
    limitations = entry.get("limitations")
    examined = bool(source and source.get("examined") is True)
    if label == "VERIFIED":
        if source is None:
            report.error(path, "VERIFIED needs a source")
            return
        if not has_locator(source):
            report.error(f"{path}.source", "VERIFIED needs a url or title")
        if not source.get("accessed"):
            report.error(f"{path}.source",
                         "VERIFIED needs the date the source was accessed")
        if not examined:
            report.error(f"{path}.source",
                         "VERIFIED needs examined: true, because the source "
                         "must have actually been read")
        if source.get("type") in NON_VERIFYING_SOURCE_TYPES:
            report.error(
                f"{path}.source.type",
                f"a {source.get('type')} cannot make a claim VERIFIED; "
                "examine the primary source or use PARTIALLY_SUPPORTED, "
                "UNVERIFIED or FOUNDER_PROVIDED")
    elif label == "PARTIALLY_SUPPORTED":
        if source is None or not has_locator(source):
            report.error(path, "PARTIALLY_SUPPORTED needs a source with a "
                               "url or title")
        if not limitations:
            report.error(path, "PARTIALLY_SUPPORTED needs limitations that "
                               "say what the evidence does not cover")
    elif label == "CONTRADICTED":
        if source is None or not has_locator(source):
            report.error(path, "CONTRADICTED needs the source that "
                               "contradicts the claim")
    elif label == "FOUNDER_PROVIDED":
        if examined:
            report.error(
                f"{path}.source",
                "FOUNDER_PROVIDED means the input was not checked; if you "
                "examined a source use VERIFIED or PARTIALLY_SUPPORTED")
    elif label == "DERIVED":
        if not entry.get("derived_from") and not entry.get("calculation"):
            report.error(path, "DERIVED needs derived_from or calculation")
    elif label == "ASSUMPTION":
        if not entry.get("validation"):
            report.warn(path, "an ASSUMPTION should say how to test it "
                              "(validation)")
    elif label == "UNKNOWN":
        if "value" in entry:
            report.error(f"{path}.value",
                         "an UNKNOWN entry must not have a value; do not "
                         "fill in what is not known")


def check_ledger_entry(entry, index, report, ids):
    path = f"evidence_ledger[{index}]"
    if not check_object(entry, path, report, LEDGER_KEYS,
                        ("id", "claim", "label")):
        return None
    entry_id = check_text(entry, "id", path, report, 8)
    if entry_id is not None:
        if not ID_PATTERN.match(entry_id) or not entry_id.startswith("E"):
            report.error(f"{path}.id", "must look like E1")
        elif entry_id in ids:
            report.error(f"{path}.id", "duplicate id")
        else:
            ids[entry_id] = index
    check_text(entry, "claim", path, report, 1000, required=True)
    check_choice(entry, "label", path, report, LABELS, required=True)
    check_text(entry, "value", path, report, 200)
    check_text(entry, "unit", path, report, 60)
    check_text(entry, "limitations", path, report, 1000)
    check_text(entry, "validation", path, report, 1000)
    source = None
    if "source" in entry:
        source = check_source(entry["source"], f"{path}.source", report)
    check_label_rules(entry, path, source, report)
    return entry


def check_references(entries, calc_ids, ids, report):
    """derived_from and calculation links must resolve, with no cycles."""
    graph = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        path = f"evidence_ledger[{index}]"
        entry_id = entry.get("id")
        sources = entry.get("derived_from", [])
        if "derived_from" in entry:
            if not isinstance(sources, list) or not all(
                    isinstance(item, str) for item in sources):
                report.error(f"{path}.derived_from",
                             "must be an array of evidence ids")
                sources = []
            elif len(sources) > MAX_ITEMS:
                report.error(f"{path}.derived_from",
                             f"at most {MAX_ITEMS} items")
                sources = []
        for target in sources:
            if target not in ids:
                report.error(f"{path}.derived_from",
                             "refers to an evidence id that does not exist")
            elif target == entry_id:
                report.error(f"{path}.derived_from",
                             "an entry cannot be derived from itself")
        if isinstance(entry_id, str):
            graph[entry_id] = [t for t in sources if t in ids]
        calc = entry.get("calculation")
        if "calculation" in entry:
            if not isinstance(calc, str):
                report.error(f"{path}.calculation",
                             "must be a calculation id string")
            elif calc not in calc_ids:
                report.error(f"{path}.calculation",
                             "refers to a calculation id that does not "
                             "exist")
    # Cycle detection (iterative depth-first search).
    state = {}
    for start in graph:
        if state.get(start):
            continue
        stack = [(start, iter(graph.get(start, [])))]
        state[start] = 1
        while stack:
            node, children = stack[-1]
            advanced = False
            for child in children:
                if state.get(child) == 1:
                    report.error("evidence_ledger",
                                 "derived_from forms a cycle")
                    return
                if not state.get(child):
                    state[child] = 1
                    stack.append((child, iter(graph.get(child, []))))
                    advanced = True
                    break
            if not advanced:
                state[node] = 2
                stack.pop()


def check_calculation(calc, index, report, ids, calc_ids):
    path = f"calculations[{index}]"
    if not check_object(calc, path, report, CALCULATION_KEYS,
                        ("id", "operation", "inputs", "result",
                         "engine_validated")):
        return
    calc_id = check_text(calc, "id", path, report, 8)
    if calc_id is not None:
        if not ID_PATTERN.match(calc_id) or not calc_id.startswith("C"):
            report.error(f"{path}.id", "must look like C1")
        elif calc_id in calc_ids:
            report.error(f"{path}.id", "duplicate id")
        else:
            calc_ids[calc_id] = index
    operations = (
        tuple(ENGINE_OPERATIONS) + tuple(FORECAST_OPERATIONS)
        + (MANUAL_OPERATION,)
    )
    operation = check_choice(calc, "operation", path, report, operations,
                             required=True)

    inputs = calc.get("inputs")
    if "inputs" in calc:
        if not isinstance(inputs, list):
            report.error(f"{path}.inputs", "must be an array")
        elif len(inputs) > MAX_ITEMS:
            report.error(f"{path}.inputs", f"at most {MAX_ITEMS} items")
        else:
            for position, item in enumerate(inputs):
                ipath = f"{path}.inputs[{position}]"
                if not check_object(item, ipath, report, INPUT_KEYS,
                                    ("name", "value", "evidence")):
                    continue
                check_text(item, "name", ipath, report, 60, required=True)
                value = check_text(item, "value", ipath, report, 64,
                                   required=True)
                if value is not None and not NUMBER_PATTERN.match(value):
                    report.error(
                        f"{ipath}.value",
                        "must be a plain number written with ASCII digits")
                evidence = check_text(item, "evidence", ipath, report, 8,
                                      required=True)
                if evidence is not None and evidence not in ids:
                    report.error(
                        f"{ipath}.evidence",
                        "must be the id of an evidence_ledger entry, so "
                        "every number has a label")
            expected = ENGINE_OPERATIONS.get(operation)
            if expected is not None and len(inputs) != expected:
                report.error(f"{path}.inputs",
                             f"{operation} takes {expected} inputs")
            allowed = FORECAST_OPERATIONS.get(operation)
            if allowed and not allowed[0] <= len(inputs) <= allowed[1]:
                report.error(
                    f"{path}.inputs",
                    f"{operation} takes from {allowed[0]} to {allowed[1]} "
                    "inputs")

    validated = calc.get("engine_validated")
    if "engine_validated" in calc and not isinstance(validated, bool):
        report.error(f"{path}.engine_validated", "must be true or false")
    elif validated is True:
        if operation == MANUAL_OPERATION:
            report.error(f"{path}.engine_validated",
                         "a manual calculation cannot be engine-validated")
        version = check_text(calc, "engine_version", path, report, 20)
        if version is None:
            report.error(path, "engine-validated results need engine_version")
        elif not SEMVER_PATTERN.match(version):
            report.error(f"{path}.engine_version", "must look like 1.2.3")
    elif validated is False:
        if not calc.get("method"):
            report.error(
                path, "a calculation that was not engine-validated needs a "
                      "method that says how it was done")
    check_text(calc, "method", path, report, 1000)

    receipt = check_text(calc, "receipt", path, report, 80)
    if receipt is not None and not RECEIPT_PATTERN.match(receipt):
        report.error(f"{path}.receipt", "must look like sha256: followed by "
                                        "64 hexadecimal characters")
    if operation in FORECAST_OPERATIONS and validated is True \
            and "receipt" not in calc:
        report.error(f"{path}.receipt",
                     f"an engine-validated {operation} result needs the "
                     "receipt fingerprint the calculator printed")
    if "receipt" in calc and validated is not True:
        report.error(f"{path}.receipt",
                     "only an engine-validated result has a receipt")

    if operation in ACQUISITION_SENSITIVE:
        counted = calc.get("acquisition_counted_once")
        if counted is not True:
            report.error(
                f"{path}.acquisition_counted_once",
                f"{operation} needs acquisition_counted_once: true, "
                "because acquisition spending must enter the model exactly "
                "once, never in both fixed costs and CAC")
    elif "acquisition_counted_once" in calc and not isinstance(
            calc["acquisition_counted_once"], bool):
        report.error(f"{path}.acquisition_counted_once",
                     "must be true or false")


def check_reviews(reviews, report):
    """Validate reviews and return the list of valid review dicts."""
    valid = []
    if not isinstance(reviews, list):
        report.error("reviews", "must be an array")
        return valid
    if len(reviews) > 20:
        report.error("reviews", "at most 20 items")
        return valid
    for index, review in enumerate(reviews):
        path = f"reviews[{index}]"
        if not check_object(review, path, report, REVIEW_KEYS,
                            ("reviewer", "result", "date")):
            continue
        reviewer = check_choice(review, "reviewer", path, report, REVIEWERS,
                                required=True)
        results = REVIEW_RESULTS.get(reviewer, ())
        result = check_text(review, "result", path, report, 60, required=True)
        if reviewer and result is not None and result not in results:
            report.error(f"{path}.result",
                         f"for {reviewer} must be one of: "
                         + ", ".join(results))
            result = None
        check_date(review, "date", path, report, required=True)
        check_text(review, "summary", path, report, 2000)
        if reviewer and result:
            valid.append(review)
    return valid


def check_decision(decision, reviews, report):
    path = "decision"
    if not check_object(decision, path, report, DECISION_KEYS,
                        ("label", "confidence")):
        return
    label = check_choice(decision, "label", path, report, DECISION_LABELS,
                         required=True)
    confidence = check_choice(decision, "confidence", path, report,
                              CONFIDENCE_LEVELS, required=True)
    check_text(decision, "rationale", path, report, 2000)
    auditor_results = [r["result"] for r in reviews
                       if r.get("reviewer") == "evidence-auditor"]
    if confidence == "AUDITED":
        if not auditor_results:
            report.error(
                f"{path}.confidence",
                "AUDITED needs a reviews entry showing that the "
                "evidence-auditor ran; otherwise use PRELIMINARY")
        elif (label in HIGH_CONFIDENCE_DECISIONS
              and not any(r in PASSING_AUDITOR_RESULTS
                          for r in auditor_results)):
            report.error(
                f"{path}.confidence",
                f"a {label} decision cannot be AUDITED unless the auditor "
                "result is PASS or PASS WITH LIMITATIONS; lower the "
                "decision to REVISE THE CONCEPT or INSUFFICIENT EVIDENCE")
    elif confidence == "PRELIMINARY" and auditor_results:
        report.error(
            f"{path}.confidence",
            "PRELIMINARY means no independent review ran, but reviews "
            "shows that the evidence-auditor ran; use AUDITED")


def validate(document):
    """Validate a parsed document. Returns a result dictionary."""
    report = Report()
    depth, nodes = measure(document)
    if nodes > MAX_NODES or depth > MAX_DEPTH + 1:
        report.error("$", "the document is too large or too deeply nested")
        return result_for(report)
    if not isinstance(document, dict):
        report.error("$", "the top level must be an object")
        return result_for(report)

    schema = document.get("schema")
    if schema != SCHEMA_ID:
        if isinstance(schema, str) and schema.startswith(
                "venturine-handoff/"):
            report.error("schema", f"unsupported version; this validator "
                                   f"checks {SCHEMA_ID}")
        else:
            report.error("schema", f"must be exactly {SCHEMA_ID}")
    check_object(document, "$", report, TOP_REQUIRED + TOP_OPTIONAL,
                 TOP_REQUIRED)
    scan_for_sensitive_text(document, report)

    check_text(document, "id", "$", report, 60)
    check_date(document, "created", "$", report, required=True)
    if "producer" in document:
        check_producer(document["producer"], report)
    if "venture" in document:
        check_venture(document["venture"], report)

    ids, calc_ids = {}, {}
    entries = document.get("evidence_ledger")
    if "evidence_ledger" in document:
        if not isinstance(entries, list):
            report.error("evidence_ledger", "must be an array")
            entries = []
        elif len(entries) > MAX_ITEMS:
            report.error("evidence_ledger", f"at most {MAX_ITEMS} items")
            entries = []
        else:
            for index, entry in enumerate(entries):
                check_ledger_entry(entry, index, report, ids)

    calculations = document.get("calculations", [])
    if "calculations" in document:
        if not isinstance(calculations, list):
            report.error("calculations", "must be an array")
            calculations = []
        elif len(calculations) > MAX_ITEMS:
            report.error("calculations", f"at most {MAX_ITEMS} items")
            calculations = []
        else:
            for index, calc in enumerate(calculations):
                check_calculation(calc, index, report, ids, calc_ids)

    if isinstance(entries, list):
        check_references(entries, calc_ids, ids, report)

    reviews = []
    if "reviews" in document:
        reviews = check_reviews(document["reviews"], report)
    if "decision" in document:
        check_decision(document["decision"], reviews, report)

    check_text_list(document, "open_questions", "$", report)
    check_text_list(document, "next_steps", "$", report)
    check_text(document, "notes", "$", report, 2000)
    return result_for(report)


def result_for(report):
    return {
        "schema": SCHEMA_ID,
        "validator_version": VALIDATOR_VERSION,
        "valid": not report.errors,
        "errors": report.errors,
        "warnings": report.warnings,
    }


def validate_text(text):
    """Parse and validate JSON text."""
    document, problem = parse_document(text)
    if problem:
        report = Report()
        report.error("$", problem)
        return result_for(report)
    return validate(document)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a venturine-handoff/v1 document.",
        epilog=(
            "Reads only the .json file you name. It never writes files or "
            "prints the file's contents. Exit status: 0 valid, 1 invalid, "
            "2 usage error."
        ),
    )
    parser.add_argument(
        "path",
        type=argparse.FileType("r", encoding="utf-8"),
        help="a .json file containing the handoff document",
    )
    args = parser.parse_args()
    name = args.path.name
    from_stdin = name == "<stdin>"
    if not from_stdin and not str(name).lower().endswith(".json"):
        args.path.close()
        parser.error("the file must have a .json extension")

    try:
        text = args.path.read(MAX_FILE_BYTES + 1)
    except (UnicodeDecodeError, OSError):
        parser.error("the file could not be read as UTF-8 text")
    finally:
        if not from_stdin:
            args.path.close()
    if len(text) > MAX_FILE_BYTES:
        parser.error(f"the file is larger than {MAX_FILE_BYTES} bytes")

    result = validate_text(text)
    print(json.dumps(result, indent=2))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
