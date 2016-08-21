DB_INIT = """
BEGIN;
CREATE TABLE IF NOT EXISTS cases(
    id INTEGER PRIMARY KEY,
    type INT,
    case_from TEXT,
    case_to TEXT,
    occurrences INT,
    UNIQUE(type, case_from, case_to)
);

CREATE TABLE IF NOT EXISTS cases_from_counter(
    id INTEGER PRIMARY KEY,
    type INT,
    case_from TEXT,
    occurrences INT,
    UNIQUE(type, case_from)
);

CREATE INDEX IF NOT EXISTS cases_def_idx ON cases(type, case_from, case_to);
CREATE INDEX IF NOT EXISTS cases_from_idx ON cases(type, case_from);
CREATE INDEX IF NOT EXISTS cases_tf_from_idx ON cases_from_counter(type, case_from);
COMMIT;
"""
