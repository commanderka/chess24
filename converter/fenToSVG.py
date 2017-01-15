'''
Created on 10.01.2017
@author: Christian
'''

from moviepy.editor import *
import urllib.request
import urllib.parse
import json
import requests
from PIL import Image
import io
import numpy as np
import wget
import os
import sys

def fenToNumpyImage(inputFen,diagramSize):
    params = urllib.parse.urlencode({'fen':inputFen,'size':diagramSize})
    req = urllib.request.Request("https://backscattering.de/web-boardimage/board.png?{0}".format(params))
    r = urllib.request.urlopen(req)
    bytecontent = r.read()
    stream = io.BytesIO(bytecontent)
    pilImage = Image.open(stream)
    numpyImage = np.array(pilImage)
    return numpyImage

if __name__ == '__main__':
    #please replace with your user name and password
    c24User = 'testUser'
    c24Password  = 'testPassword'
    #width of the final clip
    outputClip_width = 853
    #diagram size in pixels (width=height)
    diagramSize = 400
    #list of tuples containing video url and id and series id of the video
    #this information can be found in the source code of the video series webpage at chess24
    #substitute by the videos you have purchased
    videosToDownload = []
    videosToDownload.append(("https://cdn.chess24.com/2bIU7tBARJmblgmTy_4JFA/mp4/full/GI Sidelines P1 Eng.mp4",86,10))
    #login to c24
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    session = requests.Session()
    loginUrl = "https://chess24.com/de/login"
    annotationServiceUrl = "https://chess24.com/api/web/videoSeriesAPI/videoDescription"
    session.get(loginUrl)
    csrfToken = session.cookies['csrf']
    loginparams = {'yt1':'login','csrf':csrfToken,'LoginForm[rememberMe]':'0','returnUrl':'','LoginForm[emailOrUsername]':c24User,'LoginForm[password]':c24Password}
    r = session.post(loginUrl,data=loginparams,headers=headers)

    for videoToDownload in videosToDownload:
        subcliplist = []
        videoFilename = wget.download(videoToDownload[0])
        clip = VideoFileClip(videoFilename, audio=True)
        #resize to a 
        clip_resized = clip.resize(width=outputClip_width)
        subcliplist.append(clip_resized)
        params = {'id':videoToDownload[1],'series_id':videoToDownload[2]}
        r = session.get(annotationServiceUrl,params = params,headers=headers)
        decodedJson = json.loads(r.text)
        #associates each move with an FEN
        moveIdToFenImageMap = {}
       
        cuepointElement = decodedJson["cuepoints"]
        #add moves in games elements to fen list
        
        if "games" in decodedJson:   
            gameNode = decodedJson["games"]
            for game in gameNode:
                video_start_fen = game["video_start_fen"]
                video_start_image= fenToNumpyImage(video_start_fen,diagramSize)
                startClip = ImageClip(video_start_image)    
                subcliplist.append(startClip)
                moveElements = game["moves"]
                for moveElement in moveElements:
                    moveId = moveElement["id"]
                    if "fen" in moveElement:
                        fen= moveElement["fen"]
                        fenAsNumpy= fenToNumpyImage(fen,diagramSize)
                        moveIdToFenImageMap[moveId] = fenAsNumpy
                    else:
                        moveIdToFenImageMap[moveId] = video_start_image
                    
        for cuePoint in cuepointElement:
            time = cuePoint['time']
            data = cuePoint['data']
            name = cuePoint['name']
            numpyImage = None
            if name=='move':
                moveId = data['id']
                fen = data['fen']
                #retrieve fen image data  
                numpyImage = fenToNumpyImage(fen,diagramSize)
                moveIdToFenImageMap[moveId] = numpyImage
            elif name=='gotoId':
                moveId = data['id']
                if moveId in moveIdToFenImageMap:
                    numpyImage = moveIdToFenImageMap[moveId]
            #append clip
            if numpyImage is not None:
                currentClip = ImageClip(numpyImage)    
                subcliplist.append(currentClip.set_start(time))
        
        #write out combined video        
        videoClip_combined = CompositeVideoClip(subcliplist)
        videoClip_combined.duration = clip_resized.duration
        outputFileName = os.path.splitext(videoFilename)[0]+"_processed.mp4"
        videoClip_combined.write_videofile(outputFileName)
    #videoClip_combined = CompositeVideoClip([subclip, testImageClip.set_start(23.594).set_pos((20,20)),testImageClip2.set_start(30).set_pos((20,20))])
   
