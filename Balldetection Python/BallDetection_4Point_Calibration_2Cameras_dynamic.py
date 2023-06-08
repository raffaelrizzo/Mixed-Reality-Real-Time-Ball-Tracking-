import cv2
import tensorflow as tf
import numpy as np
import argparse
import socket

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true', help='preview video')
    parser.add_argument('--confidence', type=float, default=0.5, help='detection confidence')
    return parser.parse_args()

# Global Variables
modelFlag = 0
detection_model = None

def loadModel():
    global modelFlag, detection_model
    if not modelFlag:
        detection_model = tf.saved_model.load('Data/out3/saved_model')
        print("Model Loaded")
        modelFlag = 1
                
# def send_data(position, ip='127.0.0.1', port=12345):
def send_data(position, ip='192.168.137.1', port=12345):
# def send_data(position, ip='192.168.137.162', port=12345):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = f'{position[0]:.3f} {position[1]-1.75:.3f} {2.2*position[2]-1.1:.3f}'
    sock.sendto(message.encode(), (ip, port))
    sock.close()

def select_four_points(video):
    points = []

    def mouse_handler(event, x, y, flags, data):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(data, (x, y), 3, (0, 0, 255), 5, 16)
            cv2.imshow("Image", data)
            points.append([x, y])

    while cv2.waitKey(1) < 0:
        ret, image = video.read()
        if not ret:
            print("Failed to grab frame.")
            exit()
        cv2.imshow("Image", image)
        cv2.setMouseCallback("Image", mouse_handler, image)
        if len(points) == 4:
            cv2.destroyAllWindows()
            break

    points = np.array(points, dtype=np.float32)
    return points

def main(args):
    loadModel()

    # Open the first camera
    cap = cv2.VideoCapture(0)
    pts_src = select_four_points(cap)
    pts_dst = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 1.4], [0.0, 1.4]])
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Open the second camera
    cap_side = cv2.VideoCapture(1)
    pts_src_side = select_four_points(cap_side)
    h_side, status = cv2.findHomography(pts_src_side, pts_dst)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        ret_side, frame_side = cap_side.read()
        if not ret or not ret_side:
            break

        # Run the frame through the model
        frame_input = np.expand_dims(frame, axis=0)   # Add an extra dimension for batch size at the start
        frame_side_input = np.expand_dims(frame_side, axis=0)   # Add an extra dimension for batch size at the start
        output_dict = detection_model(frame_input)
        output_dict_side = detection_model(frame_side_input)


        # Get the number of objects detected
        num_detections = int(output_dict.pop('num_detections'))
        num_detections_side = int(output_dict_side.pop('num_detections'))

        # Detection scores are the detection confidence
        detection_scores = output_dict['detection_scores'][0].numpy()
        detection_scores_side = output_dict_side['detection_scores'][0].numpy()

        # Detection classes are the id of the detected object
        detection_classes = output_dict['detection_classes'][0].numpy().astype(np.uint32)
        detection_classes_side = output_dict_side['detection_classes'][0].numpy().astype(np.uint32)

        # Detection boxes are the coordinates of the detected object
        detection_boxes = output_dict['detection_boxes'][0].numpy()
        detection_boxes_side = output_dict_side['detection_boxes'][0].numpy()

        idxmax = np.argmax(detection_scores)
        score = detection_scores[idxmax]
        idxmax_side = np.argmax(detection_scores_side)
        score_side = detection_scores_side[idxmax_side]

        if score > args.confidence and score_side > args.confidence:
            box = detection_boxes[idxmax] * np.array([frame.shape[0], frame.shape[1], frame.shape[0], frame.shape[1]])
            box_side = detection_boxes_side[idxmax_side] * np.array([frame_side.shape[0], frame_side.shape[1], frame_side.shape[0], frame_side.shape[1]])

            # Get the center of the box
            center_x = (box[1] + box[3]) / 2
            center_y = (box[0] + box[2]) / 2
            center_x_side = (box_side[1] + box_side[3]) / 2
            center_y_side = (box_side[0] + box_side[2]) / 2

            # Get the radius of the ball in the image from the box dimensions
            radius = max((box[3] - box[1]) / 2, (box[2] - box[0]) / 2)
            radius_side = max((box_side[3] - box_side[1]) / 2, (box_side[2] - box_side[0]) / 2)

            # Draw a circle around the detected object
            cv2.circle(frame, (int(center_x), int(center_y)), int(radius), (0, 255, 0), 2)
            cv2.circle(frame_side, (int(center_x_side), int(center_y_side)), int(radius_side), (0, 255, 0), 2)

            # Estimate z based on size
            size = (radius * 2) / frame.shape[0]
            z = 0.5 / (3 * size - 0.1) + 0.1

            # Compute real-world position
            point = np.array([[[center_x, center_y]]], dtype=np.float32)
            point_side = np.array([[[center_x_side, center_y_side]]], dtype=np.float32)
            pointsOut = cv2.perspectiveTransform(point, h)
            pointsOut_side = cv2.perspectiveTransform(point_side, h_side)
            x, y = pointsOut[0][0]
            #z = 2 - pointsOut_side[0][0][0]  # if your x ranges from 0 to 2
            z = pointsOut_side[0][0][0]

            send_data((x, y, z))

        # Display the resulting frame
        if args.preview:
            cv2.imshow('frame', frame)
            cv2.imshow('frame_side', frame_side)

        # Press 'q' to quit the application
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    args = get_args()
    main(args)

