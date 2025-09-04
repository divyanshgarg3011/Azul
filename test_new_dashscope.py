#!/usr/bin/env python3
"""
Test script for new DashScope API with video generation
"""

import os
import sys
import time
from http import HTTPStatus

# Install dashscope if not available
try:
    import dashscope
    from dashscope import VideoSynthesis, Generation, ImageSynthesis
except ImportError:
    print("Installing dashscope...")
    os.system("pip install dashscope")
    import dashscope
    from dashscope import VideoSynthesis, Generation, ImageSynthesis

# Set up the new API key and endpoint
dashscope.api_key = "sk-e77b51911f1f4f44841d12c338a2efd3"
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

def test_text_generation():
    """Test Qwen text generation"""
    print("Testing Qwen Text Generation...")
    
    try:
        response = Generation.call(
            model='qwen-max',
            prompt='Generate a brief marketing message for a technology company focused on innovation.',
            max_tokens=100
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == HTTPStatus.OK:
            print("✅ Text generation working!")
            print(f"Generated text: {response.output.text}")
            return True
        else:
            print(f"❌ Failed: {response.code} - {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_image_generation():
    """Test Wanx image generation"""
    print("\nTesting Wanx Image Generation...")
    
    try:
        response = ImageSynthesis.call(
            model='wanx-v1',
            prompt='A professional technology company logo, modern and clean design',
            size='1024*1024'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == HTTPStatus.OK:
            print("✅ Image generation working!")
            print(f"Image URL: {response.output.results[0].url}")
            return True
        else:
            print(f"❌ Failed: {response.code} - {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_video_generation():
    """Test video generation with wan2.1-t2v-turbo"""
    print("\nTesting Video Generation...")
    
    try:
        print('Generating video, please wait...')
        response = VideoSynthesis.call(
            model='wan2.1-t2v-turbo',
            prompt='A professional marketing video showing a modern technology company office with people working on computers, clean and professional atmosphere',
            size='1280*720'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == HTTPStatus.OK:
            print("✅ Video generation working!")
            print(f"Video URL: {response.output.video_url}")
            return True
        else:
            print(f"❌ Failed: {response.code} - {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_marketing_campaign_generation():
    """Test generating content for a marketing campaign"""
    print("\nTesting Marketing Campaign Generation...")
    
    try:
        # Generate campaign strategy
        campaign_prompt = """
        Create a marketing campaign strategy for a technology company called "TechFlow" that provides cloud solutions. 
        Include:
        1. Campaign objective
        2. Target audience
        3. Key messaging
        4. Call to action
        
        Keep it concise and professional.
        """
        
        response = Generation.call(
            model='qwen-max',
            prompt=campaign_prompt,
            max_tokens=300
        )
        
        if response.status_code == HTTPStatus.OK:
            print("✅ Campaign strategy generation working!")
            print("Generated strategy:")
            print(response.output.text)
            return True
        else:
            print(f"❌ Failed: {response.code} - {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("New DashScope API Test")
    print("=" * 50)
    print(f"API Key: {dashscope.api_key}")
    print(f"Endpoint: {dashscope.base_http_api_url}")
    print("=" * 50)
    
    # Test all capabilities
    text_ok = test_text_generation()
    image_ok = test_image_generation()
    video_ok = test_video_generation()
    campaign_ok = test_marketing_campaign_generation()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Text Generation (Qwen): {'✅ Working' if text_ok else '❌ Failed'}")
    print(f"Image Generation (Wanx): {'✅ Working' if image_ok else '❌ Failed'}")
    print(f"Video Generation (wan2.1-t2v-turbo): {'✅ Working' if video_ok else '❌ Failed'}")
    print(f"Campaign Generation: {'✅ Working' if campaign_ok else '❌ Failed'}")
    
    if all([text_ok, image_ok, video_ok]):
        print("\n🎉 ALL FEATURES WORKING! Ready for full AI integration!")
    elif any([text_ok, image_ok, video_ok]):
        print("\n✅ Partial success - some features working")
    else:
        print("\n❌ API issues - check configuration")

