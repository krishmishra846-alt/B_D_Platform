import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from deepface import DeepFace
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.telegram_notifier import send_thank_you_message

# Load the Hindi/Marathi Font
font_path = "../assets/NotoSansDevanagari.ttf"
try:
    hindi_font = ImageFont.truetype(font_path, 32)
except Exception:
    print("Warning: Font not found. Make sure NotoSansDevanagari.ttf is in the assets folder!")
    hindi_font = ImageFont.load_default()

def overlay_text_devanagari(img_cv2, text, position, color=(0, 255, 0)):
    """Converts OpenCV image to PIL to render Devanagari, then converts back."""
    img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text(position, text, font=hindi_font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def run_verification_desk():
    print("Starting Organizer Touchless Desk...")
    cap = cv2.VideoCapture(0)
    
    # In a real run, this path comes from the QR code via Supabase
    reference_image_path = "../assets/reference_face.jpg" 
    
    verified = False
    verification_text = "चेहरा स्कॅन करत आहे..." # "Scanning face..." in Marathi
    box_color = (0, 165, 255) # Orange

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Draw the target box
        cv2.rectangle(frame, (150, 100), (450, 400), box_color, 2)
        
        # Overlay the Devanagari HUD
        frame = overlay_text_devanagari(frame, verification_text, (160, 50), box_color)
        
        cv2.imshow("On-Site Verification Node", frame)
        
        key = cv2.waitKey(1)
        
        # Press 'v' to manually trigger the DeepFace comparison
        if key & 0xFF == ord('v') and not verified:
            print("Verifying against baseline...")
            cv2.imwrite("temp_live.jpg", frame)
            try:
                # Compare live frame against the stored registration photo
                result = DeepFace.verify("temp_live.jpg", reference_image_path, model_name="VGG-Face", enforce_detection=False)
                if result["verified"]:
                    verified = True
                    verification_text = "पडताळणी यशस्वी!" 
                    box_color = (0, 255, 0) 
                    print("Match Confirmed! Emitting attendance log...")
                    
                    # Send the immediate Telegram ping in Marathi
                    test_chat_id = "8967689927" 
                    send_thank_you_message(donor_name="Krish", chat_id=test_chat_id, language="mr")
                else:
                    verification_text = "चेहरा जुळला नाही" # "Face not matched"
                    box_color = (0, 0, 255) # Red
            except Exception as e:
                print(f"DeepFace error: {e}")
                
        # Press 'q' to quit
        if key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_verification_desk()