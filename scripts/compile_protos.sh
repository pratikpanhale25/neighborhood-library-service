#!/usr/bin/env bash
# Compile Protocol Buffers to Python under backend/app/generated.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="$ROOT/backend/app/generated"
mkdir -p "$OUT"
# grpc_tools ships google/protobuf include files
PROTO_INC="$(python3 -c "import grpc_tools, os; print(os.path.join(os.path.dirname(grpc_tools.__file__), '_proto'))")"
python3 -m grpc_tools.protoc \
  -I "$ROOT/proto" \
  -I "$PROTO_INC" \
  --python_out="$OUT" \
  --grpc_python_out="$OUT" \
  --pyi_out="$OUT" \
  "$ROOT/proto/library/v1/library.proto"

# Stubs use ``from library.v1 import …``; with ``backend/app/generated`` on ``sys.path``
# (see ``app/__init__.py``), ``library`` / ``library.v1`` are implicit namespace packages — no ``__init__.py``.

echo "Generated Python stubs in $OUT"
