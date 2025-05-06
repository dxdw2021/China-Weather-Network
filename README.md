# 中国天气网查询工具

## 项目简介
这是一个基于Python开发的GUI应用程序，用于查询中国天气网的天气数据。

## 功能说明
- 提供省份、城市和地区的三级选择
- 实时查询选定地区的天气信息
- 以JSON格式展示原始天气数据

## 使用方法
1. 确保已安装Python 3.8+环境
2. 安装依赖包：
```
pip install requests ttkbootstrap
```
3. 运行程序：
```
python weather_request.py
```
4. 在界面中选择省份、城市和地区后点击"查询天气"按钮

## 项目结构
- `weather_request.py`: 主程序文件
- `build/`: 构建目录
- `dist/`: 可执行文件目录

## 许可证
MIT License