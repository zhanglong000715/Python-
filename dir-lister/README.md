下面我讲述一下test_1与test_3的用途:

test_1：
核心功能是收集脚本当前目录下的所有文件名和子文件夹名（不包括这些子文件夹内部的任何文件）。然后，它会在同一目录下创建一个自定义名称的 .txt 文件，并将所有收集到的数据写入其中。
dir-lister：
在 test_1 的基础上，该脚本利用递归函数来升级并覆盖原有的核心功能。dir-lister 会收集脚本当前目录下的所有文件名，包括嵌套在子目录中的所有文件，同时严格排除所有文件夹名称。

test_1:
The core functionality is to collect all file names and subfolder names within the script's current directory (excluding any files inside those subfolders). It then creates a custom-named .txt file in the same directory and writes all the collected data into it.
dir-lister:
Building upon test_1, this script utilizes a recursive function to upgrade and override the original core functionality. dir-lister collects all file names within the script's current directory, including all files nested in subdirectories, while strictly excluding all folder names.

使用须知：
    请在保证拥有权限的情况下运行脚本，否则会出现拒绝访问的报错.
