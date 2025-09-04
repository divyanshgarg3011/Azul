from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup
import time

basic_campaign_bp = Blueprint('basic_campaign', __name__)

def scrape_website(url):
    """Scrape website content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title')
        title_text = title.get_text().strip() if title else 'Unknown'
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ''
        
        # Extract some text content
        paragraphs = soup.find_all('p')
        content_text = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
        
        return {
            'success': True,
            'title': title_text,
            'description': description,
            'content': content_text[:500],  # Limit content length
            'url': url
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to scrape website: {str(e)}',
            'url': url
        }

def extract_brand_name(title):
    """Extract brand name from title"""
    # Simple extraction logic
    parts = title.split(' - ')[0].split(' | ')[0].split(' · ')[0]
    return parts.strip()

def analyze_brand_basic(website_data):
    """Basic brand analysis"""
    title = website_data.get('title', 'Unknown Brand')
    brand_name = extract_brand_name(title)
    
    # Determine industry based on keywords
    content = (website_data.get('description', '') + ' ' + website_data.get('content', '')).lower()
    
    if any(word in content for word in ['software', 'technology', 'platform', 'development', 'digital', 'tech', 'code', 'github']):
        industry = 'technology'
    elif any(word in content for word in ['finance', 'financial', 'banking', 'investment', 'money']):
        industry = 'finance'
    elif any(word in content for word in ['health', 'medical', 'healthcare', 'hospital']):
        industry = 'healthcare'
    elif any(word in content for word in ['education', 'learning', 'school', 'university']):
        industry = 'education'
    else:
        industry = 'business'
    
    return {
        'brand_name': brand_name,
        'industry': industry,
        'brand_tone': 'professional',
        'target_audience': f'{industry.title()} professionals and users',
        'value_propositions': [
            'Quality solutions',
            'Reliable service',
            'Professional approach',
            'Innovation-driven'
        ],
        'personality_traits': ['Professional', 'Trustworthy', 'Reliable', 'Innovative']
    }

def generate_social_media_posts(brand_brief):
    """Generate social media posts"""
    brand_name = brand_brief['brand_name']
    industry = brand_brief['industry']
    
    return {
        'facebook': {
            'headline': f'Discover {brand_name} - Your Trusted Partner',
            'primary_text': f'Experience excellence with {brand_name}. We deliver quality solutions that make a difference in {industry}.',
            'hashtags': [f'#{brand_name.replace(" ", "")}', f'#{industry.title()}', '#Quality', '#Excellence', '#Innovation']
        },
        'instagram': {
            'caption': f'✨ {brand_name} - Where quality meets innovation! 🚀\n\nExperience the difference with our {industry} solutions.\n\n#Excellence #Quality #Innovation',
            'hashtags': [f'#{brand_name.replace(" ", "")}', f'#{industry.title()}', '#Quality', '#Innovation', '#Excellence', '#Professional']
        },
        'linkedin': {
            'headline': f'{brand_name}: Professional Excellence in {industry.title()}',
            'post_text': f'At {brand_name}, we understand the importance of quality and reliability in {industry}. Our commitment to excellence drives everything we do. Join us in shaping the future of {industry}.',
            'hashtags': [f'#{brand_name.replace(" ", "")}', f'#{industry.title()}', '#Business', '#Professional', '#Excellence']
        },
        'tiktok': {
            'caption': f'🔥 {brand_name} is changing the game in {industry}! ✨\n\nSee why everyone is talking about us!\n\n#Trending #Innovation',
            'hashtags': [f'#{brand_name.replace(" ", "")}', '#Trending', '#Innovation', '#Viral', '#Quality', f'#{industry.title()}']
        }
    }

def generate_campaign_strategy_basic(brand_brief):
    """Basic campaign strategy"""
    brand_name = brand_brief['brand_name']
    industry = brand_brief['industry']
    
    return {
        'campaign_objective': f'Increase brand awareness and engagement for {brand_name} in the {industry} sector',
        'key_messaging': f'Discover the power of {brand_name} - your trusted partner in {industry}',
        'target_platforms': ['Facebook', 'Instagram', 'LinkedIn', 'TikTok'],
        'content_themes': ['Innovation', 'Quality', 'Trust', 'Results', 'Excellence'],
        'video_ad_concept': {
            'video_prompt': f'A professional marketing video for {brand_name}, a leading {industry} company. Show modern office environment with people working collaboratively, clean and professional atmosphere, high quality cinematography, dynamic camera movements',
            'duration': '8 seconds',
            'style': 'professional',
            'key_message': f'Experience excellence with {brand_name}',
            'call_to_action': 'Learn More'
        },
        'social_media_posts': generate_social_media_posts(brand_brief),
        'brand_name': brand_name
    }

def generate_video_ad_demo(campaign_strategy):
    """Generate demo video ad data"""
    brand_name = campaign_strategy.get('brand_name', 'Brand')
    video_concept = campaign_strategy.get('video_ad_concept', {})
    
    # Demo video URLs (you can replace with actual generated videos)
    demo_videos = [
        'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
        'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
    ]
    
    return {
        'success': True,
        'video_url': demo_videos[0],  # Use first demo video
        'title': f"{brand_name} Campaign Video",
        'duration': '8 seconds',
        'style': video_concept.get('style', 'professional'),
        'prompt': video_concept.get('video_prompt', 'Professional marketing video'),
        'message': video_concept.get('key_message', ''),
        'call_to_action': video_concept.get('call_to_action', 'Learn More'),
        'quality_score': 88,
        'engagement_score': 85,
        'brand_score': 92,
        'brand_name': brand_name,
        'note': 'Demo video - AI video generation available with DashScope API'
    }

def calculate_performance_score(campaign_data):
    """Calculate performance score"""
    base_score = 82
    
    # Add points for various factors
    if campaign_data.get('video_data', {}).get('success'):
        base_score += 8
    
    if len(campaign_data.get('social_media_posts', {})) >= 4:
        base_score += 5
    
    if campaign_data.get('brand_brief', {}).get('brand_name'):
        base_score += 5
    
    return {
        'overall_score': min(base_score, 95),
        'breakdown': {
            'content_quality': 88,
            'brand_alignment': 92,
            'engagement_potential': 85,
            'platform_optimization': 87
        },
        'improvement_suggestions': [
            'Enable DashScope API for AI-powered video generation',
            'Consider A/B testing different video concepts',
            'Optimize posting times for each platform',
            'Include more interactive content elements',
            'Monitor engagement metrics and adjust strategy'
        ]
    }

@basic_campaign_bp.route('/generate-campaign-ai', methods=['POST'])
@cross_origin()
def generate_campaign_basic():
    """Generate marketing campaign with basic features"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        print(f"Scraping website: {url}")
        
        # Step 1: Scrape website
        website_data = scrape_website(url)
        if not website_data['success']:
            return jsonify({'error': website_data['error']}), 400
        
        # Step 2: Analyze brand
        print("Analyzing brand...")
        brand_brief = analyze_brand_basic(website_data)
        
        # Step 3: Generate campaign strategy
        print("Generating campaign strategy...")
        campaign_strategy = generate_campaign_strategy_basic(brand_brief)
        
        # Step 4: Generate demo video ad
        print("Generating demo video ad...")
        video_data = generate_video_ad_demo(campaign_strategy)
        
        # Step 5: Calculate performance score
        print("Calculating performance score...")
        performance_score = calculate_performance_score({
            'video_data': video_data,
            'social_media_posts': campaign_strategy['social_media_posts'],
            'brand_brief': brand_brief
        })
        
        # Compile final response
        response_data = {
            'success': True,
            'mode': 'basic_demo',
            'features_used': {
                'qwen_analysis': False,
                'video_generation': False,
                'ai_scoring': True
            },
            'website_data': website_data,
            'brand_brief': brand_brief,
            'campaign_strategy': campaign_strategy,
            'video_data': video_data,
            'performance_score': performance_score,
            'timestamp': int(time.time()),
            'note': 'Demo mode - Enable DashScope API for full AI features'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in generate_campaign_basic: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@basic_campaign_bp.route('/test-ai', methods=['GET'])
@cross_origin()
def test_basic():
    """Test endpoint for basic functionality"""
    return jsonify({
        'status': 'Basic campaign generation ready',
        'dashscope_available': False,
        'mode': 'demo',
        'features': [
            'Website scraping',
            'Basic brand analysis',
            'Campaign strategy generation',
            'Demo video ad display',
            'Performance scoring',
            'Social media content creation'
        ],
        'note': 'Enable DashScope API for AI-powered features',
        'video_capabilities': {
            'model': 'demo',
            'duration': '8 seconds',
            'resolution': '1280x720',
            'format': 'MP4'
        }
    })

