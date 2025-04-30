#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import gi
import numpy as np

gi.require_version('Gst', '1.0')
from gi.repository import Gst



def main(args=None):
    rclpy.init(args=args)

    protocol = 'udpsrc '
    port = '5600 '
    video_codec = '! application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264'
    video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
    video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=2 drop=true'

    cap = cv2.VideoCapture('udpsrc port=5600 ! application/x-rtp,media=video,encoding-name=H264 ! queue ! rtpjitterbuffer latency=500 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=BGR ! queue ! appsink drop=1',
        # protocol + port + video_codec + video_decode + video_sink_conf, 
        cv2.CAP_GSTREAMER)
    while True:
        ret,frame = cap.read()

        if not ret:
            print('frame',frame)
            print('empty frame')
            continue 


        cv2.imshow('receive', frame)
        if cv2.waitKey(1)&0xFF == ord('q'):
            break
    cap.release()
    rclpy.shutdown()


if __name__ == '__main__':
    main()