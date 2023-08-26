
from multiprocessing import Process
import re
import shutil
import cv2
import os
import math
from pytube import YouTube

# is_downloaded = None
# video_path = None


class Constants:  # change those
    FRAMS_FOLDER_PATH = os.path.join(
        os.getcwd(), os.path.join(r"website\static\frames"))
    VIDEO_FOLDER_PATH = os.path.join(
        os.getcwd(), os.path.join(r"website\videos"))
    TEXT_FILE_PATH = os.path.join(os.getcwd(), os.path.join(r"website\static\video_path.txt"))
    STATIC_FOLDER_PATH = os.path.join(os.getcwd(), os.path.join(r"website\static"))


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


def download_youtube_video(video_url):
    os.chdir(Constants.STATIC_FOLDER_PATH)
    with open("video_path.txt", "a") as f:
        f.write("started \n")
        f.close()

    try:
        youtube = YouTube(video_url)
        video_stream = youtube.streams.get_highest_resolution()
        video_path = video_stream.download(
            output_path=Constants.VIDEO_FOLDER_PATH)
        with open("video_path.txt", "a") as f:

            f.write(video_path + "\n")
            f.write("finished")

    except Exception as e:
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


def videoToImages(cap, images_to_get):
    os.chdir(Constants.FRAMS_FOLDER_PATH)
    image_counter = 1
    for i in frames_to_get(cap, images_to_get):
        cap.set(1, i)  # Where frame_no is the frame you want
        ret, frame = cap.read()  # Read the frame
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
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
