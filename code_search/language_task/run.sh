#!/usr/bin/env bash

set -e

if [[ -z $DOCKER_ENTRYPOINT ]]; then
    echo "ERROR: Missing DOCKER_ENTRYPOINT environment variable! Use 't2t-datagen' or 't2t-trainer'"
    exit 1
fi

IMAGE_TAG=${IMAGE_TAG:-semantic-code-search:devel}

DOCKER_RUN_OPTS="-it --rm --entrypoint=$DOCKER_ENTRYPOINT"

# Mount a local data directory into the container
if [[ ! -z $DATA_DIR ]]; then
    DOCKER_RUN_OPTS="$DOCKER_RUN_OPTS -v $DATA_DIR:/data:rw"
fi

DOCKER_CMD="$@ --t2t_usr_dir=/t2t_problems --tmp_dir=/tmp --data_dir=/data"

# Mount output directory for model outputs
if [[ $DOCKER_ENTRYPOINT = "t2t-trainer" ]]; then
    if [[ -z $OUTPUT_DIR ]]; then
        echo "ERROR: Missing OUTPUT_DIR environment variable!"
        exit 1
    fi
    DOCKER_RUN_OPTS="$DOCKER_RUN_OPTS -v $OUTPUT_DIR:/train:rw"
    DOCKER_CMD="$DOCKER_CMD --output_dir=/train"
fi

CMD="docker run $DOCKER_RUN_OPTS $IMAGE_TAG $DOCKER_CMD"

echo "$CMD"
eval $CMD
