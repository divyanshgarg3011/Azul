import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, jsonify, request
import json
from datetime import datetime

video_showcase_bp = Blueprint('video_showcase', __name__)

# In-memory storage for demo (in production, use a database)
video_database = []

@video_showcase_bp.route('/api/videos', methods=['GET'])
def get_videos():
    """Get all generated videos"""
    try:
        return jsonify({
            'success': True,
            'videos': video_database,
            'total': len(video_database),
            'successful': len([v for v in video_database if v.get('status') == 'success']),
            'processing': len([v for v in video_database if v.get('status') == 'processing'])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_showcase_bp.route('/api/videos', methods=['POST'])
def add_video():
    """Add a new video to the database"""
    try:
        data = request.get_json()
        
        # Generate unique ID
        video_id = len(video_database) + 1
        
        # Create video entry
        video_entry = {
            'id': video_id,
            'url': data.get('video_url'),
            'title': data.get('title', f"Campaign Video #{video_id}"),
            'brand': data.get('brand_name', 'Unknown Brand'),
            'website': data.get('website_url'),
            'status': 'success' if data.get('video_url') else 'processing',
            'duration': data.get('duration', '5-10 seconds'),
            'resolution': data.get('resolution', '1280x720'),
            'created': datetime.now().isoformat(),
            'prompt': data.get('video_prompt', ''),
            'qualityScore': data.get('quality_score', 85),
            'engagementScore': data.get('engagement_score', 80),
            'brandScore': data.get('brand_score', 90),
            'thumbnail': data.get('thumbnail_url'),
            'campaign_data': data.get('campaign_data', {})
        }
        
        # Add to database (insert at beginning for newest first)
        video_database.insert(0, video_entry)
        
        return jsonify({
            'success': True,
            'video': video_entry,
            'message': 'Video added successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_showcase_bp.route('/api/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Get a specific video by ID"""
    try:
        video = next((v for v in video_database if v['id'] == video_id), None)
        
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
            
        return jsonify({
            'success': True,
            'video': video
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_showcase_bp.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video by ID"""
    try:
        global video_database
        video_database = [v for v in video_database if v['id'] != video_id]
        
        return jsonify({
            'success': True,
            'message': 'Video deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_showcase_bp.route('/api/videos/featured', methods=['GET'])
def get_featured_video():
    """Get the featured video (highest quality score)"""
    try:
        successful_videos = [v for v in video_database if v.get('status') == 'success']
        
        if not successful_videos:
            return jsonify({
                'success': False,
                'error': 'No successful videos found'
            }), 404
            
        # Get video with highest quality score
        featured_video = max(successful_videos, key=lambda v: v.get('qualityScore', 0))
        
        return jsonify({
            'success': True,
            'video': featured_video
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_showcase_bp.route('/api/videos/stats', methods=['GET'])
def get_video_stats():
    """Get video statistics"""
    try:
        total = len(video_database)
        successful = len([v for v in video_database if v.get('status') == 'success'])
        processing = len([v for v in video_database if v.get('status') == 'processing'])
        
        # Calculate average scores
        successful_videos = [v for v in video_database if v.get('status') == 'success']
        avg_quality = sum(v.get('qualityScore', 0) for v in successful_videos) / len(successful_videos) if successful_videos else 0
        avg_engagement = sum(v.get('engagementScore', 0) for v in successful_videos) / len(successful_videos) if successful_videos else 0
        avg_brand = sum(v.get('brandScore', 0) for v in successful_videos) / len(successful_videos) if successful_videos else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'successful': successful,
                'processing': processing,
                'averageQuality': round(avg_quality, 1),
                'averageEngagement': round(avg_engagement, 1),
                'averageBrand': round(avg_brand, 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize with sample data
def init_sample_data():
    """Initialize with sample video data"""
    global video_database
    
    if not video_database:  # Only add if empty
        sample_video = {
            'id': 1,
            'url': 'https://dashscope-result-sgp.oss-ap-southeast-1.aliyuncs.com/1d/bf/20250904/5259de3d/e3da172a-4754-4820-b63b-41a767ff02f1.mp4',
            'title': 'GitHub Campaign Video',
            'brand': 'GitHub',
            'website': 'https://github.com',
            'status': 'success',
            'duration': '8 seconds',
            'resolution': '1280x720',
            'created': '2025-09-04T03:08:32Z',
            'prompt': 'A professional marketing video for GitHub · Build and ship software on a single, collaborative platform · GitHub, a technology company. Show modern office environment with people working, clean and professional atmosphere, high quality cinematography',
            'qualityScore': 92,
            'engagementScore': 88,
            'brandScore': 95,
            'thumbnail': None,
            'campaign_data': {}
        }
        video_database.append(sample_video)

# Initialize sample data when module is imported
init_sample_data()

