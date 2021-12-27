# Libraries
import requests
import imutils
import Utilities
import cv2
import numpy as np

# Get image

# Method 1: url for connecting mobile camera with the code. In mobile Go to 'IP Webcam'->'Start server'
url = "http://192.168.0.106:8080//shot.jpg"


# Method 2: For Getting the image from pc (already saved image)
path = "D:\\PyCharm 2021.2.2\\My programs\\venv\\omr2mod.png"
img = cv2.imread(path)

'''
# Method 3: For getting the image from webcam. Camera_number=0 for inbuilt webcam, Camera_number=1 for external webcam. 
webcamfeed = True
CameraNumber = 1
capture = cv2.VideoCapture(CameraNumber)
capture.set(10,150)
'''

# Setting the size of image
imgwidth = 700
imgheight = 700

# Requirements from user
ans = [2, 2, 3, 1, 1, 4, 3, 1, 4, 3]
questions = 10

# CHECK IF REQUIRED 1
marks = 0

# Continuous Loop
while True:
    marks = 0
    '''
    # For Method 3. If not then Method 2
    if webcamfeed:
        success, img = capture.read()
    else:
        img=cv2.imread(path)
    '''
    # cv2.imshow("capture Image", img)
    ########

    # For Method 1 (Getting image from url)
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    # CHECK IF REQUIRED 2
    img = imutils.resize(img, width=1000, height=1800)

    ########

    img = cv2.resize(img, (imgwidth, imgheight))
    imgcountours = img.copy()
    imgcountoursbiggest = img.copy()

    imggrey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # Normal img -> Grey img
    imgblur = cv2.GaussianBlur(imggrey,(5,5),10) # Grey img -> Blur img
    imgcanny = cv2.Canny(imgblur,10,50) # Blur img -> Canny img

    ##############

    '''
    cv2.imshow("Raj's photo", img)
    cv2.imshow("Raj's grey photo", imggrey)
    cv2.imshow("Raj's blur photo", imgblur)
    cv2.imshow("Raj's canny photo", imgcanny)
    '''
    ##############

    try:
        # Get Countours
        countours, hierarchy = cv2.findContours(imgcanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(imgcountours, countours, -1, (0, 255, 0), 1)

        cv2.imshow("Raj's countours photo", imgcountours)

        # Getting only rectangular countours
        # Function (rectangular) gives rectangular contour array starting from biggest in area
        rectcon = Utilities.rectangular(countours)
        biggest = rectcon[0]
        Thirdbiggest = rectcon[2]

        # Getting corner points of rectangular contours
        biggestwithcorner = Utilities.getcornerpoint(biggest)
        Thirdbiggestwithcorner = Utilities.getcornerpoint(Thirdbiggest)

        print(biggestwithcorner.shape)

        #print("biggest={}".format(len(biggest)))
        #print("biggestwithcorner={}".format(len(biggestwithcorner)))


        if (len(biggestwithcorner) !=0 and len(Thirdbiggestwithcorner)!=0):

            cv2.drawContours(imgcountoursbiggest, biggestwithcorner, -1, (0, 255, 0), 5)
            cv2.drawContours(imgcountoursbiggest, Thirdbiggestwithcorner, -1, (255, 0, 0), 5)

            # Reordering the corner points
            biggestwithcorner = Utilities.reorder(biggestwithcorner)
            Thirdbiggestwithcorner = Utilities.reorder(Thirdbiggestwithcorner)

            # Wrap images (Crop images)
            pt1 = np.float32(biggestwithcorner)
            pt2 = np.float32([[0, 0], [imgwidth, 0], [0, imgheight], [imgwidth, imgheight]])
            matrix = cv2.getPerspectiveTransform(pt1, pt2)
            imgwrap = cv2.warpPerspective(img, matrix, (imgwidth, imgheight))

            pt3 = np.float32(Thirdbiggestwithcorner)
            pt4 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])   # Values are as per our requirement for result box
            matrix = cv2.getPerspectiveTransform(pt3, pt4)
            imgwrapresult = cv2.warpPerspective(img, matrix, (325, 150))

            # Converting the wrapped img into black and white image. All dark part will be white and all white part will be dark.
            # Refer this for more explanation "https://learnopencv.com/opencv-threshold-python-cpp/"
            greyimgofwarp = cv2.cvtColor(imgwrap, cv2.COLOR_BGR2GRAY)
            imgthresh = cv2.threshold(greyimgofwarp, 170, 255, cv2.THRESH_BINARY_INV)[1]

            # Converting wrapped image into pieces
            allboxes = Utilities.splitboxes(imgthresh, questions)
            print("Total no. of boxes={}".format(len(allboxes)))
            print(cv2.countNonZero(allboxes[1]), cv2.countNonZero(allboxes[49]))  #1476  1717


            emptymatrix = np.zeros((questions, 5))  #que=10, choices=4
            rcount = 0
            ccount = 0


        # Logic for matrix
            '''
            [0. 0. 1. 1. 0.]
            [0. 0. 1. 0. 0.]
            [0. 0. 0. 1. 0.]
            [0. 0. 0. 0. 0.]
            [0. 1. 0. 0. 0.]
            [0. 0. 0. 0. 1.]
            [0. 0. 0. 1. 0.]
            [0. 0. 1. 0. 0.]
            [0. 0. 0. 0. 1.]
            [0. 1. 0. 0. 0.]
            '''
            for box in allboxes:
                pixel = cv2.countNonZero(box)
                if(pixel > 3000):
                    emptymatrix[rcount][ccount] = 1
                else:
                    emptymatrix[rcount][ccount] = 0
                ccount = ccount+1
                if(ccount == 5):
                    ccount = 0
                    rcount = rcount+1
            print(emptymatrix)


        # Logic for marked answers
        # [777, 2, 3, 0, 1, 4, 3, 2, 4, 1]
        markedans = []
        arr = []
        for rr in range(questions):
            arr = emptymatrix[rr]
            ind = 0
            cc = 0
            checkdouble = 0
            while(cc < 5):
                if(arr[cc] == 1):
                    ind = cc
                    checkdouble += 1
                cc = cc+1
            if(checkdouble == 1):
                markedans.append(ind)
            if(checkdouble > 1 and checkdouble <= 4):
                markedans.append(777)
            if(checkdouble == 0):
                markedans.append(0)
        print(markedans)


        #Mark Calculation
        for t in range (len(ans)):
            if(ans[t] == markedans[t]):
                marks += 4
            if((markedans[t] == 777 or ans[t] != markedans[t]) and markedans[t] != 0):
                marks -= 1

        print(ans)
        print("Total Marks = {}".format(marks))

        # Display answer in result Box
        imgwrapcopy = imgwrap.copy()
        coloreddots = Utilities.showanswers(imgwrapcopy, ans, markedans, questions)

        blankimg = np.zeros_like(imgwrap)

        onlydots = Utilities.showanswers(blankimg, ans, markedans, questions)

        invmatrix = cv2.getPerspectiveTransform(pt2, pt1)
        invimgwrap = cv2.warpPerspective(onlydots, invmatrix, (imgwidth, imgheight))

        finalimg = img.copy()
        finalimg = cv2.addWeighted(finalimg, 1, invimgwrap, 1, 0)

        # Grade display
        blankresultimg = np.zeros_like(imgwrapresult)
        cv2.putText(blankresultimg, str(marks), (100, 100), cv2.FONT_HERSHEY_PLAIN, 7, (0, 255, 255), 8)

        invmatrixresult = cv2.getPerspectiveTransform(pt4, pt3)
        invimgwrapresultresult = cv2.warpPerspective(blankresultimg, invmatrixresult, (imgwidth, imgheight))

        finalimg = cv2.addWeighted(finalimg, 1, invimgwrapresultresult, 1, 0)


        cv2.imshow("Raj's finalresult", finalimg)
        #cv2.imshow("Raj's finalimgresult", blankresultimg)
        '''
        cv2.imshow("Raj's finalimg", finalimg)
        cv2.imshow("Raj's colored inv", invimgwrap)
        cv2.imshow("Raj's colored", onlydots)
        cv2.imshow("Raj's photo", img)
        cv2.imshow("Raj's grey photo", imggrey)
        cv2.imshow("Raj's blur photo", imgblur)
        cv2.imshow("Raj's canny photo", imgcanny)
        cv2.imshow("Raj's countours photo", imgcountours)
        cv2.imshow("Raj's omr photo", imgwrap)
        cv2.imshow("Raj's result photo", imgwrapresult)
        cv2.imshow("Raj's thresh photo", imgthresh)
        
        
        cv2.imshow("Raj's countours photo final", imgcountoursbiggest)
        '''
        #cv2.waitKey(0)

    except:
        '''
        raw = np.zeros_like(img)
        cv2.imshow("No Image",raw)
        '''
        pass

    if cv2.waitKey(1) and 0xFF == ord('s'):
        cv2.imwrite("Finalresult.jpg", finalimg)
        cv2.waitKey(0)