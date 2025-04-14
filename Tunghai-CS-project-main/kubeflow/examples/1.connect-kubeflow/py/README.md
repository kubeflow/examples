## How to use
```
KUBEFLOW_HOST=<your-kubeflow-instance-endpoint> \
KUBEFLOW_USERNAME=<your-username-account> \
KUBEFLOW_PASSWORD=<your-password> \
python3 <file-index>
```
## three pipelines
流程架構:
create_experiment -> upload_pipeline -> create_run -> get_run -> filter -> result
### decisionTree.py
功能：以乳癌資料集訓練decisionTree模型並回傳準確率

### logisticRegression.py
功能：以乳癌資料集訓練logisticRegression模型並回傳準確率

### randomForest.py
功能：以乳癌資料集訓練randomForest模型並回傳準確率
