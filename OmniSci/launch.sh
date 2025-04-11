sudo -E docker run --runtime=nvidia \
  --name omnisci \
  -v /home/ra2/omnisci/omnisci-docker-storage:/omnisci-storage \
  -v /home/ra2:/mnt/data \
  -v /home/ra2/omnisci/server.conf:/omnisci/config/server.conf \
  -p 6273-6280:6273-6280 \
   omnisci/core-os-cuda:latest