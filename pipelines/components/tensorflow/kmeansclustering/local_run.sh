docker run -v $GOOGLE_APPLICATION_CREDENTIALS:/credentials.json -e "GOOGLE_APPLICATION_CREDENTIALS=/credentials.json" <TAG> \
    --npy_uri gs://sandboxdata/cmle-pipelines/X.npy \
    --num_iterations 10 \
    --num_clusters 5 \
    --use_mini_batch False \
    --initial_clusters random \
    --distance_metric squared_euclidean \
    --random_seed 0 \
    --mini_batch_steps_per_iteration 1 \
    --kmeans_plus_plus_num_retries 2