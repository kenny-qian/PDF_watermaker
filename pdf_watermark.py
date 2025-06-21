#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
import io

def create_watermark(text, output_path=None, font_path=None, font_size=40, opacity=0.5, angle=45, color=(0, 0, 0)):
    """
    创建水印PDF
    
    参数:
    text: 水印文本
    output_path: 输出路径，如果为None则返回内存中的PDF
    font_path: 字体路径，如果为None则使用默认字体
    font_size: 字体大小
    opacity: 透明度 (0-1)
    angle: 旋转角度
    color: RGB颜色元组 (0-255, 0-255, 0-255)
    """
    # 注册字体（如果提供了字体路径）
    font_name = "custom_font"
    if font_path and os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        # 使用默认字体
        font_name = "Helvetica"
    
    # 创建内存缓冲区或文件
    if output_path:
        c = canvas.Canvas(output_path)
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
    
    # 设置颜色和透明度
    r, g, b = [x/255 for x in color]
    c.setFillColorRGB(r, g, b, alpha=opacity)
    
    # 设置字体
    c.setFont(font_name, font_size)
    
    # 获取页面大小
    page_width = c._pagesize[0]
    page_height = c._pagesize[1]
    
    # 保存当前状态
    c.saveState()
    
    # 移动到中心点
    c.translate(page_width/2, page_height/2)
    
    # 旋转
    c.rotate(angle)
    
    # 绘制文本
    c.drawCentredString(0, 0, text)
    
    # 恢复状态
    c.restoreState()
    
    # 保存PDF
    c.save()
    
    # 如果没有指定输出路径，返回内存缓冲区
    if not output_path:
        buffer.seek(0)
        return buffer

def add_watermark(input_pdf, output_pdf, watermark_pdf):
    """
    将水印添加到PDF文件的每一页
    
    参数:
    input_pdf: 输入PDF文件路径
    output_pdf: 输出PDF文件路径
    watermark_pdf: 水印PDF文件路径或文件对象
    """
    # 读取输入PDF
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    # 读取水印PDF
    if isinstance(watermark_pdf, str):
        watermark = PdfReader(watermark_pdf)
    else:
        watermark = PdfReader(watermark_pdf)
    
    watermark_page = watermark.pages[0]
    
    # 为每页添加水印
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    # 写入输出文件
    with open(output_pdf, 'wb') as f:
        writer.write(f)

def main():
    parser = argparse.ArgumentParser(description='为PDF文件添加水印')
    parser.add_argument('--input', required=True, help='输入PDF文件路径')
    parser.add_argument('--output', required=True, help='输出PDF文件路径')
    parser.add_argument('--text', required=True, help='水印文字内容')
    parser.add_argument('--opacity', type=float, default=0.5, help='水印透明度 (0.0-1.0)')
    parser.add_argument('--angle', type=float, default=45, help='水印旋转角度')
    parser.add_argument('--size', type=int, default=40, help='水印字体大小')
    parser.add_argument('--color', default='0,0,0', help='水印颜色 (格式: "R,G,B")')
    parser.add_argument('--font', help='字体文件路径（支持中文的字体）')
    
    args = parser.parse_args()
    
    # 解析颜色
    color = tuple(map(int, args.color.split(',')))
    
    # 创建临时文件用于保存水印PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # 创建水印
        create_watermark(
            text=args.text,
            output_path=temp_filename,
            font_path=args.font,
            font_size=args.size,
            opacity=args.opacity,
            angle=args.angle,
            color=color
        )
        
        # 添加水印到PDF
        add_watermark(args.input, args.output, temp_filename)
        
        print(f"水印已成功添加。输出文件: {args.output}")
    
    finally:
        # 删除临时文件
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

if __name__ == "__main__":
    main() 