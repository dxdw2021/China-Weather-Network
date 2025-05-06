import requests
import json
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from urllib.request import urlopen

cookies = {
    'f_city': '%E6%B7%B1%E5%9C%B3%7C101280601%7C',
    'Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b': '1746510639',
    'HMACCOUNT': '5F2A39D59EDB886F',
    'Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b': '1746510677',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Referer': 'https://www.weather.com.cn/',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    '_': '1746510676943',
}

def fetch_weather(area_id, result_text):
    try:
        response = requests.get(f'https://d1.weather.com.cn/weather_index/{area_id}.html', 
                              params=params, cookies=cookies, headers=headers)
        response.raise_for_status()
        
        content = response.content.decode('utf-8')
        if content.startswith('{') or content.startswith('['):
            try:
                data = json.loads(content)
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, content)
        else:
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, content)
            
    except requests.exceptions.RequestException as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"请求出错: {e}")

def get_city_data():
    url = "https://j.i8tq.com/weather2020/search/city.js"
    response = urlopen(url)
    data = response.read().decode('utf-8')
    # 移除JavaScript变量声明部分
    data = data.replace("var city_data =", "")
    return json.loads(data)

def create_gui():
    app = ttk.Window(themename="superhero")
    app.title("中国天气网查询")
    
    city_data = get_city_data()
    
    # 创建省份选择框
    province_label = ttk.Label(app, text="选择省份:")
    province_label.pack(pady=5)
    
    province_var = tk.StringVar()
    province_cb = ttk.Combobox(app, textvariable=province_var)
    province_cb['values'] = list(city_data.keys())
    province_cb.pack(pady=5)
    
    # 创建城市选择框
    city_label = ttk.Label(app, text="选择城市:")
    city_label.pack(pady=5)
    
    city_var = tk.StringVar()
    city_cb = ttk.Combobox(app, textvariable=city_var, state="readonly")
    city_cb.pack(pady=5)
    
    # 创建地区选择框
    area_label = ttk.Label(app, text="选择地区:")
    area_label.pack(pady=5)
    
    area_var = tk.StringVar()
    area_cb = ttk.Combobox(app, textvariable=area_var, state="readonly")
    area_cb.pack(pady=5)
    
    # 省份选择事件
    def on_province_select(event):
        province = province_var.get()
        cities = list(city_data[province].keys())
        city_cb['values'] = cities
        city_var.set('')
        area_var.set('')
        area_cb['values'] = []
    
    # 城市选择事件
    def on_city_select(event):
        province = province_var.get()
        city = city_var.get()
        areas = city_data[province][city]
        area_cb['values'] = list(areas.keys())
        area_var.set('')
    
    province_cb.bind("<<ComboboxSelected>>", on_province_select)
    city_cb.bind("<<ComboboxSelected>>", on_city_select)
    
    # 查询按钮
    def on_query():
        province = province_var.get()
        city = city_var.get()
        area = area_var.get()
        
        if province and city and area:
            area_id = city_data[province][city][area]["AREAID"]
            fetch_weather(area_id, result_text)
        else:
            print("请选择完整的地区信息")
    
    query_btn = ttk.Button(app, text="查询天气", command=on_query, bootstyle=PRIMARY)
    query_btn.pack(pady=20)
    
    # 创建结果显示文本框
    result_text = tk.Text(app, height=15, width=60)
    result_text.pack(pady=10, padx=10)
    
    app.mainloop()

if __name__ == "__main__":
    create_gui()