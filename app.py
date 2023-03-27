from flask import Flask, render_template, request
from steg_advanced import encode_img, decode_file
import os
import cv2

app = Flask(__name__)


@app.route('/')
def index():
    encoded_images_list= os.listdir("./static/encoded_images")
    return render_template('index.html', encoded_images_list=encoded_images_list)


@app.route('/encode' , methods = ['GET', 'POST'])
def encode():
    request_method = request.method
    if request_method == 'POST':
        method = request.form['method']
        if method == "encode":
            file_to_encode = request.files['file_to_encode']
            image = request.files['image']
            return name(method=method, file_to_encode=file_to_encode, image=image)
    return render_template('encode.html', request_method = request_method)

@app.route('/decode' , methods = ['GET', 'POST'])
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
            return name(method=method, file_to_encode="", image=encoded_name)
    return render_template('decode.html', request_method = request_method, list_files=list_files)

def name(method, file_to_encode, image):
    if method == "encode":
        UPLOAD_FOLDER = "static/"
        image.save(os.path.join(UPLOAD_FOLDER + 'uploaded_images_for_encode', image.filename))
        file_to_encode.save(os.path.join(UPLOAD_FOLDER + 'uploaded_files_to_encode', file_to_encode.filename))
        input_image = "./static/uploaded_images_for_encode/"+image.filename
        file_to_encode = "./static/uploaded_files_to_encode/"+file_to_encode.filename
        # split the absolute path and the file
        path, file = os.path.split(input_image)
        # split the filename and the image extension
        filename, ext = file.split(".")
        output_image = "./static/encoded_images/"+f"{filename}_encoded.{ext}"
        print(output_image)
        encoded_image = encode_img(image_name=input_image, secret_data=file_to_encode)
        cv2.imwrite(output_image, encoded_image)
        print("[+] Saved encoded image.")
        return render_template('encoded_image_display.html', user_image=output_image[1:])

    elif method == "decode":
        decoded_data = decode_file('./static/encoded_images/' + image, n_bits = 1)
        print(decoded_data)
        final = decoded_data[1:]
        return render_template('decoded_file_display.html', filename=final)


if __name__ == '__main__':
   app.run(debug = True)
