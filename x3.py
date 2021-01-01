import vlc

# importing time module
import time


class x2(object):

    def event_media(self, event):
        print("media")

    def event_time(self, event):
        #print(event.type)
        if event.type == vlc.EventType.MediaListPlayerNextItemSet:
            print("Hello")
        elif event.type == vlc.EventType.MediaStateChanged:
            print("GoodBye")
        else:
            print(event.type)

    def test_me(self):
        # creating a media player object
        media_player = vlc.MediaListPlayer()
        # creating Instance class object
        vlc_instance = vlc.Instance()
        # creating a new media list object
        media_list = vlc_instance.media_list_new()
        # creating a new media
        media = vlc_instance.media_new("/home/tim/Projects/OpenLP/s1.mp3")
        media_list.add_media(media)
        # setting media list to the media player
        media_player.set_media_list(media_list)
        # adding media to media list
        media_list.add_media(vlc_instance.media_new("/home/tim/Projects/OpenLP/s2.mp3"))
        media_list.add_media(vlc_instance.media_new("/home/tim/Projects/OpenLP/s3.mp3"))

        print(media_list.count())
        media.event_manager().event_attach(vlc.EventType.MediaPlayerMediaChanged, self.event_time)
        media.event_manager().event_attach(vlc.EventType.MediaStateChanged, self.event_time)
        media_player.event_manager().event_attach(vlc.EventType.MediaPlayerStopped, self.event_time)
        media.event_manager().event_attach(vlc.EventType.MediaPlayerPaused, self.event_time)
        media.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.event_time)
        media_player.event_manager().event_attach(vlc.EventType.MediaListPlayerStopped, self.event_time)
        media_player.event_manager().event_attach(vlc.EventType.MediaListPlayerNextItemSet, self.event_time)
        media_player.event_manager().event_attach(vlc.EventType.MediaListPlayerPlayed, self.event_time)
        media_list.event_manager().event_attach(vlc.EventType.MediaListEndReached, self.event_time)

        # setting media list to the media player
        media_player.set_media_list(media_list)

        # start playing video
        print("A")
        media_player.play_item_at_index(0)
        time.sleep(30)

x2().test_me()
