import requests
import json
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from urllib.request import urlopen
from urllib.parse import urlencode

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
                              params=params, cookies=cookies, headers=headers,
                              verify=False, proxies=None)
        response.raise_for_status()
        
        content = response.content.decode('utf-8')
        weather_data = {}
        
        # 解析所有JavaScript变量
        for var_line in content.split(';'):
            if '=' in var_line:
                var_name, var_value = var_line.split('=', 1)
                var_name = var_name.strip().replace('var ', '')
                try:
                    weather_data[var_name] = json.loads(var_value)
                except:
                    continue
        
        # 格式化天气信息
        formatted_text = []
        
        # 当前天气信息
        if 'dataSK' in weather_data:
            sk = weather_data['dataSK']
            formatted_text.extend([
                f"=== 当前天气 ===\n",
                f"城市: {sk.get('cityname')}",
                f"天气: {sk.get('weather')}",
                f"温度: {sk.get('temp')}°C",
                f"风向: {sk.get('WD')}",
                f"风力: {sk.get('WS')}",
                f"相对湿度: {sk.get('SD')}",
                f"能见度: {sk.get('njd')}",
                f"空气质量指数: {sk.get('aqi')}",
                f"降雨量: {sk.get('rain')}mm\n"
            ])
        
        # 生活指数
        if 'dataZS' in weather_data and 'zs' in weather_data['dataZS']:
            zs = weather_data['dataZS']['zs']
            formatted_text.extend([
                f"=== 生活指数 ===\n",
                f"穿衣指数: {zs.get('ct_hint')} - {zs.get('ct_des_s')}",
                f"紫外线强度: {zs.get('uv_hint')} - {zs.get('uv_des_s')}",
                f"感冒指数: {zs.get('gm_hint')} - {zs.get('gm_des_s')}",
                f"空气污染: {zs.get('pl_hint')} - {zs.get('pl_des_s')}",
                f"舒适度: {zs.get('co_hint')} - {zs.get('co_des_s')}\n"
            ])
        
        # 天气预报
        if 'fc' in weather_data and 'f' in weather_data['fc']:
            formatted_text.append(f"=== 未来天气预报 ===\n")
            for day in weather_data['fc']['f']:
                formatted_text.append(
                    f"{day.get('fi')} {day.get('fj')}:\n"
                    f"天气: {day.get('fa')}\n"
                    f"温度: {day.get('fd')}°C ~ {day.get('fc')}°C\n"
                    f"风向: {day.get('fe')} {day.get('fg')}\n"
                )
        
        # 显示格式化的天气信息
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, '\n'.join(formatted_text))
            
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

def get_location_by_ip():
    # 备用API列表
    ip_apis = [
        'https://api.ipify.org?format=json',
        'https://api.myip.com',
        'https://ipinfo.io/json'
    ]
    
    # 定位API列表
    location_apis = [
        ('http://ip-api.com/json/{ip}?lang=zh-CN', 'status'),
        ('https://ipapi.co/{ip}/json/', 'country'),
        ('https://ipinfo.io/{ip}/json', 'country')
    ]
    
    # 城市名称映射表(解决API返回城市名与实际名称不一致问题)
    city_name_mapping = {
        '广州': '深圳',
        '广州市': '深圳',
        'guangzhou': '深圳'
    }
    
    for ip_api in ip_apis:
        try:
            # 获取当前IP地址，带重试机制
            for _ in range(3):  # 重试3次
                try:
                    ip_response = requests.get(ip_api, timeout=3)  # 缩短超时时间
                    ip_response.raise_for_status()
                    ip_address = ip_response.json().get('ip')
                    if ip_address:
                        break
                except Exception:
                    continue
            else:
                continue  # 所有重试失败，尝试下一个API
                
            # 尝试多个定位API
            for api_url, status_field in location_apis:
                try:
                    url = api_url.format(ip=ip_address)
                    location_response = requests.get(url, timeout=3)  # 缩短超时时间
                    location_response.raise_for_status()
                    location_data = location_response.json()
                    
                    if location_data.get(status_field):
                        # 处理不同API返回的数据格式
                        if 'ip-api.com' in api_url:
                            city_name = location_data.get('city', '').replace('市', '')
                            # 检查是否需要映射城市名称
                            mapped_city = city_name_mapping.get(city_name, city_name)
                            return {
                                'province': location_data.get('regionName', ''),
                                'city': mapped_city
                            }
                        elif 'ipapi.co' in api_url or 'ipinfo.io' in api_url:
                            city_name = location_data.get('city', '').replace('市', '')
                            # 检查是否需要映射城市名称
                            mapped_city = city_name_mapping.get(city_name, city_name)
                            return {
                                'province': location_data.get('region', ''),
                                'city': mapped_city
                            }
                except Exception:
                    continue  # API失败，尝试下一个
                    
        except Exception as e:
            print(f"IP定位服务暂时不可用，请稍后再试。错误详情: {str(e)}")
            continue
            
    print("所有IP定位服务均不可用，请检查网络连接或稍后再试。")
    return None

def load_settings():
    try:
        with open('weather_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_settings(province, city, area):
    with open('weather_settings.json', 'w', encoding='utf-8') as f:
        json.dump({
            'province': province,
            'city': city,
            'area': area
        }, f, ensure_ascii=False, indent=4)

def create_gui():
    app = ttk.Window(themename="superhero")
    app.title("中国天气网查询")
    app.geometry("600x600")
    app.minsize(400, 500)
    
    city_data = get_city_data()
    
    # 加载上次设置
    settings = load_settings()
    
    # 主框架
    main_frame = ttk.Frame(app)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 选择区域框架
    select_frame = ttk.Frame(main_frame)
    select_frame.pack(fill=tk.X, pady=5)
    
    # 创建省份选择框
    province_label = ttk.Label(select_frame, text="选择省份:")
    province_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    province_var = tk.StringVar()
    province_cb = ttk.Combobox(select_frame, textvariable=province_var)
    province_cb['values'] = list(city_data.keys())
    province_cb.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
    
    # 创建城市选择框
    city_label = ttk.Label(select_frame, text="选择城市:")
    city_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    city_var = tk.StringVar()
    city_cb = ttk.Combobox(select_frame, textvariable=city_var, state="readonly")
    city_cb.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
    
    # 创建地区选择框
    area_label = ttk.Label(select_frame, text="选择地区:")
    area_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    
    area_var = tk.StringVar()
    area_cb = ttk.Combobox(select_frame, textvariable=area_var, state="readonly")
    area_cb.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
    
    # 设置默认值或上次设置
    if settings:
        province = settings.get('province', "广东")
        city = settings.get('city', "深圳")
        area = settings.get('area', "宝安")
    else:
        province, city, area = "广东", "深圳", "宝安"
        
    province_var.set(province)
    city_var.set(city)
    area_var.set(area)
    province_cb.event_generate('<<ComboboxSelected>>')
    
    # 保存设置
    save_settings(province, city, area)
    
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
            # 保存当前设置
            save_settings(province, city, area)
        else:
            print("请选择完整的地区信息")
    
    # 按钮框架
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    # 查询按钮
    query_btn = ttk.Button(button_frame, text="查询天气", command=on_query, bootstyle=PRIMARY)
    query_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    # 重置按钮
    def on_reset():
        province_var.set(default_province)
        province_cb.event_generate('<<ComboboxSelected>>')
        city_var.set(default_city)
        city_cb.event_generate('<<ComboboxSelected>>')
        area_var.set(default_area)
        result_text.delete(1.0, tk.END)
    
    reset_btn = ttk.Button(button_frame, text="重置", command=on_reset, bootstyle=SECONDARY)
    reset_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    # IP定位按钮
    def on_ip_location():
        print("开始IP定位...")
        location = get_location_by_ip()
        if location:
            print(f"获取到位置信息: {location}")
            province = location['province']
            city = location['city']
            
            # 检查并设置省份
            if province in city_data:
                print(f"找到省份: {province}")
                province_var.set(province)
                province_cb.event_generate('<<ComboboxSelected>>')
                
                # 检查并设置城市
                cities = city_data[province]
                if city in cities:
                    print(f"找到城市: {city}")
                    city_var.set(city)
                    city_cb.event_generate('<<ComboboxSelected>>')
                    
                    # 默认选择第一个地区
                    areas = list(cities[city].keys())
                    if areas:
                        print(f"设置地区为: {areas[0]}")
                        area_var.set(areas[0])
                else:
                    print(f"未找到城市: {city}")
            else:
                print(f"未找到省份: {province}")
        else:
            print("无法获取位置信息")
        print("IP定位完成")
    
    ip_location_btn = ttk.Button(button_frame, text="IP定位", command=on_ip_location, bootstyle=INFO)
    ip_location_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    # 结果显示文本框
    result_frame = ttk.Frame(main_frame)
    result_frame.pack(fill=tk.BOTH, expand=True)
    
    result_text = tk.Text(result_frame, height=15, width=60)
    result_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 配置列权重
    select_frame.columnconfigure(1, weight=1)
    
    app.mainloop()

if __name__ == "__main__":
    create_gui()