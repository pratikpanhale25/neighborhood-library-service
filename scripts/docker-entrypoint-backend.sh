#!/bin/sh
# Apply scripts/init_db.sql once Postgres is reachable, then start the library server.
# DATABASE_URL may be postgresql+psycopg2://... (strip +psycopg2 for psql).

set -eu

PGURL=$(printf '%s' "${DATABASE_URL:-}" | sed 's|postgresql+psycopg2://|postgresql://|')
if [ -z "$PGURL" ]; then
  echo "DATABASE_URL is not set" >&2
  exit 1
fi

i=0
while [ "$i" -lt 90 ]; do
  if psql "$PGURL" -c 'SELECT 1' >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

if ! psql "$PGURL" -c 'SELECT 1' >/dev/null 2>&1; then
  echo "PostgreSQL did not become ready in time: $PGURL" >&2
  exit 1
fi

psql "$PGURL" -v ON_ERROR_STOP=1 -f /app/scripts/init_db.sql

exec library-server
