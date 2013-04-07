rm -f /tmp/tmp.db && python bin/load-sqlite.py ~/datasets/gdp/ /tmp/tmp.db && sqlite3 /tmp/tmp.db < tests/check-sqlite.sql
