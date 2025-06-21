#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import filedialog, colorchooser, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
from pdf_watermark import create_watermark, add_watermark
import tempfile

# 常用中文字体及其文件名
COMMON_FONTS = {
    "宋体 (SimSun)": "simsun.ttc",
    "黑体 (SimHei)": "simhei.ttf",
    "楷体 (KaiTi)": "simkai.ttf",
    "仿宋 (FangSong)": "simfang.ttf",
    "微软雅黑 (Microsoft YaHei)": "msyh.ttc",
    "微软雅黑粗体 (Microsoft YaHei Bold)": "msyhbd.ttc",
    "微软雅黑细体 (Microsoft YaHei Light)": "msyhl.ttc",
    "隶书 (LiSu)": "SIMLI.TTF",
    "幼圆 (YouYuan)": "SIMYOU.TTF",
    "华文楷体 (STKaiti)": "STKAITI.TTF"
}

def find_font_path(font_name):
    """查找字体文件的完整路径"""
    # Windows 默认字体目录
    font_dir = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Fonts')
    font_path = os.path.join(font_dir, font_name)
    
    if os.path.exists(font_path):
        return font_path
    return None

class PDFWatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF水印工具")
        self.root.geometry("600x550")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入文件
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="输入PDF文件:").pack(side=tk.LEFT)
        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(input_frame, text="浏览...", command=self.browse_input).pack(side=tk.RIGHT)
        
        # 输出文件
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="输出PDF文件:").pack(side=tk.LEFT)
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_frame, text="浏览...", command=self.browse_output).pack(side=tk.RIGHT)
        
        # 水印文字
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(text_frame, text="水印文字:").pack(side=tk.LEFT)
        self.watermark_text = tk.StringVar(value="机密文件")
        ttk.Entry(text_frame, textvariable=self.watermark_text).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 字体选择
        font_frame = ttk.Frame(main_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="字体文件:").pack(side=tk.LEFT)
        self.font_path = tk.StringVar()
        ttk.Entry(font_frame, textvariable=self.font_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(font_frame, text="浏览...", command=self.browse_font).pack(side=tk.RIGHT)
        ttk.Button(font_frame, text="选择中文字体", command=self.choose_chinese_font).pack(side=tk.RIGHT, padx=5)
        
        # 参数设置框架
        params_frame = ttk.LabelFrame(main_frame, text="水印参数")
        params_frame.pack(fill=tk.X, pady=10)
        
        # 透明度
        opacity_frame = ttk.Frame(params_frame)
        opacity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
        self.opacity = tk.DoubleVar(value=0.3)
        ttk.Scale(opacity_frame, from_=0.1, to=1.0, variable=self.opacity, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(opacity_frame, textvariable=self.opacity).pack(side=tk.RIGHT)
        
        # 角度
        angle_frame = ttk.Frame(params_frame)
        angle_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(angle_frame, text="角度:").pack(side=tk.LEFT)
        self.angle = tk.IntVar(value=45)
        ttk.Scale(angle_frame, from_=0, to=360, variable=self.angle, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(angle_frame, textvariable=self.angle).pack(side=tk.RIGHT)
        
        # 字体大小
        size_frame = ttk.Frame(params_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
        self.font_size = tk.IntVar(value=40)
        ttk.Scale(size_frame, from_=10, to=100, variable=self.font_size, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(size_frame, textvariable=self.font_size).pack(side=tk.RIGHT)
        
        # 颜色
        color_frame = ttk.Frame(params_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.color = ((0, 0, 0), "#000000")  # (RGB, Hex)
        self.color_button = ttk.Button(color_frame, text="选择颜色", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5)
        self.color_preview = tk.Canvas(color_frame, width=20, height=20, bg=self.color[1])
        self.color_preview.pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="添加水印", command=self.add_watermark_thread).pack(side=tk.RIGHT)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 加载可用的中文字体
        self.available_fonts = {}
        self.load_available_fonts()
    
    def load_available_fonts(self):
        """加载可用的中文字体"""
        for font_name, font_file in COMMON_FONTS.items():
            font_path = find_font_path(font_file)
            if font_path:
                self.available_fonts[font_name] = font_path
    
    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")])
        if filename:
            self.input_path.set(filename)
            # 自动设置输出文件名
            if not self.output_path.get():
                base, ext = os.path.splitext(filename)
                self.output_path.set(f"{base}_watermarked{ext}")
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")])
        if filename:
            self.output_path.set(filename)
    
    def browse_font(self):
        filename = filedialog.askopenfilename(filetypes=[("字体文件", "*.ttf;*.otf;*.ttc"), ("所有文件", "*.*")])
        if filename:
            self.font_path.set(filename)
    
    def choose_chinese_font(self):
        """打开中文字体选择对话框"""
        if not self.available_fonts:
            messagebox.showwarning("警告", "未找到可用的中文字体！")
            return
        
        # 创建字体选择对话框
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("选择中文字体")
        font_dialog.geometry("450x400")
        font_dialog.transient(self.root)  # 设置为主窗口的子窗口
        font_dialog.grab_set()  # 模态对话框
        
        # 创建主框架
        main_frame = ttk.Frame(font_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 字体列表
        ttk.Label(main_frame, text="请选择一个中文字体:").pack(anchor=tk.W, pady=(0, 5))
        
        # 创建字体列表框
        font_listbox = tk.Listbox(main_frame, height=10)
        font_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 添加字体到列表
        for font_name in self.available_fonts:
            font_listbox.insert(tk.END, font_name)
        
        # 预览文本
        ttk.Label(main_frame, text="预览文本:").pack(anchor=tk.W, pady=(10, 5))
        preview_text = tk.StringVar(value=self.watermark_text.get() or "这是中文水印文字预览")
        ttk.Entry(main_frame, textvariable=preview_text).pack(fill=tk.X, pady=(0, 10))
        
        # 预览标签
        preview_label = ttk.Label(main_frame, text="选择字体以预览", font=("SimSun", 14))
        preview_label.pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 选择按钮
        def select_font():
            if font_listbox.curselection():
                index = font_listbox.curselection()[0]
                font_name = font_listbox.get(index)
                font_path = self.available_fonts.get(font_name)
                if font_path:
                    self.font_path.set(font_path)
                    self.log(f"已选择字体: {font_name} ({font_path})")
                    font_dialog.destroy()
        
        # 预览按钮
        def preview_selected_font():
            if font_listbox.curselection():
                index = font_listbox.curselection()[0]
                font_name = font_listbox.get(index)
                font_path = self.available_fonts.get(font_name)
                if font_path:
                    try:
                        # 获取字体文件名
                        font_file = os.path.basename(font_path)
                        # 更新预览标签
                        preview_label.config(text=preview_text.get(), font=(font_file, 14))
                    except Exception as e:
                        messagebox.showerror("错误", f"无法预览字体: {str(e)}")
        
        ttk.Button(button_frame, text="预览", command=preview_selected_font).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="选择", command=select_font).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=font_dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 绑定双击事件
        font_listbox.bind('<Double-1>', lambda e: select_font())
    
    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.color[1])
        if color and color[0]:
            self.color = color
            self.color_preview.config(bg=color[1])
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def add_watermark_thread(self):
        # 验证输入
        if not self.input_path.get():
            self.log("错误: 请选择输入PDF文件")
            return
        
        if not self.output_path.get():
            self.log("错误: 请指定输出PDF文件")
            return
        
        if not self.watermark_text.get():
            self.log("错误: 请输入水印文字")
            return
        
        # 启动线程处理，避免UI冻结
        threading.Thread(target=self.add_watermark_process).start()
    
    def add_watermark_process(self):
        try:
            # 显示进度条
            self.root.after(0, lambda: self.progress.start())
            
            self.log(f"正在处理: {os.path.basename(self.input_path.get())}")
            
            # 创建临时文件用于保存水印PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            try:
                # 创建水印
                self.log("正在创建水印...")
                create_watermark(
                    text=self.watermark_text.get(),
                    output_path=temp_filename,
                    font_path=self.font_path.get() if self.font_path.get() else None,
                    font_size=self.font_size.get(),
                    opacity=self.opacity.get(),
                    angle=self.angle.get(),
                    color=self.color[0]
                )
                
                # 添加水印到PDF
                self.log("正在添加水印到PDF...")
                add_watermark(self.input_path.get(), self.output_path.get(), temp_filename)
                
                self.log(f"水印已成功添加。输出文件: {self.output_path.get()}")
            
            finally:
                # 删除临时文件
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
        
        except Exception as e:
            self.log(f"错误: {str(e)}")
        
        finally:
            # 停止进度条
            self.root.after(0, lambda: self.progress.stop())

def main():
    root = tk.Tk()
    app = PDFWatermarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 