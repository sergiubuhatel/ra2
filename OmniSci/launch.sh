sudo -E docker run --runtime=nvidia \
  --name omnisci \
  -v /home/ra2/omnisci/omnisci-docker-storage:/omnisci-storage \
  -p 6273-6280:6273-6280 \
  omnisci/core-os-cuda:latest
