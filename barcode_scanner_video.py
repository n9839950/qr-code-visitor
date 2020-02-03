# USAGE
# python barcode_scanner_video.py

import firebase_admin 
from firebase_admin import credentials
from firebase_admin import firestore

from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time 
import cv2


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
print('Scan your qr code')
vs = VideoStream(src=0,resolution=(1920,1080)).start()
#vs = VideoStream(usePiCamera=True,resolution=(1920,1080)).start()
#camera.resolution =(1920,1080)
#camera.start_preview()
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
        
        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
         #printing barcode data 
        if barcodeData > str(0):
            #print(barcodeData)
            print(barcodeData + " barcode successfully scanned, Thank you!")
            
            
            
           
           
        # if the barcode text is currently not in our CSV file, write
        # the timestamp + barcode to disk and update the set
        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(),
                barcodeData))
            csv.flush()
            found.add(barcodeData)
        
        data = {u'barcodeData' :barcodeData,
                #u'init_time': datetime.datetime.now()
                    
            }
        print('Writing to database')
        qrcode_ref=db.collection(u'qrcode').document().set(data)
        qr_comp = db.collection(u'temp_data').document().set(data)
        
        print('Database updated')
            


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
