import os,sys,argparse
import cv2
import numpy as np
from time import time

class fb():
    def __init__(self,dev_fb='/dev/fb0',shrink=2):
        self.fb = open(dev_fb,"wb")
        virtual_size='/sys/class/graphics/fb0/virtual_size'
        assert os.path.exists(virtual_size)
        with open(virtual_size) as f:
            vw,vh = f.read().strip().split(',')
            self.vw,self.vh = int(vw),int(vh)
        if shrink == 3:
            self.seeks = int(self.vh/shrink) * self.vw * 4
            self.shift = int(self.vw/shrink)
        elif shrink == 2:
            self.seeks = int(self.vh/shrink/2) * self.vw * 4
            self.shift = int(self.vw/shrink/2)
        else:
            self.seeks = 0
            self.shift = 0
        self.shrink= shrink
        self.canvas = np.zeros((int(self.vh/self.shrink), int(self.vw),4), dtype=np.uint8)
        self.alpha = None

    def imshow(self,title,img):
        assert img is not None
        assert len(img.shape) == 3
        img      = cv2.resize(img, (int(self.vw/self.shrink), int(self.vh/self.shrink)))
        if self.alpha is None: self.alpha = np.zeros((img.shape[0],img.shape[1],1),dtype=np.uint8)
        bgra_win = np.concatenate([img,self.alpha],axis=2)
        if self.shrink == 1:
            bgra_str = (bgra_win.reshape(-1)).tostring()
        else:
            self.canvas[:,self.shift:int(self.shift+img.shape[1]),:] = bgra_win
            bgra_str = (self.canvas.reshape(-1)).tostring()
        self.fb.seek(self.seeks)
        self.fb.write(bgra_str)

    def blank(self):
        bgra = np.zeros((self.vh, self.vw, 4), dtype=np.uint8)
        bgra_str = (bgra.reshape(-1)).tostring()
        self.fb.seek(0)
        self.fb.write(bgra_str)

    def close(self):
        self.fb.close()

if __name__ == '__main__':
    args=argparse.ArgumentParser()
    args.add_argument('-s','--shrink',default=1,type=int)
    args.add_argument('-i','--image', default='debian2.jpg',type=str)
    args=args.parse_args()
    assert os.path.exists(args.image)

    fb = fb(shrink=args.shrink)
    start = time()
    cnt = 0
    while True:
        img = cv2.imread(args.image)
        fb.imshow('images',img)
        cnt+=1
        sys.stdout.write('\b'*20)
        sys.stdout.write('%.3fFPS'%(cnt/(time()-start)))
        sys.stdout.flush()
    fb.close()
