from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .steg_advanced import encode_img, decode_file
import os
import cv2

views = Blueprint('views', __name__)

UPLOAD_FOLDER = "website/static/"

store_dict = {}

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/method' , methods = ['GET', 'POST'])
def method():
    encoded_images_list= os.listdir(UPLOAD_FOLDER + "encoded_images")
    method = request.form['method']
    user = current_user
    if method == "encode":
        return render_template('encode.html', user=user)
    else:
        return render_template('decode.html', user=user, list_files=encoded_images_list)

@views.route('/encode' , methods = ['GET', 'POST'])
def encode():
    request_method = request.method
    if request_method == 'POST':
        method = request.form['method']
        if method == "encode":
            file_to_encode = request.files['file_to_encode']
            image = request.files['image']
            lth_bit = int(request.form['L'])
            s_bit = int(request.form['S'])
            return name(method=method, file_to_encode=file_to_encode, image=image, lth_bit=lth_bit, s_bit=s_bit)
    return render_template('encode.html', request_method = request_method, user=current_user)

@views.route('/decode' , methods = ['GET', 'POST'])
def decode():
    request_method = request.method
    if request_method == 'GET':
        ini_list = request.args.get('list_files')
        ini_list_files = ini_list.strip('][').split(', ')
        list_files = []
        for name_list in ini_list_files:
            list_files.append(name_list[1:len(name_list)-1])
    if request_method == 'POST':
        method = request.form['method']
        if method == "decode":
            encoded_name = request.form['encoded_name']
            lth_bit = int(request.form['L'])
            s_bit = int(request.form['S'])

            return name(method=method, file_to_encode="", image=encoded_name, lth_bit=lth_bit, s_bit=s_bit)
    return render_template('decode.html', request_method = request_method, list_files=list_files)

def name(method, file_to_encode, image, lth_bit, s_bit):
    if method == "encode":
        image_name = image.filename
        image.save(os.path.join(UPLOAD_FOLDER + 'uploaded_images_for_encode', image_name))
        file_to_encode.save(os.path.join(UPLOAD_FOLDER + 'uploaded_files_to_encode', file_to_encode.filename))
        input_image = UPLOAD_FOLDER + "uploaded_images_for_encode/" + image_name
        file_to_encode = UPLOAD_FOLDER + "uploaded_files_to_encode/" + file_to_encode.filename
        # split the absolute path and the file
        path, file = os.path.split(input_image)
        # split the filename and the image extension
        filename, ext = file.split(".")
        output_image = "./website/static/encoded_images/"+f"{filename}_encoded.{ext}"
        print(output_image)
        encoded_image = encode_img(image_name=input_image, secret_data=file_to_encode, lth_bit=lth_bit, s_bit=s_bit)
        cv2.imwrite(output_image, encoded_image)
        print("[+] Saved encoded image.")
        output_image = output_image[9:]
        return render_template('encoded_image_display.html', user_image=output_image, user= current_user)

    elif method == "decode":
        decoded_data = decode_file(UPLOAD_FOLDER + 'encoded_images/' + image, lth_bit=lth_bit, s_bit=s_bit)
        print(decoded_data)
        final = decoded_data[7:]
        print(final)

        return render_template('decoded_file_display.html', filename=final, user= current_user)