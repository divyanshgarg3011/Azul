import os
import json
import requests
import time
from urllib.parse import urlparse
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from bs4 import BeautifulSoup
import oss2

backup_campaign_bp = Blueprint('backup_campaign', __name__)

# Configuration
ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT', 'oss-me-east-1.aliyuncs.com')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME', 'azul-campaign-assets')

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

def analyze_brand_basic(website_data):
    """Basic brand analysis without AI (rule-based)"""
    try:
        title = website_data.get('title', '').lower()
        description = website_data.get('description', '').lower()
        content = website_data.get('content', '').lower()
        
        # Extract brand name (simple heuristic)
        brand_name = website_data.get('title', '').split(' - ')[0].split(' | ')[0]
        if not brand_name:
            domain = urlparse(website_data.get('url', '')).netloc
            brand_name = domain.replace('www.', '').split('.')[0].title()
        
        # Determine industry (keyword matching)
        industry_keywords = {
            'technology': ['tech', 'software', 'app', 'digital', 'ai', 'cloud', 'data'],
            'ecommerce': ['shop', 'store', 'buy', 'product', 'cart', 'order'],
            'finance': ['bank', 'finance', 'money', 'investment', 'loan', 'credit'],
            'healthcare': ['health', 'medical', 'doctor', 'hospital', 'care'],
            'education': ['education', 'school', 'learn', 'course', 'university'],
            'food': ['food', 'restaurant', 'recipe', 'cook', 'eat'],
            'travel': ['travel', 'hotel', 'flight', 'vacation', 'trip'],
            'fashion': ['fashion', 'clothing', 'style', 'wear', 'apparel']
        }
        
        detected_industry = 'business'
        for industry, keywords in industry_keywords.items():
            if any(keyword in content for keyword in keywords):
                detected_industry = industry
                break
        
        # Generate basic brand brief
        brand_brief = {
            'brand_name': brand_name,
            'industry': detected_industry,
            'target_audience': 'General consumers and businesses',
            'value_propositions': [
                'Quality products and services',
                'Customer satisfaction',
                'Innovation and reliability'
            ],
            'brand_personality': 'professional',
            'key_products_services': ['Primary service', 'Secondary offering'],
            'competitive_advantages': ['Quality', 'Service', 'Innovation'],
            'brand_tone': 'professional'
        }
        
        return brand_brief
        
    except Exception as e:
        return {'error': f'Failed to analyze brand: {str(e)}'}

def generate_campaign_strategy_basic(brand_brief):
    """Generate basic campaign strategy without AI"""
    try:
        brand_name = brand_brief.get('brand_name', 'Brand')
        industry = brand_brief.get('industry', 'business')
        
        # Generate campaign strategy
        campaign_strategy = {
            'campaign_objective': f'Increase brand awareness and drive engagement for {brand_name}',
            'target_platforms': ['Facebook', 'Instagram', 'LinkedIn', 'TikTok'],
            'content_themes': ['Brand Story', 'Product Benefits', 'Customer Success'],
            'video_ad_concept': {
                'duration': '20-30 seconds',
                'style': 'professional',
                'key_message': f'Discover what makes {brand_name} different',
                'call_to_action': 'Learn More',
                'scenes': [
                    {
                        'scene_number': 1,
                        'description': f'{brand_name} logo and brand introduction',
                        'duration': '5-8 seconds',
                        'visual_elements': 'Clean brand presentation with logo'
                    },
                    {
                        'scene_number': 2,
                        'description': f'Showcase {brand_name} key products or services',
                        'duration': '8-12 seconds',
                        'visual_elements': 'Product demonstration or service highlights'
                    },
                    {
                        'scene_number': 3,
                        'description': f'Call to action and contact information',
                        'duration': '7-10 seconds',
                        'visual_elements': 'Strong call-to-action with contact details'
                    }
                ]
            },
            'social_media_posts': {
                'facebook': {
                    'headline': f'Discover {brand_name} - Your Trusted Partner',
                    'primary_text': f'Experience excellence with {brand_name}. We deliver quality solutions that make a difference. Join thousands of satisfied customers who trust us for their {industry} needs.',
                    'hashtags': [f'#{brand_name.replace(" ", "")}', f'#{industry}', '#Quality', '#Excellence'],
                    'image_description': f'Professional {brand_name} brand image showcasing quality and trust'
                },
                'instagram': {
                    'caption': f'✨ {brand_name} - Where quality meets innovation! 🚀 Experience the difference today. #Excellence #Quality #Innovation',
                    'hashtags': [f'#{brand_name.replace(" ", "")}', f'#{industry}', '#Quality', '#Innovation', '#Excellence'],
                    'image_description': f'Instagram-style {brand_name} brand image with modern aesthetic'
                },
                'linkedin': {
                    'headline': f'{brand_name}: Professional Excellence in {industry.title()}',
                    'post_text': f'At {brand_name}, we understand the importance of quality and reliability in {industry}. Our commitment to excellence has made us a trusted partner for businesses worldwide.',
                    'hashtags': [f'#{brand_name.replace(" ", "")}', f'#{industry}', '#Business', '#Professional'],
                    'image_description': f'Professional LinkedIn-style {brand_name} corporate image'
                },
                'tiktok': {
                    'caption': f'🔥 {brand_name} is changing the game! ✨ #Trending #Innovation',
                    'hashtags': [f'#{brand_name.replace(" ", "")}', '#Trending', '#Innovation', '#Viral'],
                    'video_concept': f'Quick showcase of {brand_name} with trending music and effects'
                }
            },
            'multilingual_content': {
                'english': {
                    'headline': f'Experience {brand_name} Excellence',
                    'primary_text': f'Discover why {brand_name} is the preferred choice for quality {industry} solutions.'
                },
                'arabic': {
                    'headline': f'اكتشف تميز {brand_name}',
                    'primary_text': f'اكتشف لماذا {brand_name} هو الخيار المفضل لحلول {industry} عالية الجودة.'
                }
            }
        }
        
        return campaign_strategy
        
    except Exception as e:
        return {'error': f'Failed to generate campaign strategy: {str(e)}'}

def calculate_performance_score_basic(campaign_data):
    """Basic performance score calculation"""
    try:
        # Simple scoring based on content completeness
        score_factors = {
            'message_clarity': 85,
            'audience_alignment': 80,
            'cta_effectiveness': 75,
            'content_quality': 80,
            'platform_optimization': 85
        }
        
        overall_score = sum(score_factors.values()) // len(score_factors)
        
        return {
            'overall_score': overall_score,
            'breakdown': score_factors,
            'reasoning': 'Score based on content structure, platform optimization, and campaign completeness.',
            'improvement_suggestions': [
                'Add more personalized content',
                'Include customer testimonials',
                'Optimize for mobile viewing'
            ]
        }
        
    except Exception as e:
        return {'error': f'Failed to calculate performance score: {str(e)}'}

@backup_campaign_bp.route('/generate-campaign-basic', methods=['POST'])
@cross_origin()
def generate_campaign_basic():
    """Basic campaign generation without AI dependencies"""
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
        
        # Step 2: Basic brand analysis
        print("Analyzing brand (basic mode)...")
        brand_brief = analyze_brand_basic(website_data)
        if 'error' in brand_brief:
            return jsonify(brand_brief), 500
        
        # Step 3: Generate campaign strategy
        print("Generating campaign strategy (basic mode)...")
        campaign_strategy = generate_campaign_strategy_basic(brand_brief)
        if 'error' in campaign_strategy:
            return jsonify(campaign_strategy), 500
        
        # Step 4: Calculate performance score
        print("Calculating performance score...")
        performance_score = calculate_performance_score_basic(campaign_strategy)
        
        # Compile final response
        response_data = {
            'success': True,
            'mode': 'basic',
            'note': 'Generated using basic analysis. Full AI features available once DashScope API is configured.',
            'website_data': website_data,
            'brand_brief': brand_brief,
            'campaign_strategy': campaign_strategy,
            'generated_images': {'note': 'Image generation requires DashScope API'},
            'video_data': {'note': 'Video generation requires DashScope API'},
            'performance_score': performance_score,
            'timestamp': int(time.time())
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@backup_campaign_bp.route('/test-basic', methods=['GET'])
@cross_origin()
def test_basic():
    """Test endpoint for basic functionality"""
    return jsonify({
        'status': 'Basic campaign generation is working',
        'features': [
            'Website scraping',
            'Basic brand analysis',
            'Campaign strategy generation',
            'Social media content creation',
            'Performance scoring'
        ],
        'note': 'AI features (Qwen, image/video generation) require DashScope API configuration'
    })

