# chess24
Video processing script for chess24

#Purpose of the script

This script can be used for downloading mp4 videos from the purchased chess24 videos by adding an additional diagram embedding and encoding the final video as mp4. This can be useful for viewing the videos completely offline (without being logged in to chess24)

#Dependencies (to be retrieved e.g. via pip install <package>)
* moviepy
* numpy
* PIL
* wget
* requests

#Usage Instructions
* Substitute username and password in the script with your own c24 user/pw
* (optional) adapt the video size and/or diagram size
* Find out the urls and ids/series ids you want to retrieve
  * This can be done by loading the chess24 source of the page for the series you want to retrieve and searching for "mp4". You will see sth. like this then:
  ```javascript
  jQuery('#videoHolder').videoDisplay(
			'{"id":"131","series_id":"10"}',
			[{"webm":"https:\/\/cdn.chess24.com\/*****\/webm\/full\/*****.webm","mp4":"https:\/\/cdn.chess24.com\/*****\/mp4\/full\/*****.mp4"}],
			'null',
			'74328d92' 
   ````
   Just extract the values for video url (remove the backslashes), id and series id. The above would give:
   (https://cdn.chess24.com/*****/mp4/full/*****.mp4,131,10)
* Populate the videos to download list with your own video tuples by doing the following:
  * videosToDownload.append(videoUrl1,id1,series_id1)
  * videosToDownload.append(videoUrl2,id2,series_id2)
  * ...
* Make sure that write prvileges are set for the folder the script is run from

#Time for conversion
* Can be quite long depending on the chosen resolution. For the preconfigured setting conversion takes about an hour for a 20-30 minutes video.

#Feedback and comments
Feedback and comments are highly appreciated and should be posted in the chess 24 user forum
