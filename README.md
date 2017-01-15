# chess24
Video processing script for chess24

#Purpose of the script

This script can be used for downloading mp4 videos from the purchased chess24 videos by adding an additional diagram embedding and encoding the final video as mp4. This can be useful for viewing the videos completely offline (without being logged in to chess24)

#Dependencies (to be retrieved e.g. via pip install <package>)
* moviepy
* numpy
* PIL
* wget

#Usage Instructions
* Substitute username and password in the script with your own c24 user/pw
* (optional) adapt the video size and/or diagram size
* Populate the videos to download list with your own video tuples by doing the following:
  * videosToDownload.append(videoUrl1,id1,series_id1)
  * videosToDownload.append(videoUrl2,id2,series_id2)
  * ...
* Make sure that write prviliges are set for the folder the script is run from

#Time for conversion
* Can be quite long depending on the chosen resolution. For the preconfigured setting conversion takes about an our for a 20-30 minutes video.

#Feedback and comments
Feedback and comments are highly appreciated and should be posted in the chess 24 user forum
