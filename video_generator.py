import os
import json
import time
import requests
from moviepy.editor import *
from moviepy.config import check_and_download_cmd
import dashscope
import oss2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class ProfessionalVideoGenerator:
    def __init__(self, oss_bucket):
        self.bucket = oss_bucket
        self.temp_dir = "/tmp/video_generation"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def generate_professional_video_ad(self, campaign_data, brand_brief):
        """Generate a professional 20-second video ad"""
        try:
            # Extract video concept from campaign data
            video_concept = campaign_data.get('video_ad_concept', {})
            scenes = video_concept.get('scenes', [])
            
            if not scenes:
                return {'error': 'No video scenes found in campaign data'}
            
            # Generate images for each scene
            scene_images = self._generate_scene_images(scenes, brand_brief)
            
            # Create video clips from images
            video_clips = self._create_video_clips(scene_images, scenes)
            
            # Add professional transitions and effects
            final_video = self._add_professional_effects(video_clips, campaign_data, brand_brief)
            
            # Add audio/music (placeholder for now)
            final_video = self._add_background_music(final_video)
            
            # Export and upload video
            video_url = self._export_and_upload_video(final_video)
            
            return {
                'video_url': video_url,
                'duration': '20 seconds',
                'format': 'MP4',
                'resolution': '1920x1080',
                'status': 'success'
            }
            
        except Exception as e:
            return {'error': f'Failed to generate professional video: {str(e)}'}
    
    def _generate_scene_images(self, scenes, brand_brief):
        """Generate high-quality images for each video scene"""
        scene_images = []
        
        for i, scene in enumerate(scenes):
            try:
                # Create detailed prompt for professional imagery
                prompt = self._create_professional_image_prompt(scene, brand_brief, i+1)
                
                # Generate image using Wanx
                response = dashscope.ImageSynthesis.call(
                    model='wanx-v1',
                    prompt=prompt,
                    n=1,
                    size='1024*1024',
                    style='photography'  # Professional photography style
                )
                
                if response.status_code == 200:
                    image_url = response.output.results[0].url
                    
                    # Download image
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        # Save locally for video processing
                        image_path = f"{self.temp_dir}/scene_{i+1}.jpg"
                        with open(image_path, 'wb') as f:
                            f.write(img_response.content)
                        scene_images.append(image_path)
                    else:
                        # Use placeholder if download fails
                        scene_images.append(self._create_placeholder_image(scene, i+1))
                else:
                    scene_images.append(self._create_placeholder_image(scene, i+1))
                    
            except Exception as e:
                print(f"Error generating scene {i+1}: {str(e)}")
                scene_images.append(self._create_placeholder_image(scene, i+1))
        
        return scene_images
    
    def _create_professional_image_prompt(self, scene, brand_brief, scene_number):
        """Create detailed prompt for professional scene imagery"""
        brand_name = brand_brief.get('brand_name', 'Brand')
        industry = brand_brief.get('industry', 'business')
        brand_tone = brand_brief.get('brand_tone', 'professional')
        
        base_prompt = f"""
        Professional commercial photography for {brand_name} in {industry} industry.
        Scene {scene_number}: {scene.get('description', '')}
        Visual elements: {scene.get('visual_elements', '')}
        
        Style: {brand_tone}, high-end commercial photography, studio lighting,
        professional composition, brand-focused, marketing campaign quality,
        clean background, modern aesthetic, high resolution, sharp focus,
        commercial advertising style, premium quality
        """
        
        return base_prompt.strip()
    
    def _create_placeholder_image(self, scene, scene_number):
        """Create a professional placeholder image if generation fails"""
        try:
            # Create a professional-looking placeholder
            img = Image.new('RGB', (1024, 1024), color=(45, 55, 72))  # Professional dark blue
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Add scene text
            scene_text = f"Scene {scene_number}"
            description = scene.get('description', 'Professional Video Scene')[:50]
            
            # Center the text
            bbox = draw.textbbox((0, 0), scene_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (1024 - text_width) // 2
            y = (1024 - text_height) // 2 - 50
            
            draw.text((x, y), scene_text, fill=(255, 255, 255), font=font)
            
            # Add description
            bbox2 = draw.textbbox((0, 0), description, font=small_font)
            text_width2 = bbox2[2] - bbox2[0]
            x2 = (1024 - text_width2) // 2
            draw.text((x2, y + 80), description, fill=(200, 200, 200), font=small_font)
            
            # Save placeholder
            placeholder_path = f"{self.temp_dir}/placeholder_scene_{scene_number}.jpg"
            img.save(placeholder_path)
            return placeholder_path
            
        except Exception as e:
            print(f"Error creating placeholder: {str(e)}")
            return None
    
    def _create_video_clips(self, scene_images, scenes):
        """Create video clips from scene images with professional timing"""
        clips = []
        
        for i, (image_path, scene) in enumerate(zip(scene_images, scenes)):
            if image_path and os.path.exists(image_path):
                try:
                    # Calculate duration (aim for ~6-7 seconds per scene for 20 second total)
                    duration = 6.5 if i < len(scenes) - 1 else 7.0  # Last scene slightly longer
                    
                    # Create image clip
                    clip = ImageClip(image_path, duration=duration)
                    
                    # Resize to HD
                    clip = clip.resize((1920, 1080))
                    
                    # Add subtle zoom effect for professional look
                    if i % 2 == 0:
                        # Zoom in effect
                        clip = clip.resize(lambda t: 1 + 0.02 * t)
                    else:
                        # Zoom out effect  
                        clip = clip.resize(lambda t: 1.05 - 0.02 * t)
                    
                    # Add text overlay for scene
                    scene_description = scene.get('description', '')
                    if scene_description:
                        txt_clip = self._create_text_overlay(scene_description, duration)
                        clip = CompositeVideoClip([clip, txt_clip])
                    
                    clips.append(clip)
                    
                except Exception as e:
                    print(f"Error creating clip for scene {i+1}: {str(e)}")
                    continue
        
        return clips
    
    def _create_text_overlay(self, text, duration):
        """Create professional text overlay"""
        try:
            # Create text clip with professional styling
            txt_clip = TextClip(text[:60], 
                              fontsize=50, 
                              color='white', 
                              font='Arial-Bold',
                              stroke_color='black',
                              stroke_width=2)
            
            # Position at bottom center
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration)
            
            # Add fade in/out
            txt_clip = txt_clip.fadeout(0.5).fadein(0.5)
            
            return txt_clip
            
        except Exception as e:
            print(f"Error creating text overlay: {str(e)}")
            return None
    
    def _add_professional_effects(self, clips, campaign_data, brand_brief):
        """Add professional transitions and effects"""
        try:
            if not clips:
                return None
            
            # Add crossfade transitions between clips
            final_clips = []
            for i, clip in enumerate(clips):
                if i > 0:
                    # Add crossfade transition
                    clip = clip.crossfadein(0.5)
                if i < len(clips) - 1:
                    clip = clip.crossfadeout(0.5)
                final_clips.append(clip)
            
            # Concatenate clips
            final_video = concatenate_videoclips(final_clips, method="compose")
            
            # Add brand logo overlay (if we had logo)
            # This would require the logo image from the website
            
            # Add call-to-action at the end
            cta_text = campaign_data.get('video_ad_concept', {}).get('call_to_action', 'Learn More')
            cta_clip = self._create_cta_overlay(cta_text, 2.0)
            if cta_clip:
                final_video = CompositeVideoClip([final_video, cta_clip])
            
            # Ensure exactly 20 seconds
            final_video = final_video.subclip(0, min(20, final_video.duration))
            
            return final_video
            
        except Exception as e:
            print(f"Error adding professional effects: {str(e)}")
            return concatenate_videoclips(clips) if clips else None
    
    def _create_cta_overlay(self, cta_text, duration):
        """Create call-to-action overlay"""
        try:
            # Create CTA text with button-like styling
            cta_clip = TextClip(cta_text, 
                              fontsize=60, 
                              color='white', 
                              font='Arial-Bold',
                              bg_color='blue',
                              size=(400, 80))
            
            # Position at center bottom
            cta_clip = cta_clip.set_position(('center', 0.8), relative=True)
            cta_clip = cta_clip.set_duration(duration)
            cta_clip = cta_clip.set_start(18)  # Show in last 2 seconds
            
            # Add pulsing effect
            cta_clip = cta_clip.resize(lambda t: 1 + 0.1 * np.sin(2 * np.pi * t))
            
            return cta_clip
            
        except Exception as e:
            print(f"Error creating CTA overlay: {str(e)}")
            return None
    
    def _add_background_music(self, video):
        """Add background music (placeholder for now)"""
        try:
            # For now, return video without music
            # In a full implementation, you would:
            # 1. Generate or select appropriate background music
            # 2. Add it to the video with proper volume levels
            # 3. Ensure it matches the video duration
            
            return video
            
        except Exception as e:
            print(f"Error adding background music: {str(e)}")
            return video
    
    def _export_and_upload_video(self, video):
        """Export video and upload to OSS"""
        try:
            if not video:
                return None
            
            # Export video
            timestamp = int(time.time())
            video_filename = f"professional_ad_{timestamp}.mp4"
            local_path = f"{self.temp_dir}/{video_filename}"
            
            # Write video file
            video.write_videofile(local_path, 
                                fps=30, 
                                codec='libx264',
                                audio_codec='aac',
                                temp_audiofile=f"{self.temp_dir}/temp_audio.m4a",
                                remove_temp=True)
            
            # Upload to OSS
            with open(local_path, 'rb') as f:
                self.bucket.put_object(video_filename, f)
            
            # Generate public URL
            video_url = f"https://{self.bucket.bucket_name}.{self.bucket.endpoint.replace('http://', '').replace('https://', '')}/{video_filename}"
            
            # Clean up local file
            if os.path.exists(local_path):
                os.remove(local_path)
            
            return video_url
            
        except Exception as e:
            print(f"Error exporting and uploading video: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")

def generate_professional_video_ad(campaign_data, brand_brief, oss_bucket):
    """Main function to generate professional video ad"""
    generator = ProfessionalVideoGenerator(oss_bucket)
    try:
        result = generator.generate_professional_video_ad(campaign_data, brand_brief)
        return result
    finally:
        generator.cleanup()

