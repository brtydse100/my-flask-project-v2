import linecache
from multiprocessing import process
from random import randrange
import shutil
from pathlib import Path
import threading
from zipfile import ZipFile
from io import BytesIO
import os
from pathlib import Path
import glob
import os
import cv2
import _thread

from flask import Blueprint,  url_for, render_template, request, redirect, session, send_file

from .code.video_to_image import download_youtube_video, get_max_images, is_youtube_url, videoToImages, clearDicrectory
from .code.cnn_model import get_labels, cnn_model_eval

views = Blueprint('views', __name__)





@views.route('/',  methods=['GET', 'POST'])
def home():

    youtube_url = 'Please_enter_a_vaild_youtube_url'
    
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        user_id = randrange(0, 1000000)
        user_folder_path = None
        current_path = os.path.dirname(os.path.abspath(__file__))

        user_folder_path = os.path.join(current_path, (r"static\users\\" + str(user_id)))
        session['user_id'] = user_id
            
        session['user_folder_path'] = user_folder_path
        session['file_path'] = os.path.join(user_folder_path, (str(user_id)+".txt"))
        
        if is_youtube_url(youtube_url):
            session['youtube_url'] = youtube_url
            os.mkdir(user_folder_path)
            session['is_showing'] = True
            return redirect(url_for('views.wait'))  
        else:
            youtube_url = 'Please_enter_a_vaild_youtube_url'
            print("reset")

            
        if 'video_file' in request.files:
            uploaded_file =  request.files['video_file']
            if uploaded_file.filename != '':
                
                os.mkdir(user_folder_path)

                uploaded_file.save((user_folder_path + "/") + uploaded_file.filename)
                video_path = os.path.join(user_folder_path , uploaded_file.filename)

                session['video_path'] = video_path
                
                if os.path.exists(video_path):
                    session['is_showing'] = True
                    return redirect(url_for('views.final')) 

    return render_template("home.html", youtube_url=youtube_url)


@views.route('/final',  methods=['GET', 'POST'])
def final():
    user_folder_path = session.get("user_folder_path", None)
    video_path = session.get("video_path", None)
    user_id = session.get("user_id", None)
    is_showing = session.get("is_showing", None)
    
    image_files = 0
    cap = cv2.VideoCapture(video_path)
    max = get_max_images(cap)
    images_to_get =(int)(max / 2)

    
    if os.path.exists(str(video_path)) == False or 'return' in request.form or max == 0:
        session['user_folder_path'] = None
        return redirect(url_for('views.home'))
    
    

    if not is_showing and ('download' in request.form):
        return redirect(url_for('views.download_folder'))

    if not is_showing :
        image_files = [file for file in os.listdir(
            user_folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return render_template("final.html", min=1, max=max, image_files=image_files, show = is_showing, user_id = str(user_id))

    if request.method == 'POST':
        images_to_get = request.form.get("images_to_get")
        print("images_to_get: ", images_to_get)
        session['images_to_get'] = images_to_get


                
        if 'download' in request.form:
            return redirect(url_for('views.loading'))
            

    return render_template("final.html", min=1, max=max, show = is_showing, images_to_get = images_to_get,  user_id = str(user_id))



@views.route('/download_folder', methods=['GET', 'POST'])
def download_folder():
    folder_name = session.get("user_id", None)
    video_path = session.get("video_path", None)
    file_path = session.get("file_path", None)
    path = session.get("user_folder_path", None)
    root = os.path.dirname(path)

    if os.path.exists(file_path):
        os.remove(file_path)
        
    if os.path.exists(video_path):
        os.remove(video_path)
    
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
    user_folder_path = session.get("user_folder_path", None)
    session["is_showing"] = False
    
    cap = cv2.VideoCapture(video_path)
    
    videoToImages(cap, int(images_to_get), user_folder_path)
    # if(videoToImages == 0):
    #     return redirect(url_for('views.home'))
    
    return redirect(url_for('views.final'))




@views.route("/wait")
def wait():
    youtube_url = session.get("youtube_url", None)
    user_id = session.get("user_id", None)
    user_folder_path = session.get("user_folder_path", None)
    file_path = session.get("file_path", None)
    print(file_path)
    print(user_folder_path)
    if not os.path.exists(file_path):
        _thread.start_new_thread(download_youtube_video, (youtube_url,user_id,user_folder_path))
    else:
        with open(file_path) as f:
            if 'finished' in f.read():
                video_path = linecache.getline(file_path, 2).replace("\n", "")
                f.close()
                session['video_path'] = video_path
                return redirect(url_for('views.final'))
                
            else:
                print('No')
                
                
    return render_template("wait.html")

@views.route('/cnn_model',  methods=['GET', 'POST'])
def cnn_model():
    model_user_id = session.get("model_user_id", None)
    model_user_folder_path = session.get("model_user_folder_path", None)
    model_path = None
    missing_fields = False
    error_message = "enter all the fields to proceed with testing"
    
    
    if request.method == 'POST':
        model_user_id = randrange(0, 1000000)
        current_path = os.path.dirname(os.path.abspath(__file__))

        model_user_folder_path = os.path.join(current_path, (r"static\users\\" + str(model_user_id)))
        session['model_user_id'] = model_user_id
            
        session['model_user_folder_path'] = model_user_folder_path
        


    if 'model_file' in request.files:
        
        uploaded_model_file =  request.files['model_file']
        if uploaded_model_file.filename != '':
            model_path = os.path.join(model_user_folder_path , uploaded_model_file.filename)
            session['model_path'] = model_path


    if 'get_model' in request.form:
        print(model_path)
        if model_path != None:
            os.mkdir(model_user_folder_path)
            uploaded_model_file.save(model_path)
            return  redirect(url_for("views.cnn_model_final"))
        else:
            missing_fields = True
            return render_template("cnn_model.html", error_message = error_message,missing_fields = missing_fields)
            

    
    return render_template("cnn_model.html", error_message = error_message, missing_fields = missing_fields)
        




@views.route('/cnn_model_final',  methods=['GET', 'POST'])
def cnn_model_final():
    uploaded_image_file = None
    model_user_folder_path = session.get("model_user_folder_path", None)
    image_filename = session.get("image_filename", None)
    model_path = session.get("model_path", None)
    image_path = session.get("image_path", None)
    labels = session.get("labels", None)
    model_user_id = session.get("model_user_id", None)
    is_image = False
    is_done = session.get("is_done", False)
    print(is_done)
    user_inputs = []

    if is_done:
        if request.method == 'POST':
            print("what the fuck")
            
            labels_num = get_labels(model_path)
            for i in range (labels_num):
                input_name = f'input{i}'
                user_inputs.append(request.form[input_name])
                print(request.form[input_name])
            
            if 'submit_labels' in request.form:
                session["is_done"] = False
                session["labels"] = user_inputs
                return render_template("cnn_model_final.html", is_image = is_image, is_done = is_done)

            
    if request.method == 'POST':
        # if is_done:
        #     print("what the fuck")
        #     print("what the fuck")
            
        #     labels_num = get_labels(model_path)
        #     for i in range (labels_num):
        #         input_name = f'input{i}'
        #         user_inputs.append(request.form[input_name])
        #         print(request.form[input_name])
            
        #     if 'submit_labels' in request.form:
        #         session["is_done"] = False
        #         session["labels"] = user_inputs
        #         return render_template("cnn_model_final.html", is_image = is_image, is_done = is_done)
            
            
        if labels != None:
            
            if 'image_file' in request.files:
                uploaded_image_file =  request.files['image_file']
                if uploaded_image_file.filename != '':
                    image_path = os.path.join(model_user_folder_path , uploaded_image_file.filename)

            if 'submit_model' in request.form:
                if uploaded_image_file != None:
                    uploaded_image_file.save(image_path)
                    is_image = True
                    user_model = cnn_model_eval(model_path = model_path, image_path = image_path, labels = labels, model_user_id =model_user_id)
            
                    session['image_path'] = image_path
                    image_name = uploaded_image_file.filename
                    Confidence, preds_label = user_model.model_prediction()
                    return render_template("cnn_model_final.html",image_name = image_name, Confidence =Confidence, preds_label = preds_label, is_image =is_image)
                
                else:
                    return render_template("cnn_model_final.html", is_image =is_image)
        else:
            labels_num = get_labels(model_path)
            session["is_done"] = True
            return render_template("cnn_model_final.html",is_done = is_done, is_image = False, labels_num = labels_num)

    user_model = cnn_model_eval(model_path = model_path, image_path = None, labels = None)

    return render_template("cnn_model_final.html", is_image = is_image)



    

