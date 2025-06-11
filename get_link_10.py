# -*- coding: utf-8 -*-
"""
Created on Fri May 30 14:53:50 2025

@author: Admin
"""

import os
import pandas as pd
import requests
import time

df = pd.read_excel('bank.xlsx', sheet_name='Lớp 10')
bank_ids = df['bank_iid'].astype(str).tolist()

input_dir = 'input_10_new' 
os.makedirs(input_dir, exist_ok=True)

url = "https://steve-api.lotuslms.com/question-bank/export/export-questions"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://aeglobal.lotuslms.com/admin/content-manager/folder/68217090d8180d89a00c4b42',
    'Origin': 'https://aeglobal.lotuslms.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Priority': 'u=0',
    'Cookie': 'name=value'
}

for bank_id in bank_ids:
    payload = {
        'bank_iid': bank_id,
        'submit': '1',
        '_sand_ajax': '1',
        '_sand_platform': '3',
        '_sand_readmin': '1',
        '_sand_is_wan': 'false',
        '_sand_ga_sessionToken': '',
        '_sand_ga_browserToken': '',
        '_sand_domain': 'aeglobal',
        '_sand_masked': '',
        '_sand_web_url': 'https://aeglobal.lotuslms.com/admin/content-manager/folder/68217090d8180d89a00c4b42',
        '_sand_device_uuid': 'd15a6f5c-c607-452e-ae62-6f12db66bae9',
        '_sand_session_id': 'a0420fb7-d5b7-4a9e-9121-055c4e985823',
        '_sand_token': 'cc328_P7Fcw',
        '_sand_uiid': '705519',
        '_sand_uid': '6576b1b5d18d78fd5f032742',
        '_sand_user_agent': headers['User-Agent'],
        '_sand_ri': '1ab8502a2f48580d62cd777e62617dfe',
        '_sand_rit': 'a8049e4ad009661f67d9d171b4852d68:9ZlBwep+itqiu3Nl8AhBlFUmbeZDk0MyhCLLDQ5+NPiY08HUSXMWntS5r4M9KLPF'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        export_url = data.get('objects', {}).get('url', '')

        if not export_url:
            raise ValueError("Không nhận được URL từ API")

        temp_path = os.path.join(input_dir, f"{bank_id}.xlsx")
        r = requests.get(export_url, stream=True, timeout=60)
        r.raise_for_status()
        with open(temp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        # Kiểm tra bảng: bắt đầu từ dòng 3, có ít nhất 1 dòng dữ liệu
        df_check = pd.read_excel(temp_path, skiprows=2)
        if df_check.empty:
            os.remove(temp_path)
            print(f"[SKIP] {bank_id} - Chỉ có header, không lưu")
        else:
            final_path = os.path.join(input_dir, f"{bank_id}.xlsx")
            os.rename(temp_path, final_path)
            print(f"[OK] {bank_id} - Có dữ liệu, lưu vào input")

    except Exception as e:
        print(f"[ERROR] {bank_id} → {e}")

    time.sleep(1)  
