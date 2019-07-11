# Prediction

Open AI Platform and navigate to your [model](https://console.cloud.google.com/ai-platform/models), there is one model listed: 
![ai platform models](files/models.png)

Open the model and choose your version then click on the Tab `TEST & USE` and enter the following input data:

```
{"instances":  ["London on Monday evening"]}
```
![ai platform predict](files/predict.png)

After a couple of seconds, you get the prediction response

```json
{
  "predictions": [
    [
      "B-geo",
      "O",
      "B-tim",
      "I-tim",
       ]
  ]
}
```

*Previous*: [Monitor the training](step-6-monitor-training.md)