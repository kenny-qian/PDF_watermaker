#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import glob
from pdf_watermark import create_watermark, add_watermark
import tempfile
import concurrent.futures

def process_file(input_file, output_dir, watermark_file, text=None, font_path=None, 
                font_size=40, opacity=0.5, angle=45, color=(0, 0, 0)):
    """处理单个PDF文件"""
    try:
        # 确定输出文件名
        base_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, f"watermarked_{base_name}")
        
        # 如果水印文件不存在，则创建一个
        if not watermark_file:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_watermark = temp_file.name
                
            create_watermark(
                text=text,
                output_path=temp_watermark,
                font_path=font_path,
                font_size=font_size,
                opacity=opacity,
                angle=angle,
                color=color
            )
        else:
            temp_watermark = watermark_file
            
        # 添加水印
        add_watermark(input_file, output_file, temp_watermark)
        
        # 如果我们创建了临时水印文件，则删除它
        if not watermark_file and os.path.exists(temp_watermark):
            os.unlink(temp_watermark)
            
        return True, input_file, None
    except Exception as e:
        return False, input_file, str(e)

def main():
    parser = argparse.ArgumentParser(description='批量为PDF文件添加水印')
    parser.add_argument('--input', required=True, help='输入PDF文件或目录')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--text', default='机密文件', help='水印文字内容')
    parser.add_argument('--opacity', type=float, default=0.5, help='水印透明度 (0.0-1.0)')
    parser.add_argument('--angle', type=float, default=45, help='水印旋转角度')
    parser.add_argument('--size', type=int, default=40, help='水印字体大小')
    parser.add_argument('--color', default='0,0,0', help='水印颜色 (格式: "R,G,B")')
    parser.add_argument('--font', help='字体文件路径（支持中文的字体）')
    parser.add_argument('--watermark', help='预先创建的水印PDF文件')
    parser.add_argument('--threads', type=int, default=4, help='处理线程数')
    
    args = parser.parse_args()
    
    # 解析颜色
    color = tuple(map(int, args.color.split(',')))
    
    # 确保输出目录存在
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # 获取输入文件列表
    if os.path.isdir(args.input):
        input_files = glob.glob(os.path.join(args.input, "*.pdf"))
    else:
        input_files = [args.input]
    
    if not input_files:
        print(f"未找到PDF文件: {args.input}")
        return
    
    print(f"找到 {len(input_files)} 个PDF文件")
    
    # 如果指定了预先创建的水印文件，则使用它
    watermark_file = args.watermark
    
    # 如果没有指定水印文件，但有多个输入文件，则预先创建一个水印文件以提高效率
    if not watermark_file and len(input_files) > 1:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            watermark_file = temp_file.name
            
        print("创建水印文件...")
        create_watermark(
            text=args.text,
            output_path=watermark_file,
            font_path=args.font,
            font_size=args.size,
            opacity=args.opacity,
            angle=args.angle,
            color=color
        )
    
    try:
        # 使用线程池并行处理文件
        success_count = 0
        error_count = 0
        
        print(f"使用 {args.threads} 个线程处理文件...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(
                    process_file, 
                    input_file, 
                    args.output, 
                    watermark_file,
                    args.text, 
                    args.font, 
                    args.size, 
                    args.opacity, 
                    args.angle, 
                    color
                ): input_file for input_file in input_files
            }
            
            # 处理结果
            for future in concurrent.futures.as_completed(future_to_file):
                success, file_path, error = future.result()
                if success:
                    print(f"成功处理: {os.path.basename(file_path)}")
                    success_count += 1
                else:
                    print(f"处理失败: {os.path.basename(file_path)} - {error}")
                    error_count += 1
        
        print(f"\n处理完成: 成功 {success_count} 个, 失败 {error_count} 个")
        print(f"输出文件保存在: {args.output}")
    
    finally:
        # 如果我们创建了临时水印文件，则删除它
        if not args.watermark and watermark_file and os.path.exists(watermark_file):
            os.unlink(watermark_file)

if __name__ == "__main__":
    main() 