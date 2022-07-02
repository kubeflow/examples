# Objective

This example is based on the Titanic OpenVaccine competition. The objective of this exercise is to develop models and design rules for RNA degradation.

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2 and x86-64 based system which includes all Intel and AMD based CPU's. 


## Frequently encountered errors:
While running the pipeline as mentioned above you may come across this error:
![kaggle-secret-error-01](https://user-images.githubusercontent.com/17012391/175290593-aac58d80-0d9f-47bd-bd20-46e6f5207210.PNG)

errorlog:

```
kaggle.rest.ApiException: (403)
Reason: Forbidden
HTTP response headers: HTTPHeaderDict({'Content-Type': 'application/json', 'Date': 'Thu, 23 Jun 2022 11:31:18 GMT', 'Access-Control-Allow-Credentials': 'true', 'Set-Cookie': 'ka_sessionid=6817a347c75399a531148e19cad0aaeb; max-age=2626560; path=/, GCLB=CIGths3--ebbUg; path=/; HttpOnly', 'Transfer-Encoding': 'chunked', 'Vary': 
HTTP response body: b'{"code":403,"message":"You must accept this competition\\u0027s rules before you\\u0027ll be able to download files."}'

```
This error occours for two reasons:
- Your Kaggle account is not verified with your phone number.
- Rules for this specific competitions are not accepted.

Lets accept Rules of competition 
![rules](https://user-images.githubusercontent.com/17012391/175306310-10808262-07ce-4952-8fb0-3b7754e9fb46.png)

Click on "I Understand and Accept". After this you will be prompted to verify your account using your phone number:
![kaggle-secret-error-03](https://user-images.githubusercontent.com/17012391/175291608-daad1a47-119a-4e47-b48b-4f878d65ddd7.PNG)

Add your phone number and Kaggle will send the code to your number, enter this code and verify your account. ( Note: pipeline wont run if your Kaggle account is not verified )

## Success
After the kaggle account is verified pipeline run is successful we will get the following:
<img width="1244" alt="Screenshot 2022-06-06 at 3 00 51 PM" src="https://user-images.githubusercontent.com/17012391/172135040-50d6e9f3-d156-4e95-9b9f-492e99108d82.png">
