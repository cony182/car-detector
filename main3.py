import cv2
import numpy as np
from time import sleep
import mysql.connector
import datetime
import time

# DEKLARASI UTAMA / MAIN DECLARATION
video_name = "video4"
video_format = ".mp4"

date = "Januari 1"         # Masukkan tanggal yang sama seperti pada web
updated_by = "Cony"     # nama operator program
codename = "RMJ-20"           # Masukkan kode wilayah jalan

table_name = "kendaraans"
field_jumlah = "jumlah"

ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# KONFIGURASI DATABASE
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="pkl"
)

dbcursor = mydb.cursor()

min_width = 50  # Jangkauan dekteksi
min_height = 50  # Jangkauan deteksi

offset = 6  # Toleransi error

pos_line = 550  # Posisi garis vertikal
len_line = 1200  # Panjang garis

vid_fps = 60  # Tentukan FPS pada video

detected = []
vehicle = 0


def get_center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy


video_src = cv2.VideoCapture(video_name+video_format)
substractor = cv2.bgsegm.createBackgroundSubtractorMOG()

while True:
    read, frame1 = video_src.read()
    tempo = float(1/vid_fps)
    sleep(tempo)
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (3, 3), 5)
    img_sub = substractor.apply(blur)
    sensitivity = cv2.dilate(img_sub, np.ones((0, 0)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    spread = cv2.morphologyEx(sensitivity, cv2. MORPH_CLOSE, kernel)
    spread = cv2.morphologyEx(spread, cv2. MORPH_CLOSE, kernel)
    contour, h = cv2.findContours(
        spread, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.line(frame1, (25, pos_line), (len_line, pos_line), (255, 127, 0), 2)
    for (i, c) in enumerate(contour):
        (x, y, w, h) = cv2.boundingRect(c)
        validate = (w >= min_width) and (h >= min_height)
        if not validate:
            continue

        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        center = get_center(x, y, w, h)
        detected.append(center)
        cv2.circle(frame1, center, 5, (0, 0, 255), -1)

        for (x, y) in detected:
            if y < (pos_line+offset) and y > (pos_line-offset):
                vehicle += 1
                cv2.line(frame1, (25, pos_line),
                         (1200, pos_line), (0, 127, 255), 7)
                detected.remove((x, y))
                print("Kendaraan terdeteksi : "+str(vehicle))
                sql = (
                    f"UPDATE {table_name} SET {field_jumlah}={vehicle}, updated_at='{timestamp}', updated_by='{updated_by}'\
                    WHERE date='{date}' AND kode='{codename}'")
                dbcursor.execute(sql)
                mydb.commit()
                print(dbcursor.rowcount, "record(s) %s affected" % sql)

    cv2.putText(frame1, "Kendaraan : "+str(vehicle), (50, 500),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 4)
    cv2.imshow("Video Original", frame1)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
# video_src.release()
