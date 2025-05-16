import cv2
import face_recognition

images = ["Nikunj.jpg", "Nitin.jpg", "Naman.jpg", "Nishant.jpg"]

for img_path in images:
    img = cv2.imread(img_path)
    if img is None:
        print(f"[ERROR] Could not load image: {img_path}")
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(img_rgb)

    if encodings:
        print(f"[SUCCESS] Face encoding found in: {img_path}")
    else:
        print(f"[WARNING] No face found in: {img_path}")
