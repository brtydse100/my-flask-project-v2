import re
import shutil
import cv2
import os
import math
import yt_dlp


def is_youtube_url(url):
    youtube_pattern = re.compile(
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+')
    if url is not None:
        return bool(youtube_pattern.match(url))
    else:
        return False


def videoTime(cap):
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    seconds = math.floor(frame_count/fps)
    return seconds


def download_youtube_video(video_url, user_id, user_folder):
    # Change directory to the user folder
    os.chdir(user_folder)
    
    # Log the start of the process
    with open(f"{user_id}.txt", "a") as f:
        f.write("started \n")
    
    try:
        # Set up yt_dlp options
        ydl_opts = {
            'outtmpl': os.path.join(user_folder, '%(title)s.%(ext)s'),  # Save file in the specified folder with video title
            'format': 'best',  # Choose the best quality video and audio combined
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_path = os.path.join(user_folder, f"{info_dict['title']}.{info_dict['ext']}")

        # Log the video path and completion
        with open(f"{user_id}.txt", "a") as f:
            f.write(video_path + "\n")
            f.write("finished\n")
        
        return True, f"Video downloaded successfully: {video_path}"
    
    except Exception as e:
        # Log the error
        with open(f"{user_id}.txt", "a") as f:
            f.write(f"An error occurred: {str(e)}\n")
        return False, f"An error occurred: {str(e)}"


def clearDicrectory(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def videoToImages(cap, images_to_get, user_folder):
    os.chdir(user_folder)
    image_counter = 1
    for i in frames_to_get(cap, images_to_get):
        cap.set(1, i)  # Where frame_no is the frame you want
        ret, frame = cap.read()  # Read the video
        cv2.imwrite(f"{image_counter}.jpg", frame)
        image_counter += 1


def frames_to_get(cap, images_to_get):
    frames_to_get_list = []
    i = 0

    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    step = frame_count / images_to_get
    frame_counter = 0

    while frame_counter < frame_count:
        frames_to_get_list.append(frame_counter)
        frame_counter += step
        i += 1

    return frames_to_get_list


def get_max_images(cap):
    if cap.get(cv2.CAP_PROP_FPS) == 0:
        return 0
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
