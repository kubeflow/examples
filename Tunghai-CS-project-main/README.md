目的 :

這是一個node-red搭配kubeflow的作品，node-red作為畫面顯示，而kubeflow則是資料處理。在這個作品我將LSTM、mnist節點放在node-red，點擊該節點後，kubeflow則執行對應模型，模型所使用的輸入資料是normal.csv & abnormal.csv，輸出則是資料經模型訓練後的準確度。

安裝 :

1. 將檔案 git clone 到 windows/System32
2. 執行 Docker
3. 執行 Wsl 並依序輸入 cd kube-nodered,  cd examples, 最後是 ./run.sh 1.connect-kubeflow
4. 查 Docker 是否有生成的容器和映像檔
5. 執行 Docker 映像檔並執行 node-red
6. 執行 node-red後, 點擊 'intsall dependency', 接著使用者可以在'six pipeline' 頁面執行模型
7. 到路徑 kube-nodered\examples\1.connect-kubeflow\py 中調整目錄底下的模型Python檔案，將登錄帳密改為使用者的
===============================================================================

架構 :

客製化節點的關鍵在於更改.flows.json、加入js.和html到nodepipe資料夾、加入模型python到py資料夾和加入模型pipeline到pipeline資料夾。node-red顯示的部分 :  .flow.json更改會影響node-red節點的顯示，nodepipe的js.和html可以客製一個節點的功能欄位，如下拉選單。Kubeflow執行的部分 : 模型的python和pipeline。
以下是各個檔案的路徑
1.	C:\Windows\System32\kube-nodered\examples\1.connect-kubeflo的.flow.json
2.	C:\Windows\System32\kube-nodered\examples\1.connect-kubeflow\node_modules\nodepipe的js.和html
3.	C:\Windows\System32\kube-nodered\examples\1.connect-kubeflow\py的模型python
4.	C:\Windows\System32\kube-nodered\examples\1.connect-kubeflow\py\pipelines的模型pipeline
5.	
================================================================================

輸入和輸出 :

輸入資料
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/773957ef-5aeb-4321-b0b2-8dfd712c1356)
輸出結果
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/721fba7b-5aaf-4539-bd54-9f40b4d63de8)

=================================================================================

操作說明 :

打開node-red後，先點擊圖中按鈕，安裝所需套件
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/653de771-bba0-4408-acbb-a5174e34475f)
點擊圖中圓圈，切換分頁到模型節點
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/82516d3f-4c72-4ee0-89cf-79aa699ce51e)
切換後的分頁
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/2b89c8cc-4c89-44d5-9a4a-52e69be2170e)
點擊圖中按鈕，kubeflow會執行對應pipeline
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/16fb3142-a75b-42e7-a7c3-13bb8b955765)
可在畫面右側確認執行狀況，圖中範例為LSTM pipeline正在執行
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/90829686-8627-4304-9047-1151ac02f59f)
在node-red上點擊執行後，可在kubeflow上看到新增的執行pipeline
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/f6fd314e-7365-430c-978f-ca1ab0f18e18)
Kubeflow上的執行結果
![image](https://github.com/NootNoot0/Tunghai-CS-project/assets/161794667/ba16438c-92bd-4f04-b369-b191abfd97f5)










