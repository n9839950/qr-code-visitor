# USAGE
# python barcode_scanner_video.py

import firebase_admin 
from firebase_admin import credentials
from firebase_admin import firestore
import RPi.GPIO as GPIO

from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time 
import cv2

# GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.OUT)



#firestore credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
  'projectId':"qrcode-visitor",
})  
db = firestore.client()


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
    help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())



# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0,resolution=(1920,1080)).start()
time.sleep(2.0)

# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "w")
found = set()

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)
     
    # loop over the detected barcodes
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw
        # the bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # the barcode data is a bytes object so if we want to draw it
        # on our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        print('Scan your qr code')
        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
         #printing barcode data 
        if barcodeData > str(0):
            #print(barcodeData)
            print(" This is scanned barcode "+ barcodeData)
            
            
           
           
        # if the barcode text is currently not in our CSV file, write
        # the timestamp + barcode to disk and update the set
        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(),
                barcodeData))
            csv.flush()
            found.add(barcodeData)
        
        
        
        # Comparing the data from database
        docs = db.collection(u'qrcode').stream()

        for doc in docs:
            print(u"Barcode in database: {}".format(doc.to_dict()[u'barcodeData']))
     
     
            if barcodeData == format(doc.to_dict()[u'barcodeData']):
                GPIO.output(26,GPIO.HIGH)
            #print( " the data after verification "+format(doc.to_dict()[u'barcodeData']))
                time.sleep(1)
                GPIO.output(26,GPIO.LOW)
                print("Match Found")
                break
            elif():
                GPIO.output(26,GPIO.LOW)
                print("No data found")
                    

    # show the output frame
    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    
    
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
csv.close()
#camera.stop_preview()
cv2.destroyAllWindows()
vs.stop()

