from django.shortcuts import render
from django.http import HttpResponse
from .forms import InstagramDownloadForm
import instaloader
import os
import re
import concurrent.futures
import shutil

def download_instagram(request):
    if request.method == 'POST':
        form = InstagramDownloadForm(request.POST)
        if form.is_valid():
            post_url = form.cleaned_data['post_url']

            try:
                # Your Instagram download logic here (similar to your script)
                L = instaloader.Instaloader()

                # Validate and clean the URL
                url_pattern = re.compile(r"https?://www\.instagram\.com/p/[\w-]+/?")
                if not url_pattern.match(post_url):
                    return HttpResponse("Invalid URL, please try again.")

                cleaned_url = re.sub(r"[?].*", "", post_url)
                url_parts = cleaned_url.split("/")
                if len(url_parts) < 2:
                    return HttpResponse("Invalid URL, please try again.")

                # Get post details
                post = instaloader.Post.from_shortcode(L.context, url_parts[-2])

                # Create destination folder
                username = post.owner_username
                destination_folder = f"{username}_downloads"
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder, mode=0o700)

                # Download photos
                L.download_post(post, target=destination_folder)

                # Move files to format-specific folders
                files = os.listdir(destination_folder)
                jpg_files = [file for file in files if file.endswith(".jpg")]

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for file in jpg_files:
                        file_path = os.path.join(destination_folder, file)
                        format_folder = os.path.join(destination_folder, f"{username}_jpg")
                        if not os.path.exists(format_folder):
                            os.makedirs(format_folder, mode=0o700)
                        executor.submit(shutil.move, file_path, os.path.join(format_folder, file))

                # Ask the user if they want to delete certain files
                delete_files = input("Do you want to delete the .json.xz and .txt files? (y/n): ")
                if delete_files.lower() == "y":
                    files = os.listdir(destination_folder)
                    delete_extensions = (".json.xz", ".txt")
                    delete_files = [file for file in files if file.endswith(delete_extensions)]
                    for file in delete_files:
                        file_path = os.path.join(destination_folder, file)
                        os.remove(file_path)

                # Provide the user with a local download link
                download_link = os.path.abspath(destination_folder)
                return render(request, 'insta_downloader/download_complete.html', {'download_link': download_link})

            except instaloader.exceptions.InstaloaderException as e:
                return HttpResponse(f"Error occurred: {e}")

    else:
        form = InstagramDownloadForm()

    return render(request, 'insta_downloader/download_instagram.html', {'form': form})
