import linecache
import threading
from zipfile import ZipFile
from io import BytesIO
import os
import glob
import os
import cv2
import _thread
from flask import Blueprint,  url_for, render_template, request, redirect, session, send_file

from .code.video_to_image import download_youtube_video, get_max_images, is_youtube_url, videoToImages, Constants, clearDicrectory


views = Blueprint('views', __name__)


@views.route('/final',  methods=['GET', 'POST'])
def final():
    image_folder = Constants.FRAMS_FOLDER_PATH
    video_path = session.get("video_path", None)
    image_files = 0
    show = True
    is_showing = session.get("is_showing", None)
    cap = cv2.VideoCapture(video_path)
        
    max = get_max_images(cap)
    images_to_get =(int)(max / 2)
    
    
    if is_showing and 'download' in request.form:

        return redirect(url_for('views.download_folder'))

    if os.listdir(image_folder) and not is_showing :
        
        session["is_showing"] = True
        show = False
        image_files = [file for file in os.listdir(
            image_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return render_template("final.html", min=1, max=max, image_files=image_files, show = show)



    if request.method == 'POST':
        images_to_get = request.form.get("images_to_get")
        session['images_to_get'] = images_to_get

        if video_path == None or 'return' in request.form:
            return redirect(url_for('views.home'))
                
        if 'download' in request.form:
            return redirect(url_for('views.loading'))
            

    return render_template("final.html", min=1, max=max, image_files=image_files, show = show, images_to_get = images_to_get)


@views.route('/',  methods=['GET', 'POST'])
def home():
    if os.path.exists(Constants.TEXT_FILE_PATH):
        os.remove(Constants.TEXT_FILE_PATH)
        
    youtube_url = 'Please_enter_a_vaild_youtube_url'
    
    
    clearDicrectory(Constants.VIDEO_FOLDER_PATH)
    clearDicrectory(Constants.FRAMS_FOLDER_PATH)

    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        if is_youtube_url(youtube_url):
            clearDicrectory(Constants.VIDEO_FOLDER_PATH)
            clearDicrectory(Constants.FRAMS_FOLDER_PATH)
            session['youtube_url'] = youtube_url
            session['is_showing'] = False
            return redirect(url_for('views.wait'))  
        else:
            youtube_url = 'Please_enter_a_vaild_youtube_url'
            print("reset")

            
        if 'file' in request.files:
            uploaded_file =  request.files['file']
            if uploaded_file.filename != '':
                clearDicrectory(Constants.VIDEO_FOLDER_PATH)
                clearDicrectory(Constants.FRAMS_FOLDER_PATH)
                uploaded_file.save(Constants.VIDEO_FOLDER_PATH + uploaded_file.filename)
                session['video_path'] = os.path.join(Constants.VIDEO_FOLDER_PATH + uploaded_file.filename)
                return redirect(url_for('views.final'))
            



    return render_template("home.html", youtube_url=youtube_url)


@views.route('/download_folder', methods=['GET', 'POST'])
def download_folder():
    folder_name = 'downloaded_folder'
    
    path = Constants.FRAMS_FOLDER_PATH
    root = os.path.dirname(path)
    files = glob.glob(os.path.join(path, '*'))
    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        for f in files:
            zf.write(f, os.path.relpath(f, root))
    stream.seek(0)
    sorted(os.listdir(path))
    return send_file(stream,
                     as_attachment=True,
                     download_name=f'{folder_name}.zip',
                     mimetype='application/zip',
                     )


@views.route("/loading")
def loading():
    video_path = session.get("video_path", None)
    images_to_get = session.get("images_to_get", None)
    cap = cv2.VideoCapture(video_path)
    
    videoToImages(cap, int(images_to_get))
    if(videoToImages == 0):
        return redirect(url_for('views.home'))
    
    return redirect(url_for('views.final'))




@views.route("/wait")
def wait():
    youtube_url = session.get("youtube_url", None)
    if not os.path.exists(Constants.TEXT_FILE_PATH):
        _thread.start_new_thread(download_youtube_video, (youtube_url,))
    else:
        with open(Constants.TEXT_FILE_PATH) as f:
            if 'finished' in f.read():
                video_path = linecache.getline(Constants.TEXT_FILE_PATH, 2).replace("\n", "")
                session['video_path'] = video_path
                return redirect(url_for('views.final'))
                
            else:
                print('No')
                
                
    return render_template("wait.html")
                
        
    # if os.path.exists(Constants.TEXT_FILE_PATH) and (linecache.getline(Constants.TEXT_FILE_PATH, 3).replace("\n", "") == "finished"):
    #     print(linecache.getline(Constants.TEXT_FILE_PATH, 3).replace("\n", ""))
    #     video_path = linecache.getline(Constants.TEXT_FILE_PATH, 2).replace("\n", "")
    #     session['video_path'] = video_path
        




    

