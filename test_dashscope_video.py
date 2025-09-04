#!/usr/bin/env python3
"""
Test script for DashScope API video generation capabilities
"""

import os
import requests
import json
import time

# Set up environment variables
DASHSCOPE_API_KEY = "sk-4a87cc687f854499b44ba962d1d854dd"

def test_dashscope_text_generation():
    """Test basic text generation with Qwen"""
    print("Testing DashScope Text Generation (Qwen)...")
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-max",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "Generate a brief marketing message for a technology company."
                }
            ]
        },
        "parameters": {
            "max_tokens": 100
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'output' in result:
                print("✅ Text generation working!")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_dashscope_image_generation():
    """Test image generation with Wanx"""
    print("\nTesting DashScope Image Generation (Wanx)...")
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "wanx-v1",
        "input": {
            "prompt": "A professional business logo for a technology company, clean and modern design"
        },
        "parameters": {
            "style": "photography",
            "size": "1024*1024",
            "n": 1
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'results' in result['output']:
                print("✅ Image generation working!")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_dashscope_video_generation():
    """Test video generation capabilities"""
    print("\nTesting DashScope Video Generation...")
    
    # Check if video generation is available
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "video-generation-v1",
        "input": {
            "prompt": "A professional 20-second marketing video for a technology company showcasing innovation and quality"
        },
        "parameters": {
            "duration": 20,
            "style": "professional"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Video generation API accessible!")
            return True
        elif response.status_code == 404:
            print("❌ Video generation not available in this API version")
            return False
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_api_capabilities():
    """Check what capabilities are available"""
    print("\nChecking API Capabilities...")
    
    url = "https://dashscope.aliyuncs.com/api/v1/models"
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Available models:")
            if 'data' in result:
                for model in result['data']:
                    print(f"  - {model.get('id', 'Unknown')}: {model.get('object', 'Unknown')}")
            else:
                print("No model data available")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("DashScope API Capability Test")
    print("=" * 50)
    
    # Test basic connectivity and capabilities
    text_ok = test_dashscope_text_generation()
    image_ok = test_dashscope_image_generation()
    video_ok = test_dashscope_video_generation()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Text Generation (Qwen): {'✅ Working' if text_ok else '❌ Failed'}")
    print(f"Image Generation (Wanx): {'✅ Working' if image_ok else '❌ Failed'}")
    print(f"Video Generation: {'✅ Working' if video_ok else '❌ Not Available'}")
    
    if not any([text_ok, image_ok]):
        print("\n❌ API Key appears to be invalid or inactive")
        print("Please check:")
        print("1. API key is correct and active")
        print("2. Billing is set up for DashScope")
        print("3. Regional access permissions")
    elif text_ok or image_ok:
        print("\n✅ Basic API access working!")
        if not video_ok:
            print("Note: Video generation may require special access or different API endpoint")
    
    # Check available models
    check_api_capabilities()

