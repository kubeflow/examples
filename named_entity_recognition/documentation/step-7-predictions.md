# Prediction

To use the trained and deployed model please open AI Platform and navigate to your model. 

It should look similar to this: 

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