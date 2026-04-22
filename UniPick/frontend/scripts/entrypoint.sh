#! /bin/sh
set -e
cd /usr/share/nginx/html
PLACEHOLDER=$1
find . -type f -exec \
	sed -i -e "s#$1#${BACKEND_URL:-http://localhost:8000}#" {} \;
shift

exec "$@"
