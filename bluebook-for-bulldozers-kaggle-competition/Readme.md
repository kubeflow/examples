# Objective

This example is based on the Bluebook for bulldozers competition. The objective of this exercise is to predict the sale price of bulldozers sold at auctions.

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2 and x86-64 and ARM based system which includes all Intel and AMD based CPU's and M1/M2 series Macbooks.




























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

Lets accept Rules of Bulldozers competition 
![kaggle-secret-error-02](https://user-images.githubusercontent.com/17012391/175291406-7a30e06d-fc05-44c3-b33c-bccd31b381bd.PNG)

Click on "I Understand and Accept". After this you will be prompted to verify your account using your phone number:
![kaggle-secret-error-03](https://user-images.githubusercontent.com/17012391/175291608-daad1a47-119a-4e47-b48b-4f878d65ddd7.PNG)

Add your phone number and Kaggle will send the code to your number, enter this code and verify your account. ( Note: pipeline wont run if your Kaggle account is not verified )

## Success
After the kaggle account is verified pipeline run is successful we will get the following:

<img width="1380" alt="Screenshot 2022-06-10 at 12 04 48 AM" src="https://user-images.githubusercontent.com/17012391/172920115-ccefd333-c500-4577-afcb-8487c2208371.png">


