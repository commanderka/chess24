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
from enum import Enum
import chess

class EncodingMode(Enum):
    DIAGRAM_ONLY = 0
    DIAGRAM_AND_VIDEO = 1

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
    encodingMode = EncodingMode.DIAGRAM_ONLY
    #width of the final clip
    outputClip_width = 853
    #diagram size in pixels (width=height)
    diagramSize = 400
    #list of tuples containing video url and id and series id of the video
    #this information can be found in the source code of the video series webpage at chess24
    #substitute by the videos you have purchased
    videosToDownload = []
    #videosToDownload.append(("https:\/\/cdn.chess24.com\/XPv0hXY8Qb-qemUJmBPY1A\/mp4\/full\/GI_5_Bd2_Eng.mp4",89,10))
    #videosToDownload.append(("https:\/\/cdn.chess24.com\/T2CVspF-QM-pIUqP3U7XFw\/mp4\/full\/najdorfschwarzintro.mp4",148,12))
    #videosToDownload.append(("https:\/\/cdn.chess24.com\/Pzu9LI_ER9upI99rZF0ojA\/mp4\/full\/najdorf6nebenvarianten.mp4",149,12))

 
    videosToDownload.append(("https:\/\/cdn.chess24.com\/It_1ROWBSRyfREAzRXsqaA\/mp4\/full\/0 INTRO wolga.mp4",530,59))
    videosToDownload.append(("https:\/\/cdn.chess24.com\/tSUDwoTwRR-a0Xj4xqFDbw\/mp4\/full\/1_abweichungen_im_4_zug_verbesserte_version.mp4",531,59))
    videosToDownload.append(("https:\/\/cdn.chess24.com\/74cvWx21TmiTxVcPk7ZzTg\/mp4\/full\/2 abweichungen im 5. zug.mp4",532,59))
    videosToDownload.append(("https:\/\/cdn.chess24.com\/HYQSM97lTTepJ2F3PugS-A\/mp4\/full\/3_fianchetto_system.mp4",533,59))
    videosToDownload.append(("https:\/\/cdn.chess24.com\/50Zlpx7sRDShGYH5PrZgWA\/mp4\/full\/4 k\u00fcnstliche rochade.mp4",534,59))
    
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
        videoUrl = videoToDownload[0].replace("\\","")
        videoFilename = videoUrl.rsplit('/', 1)[-1]
        if not os.path.exists(videoFilename):
            videoFilename = wget.download(videoUrl)
        clip = VideoFileClip(videoFilename, audio=True)
        if encodingMode == EncodingMode.DIAGRAM_AND_VIDEO:
            clip_resized = clip.resize(width=outputClip_width)
            subcliplist.append(clip_resized)
        params = {'id':videoToDownload[1],'series_id':videoToDownload[2]}
        r = session.get(annotationServiceUrl,params = params,headers=headers)
        decodedJson = json.loads(r.text)
        #associates each move with an FEN
        moveIdToFenImageMap = {}
        moveIdToFenStringMap = {}
       
        cuepointElement = decodedJson["cuepoints"]
        #add moves in games elements to fen list
        gameId = 0
        if "games" in decodedJson:   
            gameNode = decodedJson["games"]
            for game in gameNode:
                if not gameId in moveIdToFenStringMap:
                    moveIdToFenStringMap[gameId] = {}
                if not gameId in moveIdToFenImageMap:
                    moveIdToFenImageMap[gameId] = {}
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
                        moveIdToFenImageMap[gameId][moveId] = fenAsNumpy
                        moveIdToFenStringMap[gameId][moveId] = fen
                    else:
                        previousMoveId = moveElement["pm"]
                        moveString = moveElement["m"]
                        #get board of previous move
                        previousMoveBoard = chess.Board(moveIdToFenStringMap[gameId][previousMoveId])
                        #make the move
                        currentMove = chess.Move.from_uci(moveString.lower())
                        previousMoveBoard.push(currentMove)
                        moveIdToFenStringMap[gameId][moveId] = previousMoveBoard.fen()
                gameId= gameId+1
                    
        for cuePoint in cuepointElement:
            time = cuePoint['time']
            data = cuePoint['data']
            name = cuePoint['name']
            numpyImage = None
            if name=='move':
                gameIndex = data['gameIndex']
                moveId = data['id']
                fen = data['fen']
                #retrieve fen image data  
                numpyImage = fenToNumpyImage(fen,diagramSize)
                moveIdToFenImageMap[gameIndex][moveId] = numpyImage
            elif name=='gotoId':
                moveId = data['id']
                gameIndex = data['gameIndex']
                if moveId in moveIdToFenImageMap[gameIndex]:
                    numpyImage = moveIdToFenImageMap[gameIndex][moveId]
                elif moveId in moveIdToFenStringMap[gameIndex]:
                    numpyImage = fenToNumpyImage(moveIdToFenStringMap[gameIndex][moveId],diagramSize)
                    moveIdToFenImageMap[gameIndex][moveId] = numpyImage
            elif name=='selectGame':
                if 'initialMoveId' in data:
                    initialMoveId = data['initialMoveId']
                    gameIndex = data['gameIndex']
                    if initialMoveId in moveIdToFenImageMap[gameIndex]:
                        numpyImage = moveIdToFenImageMap[gameIndex][initialMoveId]
                    elif initialMoveId in moveIdToFenStringMap[gameIndex]:
                        numpyImage = fenToNumpyImage(moveIdToFenStringMap[gameIndex][initialMoveId],diagramSize)
                        moveIdToFenImageMap[gameIndex][initialMoveId] = numpyImage
            #append clip
            if numpyImage is not None:
                currentClip = ImageClip(numpyImage)    
                subcliplist.append(currentClip.set_start(time))
        
        #write out combined video        
        videoClip_combined = CompositeVideoClip(subcliplist)
        videoClip_combined.fps = 5
        videoClip_combined.duration = clip.duration
        if encodingMode == EncodingMode.DIAGRAM_ONLY:
            videoClip_combined = videoClip_combined.set_audio(clip.audio)
        
        outputFileName = os.path.splitext(videoFilename)[0]+"_processed.mp4"
        videoClip_combined.write_videofile(outputFileName)
        os.remove(videoFilename)
   
