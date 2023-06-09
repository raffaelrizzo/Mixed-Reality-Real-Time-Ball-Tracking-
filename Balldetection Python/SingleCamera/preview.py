import cv2
import numpy as np
import tensorflow as tf
import depthai as dai
import argparse



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cameraid', type=int, default=0, help='index of the camera')
    parser.add_argument('--depthai', action='store_true', help='use DepthAI plugin')
    parser.add_argument('--modelpath', type=str, default='./Data/out3/saved_model', help='path of the object detection model')
    parser.add_argument('--confidence', type=float, default=0.5, help='detection confidence')
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
    
    return frame


def main(args):
    loadModel(args.modelpath)

    if args.depthai:
        pipeline = setup_pipeline()

        with dai.Device(pipeline) as device:
            print('Connected cameras:', device.getConnectedCameraFeatures())
            print('Usb speed:', device.getUsbSpeed().name)
            if device.getBootloaderVersion() is not None:
                print('Bootloader version:', device.getBootloaderVersion())
            print('Device name:', device.getDeviceName())

            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False) # output queue will be used to get the rgb frames from the output

            while True:
                inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
                frame = inRgb.getCvFrame() # BGR

                frame = detect_ball(frame, args.confidence)
                cv2.imshow("rgb", frame)

                if cv2.waitKey(1) == ord('q'):
                    break
    
    else:
        cap = cv2.VideoCapture(args.cameraid)

        while True:
            ret, frame = cap.read()
            
            frame = detect_ball(frame, args.confidence)
            cv2.imshow('rgb', frame)

            if cv2.waitKey(1) == ord('q'):
                break
    

if __name__ == '__main__':
    main(get_args())