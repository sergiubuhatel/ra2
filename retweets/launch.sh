docker run --gpus all -it --rm \
    -v /home/ra2/retweets:/workspace \
    -v /home/ra2/retweets:/data \
    rapidsai/base:25.12-cuda12-py3.10 \
    bash
