sudo -E docker run --runtime=nvidia \
  --name omnisci \
  -v /home/ra2/omnisci/omnisci-docker-storage:/omnisci-storage \
  -v /home/ra2:/mnt/data \
  -p 6273-6280:6273-6280 \
  omnisci/core-os-cuda:latest