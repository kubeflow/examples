def modify_python_file(file_path, new_code):
    # 打開文件並讀取內容
    with open(file_path, 'r') as file:
        content = file.read()

    start_tag = "        # START_MODEL_CODE"
    end_tag = "        # END_MODEL_CODE"

    start_index = content.find(start_tag)
    end_index = content.find(end_tag)

    if start_index != -1 and end_index != -1:
        old_code = content[start_index:end_index + len(end_tag)]
        replacement = start_tag + '\n' + new_code + '\n' + end_tag
        content = content.replace(old_code, replacement)
        with open(file_path, 'w') as file:
            file.write(content)
        print("File modified successfully.")
    else:
        print("Custom code tags not found.")

input_shape = '(32,32,3)'
new_code = "        return tf.keras.models.Sequential([tf.keras.layers.Flatten(input_shape = ",input_shape,"),tf.keras.layers.Dense(512, activation = 'relu'),tf.keras.layers.Dropout(0.2),tf.keras.layers.Dense(256, activation = 'relu'),tf.keras.layers.Dropout(0.2),tf.keras.layers.Dense(10, activation = 'softmax')])" #NN
#new_code = "        from sklearn.ensemble import RandomForestClassifier\n        return RandomForestClassifier(n_estimators=100, criterion = 'gini')"
file_path = "./pipeline.py"

modify_python_file(file_path, new_code)
