import numpy as np
import cv2
import sys
import subprocess
from skimage.measure import structural_similarity as ssim


def sim(pic1, pic2):
    pic_norm1 = pic1 / np.sqrt(np.sum(pic1 ** 2))
    pic_norm2 = pic2 / np.sqrt(np.sum(pic2 ** 2))

    return np.sum(pic_norm1 * pic_norm2)


def closest(pic, vid):
    fps = 15
    # int(vid.get(cv2.cv.CV_CAP_PROP_FPS))
    best_sim = -1
    offset = 0
    #pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    for i in xrange(0, 8*fps):
        ret, img = vid.read()
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        similarity = ssim(img, pic)
        if similarity > best_sim:
            best_sim = similarity
            offset = vid.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    return offset

def extract_images(file1, offset1, file2, offset2):
    cmd1 = ["ffmpeg", "-ss", str(offset1/1000),"-t", str(30), "-i", str(file1),"-r",
            "15.0","img-%4d.jpg"]
    cmd2 = ["ffmpeg", "-ss", str(offset2/1000),"-t", str(30), "-i", str(file2),"-r",
            "15.0","img-%4d_.jpg"]
    subprocess.call(cmd1)
    subprocess.call(cmd2)



def main():
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    vid1 = cv2.VideoCapture(file1)
    vid2 = cv2.VideoCapture(file2)

    fps = 15    # int(vid.get(cv2.cv.CV_CAP_PROP_FPS))

    for i in xrange(0, 2*fps):
        ret, img = vid1.read()
    off1 = vid1.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    off2 = closest(img, vid2)

    extract_images(file1,off1, file2, off2)
    return True


if __name__ == "__main__": main()
