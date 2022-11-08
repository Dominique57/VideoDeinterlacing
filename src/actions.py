import cv2 as cv

def show_image(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imshow('window', img)
    while cv.waitKey(0) not in [27, 235]:
        cv.imshow('window', img)

def save_image(img, filename):
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite(filename, img)
