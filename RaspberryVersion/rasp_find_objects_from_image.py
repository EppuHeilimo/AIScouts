import os
import time
import pickle
from PIL import Image
from PIL import ImageDraw, ImageFont
import numpy as np
class ObjectRecognition:
    crop_size = 128
    image_width = 0
    image_height = 0
    model = None
    curr_position = [0, 0]
    visualize = False
    interesting = []
    # fromat: {center[x,y], cropsize[x,y]}
    saved_poi = []
    auto_find = False
    show_poi = False
    labels_counts = {}
    curr_image = None
    curr_image_gray = None
    #MouseClickCallback variables
    refPtStart = []
    refPtEnd = []
    cropping = False
    setupImage = None
    setupImage2 = None
    font = None

    elapsed_time = 0
    start_time = 0

    # If interesting labels is None, the script will ask the user to draw his points of interest
    def __init__(self, model, interesting_labels, auto_find=False, visualize=False):
        self.model = model
        self.visualize = visualize
        self.auto_find = auto_find
        self.interesting = interesting_labels
        script_dir = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
        self.font = ImageFont.truetype(script_dir + '/DejaVuSans-Bold.ttf', 16)
        for label in model.label_folders:
            self.labels_counts.update({label.split('/')[-2]: []})


    def predict_poi(self, crop):
        img = Image.fromarray(crop, 'L')
        img = img.resize((self.img_size, self.img_size), Image.ANTIALIAS)
        label, confidence = self.model.predict(img)
        if label in self.interesting:
            return True
        return False


    def save_poi(self, path):
        f = open(path + '.poi', 'wb')
        pickle.dump(self.saved_poi, f, 2)
        f.close()

    def load_poi(self, path):
        f = open(path + '.poi', 'rb')
        self.saved_poi = pickle.load(f)

    def save_images_from_poi(self, image, path, every_x_s):
        if not os.path.isdir(path):
            os.mkdir(path)
        # if start time hasn't been initialized
        if self.start_time == 0:
            self.start_time = time.time()
        self.elapsed_time = time.time() - self.start_time
        image_array = np.asarray(image)
        if self.elapsed_time >= every_x_s:
            for key, value in self.saved_poi:
                crop = image_array[int(key[1] - value[1] / 2):int(key[1] + value[1] / 2),
                       int(key[0] - value[0] / 2):int(key[0] + value[0] / 2)]
                img = Image.fromarray(crop, 'L')
                label, confidence = self.model.predict(img)
                if not os.path.isdir(path + label):
                    os.mkdir(path + label)
                dirlen = len(os.listdir(path + label))
                img.save(path + label + '/' + str(dirlen + 1) + '.bmp')
            self.start_time = time.time()
            self.elapsed_time = 0

    def find_objects(self, img):
        if isinstance(img, str):
            image = Image.open(img)
        else:
            image = img
        gray_image = image.convert('L')
        for key in self.labels_counts:
            self.labels_counts[key].clear()
        i = 0
        ret = image
        image_array = np.asarray(gray_image)
        for key, value in self.saved_poi:
            crop = image_array[int(key[1] - value[1] / 2):int(key[1] + value[1] / 2),
                   int(key[0] - value[0] / 2):int(key[0] + value[0] / 2)]
            img = Image.fromarray(crop, 'L')
            label, confidence = self.model.predict(img)
            if label in self.interesting:
                ret = ImageDraw.Draw(image)
                if label == self.interesting[0]:
                    color = 'black'
                elif label == self.interesting[1]:
                    color = 'white'
                elif label == self.interesting[2]:
                    color = 'red'
                else:
                    color = 'blue'
                ret.rectangle(((int(key[0] - value[0]/2),
                                int(key[1] - value[1]/2)),
                               (int(key[0] + value[0]/2),
                                int(key[1] + value[1]/2))),
                              outline=color)
                w, h = ret.textsize(str(i), font=self.font)
                ret.ellipse(((int(key[0] - 10),
                              int(key[1] - 10)),
                             (int(key[0] + 10),
                              int(key[1] + 10))),
                            fill=(255,255,255))
                ret.text((key[0] - w/2, key[1] - h/2), str(i), (0,0,0), font=self.font)
                self.labels_counts[label].append(i)
            i += 1
        return image, self.labels_counts
