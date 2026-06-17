# 导入 os 模块
import os

# 定义一个函数用于获取当前文件夹文件：
def get_current_folder_files():

    """
    功能：获取当前脚本所在目录下的所有文件以及子文件夹内的所有文件(排除了文件夹)
    返回值：一个包含脚本所在目录以及此目录下的所有子文件夹目录的列表(排除了文件夹)
    """

    # 获取脚本当前位置的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 在get_current_folder_files函数内部定义一个递归函数将当前目录下所有文件和文件夹名称，并返回一个列表:
    def get_files_recursion_from_dir(current_dir):
        items = []
        if os.path.exists(current_dir):
            for f in os.listdir(current_dir):
                new_path = current_dir + "/" + f
                if os.path.isdir(new_path):
                    items += get_files_recursion_from_dir(new_path)
                elif os.path.isfile(new_path):
                    items.append(new_path)

        else:
            print(f"指定的目录:{current_dir},不存在")
            return []
        return items

    # 将递归函数的返回值定义成一个变量:
    items = get_files_recursion_from_dir(current_dir)

    # 将函数的得到的列表返回出来:
    return items

# 定义一个函数用于写入txt文件:
def write_to_txt(items):

    """
    功能：将传入的文件名称写入到 txt 文件中
    参数：items - 包含文件名称的列表(排除了文件夹)
    返回值：生成的 txt 文件的绝对路径
    """

    # 定义输出文件的名称
    output_filename = "test_文件列表.txt"

    # os.getcwd() 获取当前工作目录（Current Working Directory）
    # os.path.join() 将目录和文件名安全地拼接成完整路径，自动处理不同操作系统的路径分隔符（如Windows的\和Linux的/）
    file_path = os.path.join(os.getcwd(), output_filename)

    # 使用 with 语句打开文件,确保文件操作完成后会自动关闭,使用w写入模式防止多次运行导致报错,w模式可覆盖原文件
    with open(file_path, "w", encoding='UTF-8') as f:

        # 写入标题和分隔线
        f.write("文件内容列表\n")
        f.write("=" * 30 + "\n")

        # 初始化文件数量和文件夹数量的计数器
        files_count = 0

        # 遍历传入的列表
        for item in items:

            # 拼接出当前遍历项目的完整绝对路径，用于后续判断它是文件还是文件夹
            item_path = os.path.join(os.getcwd(), item)

            # os.path.isfile() 怕毛短该路径是否是一个文件
            # split切分用与获取目录下需要的部分(文件名)
            if os.path.isfile(item_path):
                item = item.split("/")[-1]
                f.write(f"[文件] {item}\n")
                files_count += 1

        # 写入统计汇总信息
        f.write("\n" + "=" * 30 + "\n")
        f.write(f"总计: {len(items)} 个项目\n")
        f.write(f"文件数量: {files_count}\n")
        f.write(f"文件夹数量: 0 \n")

    # 返回值:当前目录/指定的文件名(test_文件列表)
    return file_path

# 请定义一个主体函数:
def main():

    """
    功能：脚本的主控制流程，协调各个函数并输出控制台提示
    """
    # print语句打印脚本运行状态
    print("请等待")

    # 调用函数获取文件列表
    list = get_current_folder_files()

    # 定义一个空列表用于储存处理后的数据
    file_list = []
    # 使用for循环对get_current_folder_files函数的返回值进行进一步处理
    for item in list:
        # 定义一个空字符
        str_list = ""
        # 将遍历出的列表变为字符串
        str_list += item
        # 用replace将目录中的\替换为/
        str_list = str_list.replace("\\", "/")
        # 将本次遍历得到的列表处理后的追加进file_list空列表中
        file_list.append(str_list)

    # 将列表定义为指定变量"items"
    items = file_list
    # 调用write_to_txt函数进行数据写入并保存
    output_file = write_to_txt(items)
    # 告知使用者文件存储在了哪个位置,write_to_txt函数的返回值就是文件的位置
    print(f"脚本已工作完成,我文件列表已保存至: {output_file} ")
    # 告知用户总共扫描到了多少个项目,使用len函数统计列表中的顶层有多少个元素
    print(f"共扫描到 {len(items)} 个项目")

    # 在控制台再次计算并显示统计信息(使用生成器表达式和sum函数进行快速统计)
    files_count = sum(1 for item in items if os.path.isfile(os.path.join(os.getcwd(), item)))
    # 通过print语句打印告知使用者当前一共收录了多少个文件/文件夹
    print(f"其中文件: {files_count} 个，文件夹: 0 个")

if __name__ == '__main__':
    main()
