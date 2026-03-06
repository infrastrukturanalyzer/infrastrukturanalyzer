from flask import Flask, render_template, request, send_from_directory
import os
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    img = cv2.imread(filepath)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)

    edges = cv2.Canny(blur,70,150)

    contours,_ = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    crack_pixels = 0
    total_length = 0
    total_width = 0
    pothole_area = 0
    count = 0

    for c in contours:

        area = cv2.contourArea(c)

        if area > 500:

            crack_pixels += area

            x,y,w,h = cv2.boundingRect(c)

            total_length += max(w,h)
            total_width += min(w,h)

            count += 1

        if area > 3000:

            pothole_area += area


    if count > 0:
        avg_width = total_width / count
    else:
        avg_width = 0


    total_pixels = img.shape[0]*img.shape[1]

    percent = (crack_pixels/total_pixels)*100


    # DETEKSI RETAK BUAYA
    if count > 25 and percent > 10:
        jenis_kerusakan = "Retak Buaya"
    elif percent > 5:
        jenis_kerusakan = "Retak Memanjang"
    else:
        jenis_kerusakan = "Retak Ringan"


    # DETEKSI LUBANG
    if pothole_area > 5000:
        pothole = "Terdeteksi Lubang Jalan"
    else:
        pothole = "Tidak Ada Lubang Besar"


    now = datetime.now()

    tanggal = now.strftime("%d-%m-%Y")
    jam = now.strftime("%H:%M:%S")


    return render_template(
        "result.html",
        filename=file.filename,
        percent=round(percent,2),
        length=round(total_length,2),
        width=round(avg_width,2),
        jenis=jenis_kerusakan,
        pothole=pothole,
        tanggal=tanggal,
        jam=jam
    )


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)