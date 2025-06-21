# PDF水印工具 (PDF Watermarker)

一个简单易用的PDF水印工具，可以为PDF文件添加自定义水印，特别支持中文字符。

## 功能特点

- 为PDF文件添加文字水印
- 完全支持中文水印
- 内置中文字体选择器
- 可自定义水印文字、颜色、透明度、角度等属性
- 提供图形用户界面(GUI)和命令行界面
- 支持批量处理多个PDF文件

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/wangqiannian6/PDF_watermaker.git
cd PDF_watermaker
```

### 2. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv pdfenv

# 激活虚拟环境
# Windows:
pdfenv\Scripts\activate
# Linux/Mac:
# source pdfenv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 图形界面

运行以下命令启动图形界面：

```bash
python pdf_watermark_gui.py
```

1. 点击"浏览..."选择输入PDF文件
2. 指定输出PDF文件路径
3. 输入水印文字
4. 点击"选择中文字体"按钮选择合适的中文字体
5. 调整水印参数（透明度、角度、字体大小、颜色）
6. 点击"添加水印"按钮处理文件

### 命令行

```bash
python pdf_watermark.py --input input.pdf --output output.pdf --text "机密文件" --font C:\Windows\Fonts\simhei.ttf
```

参数说明：
- `--input`: 输入PDF文件路径
- `--output`: 输出PDF文件路径
- `--text`: 水印文字内容
- `--opacity`: 水印透明度 (0.0-1.0)
- `--angle`: 水印旋转角度
- `--size`: 水印字体大小
- `--color`: 水印颜色 (格式: "R,G,B")
- `--font`: 字体文件路径（支持中文的字体）

### 批量处理

```bash
python pdf_watermark_batch.py --input PDF文件夹路径 --output 输出文件夹路径 --text "机密文件" --font C:\Windows\Fonts\simhei.ttf
```

额外参数：
- `--threads`: 处理线程数（默认为4）
- `--watermark`: 预先创建的水印PDF文件（可选）

## 关于中文支持

要正确显示中文水印，您需要指定一个支持中文的字体文件。本工具内置了中文字体选择器，可以自动检测系统中安装的中文字体。

常用的中文字体包括：
- 宋体(simsun.ttc)：正式文档常用
- 黑体(simhei.ttf)：粗体效果，更醒目
- 微软雅黑(msyh.ttc)：现代感更强，清晰度高
- 楷体(simkai.ttf)：手写风格

## 系统要求

- Python 3.6+
- PyPDF2
- reportlab
- Pillow

## 许可证

[MIT](LICENSE)

## 贡献

欢迎提交问题和改进建议！ 