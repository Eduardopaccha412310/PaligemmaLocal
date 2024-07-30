from flask import render_template, request, redirect, url_for, flash, jsonify
import os
import base64
import re
from werkzeug.utils import secure_filename
from PIL import Image
import io
import torch
from transformers import AutoProcessor, PaliGemmaForConditionalGeneration

UPLOAD_FOLDER = 'uploads/'
TEMP_IMAGE_PATH = 'temp_image.png'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
processor = None

def init_app(app):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = 'supersecretkey'

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/process_image', methods=['POST'])
    def process_image_route():
        data = request.get_json()
        text_input = data.get('text_input', '')
        image_data = data.get('image_data', '')
        
        if not text_input:
            return jsonify({'result': 'No se ingresó ningún texto'})
        
        if not image_data:
            return jsonify({'result': 'No se subió ninguna imagen'})
        
        result = process_image_cam(image_data, text_input)
        return jsonify({'result': result})

    def process_image_cam(image_data, text_input):
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        image_data = base64.b64decode(image_data)
        
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        global model, processor
        if model is None or processor is None:
            model_path = "Model"
            token = "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"
            model = PaliGemmaForConditionalGeneration.from_pretrained(model_path, use_auth_token=token).to(device).eval()
            processor = AutoProcessor.from_pretrained(model_path)
        
        print("Procesando la imagen y el texto...")
        prompt = text_input
        model_inputs = processor(text=prompt, images=image, return_tensors="pt").to(device)
        input_len = model_inputs["input_ids"].shape[-1]

        print("Generando texto...")
        with torch.no_grad():
            generation = model.generate(**model_inputs, max_new_tokens=100, do_sample=False)
            generation = generation[0][input_len:]
            decoded = processor.decode(generation, skip_special_tokens=True)
        
        print("Proceso completado.")
        return decoded

    def process_image(image_path, text_input):
        print("Cargando la imagen...")
        image = Image.open(image_path).convert("RGB")

        global model, processor
        if model is None or processor is None:
            model_path = "Model"
            token = "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"
            model = PaliGemmaForConditionalGeneration.from_pretrained(model_path, use_auth_token=token).to(device).eval()
            processor = AutoProcessor.from_pretrained(model_path)

        print("Procesando la imagen y el texto...")
        prompt = text_input
        model_inputs = processor(text=prompt, images=image, return_tensors="pt").to(device)
        input_len = model_inputs["input_ids"].shape[-1]

        print("Generando texto...")
        with torch.no_grad():
            generation = model.generate(**model_inputs, max_new_tokens=100, do_sample=False)
            generation = generation[0][input_len:]
            decoded = processor.decode(generation, skip_special_tokens=True)
        
        print("Proceso completado.")
        return decoded
    
    @app.route('/descripcionnumeros', methods=['GET', 'POST'])
    def descripcionnumeros():
        result = None
        if request.method == 'POST':
            text_input = request.form.get('text_input', '')
            if not text_input:
                flash('No se ingresó ningún texto')
                return redirect(request.url)
            
            if 'image' not in request.files:
                flash('No se subió ninguna imagen')
                return redirect(request.url)
            
            file = request.files['image']
            if file.filename == '':
                flash('No se seleccionó ninguna imagen')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                result = process_image(filepath, text_input)
                flash('Imagen y texto procesados correctamente')
        return render_template('DescripciónNumeros.html', result=result)

    @app.route('/paligemmacamara')
    def paligemmacamara():
        return render_template('PaligemmaCamara.html')

    @app.route('/paligemma', methods=['GET', 'POST'])
    def paligemma(): 
        result = None
        if request.method == 'POST':
            text_input = request.form.get('text_input', '')
            if not text_input:
                flash('No se ingresó ningún texto')
                return redirect(request.url)
            
            if 'image' not in request.files:
                flash('No se subió ninguna imagen')
                return redirect(request.url)
            
            file = request.files['image']
            if file.filename == '':
                flash('No se seleccionó ninguna imagen')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                result = process_image(filepath, text_input)
                flash('Imagen y texto procesados correctamente')
        return render_template('Paligemma.html', result=result)
