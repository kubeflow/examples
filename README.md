# Chinese-multiperson-voice-recognition-using-transfer-learning
This is an example of applying transfer learning to the Chinese multi-person voice recognition application.  Transfer learning is an AI technique used to enhance the training accuracy of use cases when the dataset is small or the training accuracy is low given the high noise of the original dataset.  Multi-person voice recognition is known to contain high noise in the dataset.  Chinese voice voice recognition has gained much progress recently thanks to the effort by the big name company such as Google.  However many issues remain unsolved.  Multi-person Chinese voice recognition is one of them.  This example provieds not only multi-person Chinese voice sample dataset, but applied a transfer learning technique to the CNN trained model of the Chinese voice samples dataset.  Satisfactory results can be achieved through transfer learning after an initial CNN training.
This example provides a feasibility evidence of the transfer learning techniques, and it is our wish to convert the transfer learning technique to a Kubeflow asset through this illustration case.  A transfer learning pipeline will be constructed to make kubeflow user easy to adapt to their model for training accuracy enhancement.  Eventually, other users can benefit from such convenient features of the kubeflow resources.

usage briefing:
1.Process audio files and convert them into spectrograms.
2.Establish experimental data, divide them into 3 categories, and set them into CNN network training.
3.Perform two training sessions to improve accuracy.
4.Compare training methods.

Tools used:
1. TensorFlow
2. Anaconda
3. Python3.7

1. preprocess(spectrograms production)

![image](https://user-images.githubusercontent.com/58965086/122675714-48a34700-d20d-11eb-81d7-865209ac8367.png)

2. import spectrogram files.
![image](https://user-images.githubusercontent.com/58965086/122675748-712b4100-d20d-11eb-96cd-1523b9329020.png)

![image](https://user-images.githubusercontent.com/58965086/122675762-8011f380-d20d-11eb-90db-f7b8942571d5.png)

3. build training dataset:
divide the dataset into training, validation, and testing sets.

![image](https://user-images.githubusercontent.com/58965086/122675818-b8b1cd00-d20d-11eb-836a-08fa3e870823.png)

4. build CNN taining:

![image](https://user-images.githubusercontent.com/58965086/122675838-d54e0500-d20d-11eb-8076-8dc78600a779.png)

5. first training
![image](https://user-images.githubusercontent.com/58965086/122675851-e565e480-d20d-11eb-8ad4-4dada12f70a0.png)
![image](https://user-images.githubusercontent.com/58965086/122675854-ea2a9880-d20d-11eb-82f8-4ad9fc506386.png)

6. first training result:
![image](https://user-images.githubusercontent.com/58965086/122675877-03cbe000-d20e-11eb-8f64-1c4ad9cec5a8.png)

7. visualize the result
![image](https://user-images.githubusercontent.com/58965086/122675890-1b0acd80-d20e-11eb-84da-1793cac58fe2.png)

![image](https://user-images.githubusercontent.com/58965086/122675896-2100ae80-d20e-11eb-8901-240b7d9b3566.png)

8. import VGG16 model
![image](https://user-images.githubusercontent.com/58965086/122675911-37a70580-d20e-11eb-95ab-a4a652fa79ab.png)
![image](https://user-images.githubusercontent.com/58965086/122675916-3e357d00-d20e-11eb-99ab-a5d22facba9c.png)

9. use conv_base model to extract features and labels
![image](https://user-images.githubusercontent.com/58965086/122675969-7937b080-d20e-11eb-885d-c5f202b3457a.png)

10. training
![image](https://user-images.githubusercontent.com/58965086/122676010-92d8f800-d20e-11eb-8826-5b599bc78b4b.png)

11. visualize the results
![image](https://user-images.githubusercontent.com/58965086/122676032-a71cf500-d20e-11eb-82fc-a2a468340a53.png)

12. build confusion matrix
![image](https://user-images.githubusercontent.com/58965086/122676055-c1ef6980-d20e-11eb-81af-c394696124c7.png)

13. visualiz the confusion matrix
![image](https://user-images.githubusercontent.com/58965086/122676069-d7fd2a00-d20e-11eb-8dcb-064f8406e9a4.png)

14. sample Chinese multiperson voice spectrogram files are added
15. sample VGG16 transfer learning code: vgg16.ipynb is added to the repository 
 

