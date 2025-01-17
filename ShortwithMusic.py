from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip, AudioFileClip
import numpy as np

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
        font = ImageFont.load_default()  # Fallback to default font
    
    # Calculate text size using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill=color, font=font)
    return img

# Paths
input_video_path = r"C:\Users\amuke\Downloads\WhatsApp Video 2025-01-17 at 18.49.33.mp4"  # Replace with your video path
background_music_path = r"C:\Users\amuke\Downloads\Tera_Nasha_14.mp3"  # Replace with your music file path
output_video_path = "output_video_with_music.mp4"

# Define the interesting parts of the video (start and end times in seconds)
clip_intervals = [(15, 40)]  # Example intervals
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
    text_clip = text_clip.set_start(sum(end - start for _, start in clip_intervals[:i]))  # Set start time
    text_clips.append(text_clip)

# Combine text overlays with the video
final_video = CompositeVideoClip([final_clip, *text_clips])

# Add background music
background_music = AudioFileClip(background_music_path)
final_video = final_video.set_audio(background_music.set_duration(final_video.duration))

# Write the output video
final_video.write_videofile(output_video_path, codec="libx264", fps=24)


