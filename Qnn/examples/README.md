

https://hackmd.io/cocSOGQMR-qzo7DHdwgRsQ

本篇在講述使用者如何透過修改html和javascript檔案來新增一個演算法，以利使用者在 Node-RED 平台的 autoAI pipeline 中整合多種機器學習演算法。


# 目錄
[TOC]
## **後端 (JavaScript)**


若您希望新增或修改機器學習演算法，以下步驟將協助您完成這項任務。

在 model_func 函式中定義演算法建立方式：
1. 進入 create_model() 函式：根據所選擇的演算法，修改 create_model() 函式的部分，例如從 RandomForestClassifier 改為其他的演算法建模方式。

2. 修改模型建立程式碼：
* 根據所選擇的演算法，使用相對應的機器學習套件及演算法來建立模型。
* 請確認模型建立的方式符合所選擇演算法的需求及參數配置。

3. 注意事項：
* 修改程式碼時請小心，確保函式返回值和參數配置符合所選擇的演算法。
* 事前了解所選擇演算法的特性及文件，以便正確修改 create_model() 函式。

### **snippets.js**

```python=
def create_model():
    # START_MODEL_CODE
    # 在此更改以新增或更改演算法的模型建立程式碼
    from sklearn.ensemble import RandomForestClassifier
    # 根據選擇的演算法，更改下列程式碼片段
    return RandomForestClassifier(n_estimators=%s, criterion='%s', max_depth=%s, min_samples_split=%s, min_samples_leaf=%s)
    # END_MODEL_CODE
        
model = create_model()
```
  
### **更改 base_image 步驟：**

* 在 func_to_container_op() 中指定了 base_image以符合特定演算法的映像。
* packages_to_install要根據package的不同進行修改。

### **修改 pipeline_name 步驟：**

* 使用者可以根據不同的演算法，修改 pipeline_name 變數以標示所建立 Pipeline 的名稱。

```python=
def randomforest_pipeline(epochs=%s, model_name="%s"):
# END_DEPLOY_CODE
    ...
    load_data_op = func_to_container_op(
        func=load_data_func,
        base_image="tensorflow/tensorflow:2.14.0",
        packages_to_install=["pandas","minio"]
    )
    ... 
pipeline_name='randomforest_pipeline{}.yaml'.format('%s')
kfp.compiler.Compiler().compile(randomforest_pipeline, pipeline_name)
```

### **演算法整合**

用途: 在 Node-RED 流程中整合演算法。

### **如何新增/修改演算法：**
新增演算法：

* 在 Algorithm 建構子中註冊新演算法。
* 創建新演算法的函式，處理其特定參數。

修改現有演算法：

* 更新現有演算法函式或根據需要新增新的函式。
* 確保這些函式根據 Node-RED 介面中提供的配置生成腳本。

### **algorithm.js**
```javascript=
const util = require('util');
const snippets = require('../snippets');

module.exports = function(RED) {
    function Algorithm(config) {
        RED.nodes.createNode(this, config);
        var node = this;

        // RandomForest 演算法函式
        function randomForest(msg) {
            const script = util.format(snippets.RANDOMFOREST, config.n_estimators, config.criterion, config.max_depth, config.min_samples_split, config.min_samples_leaf);
            msg.payload += script;
            return msg;
        }
        ...

        node.on('input', function(msg) {
            switch (config.algorithm) {
                case "randomforest":
                    msg = randomForest(msg);
                    break;
                ...
            
            msg.algorithm = config.algorithm;
            node.send(msg);
        });
    }

    RED.nodes.registerType("algorithm", Algorithm);
}
```



## **前端 (HTML/模板)**

### **用途:**
* 提供用於在 Node-RED 編輯器中配置演算法參數的使用者介面。

### **如何更新:**
* 新增/修改與每個演算法參數相對應的欄位。
* 確保 UI 元素與後端 JavaScript 中每個演算法的函式相關聯。


使用者需更新 defaults 部分，加入新演算法所需的預設參數。這些參數將顯示在使用者界面上，供使用者進行配置。

在 RED.nodes.registerType('algorithm', {... 部分，根據新演算法的需求添加相應的邏輯。例如，在 function algorithm(config) {... 中加入新演算法的處理邏輯。



### **algorithm.html**
```javascript=
<script type="text/javascript">
    RED.nodes.registerType('algorithm', {
        category: 'autoAI pipeline',
        color: '#2E8B57',
        defaults: {
            name: {value:""},
            algorithm: {value:"", required:true},
            n_estimators: {
                 value: "100",
                 required: true,
                 validate: function(x) {
                    return /^(?:[1-9]\d{2,}|[1-9]\d|10)$/.test(x);
                }
            },
            ...                   
        },
        ...
```

在 JavaScript 代碼中，可能需要修改 algorithmValue 的邏輯，以支援新增的演算法。當使用者選擇新演算法時，確保相關的界面欄位能夠顯示，例如透過 $(".toggle-new_algorithm").show(); 的方式。

```javascript=
if(algorithmValue === "randomforest"){
    $(".toggle-common, .toggle-randomforest").show();
    ...
}
```


使用者可根據需求在 HTML 代碼中新增新演算法所需的特定欄位。例如，若要新增名為 new_algorithm 的演算法，需在 HTML 中加入與此演算法相關的欄位。

```htmlembedded=
<!-- Random Forest Specific Fields -->
<div class="form-row toggle-randomforest">
    <label for="node-input-n_estimators"><i class="fa"></i>n_estimators</label>
    <input type="number" min="10" id="node-input-n_estimators" />
</div>

<!-- Other Specific Fields -->
<!-- Add other specific fields for Random Forest here -->

```
