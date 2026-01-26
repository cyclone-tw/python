#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""列出可用的 Gemini 模型"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import google.generativeai as genai
from config import SETTINGS

genai.configure(api_key=SETTINGS['gemini']['api_key'])

print("=" * 60)
print("📋 列出所有可用的 Gemini 模型")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✅ {model.name}")
        print(f"   顯示名稱: {model.display_name}")
        print(f"   描述: {model.description}")
        print(f"   支援方法: {', '.join(model.supported_generation_methods)}")

print("\n" + "=" * 60)
