# Custom prediction routine

Allow us to determine which code runs when sending a prediction request.
Without custom prediction routine the machine learning framework handles the prediction operation.
With custom prediction routine we can define custom code which runs for each prediction request.

## Why custom prediction routine
Our model requires numeric inputs, remember the preprocessing steps.
This is very unhandy if we want to use our model with raw text.
To support preprocessing also on prediction time we have to define a custom prediction route.

> Without custom prediction routine we would need to implement this preprocessing in an additional wrapper, for example, App Engine or Cloud Function. Which adds complexity and latency.

## How is it working?

Our custom prediction routine requires five parts

* `keras_saved_model.h5` - The model stored as part of our training component (artifact).
* `processor_state.pkl` - The preprocessing state stored as part of our training component (artifact).
* `model_prediction.py` - The custom prediction routine logic.
* `text_preprocessor.py` - The pre-processing logic.  
* `custom_prediction_routine.tar.gz` - A Python package `tar.gz` which contains our implementation.
* `setup.py` - Used to create the Python package. 

To build our custom prediction routine run the build script located `/routine/build_routine.sh`. This will create a `tar.gz` which is required when we deploy our model. 

Navigate to the routine folder `/routine/` and run the following build script:

```bash
$ sh build_routine.sh
```

## Upload custom prediction routine to Google Cloud Storage

```bash
gsutil cp custom_prediction_routine-0.2.tar.gz gs://${BUCKET}/routine/custom_prediction_routine-0.2.tar.gz
```

*Next*: [Run the pipeline](step-5-run-pipeline.md)

*Previous*: [Upload the dataset](step-3-upload-dataset.md)