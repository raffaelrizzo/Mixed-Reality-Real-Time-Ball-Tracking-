import cv2
import numpy as np
import tensorflow as tf
import depthai as dai
import socket
import json
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cameraid', type=int, default=0, help='index of the camera')
    parser.add_argument('--depthai', action='store_true', help='use DepthAI plugin')
    parser.add_argument('--modelpath', type=str, default='../Data/out3/saved_model', help='path of the object detection model')
    parser.add_argument('--confidence', type=float, default=0.5, help='detection confidence')
    parser.add_argument('--preview', action='store_true', help='preview video')
    parser.add_argument('--calibdata', type=str, default='./calibdata/00/parameters.json', help='path of the calibration data')
    parser.add_argument('--serverip', type=str, default='192.168.137.162', help='local ip address of the UDP server')
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

        return frame, center_x, center_y, radius
    
    else:
        return frame, 0, 0, -1


def estimate_position(_x, _y, _rad, params):

    def perspective(_position, params):
        z = _position[2]
        x = _position[0] * z * params['width']
        y = _position[1] * z * params['height']
        return x, y, z

    x = -0.5 + _x / params['resolution_x']
    y = 0.5 - _y / params['resolution_y']
    size = (_rad*2) / params['resolution_y'] # != diameter

    z = params['a'] / size + params['b']
    x, y, z = perspective((x,y,z), params)
    # print(f'{x:.3f} {y:.3f} {z:.3f}')

    return x, y, z


def send_data(position, ip='127.0.0.1', port=12345):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = f'{position[0]:.3f} {position[1]:.3f} {position[2]:.3f}'
    sock.sendto(message.encode(), (ip, port))
    print(message)
    sock.close()


def main(args):
    loadModel(args.modelpath)

    with open(args.calibdata, 'r') as f:
        params = json.load(f)

    if args.depthai:
        pipeline = setup_pipeline()

        with dai.Device(pipeline) as device:
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False) # output queue will be used to get the rgb frames from the output

            while True:
                inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
                frame = inRgb.getCvFrame() # BGR

                frame, center_x, center_y, radius = detect_ball(frame, args.confidence)
                if args.preview:
                    cv2.imshow("rgb", frame)

                x, y, z = estimate_position(center_x, center_y, radius, params)
                if z > 0.5: # ignore miss-detections where z is too low
                    send_data((x,y,z), ip=args.serverip)
                
                if cv2.waitKey(1) == ord('q'):
                    break
    
    else:
        cap = cv2.VideoCapture(args.cameraid)

        while True:
            ret, frame = cap.read()
            
            frame, center_x, center_y, radius = detect_ball(frame, args.confidence)
            if args.preview:
                cv2.imshow("rgb", frame)

            x, y, z = estimate_position(center_x, center_y, radius, params)
            if z > 0.5: # ignore miss-detections where z is too low
                send_data((x,y,z), ip=args.serverip)

            if cv2.waitKey(1) == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(get_args())