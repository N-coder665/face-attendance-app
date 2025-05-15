# from flask import Flask, render_template, redirect, url_for
# from openpyxl import load_workbook
# from datetime import datetime
# import subprocess
# import threading


# app = Flask(__name__)

# scanning_process = None  # Track if main.py is running

# def run_scanning_script():
#     global scanning_process
#     # Run main.py with python command; adjust 'python3' if needed
#     scanning_process = subprocess.Popen(['python', 'main.py'])

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/start-attendance')
# def start_attendance():
#     global scanning_process
#     if scanning_process is None or scanning_process.poll() is not None:
#         threading.Thread(target=run_scanning_script).start()
#     return redirect(url_for('attendance'))

# @app.route('/attendance')
# def attendance():
#     today = datetime.now().strftime('%Y-%m-%d')
#     try:
#         wb = load_workbook("Attendance.xlsx")
#         if today in wb.sheetnames:
#             ws = wb[today]
#             data = [list(row) for row in ws.iter_rows(values_only=True)]
#             headers = data[0]
#             rows = data[1:]
#             return render_template("attendance.html", headers=headers, rows=rows)
#         else:
#             return render_template("attendance.html", headers=[], rows=[], no_data=True)
#     except FileNotFoundError:
#         return render_template("attendance.html", headers=[], rows=[], no_data=True)

# if __name__ == '__main__':
#     app.run(debug=True)





















# from flask import Flask, render_template, redirect, url_for
# import subprocess

# # @app.route('/attendance')
# # def attendance():
# #     today = datetime.now().strftime('%Y-%m-%d')
# #     try:
# #         wb = load_workbook("Attendance.xlsx")
# #         if today in wb.sheetnames:
# #             ws = wb[today]
# #             data = [list(row) for row in ws.iter_rows(values_only=True)]
# #             headers = data[0]
# #             rows = data[1:]
# #             return render_template("attendance.html", headers=headers, rows=rows)
# #         else:
# #             return render_template("attendance.html", headers=[], rows=[], no_data=True)
# #     except FileNotFoundError:
# #         return render_template("attendance.html", headers=[], rows=[], no_data=True)


# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/attendance')
# def attendance():
#     # You can keep or remove this route if you don't want to show attendance data
#     return "Attendance page (optional)"

# @app.route('/start_attendance')
# def start_attendance():
#     subprocess.Popen(["python", "main.py"])  # Starts main.py in background
#     return redirect(url_for('index'))  # Redirects back to home page without message

# if __name__ == '__main__':
#     app.run(debug=True)










# from flask import Flask, render_template, redirect, url_for
# from openpyxl import load_workbook
# from datetime import datetime
# import subprocess

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/start_attendance')
# def start_attendance():
#     subprocess.Popen(["python", "main.py"])  # Launches the attendance system
#     return redirect(url_for('index'))

# @app.route('/attendance')
# def attendance():
#     today = datetime.now().strftime('%Y-%m-%d')
#     try:
#         wb = load_workbook("Attendance.xlsx")
#         if today in wb.sheetnames:
#             ws = wb[today]
#             data = [list(row) for row in ws.iter_rows(values_only=True)]
#             headers = data[0]
#             rows = data[1:]
#             return render_template("attendance.html", headers=headers, rows=rows)
#         else:
#             return render_template("attendance.html", headers=[], rows=[], no_data=True)
#     except FileNotFoundError:
#         return render_template("attendance.html", headers=[], rows=[], no_data=True)

# if __name__ == '__main__':
#     app.run(debug=True)








from flask import Flask, render_template, request, jsonify
import face_recognition
import numpy as np
import os
import base64
from datetime import datetime
from openpyxl import Workbook, load_workbook
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Load known face encodings
known_encodings = []
known_names = []

for filename in os.listdir('Training_images'):
    img = face_recognition.load_image_file(f'Training_images/{filename}')
    enc = face_recognition.face_encodings(img)
    if enc:
        known_encodings.append(enc[0])
        known_names.append(os.path.splitext(filename)[0])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'message': 'No image received'}), 400

    image_data = data['image'].split(',')[1]
    image_bytes = BytesIO(base64.b64decode(image_data))
    img = np.array(Image.open(image_bytes))

    face_encodings = face_recognition.face_encodings(img)
    if not face_encodings:
        return jsonify({'message': 'No face detected'})

    encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_encodings, encoding)
    name = "Unknown"

    if True in matches:
        idx = matches.index(True)
        name = known_names[idx]
        mark_attendance(name)
        return jsonify({'message': f"{name} recognized and attendance marked"})
    else:
        return jsonify({'message': "Face not recognized"})

def mark_attendance(name):
    file = "Attendance.xlsx"
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    if not os.path.exists(file):
        wb = Workbook()
        ws = wb.active
        ws.title = today
        ws.append(["Name", "Date", "Time"])
    else:
        wb = load_workbook(file)
        if today not in wb.sheetnames:
            ws = wb.create_sheet(title=today)
            ws.append(["Name", "Date", "Time"])
        else:
            ws = wb[today]

    for row in ws.iter_rows(min_row=2):
        if row[0].value == name:
            return
    ws.append([name, today, now])
    wb.save(file)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
