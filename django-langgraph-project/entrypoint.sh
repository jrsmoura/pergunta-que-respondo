#!/bin/sh
set -e

# espera DB se houver DATABASE_URL (opcional)
if [ -n "$DATABASE_URL" ]; then
  echo "Aguardando banco: $DATABASE_URL"
  ATTEMPTS=0; MAX_ATTEMPTS=30
  while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    python - <<'PY'
import os, socket, sys, urllib.parse as u
p=u.urlparse(os.environ.get("DATABASE_URL",""))
host=p.hostname or "db"; port=p.port or 5432
with socket.socket() as s:
    sys.exit(0 if s.connect_ex((host,port))==0 else 1)
PY
    [ $? -eq 0 ] && echo "Banco disponível." && break
    ATTEMPTS=$((ATTEMPTS+1)); sleep 1
  done
fi

python manage.py migrate --noinput

if [ "$DJANGO_DEBUG" != "1" ]; then
  python manage.py collectstatic --noinput
else
  echo "DEBUG=1 → pulando collectstatic"
fi

python manage.py runserver 0.0.0.0:8000
