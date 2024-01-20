def modify_python_file(file_path, new_code):
    # 打開文件並讀取內容
    with open(file_path, 'r') as file:
        content = file.read()

    # 定義要替換的片段的開始和結束標記
    start_tag = "# START_CUSTOM_CODE"
    end_tag = "# END_CUSTOM_CODE"

    # 找到標記的位置
    start_index = content.find(start_tag)
    end_index = content.find(end_tag)

    if start_index != -1 and end_index != -1:
        # 提取標記之間的內容
        old_code = content[start_index:end_index + len(end_tag)]

        # 創建新的片段，包括新的代碼
        replacement = start_tag + '\n' + new_code + '\n' + end_tag

        # 替換舊的片段
        content = content.replace(old_code, replacement)

        # 將修改後的內容寫回文件
        with open(file_path, 'w') as file:
            file.write(content)

        print("File modified successfully.")
    else:
        print("Custom code tags not found.")

dataset = "cifar10"

# 要插入的新代碼
new_code = "dataset = " + dataset

# 要修改的文件的路徑
file_path = "./test_target.py"

# 調用函數進行修改
modify_python_file(file_path, new_code)
