import os
import json
import requests
import time
from urllib.parse import urlparse
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from bs4 import BeautifulSoup
import dashscope
import oss2

campaign_bp = Blueprint('campaign', __name__)

# Configuration - these will be set via environment variables
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT', 'oss-me-east-1.aliyuncs.com')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME', 'azul-campaign-assets')

# Initialize DashScope
if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY

# Initialize OSS
if ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET:
    auth = oss2.Auth(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

def scrape_website(url):
    """Scrape website content and extract relevant information"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract meta information
        title = soup.find('title')
        title_text = title.get_text() if title else ""
        
        description = soup.find('meta', attrs={'name': 'description'})
        description_text = description.get('content') if description else ""
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            img_url = img['src']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                parsed_url = urlparse(url)
                img_url = f"{parsed_url.scheme}://{parsed_url.netloc}{img_url}"
            elif not img_url.startswith('http'):
                parsed_url = urlparse(url)
                img_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{img_url}"
            images.append(img_url)
        
        return {
            'title': title_text,
            'description': description_text,
            'content': text[:5000],  # Limit content length
            'images': images[:10],  # Limit number of images
            'url': url
        }
    except Exception as e:
        return {'error': f'Failed to scrape website: {str(e)}'}

def analyze_brand_with_qwen(website_data):
    """Use Qwen to analyze website content and generate brand brief"""
    try:
        prompt = f"""
        Analyze the following website content and generate a comprehensive brand brief in JSON format:
        
        Website Title: {website_data.get('title', '')}
        Description: {website_data.get('description', '')}
        Content: {website_data.get('content', '')}
        
        Generate a JSON response with the following structure:
        {{
            "brand_name": "extracted or inferred brand name",
            "industry": "business industry/sector",
            "target_audience": "primary target audience description",
            "value_propositions": ["key value proposition 1", "key value proposition 2", "key value proposition 3"],
            "brand_personality": "brand personality description",
            "key_products_services": ["product/service 1", "product/service 2"],
            "competitive_advantages": ["advantage 1", "advantage 2"],
            "brand_tone": "professional/casual/friendly/authoritative etc."
        }}
        """
        
        response = dashscope.Generation.call(
            model='qwen-max',
            prompt=prompt,
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    return {'error': 'No valid JSON found in Qwen response'}
            except json.JSONDecodeError:
                return {'error': 'Failed to parse JSON from Qwen response'}
        else:
            return {'error': f'Qwen API error: {response.message}'}
    except Exception as e:
        return {'error': f'Failed to analyze brand: {str(e)}'}

def generate_campaign_strategy(brand_brief):
    """Generate comprehensive campaign strategy using Qwen"""
    try:
        prompt = f"""
        Based on the following brand brief, generate a comprehensive marketing campaign strategy in JSON format:
        
        Brand Brief: {json.dumps(brand_brief)}
        
        Generate a JSON response with the following structure:
        {{
            "campaign_objective": "main campaign goal",
            "target_platforms": ["Facebook", "Instagram", "LinkedIn", "TikTok"],
            "content_themes": ["theme 1", "theme 2", "theme 3"],
            "video_ad_concept": {{
                "duration": "20-30 seconds",
                "style": "professional/casual/dynamic etc.",
                "key_message": "main message for video",
                "call_to_action": "specific CTA",
                "scenes": [
                    {{
                        "scene_number": 1,
                        "description": "detailed scene description",
                        "duration": "5-8 seconds",
                        "visual_elements": "what should be shown"
                    }},
                    {{
                        "scene_number": 2,
                        "description": "detailed scene description", 
                        "duration": "8-12 seconds",
                        "visual_elements": "what should be shown"
                    }},
                    {{
                        "scene_number": 3,
                        "description": "detailed scene description",
                        "duration": "7-10 seconds", 
                        "visual_elements": "what should be shown"
                    }}
                ]
            }},
            "social_media_posts": {{
                "facebook": {{
                    "headline": "engaging headline",
                    "primary_text": "compelling post text",
                    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                    "image_description": "description for image generation"
                }},
                "instagram": {{
                    "caption": "instagram caption with emojis",
                    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"],
                    "image_description": "description for image generation"
                }},
                "linkedin": {{
                    "headline": "professional headline",
                    "post_text": "professional post content",
                    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                    "image_description": "description for image generation"
                }},
                "tiktok": {{
                    "caption": "catchy tiktok caption",
                    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4"],
                    "video_concept": "short video concept description"
                }}
            }},
            "multilingual_content": {{
                "english": {{
                    "headline": "English headline",
                    "primary_text": "English primary text"
                }},
                "arabic": {{
                    "headline": "Arabic headline",
                    "primary_text": "Arabic primary text"
                }}
            }}
        }}
        """
        
        response = dashscope.Generation.call(
            model='qwen-max',
            prompt=prompt,
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    return {'error': 'No valid JSON found in campaign strategy response'}
            except json.JSONDecodeError:
                return {'error': 'Failed to parse JSON from campaign strategy response'}
        else:
            return {'error': f'Campaign strategy API error: {response.message}'}
    except Exception as e:
        return {'error': f'Failed to generate campaign strategy: {str(e)}'}

def generate_images_with_wanx(image_prompts):
    """Generate images using Wanx (Tongyi Wanxiang) model"""
    generated_images = {}
    
    try:
        for key, prompt in image_prompts.items():
            try:
                response = dashscope.ImageSynthesis.call(
                    model='wanx-v1',
                    prompt=prompt,
                    n=1,
                    size='1024*1024'
                )
                
                if response.status_code == 200:
                    image_url = response.output.results[0].url
                    
                    # Download and upload to OSS
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        # Generate unique filename
                        timestamp = int(time.time())
                        filename = f"generated_{key}_{timestamp}.jpg"
                        
                        # Upload to OSS
                        bucket.put_object(filename, img_response.content)
                        
                        # Generate public URL
                        oss_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{filename}"
                        generated_images[key] = oss_url
                    else:
                        generated_images[key] = {'error': 'Failed to download generated image'}
                else:
                    generated_images[key] = {'error': f'Image generation failed: {response.message}'}
                    
            except Exception as e:
                generated_images[key] = {'error': f'Failed to generate image for {key}: {str(e)}'}
                
        return generated_images
    except Exception as e:
        return {'error': f'Failed to generate images: {str(e)}'}

def generate_video_with_wan(video_concept, brand_brief, bucket):
    """Generate professional video using enhanced video generation"""
    try:
        from src.routes.video_generator import generate_professional_video_ad
        
        # Prepare campaign data for video generation
        campaign_data = {
            'video_ad_concept': video_concept
        }
        
        # Generate professional video
        result = generate_professional_video_ad(campaign_data, brand_brief, bucket)
        
        if 'error' not in result:
            return {
                'video_url': result.get('video_url'),
                'thumbnail_url': result.get('thumbnail_url'),
                'duration': result.get('duration', '20 seconds'),
                'resolution': result.get('resolution', '1920x1080'),
                'format': result.get('format', 'MP4'),
                'status': 'Professional video ad generated successfully'
            }
        else:
            return result
            
    except Exception as e:
        return {'error': f'Failed to generate professional video: {str(e)}'}

def calculate_performance_score(campaign_data):
    """Use Qwen to analyze campaign and predict performance score"""
    try:
        prompt = f"""
        Analyze the following marketing campaign and provide a performance prediction score from 0-100 with detailed reasoning:
        
        Campaign Data: {json.dumps(campaign_data, indent=2)}
        
        Consider factors like:
        - Message clarity and appeal
        - Target audience alignment
        - Call-to-action effectiveness
        - Content quality and engagement potential
        - Platform-specific optimization
        
        Provide response in JSON format:
        {{
            "overall_score": 85,
            "breakdown": {{
                "message_clarity": 90,
                "audience_alignment": 85,
                "cta_effectiveness": 80,
                "content_quality": 88,
                "platform_optimization": 82
            }},
            "reasoning": "Detailed explanation of the score",
            "improvement_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
        }}
        """
        
        response = dashscope.Generation.call(
            model='qwen-max',
            prompt=prompt,
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    return {'error': 'No valid JSON found in performance score response'}
            except json.JSONDecodeError:
                return {'error': 'Failed to parse JSON from performance score response'}
        else:
            return {'error': f'Performance score API error: {response.message}'}
    except Exception as e:
        return {'error': f'Failed to calculate performance score: {str(e)}'}

@campaign_bp.route('/generate-campaign', methods=['POST'])
@cross_origin()
def generate_campaign():
    """Main endpoint to generate complete marketing campaign from URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        
        # Step 1: Scrape website
        print(f"Scraping website: {url}")
        website_data = scrape_website(url)
        if 'error' in website_data:
            return jsonify(website_data), 400
        
        # Step 2: Analyze brand with Qwen
        print("Analyzing brand with Qwen...")
        brand_brief = analyze_brand_with_qwen(website_data)
        if 'error' in brand_brief:
            return jsonify(brand_brief), 500
        
        # Step 3: Generate campaign strategy
        print("Generating campaign strategy...")
        campaign_strategy = generate_campaign_strategy(brand_brief)
        if 'error' in campaign_strategy:
            return jsonify(campaign_strategy), 500
        
        # Step 4: Generate images for social media posts
        print("Generating images...")
        image_prompts = {}
        if 'social_media_posts' in campaign_strategy:
            for platform, post_data in campaign_strategy['social_media_posts'].items():
                if 'image_description' in post_data:
                    image_prompts[f"{platform}_image"] = post_data['image_description']
        
        generated_images = generate_images_with_wanx(image_prompts)
        
        # Step 5: Generate video (enhanced professional video)
        print("Generating professional video...")
        video_data = None
        if 'video_ad_concept' in campaign_strategy:
            video_data = generate_video_with_wan(campaign_strategy['video_ad_concept'], brand_brief, bucket)
        
        # Step 6: Calculate performance score
        print("Calculating performance score...")
        performance_score = calculate_performance_score(campaign_strategy)
        
        # Compile final response
        response_data = {
            'success': True,
            'website_data': website_data,
            'brand_brief': brand_brief,
            'campaign_strategy': campaign_strategy,
            'generated_images': generated_images,
            'video_data': video_data,
            'performance_score': performance_score,
            'timestamp': int(time.time())
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@campaign_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'dashscope': 'configured' if DASHSCOPE_API_KEY else 'not configured',
            'oss': 'configured' if ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET else 'not configured'
        }
    })

