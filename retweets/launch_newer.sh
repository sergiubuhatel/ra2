docker run --gpus all -it --rm \
    -v /home/ra2/retweets:/workspace \
    -v /home/ra2/retweets:/data \
    rapidsai/base:26.02a-cuda13-py3.13 \
    bash
