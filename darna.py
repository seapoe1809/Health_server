##Sets up the flask server for viewing the folder locally at {ip_address}:3001
from flask import Flask, render_template, send_file, send_from_directory, session, request, redirect, jsonify, url_for, Response, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote, unquote
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import requests
import json
import webbrowser
import os, subprocess
from subprocess import run, CalledProcessError
import getpass
import variables
import qrcode
import pyzipper
from pdf2image import convert_from_path
#dicom #numpy, pydicom, matplotlib
import io
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import numpy as np
import matplotlib.pyplot as plt




app = Flask(__name__)
#app.config.update(
    #SESSION_COOKIE_SECURE=True,
    #SESSION_COOKIE_SAMESITE='None',
#)

# Initialize Flask extensions and Flask_login
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#generates a app.secret_key that is variable and encrypted
key = Fernet.generate_key()
cipher_suite = Fernet(key)
app.secret_key = cipher_suite.encrypt(os.getcwd().encode())


# Configure static folder path
app.static_folder = 'static'

# Configure the SQLAlchemy part to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Define User model, access
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def get_paths(self):
        base_path = os.getcwd()
        if self.username == 'ADMIN':
            folder_name = 'Health_files'
        elif self.username == 'USER1':
            folder_name = 'Health_files2'
        else:
            folder_name = f'Health_files_{self.username}'  # fallback

        folderpath = os.path.join(base_path, folder_name)
        APP_dir = os.path.join(base_path, 'install_module')
        ocr_files = os.path.join(folderpath, 'ocr_files')
        upload_dir = os.path.join(folderpath, 'upload')
        summary_dir = os.path.join(folderpath, 'summary')

        return {
            'HS_path': base_path,
            'folderpath': folderpath,
            'APP_dir': APP_dir,
            'ocr_files': ocr_files,
            'upload_dir': upload_dir,
            'summary_dir': summary_dir
            
        }

#importing variables from variables.py
# Label current dir and parent dir
HS_path = os.getcwd()
ip_address = variables.ip_address
APP_dir = f"{HS_path}/install_module"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


#@app.before_first_request
def create_users():
    db.create_all()
    admin = User(username='ADMIN', password=bcrypt.generate_password_hash('health').decode('utf-8'))
    user1 = User(username='USER1', password=bcrypt.generate_password_hash('wellness').decode('utf-8'))
    db.session.add(admin)
    db.session.add(user1)
    db.session.commit()
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            if username == "ADMIN":
                session['folderpath'] = f"{os.getcwd()}/Health_files"
            elif username == "USER1":
                session['folderpath'] = f"{os.getcwd()}/Health_files2"

            return redirect(url_for('protected'))
        else:
            error_message = "Password ⚠️"

    return render_template('login.html', error_message=error_message)

@app.route('/protected')
@login_required
def protected():
    return redirect(url_for('home'))

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
    
@app.route('/shutdown')
@login_required
def shutdown():
    try:
        pid = subprocess.check_output(["lsof", "-t", "-i:3001"]).decode().strip()
        if pid:  # Checks for pid
            subprocess.run(["kill", pid], check=True)
        else:
            return "No process found on port 3001."
    except subprocess.CalledProcessError:
        try:
            # If fail, attempt forceful process kill
            subprocess.run(["kill", "-9", pid], check=True)
        except subprocess.CalledProcessError as e:
            return f'Forceful kill failed: {e}', 500
    return 'Server shutting down...'
    

@app.route('/')
def home():
    if current_user.is_authenticated:
        # User is logged in
        return render_template('index.html')
    else:
        # User is not logged in
        return redirect(url_for('login'))


#making links for folder directory and files
@app.route('/folder')
@login_required
def folder_index():

    folder_path = session.get('folderpath')
    if folder_path is None:
        return "No folder path set in the session, please log in again.", 400

    files = []
    files = os.listdir(folder_path)

    file_links = []

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        is_directory = os.path.isdir(file_path)

        if is_directory:
            file_links.append({'filename': filename, 'path': f'/folder/{filename}', 'is_folder': True})
        else:
            file_links.append({'filename': filename, 'path': f'/{filename}', 'is_folder': False})

    return render_template('folder_index.html', files=file_links)

#serving files from folder directory
@app.route('/<path:filename>')
@login_required
def serve_file(filename):
    if not current_user.is_authenticated:
        return redirect('/login')
    
    folderpath = session.get('folderpath')
    decoded_filename = unquote(filename)
    return send_from_directory(folderpath, decoded_filename, as_attachment=False)

#making file links in subdirectory    
@app.route('/folder/<path:subfolder>')
@login_required
def subfolder_index(subfolder):
    
    folderpath = session.get('folderpath')
    folder_path = os.path.join(folderpath, subfolder)

    files = []
    if os.path.exists(folder_path):
        files = os.listdir(folder_path)

    file_links = []

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        is_directory = os.path.isdir(file_path)

        if is_directory:
            file_links.append({'filename': filename, 'path': f'/folder/{subfolder}/{filename}', 'is_folder': True})
        else:
            file_links.append({'filename': filename, 'path': f'/folder/{subfolder}/{filename}', 'is_folder': False})

    return render_template('folder_index.html', files=file_links)

    
@app.route('/folder/<path:subfolder>/<path:nested_subfolder>/<path:filename>')
@app.route('/folder/<path:subfolder>/<path:filename>')
@login_required
def serve_file_or_subfolder(subfolder, filename, nested_subfolder=''):
    
    folderpath = session.get('folderpath')
    folder_path = os.path.join(folderpath, subfolder, nested_subfolder)

    decoded_filename = unquote(filename)

    if os.path.isdir(os.path.join(folder_path, decoded_filename)):
        # Render subfolder index
        files = os.listdir(os.path.join(folder_path, decoded_filename))
        file_links = []

        for file in files:
            file_path = os.path.join(folder_path, decoded_filename, file)
            is_directory = os.path.isdir(file_path)

            if is_directory:
                file_links.append({'filename': file, 'path': f'/folder/{subfolder}/{nested_subfolder}/{decoded_filename}/{file}', 'is_folder': True})
            else:
                file_links.append({'filename': file, 'path': f'/folder/{subfolder}/{nested_subfolder}/{decoded_filename}/{file}', 'is_folder': False})

        return render_template('folder_index.html', files=file_links)
    else:
        # Serve file
        return send_from_directory(folder_path, decoded_filename, as_attachment=False)

"""
@app.route('/summary')
@login_required
def summary():
    return render_template('summary.html')
    """

@app.route('/zip_summary', methods=['POST'])
@login_required
def zip_summary():
    folderpath = session.get('folderpath')
    folder = folderpath
    zip_password = '2023'.encode('utf-8')  # CHANGE PASSWORD TO YOUR CHOICE HERE FOR ZIP ENCRYPT
    folder_to_zip = f'{folder}/summary'
    zip_filename = f'{folder}/my_summary.zip'

    try:
        with pyzipper.AESZipFile(zip_filename,
                                'w',
                                compression=pyzipper.ZIP_DEFLATED,
                                encryption=pyzipper.WZ_AES) as zipf:
            zipf.setpassword(zip_password)
            for root, _, files in os.walk(folder_to_zip):
                for file in files:
                    zipf.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               folder_to_zip))
        return render_template('success.html', message="ZIP file created and encrypted.")
    except Exception as e:
        return render_template('error.html', message=str(e))

#The Following 3 sections are removed in ver 2.2 as sudo in app is security risk    
"""
@app.route('/launch-program')
@login_required
def launch_program():
    return redirect('/sudopwd')

@app.route('/sudopwd', methods=['GET', 'POST'])
@login_required
def sudopwd():
    if request.method == 'POST':
        password1 = request.form['sudopwd']

        # Set the sudo password in the session
        session['sudopwd'] = password1

        return redirect('/execute-command')

    return render_template('sudopwd.html')

@app.route('/execute-command')
@login_required
def execute_command():
    if 'sudopwd' not in session:
        return redirect('/sudopwd')

    command1 = ['sudo', '-S', 'rsync', '-avz', '--chmod=750']
    
    folderpath = session.get('folderpath')
    upload_dir = os.path.join(folderpath, 'upload')        
    source_dir = upload_dir
    destination_dir1 = os.path.join(folderpath, 'ocr_files')
    destination_dir2 = folderpath
    destination_dir3 =  os.path.join(folderpath, 'summary')
    
    password1 = session.get('sudopwd', '')
    
        
    #Step1 Rsyncing files to parent directory Health_files except ones beginning with HL_, fist code to execute
    command1_all_files = ['sudo', '-S', 'rsync', '-avz', '--chmod=750', '--exclude=HL_*', f"{upload_dir}/", f"{folderpath}/"]
    try:
        process_all_files_sync=subprocess.Popen(
           command1_all_files,
           stdin=subprocess.PIPE,
           stdout=subprocess.PIPE,
           universal_newlines=True
        )
        output, error = process_all_files_sync.communicate(input=password1 + '\n')
        if process_all_files_sync.returncode != 0:
            return "Unable to run due to non-superuser status!"
    except subprocess.CalledProcessError as e:
        return "Error occurred while indexing files in the upload directory."
    
    # Function to execute rsync command
    def run_rsync(command, password):
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            output, error = process.communicate(input=password + '\n')

            if process.returncode != 0:
                print("Unable to run due to non-superuser status!")
            else:
                print("Synchronization successful!")
            
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running rsync command: {str(e)}")
        
    files_to_rsync_for_summary = []
    files_to_rsync_for_ocr = []

    # Step 2 and Step 3 combined rsync to ocr_files and summary folder
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isfile(file_path):
            if filename.startswith('HL_'):
                files_to_rsync_for_summary.append(file_path)

                if any(filename.endswith(ext) for ext in ['.pdf', '.png', '.jpg', '.txt', '.jpeg']):
                    files_to_rsync_for_ocr.append(file_path)
   

    # Rsync files for /summary directory
    if files_to_rsync_for_summary:
        command1 = ['sudo', '-S', 'rsync', '-avz', '--chmod=750']
        command1.extend(files_to_rsync_for_summary)
        command1.append(destination_dir3)
        run_rsync(command1, password1)
    else:
        print("No files to synchronize for /summary!")

    # Rsync files for ocr_files directory
    if files_to_rsync_for_ocr:
        command1 = ['sudo', '-S', 'rsync', '-avz', '--chmod=750']
        command1.extend(files_to_rsync_for_ocr)
        command1.append(destination_dir1)
        run_rsync(command1, password1)
    else:
        print("No files to synchronize for ocr_files!")
   
   
        
    #Step 4 running caffeine to keep computer awake
    command2 = ['caffeine']
    #command2a = ['gsettings set org.gnome.desktop.session idle-delay 600']

    try:
        process2 = subprocess.Popen(command2)
    except subprocess.CalledProcessError as e:
        return "Error occurred while running caffeine."
    #try:
        #process2a = subprocess.Popen(command2a)
    #except subprocess.CalledProcessError as e:
        #print("Error occurred while running gsettings.")
    
    #Step 5 setting up to run apple health grafana
    command3 = ['sudo', '-S', 'docker-compose', '-f', 'apple-health-grafana/docker-compose.yml', '-p', 'apple-health-grafana', 'pull']
    command4 = ['sudo', '-S', 'docker-compose', '-f', 'apple-health-grafana/docker-compose.yml', '-p', 'apple-health-grafana', 'up', '-d', 'grafana', 'influx']
    command5 = ['sudo', '-S', 'docker-compose', '-f', 'apple-health-grafana/docker-compose.yml', '-p', 'apple-health-grafana', 'up', 'ingester']
    

    try:
        export_zip_path = os.path.join(source_dir, 'export.zip')
        if os.path.isfile(export_zip_path):
            process3 = subprocess.Popen(
                command3,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True
            )
            output, error = process3.communicate(input=password1 + '\n')

            process4 = subprocess.Popen(
                command4,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True
            )
            output, error = process4.communicate(input=password1 + '\n')

            process5 = subprocess.run(command5, check=True)
            

    except subprocess.CalledProcessError as e:
        return "Error occurred while running Grafana Docker commands."
     
    #running command 6 to clear files in upload dir
    command6 = f'rm -rf {source_dir}/*'
    try:
        process6 = subprocess.run(command6, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        return "Error occurred while clearing files in the upload directory."
    return render_template('success.html', success_message='"Programs launched successfully! Clearing files in the upload directory."')
"""

#the following are to chart your medications and past medical history in fhir format
@app.route('/chart')
@login_required
def chart():
    chart_json_url = url_for('custom_static', filename='chart.json')
    #vitals_json_url = url_for('custom_static', filename='vitals.json')
    return render_template('chart.html', chart_json_url=chart_json_url)


  
@app.route('/save-edits', methods=['POST'])
@login_required
def save_edits():
    folderpath = session.get('folderpath', '')
    destination_dir3 = os.path.join(folderpath, 'summary')
    file_path = os.path.join(destination_dir3, 'chart.json')
    updatedData = request.json  # Get the updated data from the request
    try:
        with open(file_path, 'w') as jsonFile:
            json.dump(updatedData, jsonFile, indent=4)
        return jsonify({"status": "success", "message": "Data saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500 

#Portal access viewer in Sky        
@app.route('/pabv')
def pabv():
    if current_user.is_authenticated:
        # User is logged in
        return render_template('pabv.html')
    else:
        # User is not logged in
        return redirect(url_for('login'))   

#Launches the darnabot with user ID
@app.route('/gradio_user')
@login_required
def gradio_user():
    user_id = current_user.id  # Get the user's ID
    current_ip = request.host.split(':')[0]  # Extract the IP part from the host
    return redirect(f"http://{current_ip}:3012?user={user_id}")
           


# Keep the original custom_static function 
@app.route('/custom_static/<filename>')
@login_required
def custom_static(filename):
    folderpath = session.get('folderpath', '')
    directory = os.path.join(folderpath, 'summary')
    return send_from_directory(directory, filename)

#view dicom files in Health files    
@app.route('/summary/', methods=['GET'])
@login_required
def dicom_files():
    folderpath = session.get('folderpath', '')
    directory = os.path.join(folderpath, 'summary')

    # Lists to store file names
    pdf_files = []
    xml_files = []
    dicom_files = []

    # Scan directory and categorize files by extension
    for f in os.listdir(directory):
        if f.lower().endswith(('.pdf', '.PDF')):
            pdf_files.append(f)
        elif f.lower().endswith(('.xml', '.XML')):
            xml_files.append(f)
        elif f.lower().endswith(('.dcm', '.dicom', '.DCM')):
            dicom_files.append(f)

    # Pass the lists to the template
    print(pdf_files)
    print(dicom_files)
    return render_template('summary.html', pdf_files=pdf_files, xml_files=xml_files, dicom_files=dicom_files)


@app.route('/summary/<filename>')
@login_required
def display_file(filename):
    folderpath = session.get('folderpath', '')
    directory = os.path.join(folderpath, 'summary')
    file_path = os.path.join(directory, filename)

    # Handle DICOM files
    if filename.lower().endswith(('.dcm', '.dicom', '.DCM')):
        # Load the DICOM file to compute max_slice
        dicom_data = pydicom.dcmread(file_path)
        
        # Ensure it's a multi-dimensional dataset to calculate max_slice
        if dicom_data.pixel_array.ndim > 2:
            max_slice = dicom_data.pixel_array.shape[0] - 1
        else:
            max_slice = 0  # Handle single-slice (2D) DICOM images as well

        return render_template('view_dicom.html', filename=filename, max_slice=max_slice)

    # Directly serve PDF files
    if filename.lower().endswith('.pdf'):
        return send_from_directory(directory, filename, mimetype='application/pdf')

    # Directly serve XML files
    elif filename.lower().endswith('.xml'):
        return send_from_directory(directory, filename, mimetype='application/xml')

    # Fallback for unsupported file types
    return 'Unsupported file type', 404



@app.route('/dicom/slice/<filename>/<int:slice_index>')
@login_required
def serve_dicom_slice(filename, slice_index):
    folderpath = session.get('folderpath', '')
    directory = os.path.join(folderpath, 'summary')
    dicom_file_path = os.path.join(directory, filename)
    
    dicom_data = pydicom.dcmread(dicom_file_path)
    image_3d = apply_voi_lut(dicom_data.pixel_array, dicom_data)
    
    # Selecting the requested slice
    try:
        image_slice = image_3d[slice_index]
    except IndexError:
        return "Slice index out of range", 400
    
    # Normalize and convert to uint8
    image_slice = np.interp(image_slice, (image_slice.min(), image_slice.max()), (0, 255))
    image_slice = image_slice.astype(np.uint8)
    
    # Convert to PNG
    buf = io.BytesIO()
    plt.imsave(buf, image_slice, cmap='gray', format='png')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')  
          
"""
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file_type = request.form['Type']
        file = request.files['File']
        
        if file:
            filename = file.filename
            
            if file_type == 'HL_File':
                filename = f'HL_{filename}'
            
            folderpath = session.get('folderpath')        
            upload_dir = os.path.join(folderpath, 'upload')
            file_path = os.path.join(upload_dir, filename)
            
            # Save the file temporarily
            file.save(file_path)
            
            try:
                # Run clamscan on the uploaded file
                result = subprocess.run(['clamscan', '-r', file_path], capture_output=True, text=True, check=True)
                
                if "Infected files: 0" in result.stdout:
                    return render_template('success.html')
                else:
                    os.remove(file_path)  # Remove the infected file
                    return render_template('upload.html', message='File is infected!')
                    
            except subprocess.CalledProcessError:
                print("clamscan found an infected file.")
                os.remove(file_path)  # Remove the infected file
                return render_template('upload.html', message='File is infected!')
                
            except Exception as e:
                # This block will be executed if clamscan is not available
                print(f"An error occurred. Clamscan is not available: {e}")
                return render_template('success.html')  # Ignore the scan if clamscan is not available

    return render_template('upload.html')
"""

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    folderpath = session.get('folderpath', '')
    destination_dir1 = os.path.join(folderpath, 'ocr_files')
    upload_dir = os.path.join(folderpath, 'upload')
    destination_dir3 = os.path.join(folderpath, 'summary')

    if request.method == 'POST':
        file_type = request.form.get('Type')
        file = request.files.get('File')

        if file:
            filename = file.filename
            file_path1 = os.path.join(destination_dir1 if file_type == 'HL_File' else folderpath, filename)
            file.save(file_path1)  # Save the file temporarily

            try:
                # Run clamscan on the uploaded file
                result = subprocess.run(['clamscan', '-r', file_path1], capture_output=True, text=True, check=True)

                if "Infected files: 0" in result.stdout:
                    if file_type == 'HL_File':
                        file_path2 = os.path.join(destination_dir3, filename)
                        # Use subprocess to copy the file
                        if os.name == 'posix':  # Unix-based system
                            subprocess.run(['cp', file_path1, file_path2], check=True)
                        elif os.name == 'nt':  # Windows
                            subprocess.run(['copy', file_path1, file_path2], shell=True, check=True)
                    return render_template('success.html')
                else:
                    os.remove(file_path1)  # Remove the infected file
                    return render_template('upload.html', message='File is infected!')

            except subprocess.CalledProcessError as e:
                print(f"An error occurred during file operation: {e}")
                os.remove(file_path1)  # Ensure the source file is removed in case of error
                return render_template('upload.html', message='An error occurred during file processing!')

            except Exception as e:
                print(f"An error occurred: {e}")
                if file_type == 'HL_File':
                    file_path2 = os.path.join(destination_dir3, filename)
                    # Use subprocess to copy the file
                    if os.name == 'posix':  # Unix-based system
                        subprocess.run(['cp', file_path1, file_path2], check=True)
                    elif os.name == 'nt':  # Windows
                        subprocess.run(['copy', file_path1, file_path2], shell=True, check=True)
                return render_template('success.html')  # Proceed if ClamAV scan is not performed

    return render_template('upload.html')

@app.route('/connect_nc')
@login_required
def connect_nc():
    url = request.remote_addr
    client_ip = request.remote_addr
    if url == '127.0.0.1':
        url = f"http://{ip_address}:3001"  
    else:
        url = f"http://{url}:3001"
    print(url)
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    image = qr.make_image()
    image.save(f'{HS_path}/static/qrcode.png')
    return render_template('connect_nc.html')
 
#update password in connect_nc   
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        # Get the new password from the form
        new_password = request.form['password']
        
        # Hash the new password
        hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Look up the current user in your database
        user = User.query.filter_by(username=current_user.username).first()
        
        if user:
            # Update the password in the database
            user.password = hashed_new_password
            db.session.commit()
            
            flash('Password change successful. You can now log in.')
            return redirect(url_for('login'))
        else:
            flash('Error: User not found.')
            return redirect(url_for('register'))

    return render_template('register.html')
   

@app.route('/pi')
@login_required
def pi():
    with open('install_module/templates/index2.html', 'r') as f:
        content = f.read()
    return Response(content, content_type='text/html')
        
@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():

    if request.method == 'POST':
        age = request.form['age']
        sex = request.form['sex']
        ignore_words = request.form['ignore-words']
        print(f"Age: {age}")
        print(f"Sex: {sex}")
        print(f"Ignore Words: {ignore_words}")
        formatted_ignore_words = ignore_words.replace(' ', '|')

        content = f"age = '{age}'\nsex = '{sex}'\nignore_words = '{formatted_ignore_words}'\n"
        file_path = f"{HS_path}/variables2.py"

        try:
            with open(file_path, 'w') as file:
                file.write(content)
        except Exception as e:
            print(f"Error writing to variables2.py: {str(e)}")
            return str(e)

        # Run the analyze script asynchronously using nohup and pass session cookie
        folderpath = session.get('folderpath')
        env_vars = os.environ.copy()
        env_vars['FOLDERPATH'] = folderpath
        command = f'nohup python3 {HS_path}/analyze.py > /dev/null 2>&1 &'
        #subprocess.Popen(command, shell=True, env=env_vars)
        print("Process time is 3 minutes")
        try:
            subprocess.Popen(command, shell=True, env=env_vars)
        except Exception as e:
            print(f"Error running analyze.py: {str(e)}")
            return str(e)

        return render_template('success.html', message="Process time is 3 minutes")

    return render_template('analyze.html', submitted=True)


    
@app.route('/install_module/<path:filename>')
@login_required
def serve_install_module(filename):
    return send_from_directory('install_module', filename)
     
@app.route('/install')
@login_required
def install():
    print("Inside /install")
    app_name_file = request.args.get('app_name_file') + '.js'
    app_folder = request.args.get('app_folder')
    session['app_name_file']= app_name_file
    app_name = session.get('app_name_file', '').replace('.js', '')
    
    print(f"Session variables: {session}")

    # Additional logic to process the app_name_file and app_folder if needed
    return render_template('install.html', app_name_file=app_name_file, app_folder=app_folder)


@app.route('/execute_script', methods=['GET', 'POST'])
@login_required
# executes the install script
def execute_script():
    try:
        print("Inside /execute_script")
        app_name = session.get('app_name_file', '').replace('.js', '')
        if not app_name:
            return jsonify(success=False, error="Missing app_name")

        app_name_file = session['app_name_file']
        # import ip_address from variables and pass to env_var to install app_name
        app_name = request.json.get('app_name')
        url = f"http://{ip_address}"
        env_vars = os.environ.copy()
        env_vars['URL'] = url

        cmd = ['python3', f'install_module/{app_name}/{app_name}.py']
        proc = subprocess.Popen(cmd, env=env_vars, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = proc.communicate()

        if proc.returncode == 0:
            return jsonify(success=True, message="Please Refresh App")
        else:
            print(f'Subprocess output: {stdout}')
            print(f'Subprocess error: {stderr}')
            return jsonify(success=False, error="Non-zero return code")

        print(f"Session variables: {session}")

    except Exception as e:
        return jsonify(success=False, error=str(e))

 
@app.errorhandler(404)
@login_required
def page_not_found(error):
    print("Error 404 Encountered")
    return render_template('errors.html', error_message='Page not found'), 404

        
if __name__== '__main__':
    app.run('0.0.0.0', port=3001)
    print("server is running at http://localhost:3001")
