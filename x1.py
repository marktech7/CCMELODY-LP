import vlc

# importing time module
import time

# creating a media player object
media_player = vlc.MediaListPlayer()

# creating Instance class object
player = vlc.Instance()

# creating a new media list object
media_list = player.media_list_new()

# creating a new media
media = player.media_new("/home/tim//videos/MVI_0365.MP4")
# MVI_0388.MP4
# MVI_0402.MP4
# adding media to media list
media_list.add_media(media)

# setting media list to the media player
media_player.set_media_list(media_list)

# creating a new media
media = player.media_new("/home/tim/Projects/OpenLP/s1.mp3")

# adding media to media list
media_list.add_media(media)

# setting media list to the media player
media_player.set_media_list(media_list)

# start playing video
media_player.play_item_at_index(1)

# wait so the video can be played for 5 seconds
# irrespective for length of video
time.sleep(5)
