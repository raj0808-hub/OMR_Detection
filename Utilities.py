import cv2
import numpy
import numpy as np


def rectangular(countours):
    rectcon=[]
    for i in countours:
        area=cv2.contourArea(i)
        print("Area={}".format(area), end=" ")
        if(area>500):
            perimeter=cv2.arcLength(i,True)
            approx=cv2.approxPolyDP(i, 0.02*perimeter, True)
            #print("perimeter={}, Approximation={}".format(perimeter, approx))
            #print("corner point={}".format(len(approx)))
            if(len(approx)==4):
                rectcon.append(i)
    #print("rectcon=",rectcon)
    rectcon=sorted(rectcon,key=cv2.contourArea,reverse=True)
    return rectcon



def getcornerpoint(cont):
    perimeter = cv2.arcLength(cont, True)
    approx = cv2.approxPolyDP(cont, 0.02 * perimeter, True)
    return approx

def reorder(mypoints):
    mypoints=mypoints.reshape((4,2))
    add=mypoints.sum(1)
    diff=np.diff(mypoints,axis=1)
    #print(mypoints)
    #print(add)
    #print(diff)
    newpoints=np.zeros((4,1,2),np.int32)
    newpoints[0] = mypoints[np.argmin(add)]
    newpoints[3] = mypoints[np.argmax(add)]
    newpoints[2] = mypoints[np.argmax(diff)]
    newpoints[1] = mypoints[np.argmin(diff)]
    return newpoints


def splitboxes(imgthresh,questions):
    rows=np.vsplit(imgthresh,questions)
    #cv2.imshow("rows",rows[1])
    print(len(rows))
    boxes=[]
    for r in rows:
        cols=np.hsplit(r,5)
        #cv2.imshow("cols", cols[4])
        for c in cols:
            boxes.append(c)

    return boxes


def showanswers(imgwrap,ans,markedans,questions):
    secwidth = int(imgwrap.shape[1]/5)
    secheight = int(imgwrap.shape[0]/questions)
    Green = (0,255,0)
    Red = (0,0,255)
    Orange = (0,165,255)

    for x in range (questions):

        myans = markedans[x]

        cx = (ans[x]*secwidth)+secwidth//2
        cy = (x*secheight)+secheight//2


        cv2.circle(imgwrap,(cx,cy),30,Green,cv2.FILLED)        #For all correct answers


        if (markedans[x] == 0) :
            cxx = secwidth//2
            cv2.circle(imgwrap, (cxx, cy), 30, Orange, cv2.FILLED)


        if(markedans[x] != ans[x] and markedans[x] != 0):
            cx = (markedans[x] * secwidth) + secwidth // 2
            cy = (x * secheight) + secheight // 2
            cv2.circle(imgwrap, (cx, cy), 30, Red, cv2.FILLED)

    #cv2.imshow("Raj's colored", imgwrap)
    return imgwrap

