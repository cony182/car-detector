import cv2 as cv
import numpy as np
from time import sleep

largura_min = 80  # Lebar persegi panjang minimum
altura_min = 80  # Tinggi persegi panjang minimum

offset = 5  # Error yang diizinkan di antara piksel

post_line_vertical = 400  # Posisi garis vertikal
post_line_horizontal = 1200  # Posisi garis horizontal


delay = 60  # Video FPS

detec = []
carros = 0


def get_center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy


capt = cv.VideoCapture('video2.mp4')
substractor = cv.bgsegm.createBackgroundSubtractorMOG()

while True:
    ret, frame1 = capt.read()
    tempo = float(1/delay)
    sleep(tempo)
    grey = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(grey, (3, 3), 5)
    img_sub = substractor.apply(blur)
    dilat = cv.dilate(img_sub, np.ones((5, 5)))
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    dilatada = cv.morphologyEx(dilat, cv. MORPH_CLOSE, kernel)
    dilatada = cv.morphologyEx(dilatada, cv. MORPH_CLOSE, kernel)
    contorno, h = cv.findContours(
        dilatada, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    cv.line(frame1, (25, post_line_vertical),
            (post_line_horizontal, post_line_vertical), (255, 127, 0), 3)
    for (i, c) in enumerate(contorno):
        (x, y, w, h) = cv.boundingRect(c)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue

        cv.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        centro = get_center(x, y, w, h)
        detec.append(centro)
        cv.circle(frame1, centro, 4, (0, 0, 255), -1)

        for (x, y) in detec:
            if y < (post_line_vertical+offset) and y > (post_line_vertical-offset):
                carros += 1
                cv.line(frame1, (25, post_line_vertical),
                        (post_line_horizontal, post_line_vertical), (0, 127, 255), 3)
                detec.remove((x, y))
                print("Kendaraan terdekteksi : "+str(carros))

    cv.putText(frame1, "Kendaraan : "+str(carros), (450, 70),
               cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv.imshow("Video Original", frame1)
    # cv.imshow("Detectar", dilatada)

    if cv.waitKey(1) == 27:
        break

cv.destroyAllWindows()
capt.release()
