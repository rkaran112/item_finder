from flask import Flask, render_template_string, request, send_file, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from agent import process_excel

app = Flask(__name__)
app.secret_key = "super_secret_key_for_flash_messages" # Needed for flash messages
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Search Agent</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; color: #333; margin: 0; padding: 40px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { text-align: center; color: #2c3e50; }
        p { text-align: center; color: #7f8c8d; line-height: 1.6; }
        form { display: flex; flex-direction: column; gap: 20px; margin-top: 30px; }
        .file-upload-wrapper { border: 2px dashed #bdc3c7; padding: 40px; text-align: center; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
        .file-upload-wrapper:hover { border-color: #3498db; background-color: #f7f9fa; }
        input[type="file"] { display: none; }
        .custom-file-upload { display: inline-block; padding: 8px 15px; cursor: pointer; background-color: #ecf0f1; border-radius: 5px; border: 1px solid #bdc3c7; }
        button { background-color: #3498db; color: white; border: none; padding: 15px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; transition: background-color 0.3s; font-weight: bold; }
        button:hover { background-color: #2980b9; }
        .alert { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-top: 20px; display: flex; flex-direction: column; align-items: center; gap: 15px;}
        .alert-error { background-color: #f8d7da; color: #721c24; }
        .download-btn { background-color: #27ae60; text-decoration: none; display: inline-block; text-align: center;}
        .download-btn:hover { background-color: #2ecc71; }
        #file-name { margin-top: 10px; font-size: 14px; color: #34495e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Product Search Agent</h1>
        <p>Upload your Excel file to find product links on Amazon and Flipkart automatically based on the GeM Brand, GeM Model, and GeM Title.</p>
        
        <form action="/process" method="POST" enctype="multipart/form-data">
            <label class="file-upload-wrapper" id="drop-zone">
                📁 Click here to select your Excel file (.xlsx)
                <input type="file" name="file" accept=".xlsx" id="file-input" required onchange="document.getElementById('file-name').innerText = this.files[0].name">
                <div id="file-name"></div>
            </label>
            <button type="submit">Start Search</button>
        </form>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert {% if category == 'error' %}alert-error{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% if output_file %}
            <div class="alert">
                🎉 Processing complete!
                <a href="/download/{{ output_file }}" class="download-btn"><button class="download-btn">📥 Download Excel Results</button></a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        flash('No file part provided.', 'error')
        return redirect(url_for('index'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('index'))
        
    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run our automated agent
        output_file = process_excel(filepath)
        
        if output_file:
            return render_template_string(HTML_TEMPLATE, output_file=output_file)
        else:
            flash('Error processing file. Please check the Excel format according to the documentation.', 'error')
            return redirect(url_for('index'))
    else:
        flash('Invalid file format. Please upload an .xlsx file.', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("Starting HTML Visualizer...")
    print("Local URL: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
