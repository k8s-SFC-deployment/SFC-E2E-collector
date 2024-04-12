# E2E_COLLECTOR_URL=http://<my-url>:<my-port>
# SFC_PATH=http://<vnf-1-url>:<vnf-1-port>/loadv2,http://<vnf-2-url>:<vnf-1-port>/loadv2

if [[ -z "${E2E_COLLECTOR_URL}" ]]; then
  echo "env(E2E_COLLECTOR_URL) is required"
  exit -1
fi

if [[ -z "${SFC_PATH}" ]]; then
  echo "env(SFC_PATH) is required"
  exit -1
fi

E2E_COLLECTOR_REQUEST_URL=${E2E_COLLECTOR_URL}/start?end_url=$(urlencode ${E2E_COLLECTOR_URL}/end)

while true; do
  curl -X 'POST' $E2E_COLLECTOR_REQUEST_URL \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@README.md' \
  -F "path=$SFC_PATH"
done