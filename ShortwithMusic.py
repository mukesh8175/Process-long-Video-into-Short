from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip, AudioFileClip
import numpy as np
import os

# Function to create a text image using Pillow
def create_text_image(text, size, color, font_path="arial.ttf"):
    """
    Create a transparent image with centered text.

    Args:
        text (str): The text to display.
        size (tuple): The size of the image (width, height).
        color (str): The color of the text.
        font_path (str): Path to the font file.

    Returns:
        PIL.Image.Image: The generated text image.
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, 50)  # Adjust font size
    except OSError:
        print("Font not found. Using default font.")
        font = ImageFont.load_default()  # Fallback to default font
    
    # Calculate text size using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill=color, font=font)
    return img

# Validate file paths
def validate_file(path, file_type):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The {file_type} file does not exist: {path}")

# Paths
input_video_path = r"C:\Users\amuke\Downloads\WhatsApp Video 2025-01-17 at 18.49.33.mp4"
background_music_path = r"C:\Users\amuke\Downloads\teri-ye-adaa-romantic-song-206526.mp3"
output_video_path = "output_video_with_music.mp4"

# Validate input files
validate_file(input_video_path, "video")
validate_file(background_music_path, "audio")

# Define the interesting parts of the video (start and end times in seconds)
clip_intervals = [(2, 15),(22,25),(36,42),(44,55),]   # Example intervals
clips = []

# Load and crop clips
for start, end in clip_intervals:
    clip = VideoFileClip(input_video_path).subclip(start, end)
    # Crop to 9:16 aspect ratio (center crop for vertical format)
    clip = clip.crop(x_center=clip.w / 2, width=clip.h * 9 / 16, height=clip.h)
    clips.append(clip)

# Concatenate selected clips
final_clip = concatenate_videoclips(clips)

# Add text overlays
text_clips = []
video_size = (final_clip.w, final_clip.h)  # Size of the video frame
for i, (start, end) in enumerate(clip_intervals):
    # Create a text image
    text_image = create_text_image(f"Scene {i+1}", video_size, "white")
    text_clip = ImageClip(np.array(text_image)).set_duration(end - start).set_position("center")
    # Set start time based on accumulated duration of previous clips
    text_clip = text_clip.set_start(sum(end - start for start, end in clip_intervals[:i]))
    text_clips.append(text_clip)

# Combine text overlays with the video
final_video = CompositeVideoClip([final_clip, *text_clips])

# Add background music
background_music = AudioFileClip(background_music_path)

# Ensure the background music's time range is within the clip duration
audio_duration = background_music.duration
if audio_duration < final_video.duration:
    # Loop audio if it's shorter than the video
    background_music = background_music.fx(lambda a: a.audio_loop(final_video.duration))
else:
    # Trim audio to the video duration if it exceeds
    background_music = background_music.subclip(0, final_video.duration)

final_video = final_video.set_audio(background_music.set_duration(final_video.duration))

# Write the output video
final_video.write_videofile(output_video_path, codec="libx264", fps=24, bitrate="3000k", audio_codec="aac")

