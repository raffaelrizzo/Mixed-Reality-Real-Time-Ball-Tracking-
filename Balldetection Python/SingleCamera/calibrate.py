import cv2
import numpy as np
import tensorflow as tf
import depthai as dai
import os
import csv
import json
import time
import matplotlib.pyplot as plt
import argparse



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cameraid', type=int, default=0, help='index of the camera')
    parser.add_argument('--depthai', action='store_true', help='use DepthAI plugin')
    parser.add_argument('--modelpath', type=str, default='./Data/out3/saved_model', help='path of the object detection model')
    parser.add_argument('--confidence', type=float, default=0.5, help='detection confidence')
    parser.add_argument('--capture', action='store_true', help='strat from capturing images')
    parser.add_argument('--datadir', type=str, default='./calibdata/00/', help='path of the calibration data')
    parser.add_argument('--unitwidth', type=float, default=1.2, help='width of view away 1m from camera')
    parser.add_argument('--unitheight', type=float, default=0.8, help='height of view away 1m from camera')
    return parser.parse_args()


def setup_pipeline():
    pipeline = dai.Pipeline()

    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")

    camRgb.setPreviewSize(1920, 1080)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    camRgb.setFps(60)

    camRgb.preview.link(xoutRgb.input)
    
    return pipeline


# global Variables
modelFlag = 0
detection_model = None

def loadModel(path):
    global modelFlag, detection_model
    if not modelFlag:
        detection_model = tf.saved_model.load(path)
        print("Model Loaded")
        modelFlag = 1


def detect_ball(frame, confidence):
    rgb_frame = frame[:, :, ::-1] # convert the image from BGR to RGB
    rgb_frame_expanded = np.expand_dims(rgb_frame, axis=0) # add a new axis to match the input size requirement of the model

    output_dict = detection_model(rgb_frame_expanded)

    detection_scores = output_dict['detection_scores'][0].numpy()
    detection_boxes = output_dict['detection_boxes'][0].numpy()

    most_conf = np.argmax(detection_scores)
    score = detection_scores[most_conf]
    if score > confidence:
        box = detection_boxes[most_conf] * np.array([frame.shape[0], frame.shape[1], frame.shape[0], frame.shape[1]])

        center_x = (box[1] + box[3]) / 2
        center_y = (box[0] + box[2]) / 2
        radius = max((box[3] - box[1]) / 2, (box[2] - box[0]) / 2)

        cv2.circle(frame, (int(center_x), int(center_y)), int(radius), (0, 255, 0), 2)            

        return frame, radius
    
    else:
        return frame, -1


def capture(args, distances=[0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0]):
    os.makedirs(args.datadir, exist_ok=True)
    os.makedirs(os.path.join(args.datadir, 'images/'), exist_ok=True)

    def save(frame, distance):
        path = os.path.join(args.datadir, f'images/{int(distance*10):02d}.png')
        cv2.imwrite(path, frame)
        with open(os.path.join(args.datadir, 'data.csv'), 'a') as f:
            f.write(f'{path} {distance:.3f}\n')
        print(f'captured {distance:.3f} m')

    if args.depthai:
        pipeline = setup_pipeline()

        with dai.Device(pipeline) as device:
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False) # output queue will be used to get the rgb frames from the output

            i = 0
            start_time = time.time()
            while i < len(distances):
                inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
                frame = inRgb.getCvFrame() # BGR

                elapsed_time = int(time.time() - start_time)
                if elapsed_time > 5:
                    save(frame, distances[i])
                    start_time = time.time()
                    i += 1

                frame, _ = detect_ball(frame, args.confidence)
                cv2.imshow("rgb", frame)

                if cv2.waitKey(1) == ord('q'):
                    break
    
    else:
        cap = cv2.VideoCapture(args.cameraid)

        i = 0
        start_time = time.time()
        while i < len(distances):
            ret, frame = cap.read()

            elapsed_time = int(time.time() - start_time)
            if elapsed_time > 5:
                save(frame, distances[i])
                start_time = time.time()
                i += 1
            
            frame, _ = detect_ball(frame, args.confidence)
            cv2.imshow('rgb', frame)

            if cv2.waitKey(1) == ord('q'):
                break
    
    cv2.destroyAllWindows()


def least_squares(X, Y):
    '''
    Assumption:
        distance = a/size + b
    
    denote y = a/_x + b, x = 1/_x
    derive optimal a and b
    '''

    # averages
    X_ = np.mean([1/x for x in X])
    Y_ = np.mean([y for y in Y])
    X2_ = np.mean([(1/x)*(1/x) for x in X])
    XY_ = np.mean([y/x for x,y in zip(X,Y)])

    a = (len(X)*XY_ - X_*Y_) / (len(X)*X2_ - X_*X_)
    b = (X2_*Y_ - X_*XY_) / (len(X)*X2_ - X_*X_)

    return a, b


def main(args):
    loadModel(args.modelpath)
    
    if args.capture:
        capture(args)

    images = []
    distances = []
    with open(os.path.join(args.datadir, 'data.csv'), 'r') as f:
        _data = csv.reader(f, delimiter=' ')
        for row in _data:
            images.append(cv2.imread(row[0]))
            distances.append(float(row[1]))
    
    X = []
    Y = []
    for i, image in enumerate(images):
        print(i, end=' ')
        _, radius = detect_ball(image, args.confidence)
        resolution = image.shape[:2]
        if radius > 0:
            size = (radius*2) / resolution[0] # != diameter
            print('deteted')
            X.append(size)
            Y.append(distances[i])
        else:
            print('not detected')
    
    fig = plt.figure()
    plt.plot(X, Y)
    for x,y in zip(X,Y):
        print(f'size:{x:.3f}, distance:{y:.3f}')

    a, b = least_squares(X, Y)
    print(f'a = {a:.5f}, b = {b:.5f}')

    sampleX = np.arange(0.05,1,0.01)
    sampleY = np.array([a/x + b for x in sampleX])
    plt.plot(sampleX, sampleY)
    plt.grid()
    plt.show()
    fig.savefig(os.path.join(args.datadir, 'graph.png'))

    with open(os.path.join(args.datadir, 'parameters.json'), 'w') as f:
        _data = {'a': a, 'b': b,
                 'width': args.unitwidth, 'height': args.unitheight,
                 'resolution_x': resolution[1], 'resolution_y': resolution[0]}
        json.dump(_data, f)


if __name__ == '__main__':
    main(get_args())