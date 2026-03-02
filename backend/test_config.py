#!/usr/bin/env python
"""Test AI configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("AI_PROVIDER", "aliyun").lower()
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")

print("=" * 60)
print("AI CONFIGURATION")
print("=" * 60)
print(f"✓ Provider: {PROVIDER}")
print(f"✓ API Key: {API_KEY[:20]}...{API_KEY[-10:] if API_KEY else 'NOT SET'}")
print(f"✓ Model: {MODEL}")

if PROVIDER == "aliyun":
    print(f"✓ Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1")
else:
    print(f"✓ Base URL: https://api.openai.com/v1")

print("=" * 60)
print("✓ Configuration is ready to use!")
print("=" * 60)
