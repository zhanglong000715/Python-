# 导入 os 模块
import os


def get_current_folder_files():
    """
    功能：获取当前脚本所在文件夹的所有文件和子文件夹名称
    返回值：一个包含当前目录下所有项目（排除脚本自身）名称的列表
    """
    # __file__ 是Python的内置属性，表示当前脚本的文件路径
    # os.path.abspath(__file__) 获取脚本的绝对路径
    # os.path.dirname() 提取绝对路径中的目录部分，即脚本所在的文件夹路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # os.listdir() 读取指定目录下的所有文件和文件夹名称，返回一个列表
    items = os.listdir(current_dir)

    # os.path.basename() 提取路径中的文件名部分（包含扩展名）
    script_name = os.path.basename(__file__)

    # 使用列表推导式过滤掉脚本自身，避免把脚本自己也算进文件列表中
    filtered_items = [item for item in items if item != script_name]

    return filtered_items


def write_to_txt(items):
    """
    功能：将传入的文件和文件夹名称列表写入到 txt 文件中，并设置只读权限
    参数：items - 包含文件和文件夹名称的列表
    返回值：生成的 txt 文件的绝对路径
    """
    # 定义输出文件的名称
    output_filename = "文件列表.txt"

    # os.getcwd() 获取当前工作目录(Current Working Directory)
    # os.path.join() 将目录和文件名安全地拼接成完整路径，自动处理不同操作系统的路径分隔符（如Windows的\和Linux的/）
    file_path = os.path.join(os.getcwd(), output_filename)

    # 使用 with 语句打开文件，确保文件操作完成后会自动关闭，防止内存泄漏
    # 'w' 表示写入模式(会覆盖原文件)，encoding='utf-8' 确保支持中文等多语言字符
    with open(file_path, 'w', encoding='utf-8') as f:
        # 写入标题和分隔线
        f.write("文件夹内容列表\n")
        f.write("=" * 30 + "\n")

        # 初始化文件数量和文件夹数量的计数器
        files_count = 0
        folders_count = 0

        # 遍历传入的列表
        for item in items:
            # 拼接出当前遍历项目的完整绝对路径，用于后续判断它是文件还是文件夹
            item_path = os.path.join(os.getcwd(), item)

            # os.path.isfile() 判断该路径是否是一个文件
            if os.path.isfile(item_path):
                f.write(f"[文件] {item}\n")  # 使用 f-string 格式化字符串
                files_count += 1
            # os.path.isdir() 判断该路径是否是一个目录（文件夹）
            elif os.path.isdir(item_path):
                f.write(f"[文件夹] {item}\n")
                folders_count += 1

        # 写入统计汇总信息
        f.write("\n" + "=" * 30 + "\n")
        f.write(f"总计: {len(items)} 个项目\n")  # len() 获取列表的总长度
        f.write(f"文件数量: {files_count}\n")
        f.write(f"文件夹数量: {folders_count}\n")

    # ================= 权限设置部分 =================
    # os.chmod() 用于修改文件的访问权限
    # 0o444 是八进制表示法，代表 Unix/Linux 系统下的只读权限 (r--r--r--)
    os.chmod(file_path, 0o444)

    # 针对 Windows 系统的特殊处理：使用 stat 模块设置只读属性
    try:
        import stat  # 导入 stat 模块，提供文件状态和权限相关的常量
        # stat.S_IREAD 是 Windows 下表示只读属性的常量
        os.chmod(file_path, stat.S_IREAD)
    except:
        # 如果导入或执行失败（例如在非Windows系统上），则忽略异常
        pass

    return file_path


def main():
    """
    功能：脚本的主控制流程，协调各个函数并输出控制台提示
    """
    print("正在扫描当前文件夹...")
    # 调用函数获取文件列表
    items = get_current_folder_files()

    # 如果列表为空，说明文件夹里没有其他东西，直接结束程序
    if not items:
        print("当前文件夹为空或没有找到任何项目")
        return

    # 调用写入函数，并接收返回的文件路径
    output_file = write_to_txt(items)
    print(f"已完成！文件列表已保存至: {output_file}")
    print(f"共扫描到 {len(items)} 个项目")

    # 在控制台再次计算并显示统计信息（使用生成器表达式和 sum 函数进行快速统计）
    files_count = sum(1 for item in items if os.path.isfile(os.path.join(os.getcwd(), item)))
    folders_count = sum(1 for item in items if os.path.isdir(os.path.join(os.getcwd(), item)))
    print(f"其中文件: {files_count} 个，文件夹: {folders_count} 个")


# Python 的标准入口检查
# 当脚本被直接运行时，__name__ 的值会被设置为 "__main__"
# 如果该脚本被其他文件 import 导入，则不会自动执行 main()，提高了代码的复用性
if __name__ == "__main__":
    main()
