import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy.io import wavfile
import cv2
import shutil
from pathlib import Path

def generate_text_file():
    """Generate a sample text file with random content"""
    text = "Sample text for testing OCR and semantic search capabilities.\n\n"
    text += "This is a test document containing various types of content:\n"
    text += "- Technical specifications\n"
    text += "- Product descriptions\n"
    text += "- User reviews\n\n"
    text += "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
    text += "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n"
    
    os.makedirs("test_data/text", exist_ok=True)
    with open("test_data/text/sample.txt", "w") as f:
        f.write(text)

def generate_image():
    """Generate a sample image with text and shapes"""
    # Create a white image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes
    draw.rectangle([100, 100, 300, 200], outline='blue', width=2)
    draw.ellipse([400, 100, 600, 200], outline='red', width=2)
    
    # Add some text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 300), "Sample Image for OCR Testing", font=font, fill='black')
    draw.text((100, 350), "This is a test image with multiple elements", font=font, fill='black')
    
    os.makedirs("test_data/image", exist_ok=True)
    img.save("test_data/image/sample.jpg")

def generate_audio():
    """Generate a sample audio file"""
    # Generate a simple sine wave
    sample_rate = 44100
    duration = 5  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # Hz (A4 note)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Normalize and convert to 16-bit integer
    audio_data = (audio_data * 32767).astype(np.int16)
    
    os.makedirs("test_data/audio", exist_ok=True)
    wavfile.write("test_data/audio/sample.mp3", sample_rate, audio_data)

def generate_video():
    """Generate a sample video file"""
    # Create a video with moving shapes
    width, height = 640, 480
    fps = 30
    duration = 5  # seconds
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_data/video/sample.mp4', fourcc, fps, (width, height))
    
    for frame in range(fps * duration):
        # Create a frame
        frame_img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw a moving circle
        x = int(width/2 + 100 * np.sin(frame/30))
        y = int(height/2 + 100 * np.cos(frame/30))
        cv2.circle(frame_img, (x, y), 50, (0, 255, 0), -1)
        
        # Add some text
        cv2.putText(frame_img, "Sample Video", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame_img)
    
    out.release()

def generate_test_data():
    # Create test data directories
    base_dir = Path("test_data")
    directories = ["text", "image", "audio", "video"]
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

    # Generate Shakespeare text sample
    shakespeare_text = """To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take Arms against a Sea of troubles,
And by opposing end them: to die, to sleep
No more; and by a sleep, to say we end
The heart-ache, and the thousand natural shocks
That flesh is heir to? 'Tis a consummation
Devoutly to be wished. To die, to sleep,
To sleep, perchance to Dream; aye, there's the rub,
For in that sleep of death, what dreams may come,
When we have shuffled off this mortal coil,
Must give us pause.

All the world's a stage,
And all the men and women merely players;
They have their exits and their entrances,
And one man in his time plays many parts,
His acts being seven ages.

Tomorrow, and tomorrow, and tomorrow,
Creeps in this petty pace from day to day,
To the last syllable of recorded time;
And all our yesterdays have lighted fools
The way to dusty death. Out, out, brief candle!
Life's but a walking shadow, a poor player
That struts and frets his hour upon the stage
And then is heard no more."""

    # Write Shakespeare text to file
    shakespeare_path = base_dir / "text" / "shakespeare_sample.txt"
    with open(shakespeare_path, "w", encoding="utf-8") as f:
        f.write(shakespeare_text)

    print(f"Generated Shakespeare text sample at {shakespeare_path}")

    # Generate other test files here...
    # (Previous test data generation code remains unchanged)

def main():
    """Generate all sample test data"""
    print("Generating test data...")
    
    # Generate text file
    print("Generating text file...")
    generate_text_file()
    
    # Generate image
    print("Generating image...")
    generate_image()
    
    # Generate audio
    print("Generating audio...")
    generate_audio()
    
    # Generate video
    print("Generating video...")
    generate_video()
    
    print("Test data generation complete!")

if __name__ == "__main__":
    generate_test_data() 