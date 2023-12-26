from django.shortcuts import render
from .instagram_downloader import Instagram_Downloader
import time

def download_instagram(request, username):
    try:
        user = Instagram_Downloader(username)
        user.create_download_directory()
        user.get_jsondata_instagram()
        user.download_photos()
        user.download_videos()
        user.set_apilabel("data")
        user.read_resume_end_cursor_timeline_media()
        while True:
            time.sleep(5)  # pause to avoid ban
            user.get_jsondata_instagram()
            user.download_photos()
            user.download_videos()
            user.write_resume_end_cursor_timeline_media()
            if not user.has_next_page():
                user.remove_resume_file()
                message = f"Done. All images/videos downloaded for {username} account."
                return render(request, 'download_complete.html', {'message': message})
    except:
        message = "Notice: script prematurely finished due to the daily limit of requests to Instagram API."
        message += "Just execute the script AGAIN in a few hours to continue RESUME of pending images/videos to download."
        return render(request, 'error.html', {'message': message})

