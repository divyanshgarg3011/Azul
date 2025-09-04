#!/usr/bin/env python3
"""
Test script to debug Alibaba Cloud API key issues
"""
import os
import sys
import dashscope
import oss2

def test_dashscope_api():
    """Test DashScope API key"""
    print("=== Testing DashScope API ===")
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        dashscope.api_key = api_key
        
        # Test with a simple generation call
        print("Testing simple text generation...")
        response = dashscope.Generation.call(
            model='qwen-turbo',  # Try with turbo model first (might have different access)
            prompt='Hello, this is a test. Please respond with "API working".',
            result_format='message'
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response}")
        
        if response.status_code == 200:
            print("✅ DashScope API is working!")
            return True
        else:
            print(f"❌ DashScope API error: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ DashScope API exception: {str(e)}")
        return False

def test_oss_api():
    """Test OSS API credentials"""
    print("\n=== Testing OSS API ===")
    
    access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    endpoint = os.getenv('OSS_ENDPOINT', 'oss-me-east-1.aliyuncs.com')
    bucket_name = os.getenv('OSS_BUCKET_NAME', 'azul-campaign-assets')
    
    if not access_key_id or not access_key_secret:
        print("❌ OSS credentials not found in environment variables")
        return False
    
    print(f"✅ Access Key ID: {access_key_id[:10]}...{access_key_id[-4:]}")
    print(f"✅ Endpoint: {endpoint}")
    print(f"✅ Bucket Name: {bucket_name}")
    
    try:
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        # Test bucket access
        print("Testing bucket access...")
        
        # Try to check if bucket exists
        try:
            bucket.get_bucket_info()
            print("✅ Bucket exists and accessible!")
            return True
        except oss2.exceptions.NoSuchBucket:
            print("⚠️  Bucket doesn't exist. Attempting to create...")
            try:
                bucket.create_bucket()
                print("✅ Bucket created successfully!")
                return True
            except Exception as create_error:
                print(f"❌ Failed to create bucket: {str(create_error)}")
                return False
        except Exception as e:
            print(f"❌ OSS API error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ OSS API exception: {str(e)}")
        return False

def test_alternative_models():
    """Test alternative DashScope models"""
    print("\n=== Testing Alternative Models ===")
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        return False
    
    dashscope.api_key = api_key
    
    models_to_test = [
        'qwen-turbo',
        'qwen-plus', 
        'qwen-max',
        'qwen1.5-72b-chat',
        'qwen1.5-14b-chat'
    ]
    
    working_models = []
    
    for model in models_to_test:
        try:
            print(f"Testing model: {model}")
            response = dashscope.Generation.call(
                model=model,
                prompt='Test',
                result_format='message'
            )
            
            if response.status_code == 200:
                print(f"✅ {model} - Working!")
                working_models.append(model)
            else:
                print(f"❌ {model} - Error: {response.message}")
                
        except Exception as e:
            print(f"❌ {model} - Exception: {str(e)}")
    
    return working_models

def main():
    print("🔍 Alibaba Cloud API Key Diagnostic Tool")
    print("=" * 50)
    
    # Check environment variables
    print("Environment Variables:")
    env_vars = [
        'DASHSCOPE_API_KEY',
        'ALIBABA_CLOUD_ACCESS_KEY_ID', 
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET',
        'OSS_ENDPOINT',
        'OSS_BUCKET_NAME'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var:
                print(f"✅ {var}: {value[:10]}...{value[-4:]}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print("\n" + "=" * 50)
    
    # Test APIs
    dashscope_ok = test_dashscope_api()
    oss_ok = test_oss_api()
    
    if not dashscope_ok:
        working_models = test_alternative_models()
        if working_models:
            print(f"\n✅ Working models found: {working_models}")
        else:
            print("\n❌ No working models found")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print(f"DashScope API: {'✅ Working' if dashscope_ok else '❌ Not Working'}")
    print(f"OSS API: {'✅ Working' if oss_ok else '❌ Not Working'}")
    
    if not dashscope_ok:
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Check if DashScope service is enabled in Alibaba Cloud console")
        print("2. Verify API key is activated and has proper permissions")
        print("3. Check if you're in the correct region")
        print("4. Ensure billing is set up for DashScope usage")
        print("5. Try regenerating the API key")
    
    if not oss_ok:
        print("\n🔧 OSS TROUBLESHOOTING:")
        print("1. Check if OSS service is enabled")
        print("2. Verify Access Key has OSS permissions")
        print("3. Check the endpoint region matches your account")

if __name__ == "__main__":
    main()

