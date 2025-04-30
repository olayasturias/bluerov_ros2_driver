/*
* Receiver.cpp: Receiver for OpenCV_GStreamer example
*
* Copyright (C) 2019 Simon D. Levy
*
* MIT License
%https://stackoverflow.com/questions/70597020/lower-latency-from-webcam-cv2-videocapture
*/

// #include "pch.h"

#include <opencv2/opencv.hpp>
using namespace cv;

#include <iostream>
using namespace std;

int main()
{
    // The sink caps for the 'rtpjpegdepay' need to match the src caps of the 'rtpjpegpay' of the sender pipeline
    // Added 'videoconvert' at the end to convert the images into proper format for appsink, without
    // 'videoconvert' the receiver will not read the frames, even though 'videoconvert' is not present
    // in the original working pipeline
	// VideoCapture cap("udpsrc port=5600 ! application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! decodebin ! videorate ! video/x-raw,framerate=5/1 ! videoconvert ! video/x-raw,format=(string)BGR  ! appsink emit-signals=true sync=false max-buffers=2 drop=true", 
    //         CAP_GSTREAMER);
    // VideoCapture cap("udpsrc port=5600 ! application/x-rtp,media=video,payload=26,clock-rate=90000,encoding-name=JPEG,framerate=30/1 ! rtpjpegdepay ! jpegdec ! videoconvert ! appsink", 
    //         CAP_GSTREAMER);

    VideoCapture cap;
    cap.open("udpsrc port=5600 ! application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! decodebin ! videorate ! video/x-raw,framerate=5/1 ! videoconvert ! video/x-raw,format=(string)BGR  ! appsink emit-signals=true sync=false max-buffers=2 drop=true", 
              CAP_GSTREAMER);

    
	if (!cap.isOpened()) {
        cerr <<"VideoCapture not opened"<<endl;
        exit(-1);
    }
    
    while (true) {

        Mat frame;

        cap.read(frame);

        imshow("receiver", frame);

        if (waitKey(1) == 27) {
            break;
        }
    }

    return 0;
}