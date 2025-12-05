# Windows Filename Sanitizer (Python Version)

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

这是一个 Windows 桌面工具，用于自动修正文件保存对话框中的非法文件名。

## 许可证 (License)

本项目采用 **CC BY-NC-SA 4.0** (署名-非商业性使用-相同方式共享 4.0 国际) 协议进行许可。

这意味着您可以：
*   **共享** — 在任何媒介以任何形式复制、发行本作品。
*   **演绎** — 修改、转换或以本作品为基础进行创作。

只要您遵守以下条件：
*   **署名** — 您必须给出适当的署名，提供指向本许可协议的链接，同时标明是否（对原始作品）作了修改。
*   **非商业性使用** — 您**不得**将本作品用于商业目的。
*   **相同方式共享** — 如果您再混合、转换或者基于本作品进行创作，您必须基于与原先许可协议相同的许可协议分发您贡献的作品。

详细信息请参阅 [LICENSE](LICENSE) 文件。

## 功能

1.  **剪贴板自动净化**：当你复制包含非法字符（如 `|`, `*`, `?`）的文本时，它会自动将其替换为下划线 `_`，方便你直接粘贴。
2.  **对话框自动修正**：自动检测活动的 "另存为" (Save As) 窗口，如果文件名输入框中包含非法字符，会自动修正。

## 安装与运行

你需要安装 Python 环境。

1.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

2.  运行程序：
    ```bash
    python main.py
    ```

3.  保持程序在后台运行即可。

## 打包为 EXE (可选)

如果你想生成一个独立的 .exe 文件，可以使用 pyinstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

生成的文件位于 `dist/main.exe`。

## 注意事项

- 程序需要识别窗口标题，目前支持中文 "另存为" 和英文 "Save As"。
- 如果遇到权限问题，请尝试以管理员身份运行。
