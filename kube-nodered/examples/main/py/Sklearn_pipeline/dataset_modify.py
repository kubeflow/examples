def modify_python_file(file_path, new_code):
    # 打開文件並讀取內容
    with open(file_path, 'r') as file:
        content = file.read()

    start_tag = "    # START_DATASET_CODE"
    end_tag = "    # END_DATASET_CODE"

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

new_code = "    dataset = tf.keras.datasets.mnist"
#new_code = "    dataset = tf.keras.datasets.cifar10"
file_path = "./target.py"

modify_python_file(file_path, new_code)
