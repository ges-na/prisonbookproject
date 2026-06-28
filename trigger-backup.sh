set -eo pipefail

if [[ -z "$FLY_APP" || -z "$FLY_API_TOKEN" ]]; then
  >&2 echo "Env vars FLY_APP and FLY_API_TOKEN must not be empty"
  exit 1
fi

echo "Starting machine with volume $volume_id"
flyctl machine run \
    --app="ppbp-db-backup-worker" \
    --region="iad" \
    --restart=no \
    --rm \
    "ghcr.io/significa/fly-pg-dump-to-s3" \
