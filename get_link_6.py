# -*- coding: utf-8 -*-
"""
Created on Wed May 28 13:39:53 2025

@author: Admin
"""

import os
import pandas as pd
import requests
import time

df = pd.read_excel('Bank.xlsx', sheet_name='Lớp 6')
bank_ids = df['bank_iid'].astype(str).tolist()

input_dir = 'input_6' 
os.makedirs(input_dir, exist_ok=True)

url = "https://steve-api.lotuslms.com/question-bank/export/export-questions"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://aeglobal.lotuslms.com/admin/content-manager/folder/677e1f831879aa54870b2004',
    'Origin': 'https://aeglobal.lotuslms.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Priority': 'u=0',
    'Cookie': 'name=value; name=value' 
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
        '_sand_web_url': 'https://aeglobal.lotuslms.com/admin/content-manager/folder/677e1f831879aa54870b2004',
        '_sand_device_uuid': 'd15a6f5c-c607-452e-ae62-6f12db66bae9',
        '_sand_session_id': '8947f57c-d4e6-4829-8132-6f2bf172e4da',
        '_sand_token': 'cc328_P7Fcw',
        '_sand_uiid': '705519',
        '_sand_uid': '6576b1b5d18d78fd5f032742',
        '_sand_user_agent': headers['User-Agent'],
        '_sand_ri': '1ee6b769c3035ab686d1d967ec0aec6c',
        '_sand_rit': 'bd560f8835c1376c6439fea07cdf447d:yt9dw+2zRunYzl+021K6XThC+NIne+aVpvf5lVcL03ObMiFry7WN1+B+Csxl34Rx'
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
        print(f"[ERROR] {bank_id} - {e}")

    time.sleep(1) 
