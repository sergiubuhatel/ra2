sudo -E docker run --rm --gpus all \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  --name omnisci \
  -v /home/ra2/omnisci/omnisci-docker-storage:/omnisci-storage \
  -v /home/ra2:/data \
  -p 6273-6280:6273-6280 \
  omnisci/core-os-cuda:latest
