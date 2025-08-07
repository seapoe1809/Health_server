#/* DARNA.HI
# * Copyright (c) 2023 Seapoe1809   <https://github.com/seapoe1809>
# * Copyright (c) 2023 pnmeka   <https://github.com/pnmeka>
# * 
# *
# *   This program is free software: you can redistribute it and/or modify
# *   it under the terms of the GNU General Public License as published by
# *   the Free Software Foundation, either version 3 of the License, or
# *   (at your option) any later version.
# *
# *   This program is distributed in the hope that it will be useful,
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *   GNU General Public License for more details.
# *
# *   You should have received a copy of the GNU General Public License
# *   along with this program. If not, see <http://www.gnu.org/licenses/>.
# */
#uses chromaminer to chunk and embed and then uses function to extract relevant component
import os, subprocess
import re
import json
import random
import requests
import gradio as gr
import chromadb
import sqlite3
import base64
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
import threading
from threading import local
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
from PIL import Image
import io
from ollama import AsyncClient
import asyncio
####NEW
#install pytesseract
#install pdf2image pip install reportlab PyPDF2 nltk wordcloud unidecode
#pdfplumber ollama

#from transformers import pipeline
#set model
model="gemma3:4b"
directory = ""
folderpath= ""
basic_info=""




conversation_memory = []

async def chat(messages):

     async for part in await AsyncClient().chat(model=f'{model}', messages=messages, stream=True):
         chunk=part['message']['content']
         yield chunk


#this truncates the words for use by Chroma to build context
def truncate_words(documents):
    truncated_documents = []
    for doc in documents:
        doc=str(doc)
        words = doc.split()[:300]  # Truncate to 300 words
        truncated_documents.append(' '.join(words))
    return truncated_documents

def generate_context_and_sources(
    query: str, 
    collection_name: str = "documents_collection", 
    persist_directory: str = "chroma_storage"
) -> (str, str):
    print(persist_directory)
    context, sources = "No data available", "No sources available."
    try:
        # Check if persist_directory exists; if not
        if not os.path.exists(persist_directory):
            print(f"Directory '{persist_directory}' does not exist. Skipping.")
            return context, sources

        chroma_client = chromadb.PersistentClient(path=persist_directory)
        collection = chroma_client.get_collection(name=collection_name)

        results = collection.query(query_texts=[query], n_results=3, include=["documents", "metadatas"])
        sources = "\n".join(
            [
                f"{result.get('filename', 'Unknown filename')}: batch {result.get('batch_number', 'Unknown batch')}"
                for result in results["metadatas"][0]  # type: ignore
            ]
        )
        truncated_documents = truncate_words(results["documents"])
        context = "".join(truncated_documents)

    except Exception as e:
        print(f"Error accessing collection or processing query: {e}")
    return context, sources

#set global directory
def set_user_directory(request: gr.Request):
    global directory
    referer= request.headers.get('referer')
    if "user=1" in referer:
        # Admin user
        directory = "../Health_files/ocr_files/Darna_tesseract/"
    elif "user=2" in referer:
        # Non-admin user
        directory = "../Health_files2/ocr_files/Darna_tesseract/"
    else:
        # Handle unexpected user types
        directory = "/"
    print(f"Current ocr directory: {directory}")
    
def set_user_health_files_directory(request: gr.Request):
    global folderpath
    referer= request.headers.get('referer')
    if "user=1" in referer:
        # Admin user
        folderpath = "../Health_files/"
    elif "user=2" in referer:
        # Non-admin user
        folderpath = "../Health_files2/"
    else:
        # Handle unexpected user types
        folderpath = "/"
    print(f"Current folderpath: {folderpath}")
    
       
#function to ananlyze the input query using re and make some assessment on where to get context
def analyze_query(query, directory):
    #pattern for keyword
    darna_pattern = r'(?:darnahi|darna|server|hello)\s*[:=]?\s*'
    darna_match = re.search(darna_pattern, query, re.IGNORECASE)
    darna_value = darna_match.group().strip() if darna_match else None
    
    med_pattern = r'(?:meds|medication|medications|medicine|medicine|drug|drugs)\s*[:=]?\s*'
    med_match = re.search(med_pattern, query, re.IGNORECASE)
    med_value = med_match.group().strip() if med_match else None
    
    summary_pattern = r'(?:medical|clinical|advice|advise|weight|diet)\s*[:=]?\s*'
    summary_match = re.search(summary_pattern, query, re.IGNORECASE)
    summary_value = summary_match.group().strip() if summary_match else None
    
    past_medical_history_pattern = r'(?:history|procedure|procedures|surgery|pastmedical|pmh|past-medical|past-history)\s*[:=]?\s*'
    past_medical_history_match = re.search(past_medical_history_pattern, query, re.IGNORECASE)
    past_medical_history_value = past_medical_history_match.group().strip() if past_medical_history_match else None
    
    xmr_pattern = r'(?:monero|xmr|crypto|cryptocurrency|privacy|XMR|MOnero)\s*[:=]?\s*'
    xmr_match = re.search(xmr_pattern, query, re.IGNORECASE)
    xmr_value = xmr_match.group().strip() if xmr_match else None
    
    json_file_path= f'{directory}/wordcloud_summary.json'
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
                existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}
    
    result = ""
    if darna_value is not None:
        print(darna_value)
        key='darnahi'
        result += existing_data.get(key, " ")[:200]
    if med_value is not None:
        print(med_value)
        key = 'darnahi_medications'
        result += existing_data.get(key, " ")[:500]
    if summary_value is not None:
        print(summary_value)
        key = 'darnahi_summary'
        result += existing_data.get(key, "No data found for 'summary' key.")[:350]
    if past_medical_history_value is not None:
        print(past_medical_history_value)
        key = 'darnahi_past_medical_history'
        result += existing_data.get(key, " ")[:500]  
    if xmr_value is not None:
        print(xmr_value)
        key = 'darnahi_xmr'
        result += existing_data.get(key, " ")[:200]

     # Check if no pattern matched
    if not (darna_match or med_match or summary_match or xmr_match or past_medical_history_match):
    
        collection_name="documents_collection"
        context, sources = generate_context_and_sources(query, collection_name, os.path.join(directory, 'chroma_storage'))

        print(context, sources)
        result = context[:150]
    if result is None:
        result={''}
   
    print(result)
    return result


    
#generate a chat function using the query and context
async def my_function(query, request: gr.Request, chat_history):
    #pass userID
    global conversation_memory    
    history ="<history>\n".join(conversation_memory)
    if len(history) > 300:
        history = history[-400:]
    
    print(history)
    referer= request.headers.get('referer')
    if "user=2" in referer:
        #non admin user
        directory="../Health_files2/ocr_files/Darna_tesseract/"
        print(directory)
    elif "user=1" in referer:
        #admin
        directory="../Health_files/ocr_files/Darna_tesseract/"
        print(directory)
    else:
        directory="/"
        print("default dir")
        
    #chroma rag
    context=analyze_query(query, directory)
    context=f'<context>{context}</context>'

    messages = [
        {"role": "user", "content": "You are Darnabot. End with a followup"},
        {"role": "assistant", "content": "I am 'Darnabot', AI health assistant with domain expertise. How can I help?"},
        {"role": "user", "content": f"'Darnabot' answer query: {query} using context: {context}. Also here is history of previous conversation with user but ignore if not relevant to query: {history}"},
        ]

    
    
    full_response=""
    async for content in chat(messages):
        full_response += content
        yield chat_history + [(query, full_response)]
        

    conversation_memory.append(f"<history> {full_response}</history>")
    conversation_memory = conversation_memory[-4:]

def clear_conversation():
    global conversation_memory
    conversation_memory = []
    gr.ClearButton([msg, chatbot])
    return "", None

################################
"""
#run ai to analyze records
#from analyze  import *
import logging
import json
import subprocess
from typing import List, Tuple

def stepwise_error_handling_analyze(deidentify_words, folderpath: str, ocr_files: str, age: int, sex: str) -> List[Tuple[str, str]]:
    logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    steps = [
        ("Extract and write LForms data", lambda: extract_and_write_lforms_data(folderpath)),
        ("Process OCR files", lambda: process_ocr_files(ocr_files)),
        ("Collate images", lambda: collate_images(ocr_files, f"{ocr_files}/Darna_tesseract")),
        ("Deidentify records", deidentify_records(ocr_files, deidentify_words)),
        ("Generate recommendations", lambda: generate_recommendations(folderpath, age=age, sex=sex)),
        ("Process PDF files", lambda: process_pdf_files(ocr_files)),
        ("Process directory summary", lambda: process_directory_summary(ocr_files, ['HPI', 'history', 'summary'])),
        ("Create wordcloud", lambda: preprocess_and_create_wordcloud(process_directory_summary(ocr_files, ['HPI', 'history', 'summary']), f'{ocr_files}/Darna_tesseract/')),
        ("Process directory meds", lambda: process_directory_meds(ocr_files, ['medications', 'MEDICATIONS:', 'medicine', 'meds'])),
        ("Load screening text", lambda: load_text_from_json_screening(f'{ocr_files}/Darna_tesseract/combined_output.json', ['RECS', 'RECOMMENDATIONS'])),
        ("Process directory PMH", lambda: process_directory_pmh(ocr_files, ['PMH', 'medical', 'past medical history', 'surgical', 'past'])),
        ("Generate wordcloud summary", lambda: wordcloud_summary(
            ("darnahi_summary", "darnahi_past_medical_history", "darnahi_medications", "darnahi_screening"),
            (process_directory_summary(ocr_files, ['HPI', 'history', 'summary']),
             process_directory_pmh(ocr_files, ['PMH', 'medical', 'past medical history', 'surgical', 'past']),
             process_directory_meds(ocr_files, ['medications', 'MEDICATIONS:', 'medicine', 'meds']),
             load_text_from_json_screening(f'{ocr_files}/combined_output.json', ['RECS', 'RECOMMENDATIONS'])),
            f'{ocr_files}/Darna_tesseract/'
        )),
        #("Chromadb embed", lambda: chromadb_embed(ocr_files)),
        #("Clean up directory", lambda: subprocess.run(f'find {ocr_files} -maxdepth 1 -type f -exec rm {{}} +', shell=True))
    ]
    
    results = []
    
    for step_name, step_function in steps:
        try:
            step_function()
            results.append((step_name, "Success"))
        except Exception as e:
            error_message = f"Error in {step_name}: {str(e)}"
            logging.error(error_message)
            results.append((step_name, f"Error: {str(e)}"))
    
    return results

def extract_and_write_lforms_data(folderpath: str):
    with open(f'{folderpath}/summary/chart.json', 'r') as file:
        json_data = json.load(file)
        
    extracted_info = extract_lforms_data(json.dumps(json_data))
    json_output = json.dumps(extracted_info, indent=4)
    write_text_to_pdf(folderpath, str(extracted_info))
    with open(f'{folderpath}/ocr_files/fhir_output.json', 'w', encoding='utf-8') as f:
        f.write(json_output)

"""

def extract_lforms_data(json_data):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    extracted_info = {
        "date_of_birth": None,
        "sex": None,
        "allergies": [],
        "past_medical_history": [],
        "medications": []
    }

    for item in data.get("items", []):
        if item.get("question") == "ABOUT ME":
            for subitem in item.get("items", []):
                if subitem.get("question") == "DATE OF BIRTH":
                    extracted_info["date_of_birth"] = subitem.get("value")
                elif subitem.get("question") == "BIOLOGICAL SEX":
                    extracted_info["sex"] = subitem.get("value", {}).get("text")
        
        elif item.get("question") == "ALLERGIES":
            for allergy_item in item.get("items", []):
                if allergy_item.get("question") == "Allergies and Other Dangerous Reactions":
                    for subitem in allergy_item.get("items", []):
                        if subitem.get("question") == "Name" and "value" in subitem:
                            value = subitem["value"]
                            if isinstance(value, dict):
                                allergy_text = value.get("text")
                            else:
                                allergy_text = value
                            if allergy_text:
                                extracted_info["allergies"].append(allergy_text)
        
        elif item.get("question") == "PAST MEDICAL HISTORY:":
            for condition_item in item.get("items", []):
                if condition_item.get("question") == "PAST MEDICAL HISTORY" and "value" in condition_item:
                    condition = extract_condition(condition_item)
                    if condition:
                        extracted_info["past_medical_history"].append(condition)                  
        
        elif item.get("question") == "MEDICATIONS:":
            medication = {}
            for med_item in item.get("items", []):
                if med_item.get("question") == "MEDICATIONS":
                    medication["name"] = extract_med_value(med_item)
                elif med_item.get("question") == "Strength":
                    medication["strength"] = extract_med_value(med_item)
                elif med_item.get("question") == "Instructions":
                    medication["instructions"] = extract_med_value(med_item)
            if medication:
                extracted_info["medications"].append(medication)

    return extracted_info


def extract_condition(condition_item):
    if isinstance(condition_item.get("value"), dict):
        return condition_item["value"].get("text", "")
    elif isinstance(condition_item.get("value"), str):
        return condition_item["value"]
    return ""
    
def extract_med_value(med_item):
    if "value" not in med_item:
        return ""
    value = med_item["value"]
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return value.get("text", "")
    return ""


##run analyze located in ../dir
def analyze(request: gr.Request, deidentify_words):
    set_user_health_files_directory(request)
    if not folderpath:
        print("folderpath value is empty. Skipping.")
        return
    # Set up environment variables
    env_vars = os.environ.copy()
    env_vars['FOLDERPATH'] = folderpath
    if deidentify_words:
        content = f"\nignore_words = '{deidentify_words}'\n"
        file_path_variables2 = "../variables/variables2.py"
        try:
            with open(file_path_variables2, 'a') as file:
                file.write(content)
            print(f"Successfully appended deidentify_words to {file_path_variables2}")
        except IOError as e:
            error_message = f"IOError writing to variables2.py: {str(e)}"
            print(error_message)
            return error_message
        except Exception as e:
            error_message = f"Unexpected error writing to variables2.py: {str(e)}"
            print(error_message)
            return error_message
    # Get the absolute path to the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Set up the paths
    venv_dir = os.path.abspath(os.path.join(current_dir, '..', 'darnavenv'))
    venv_python = os.path.join(venv_dir, 'bin', 'python3.10')
    analyze_script = os.path.abspath(os.path.join(current_dir, '..', 'analyze.py'))

    command = [venv_python, analyze_script]

    try:
        result = subprocess.run(command, env=env_vars, check=True, text=True, capture_output=True)
        print("Running Analyzer output:", result.stdout)
        return "🟢 Analysis completed successfully"
    except subprocess.CalledProcessError as e:
        print("Error running analyze.py:", e)
        print("Error output:", e.stderr)
    
        
##fetch age/sex in analyze module    
def fetch_age_sex(request: gr.Request):
    set_user_health_files_directory(request)
    if not folderpath:
        print("Directory value is empty. Skipping.")
        return None, None, gr.update(visible=False), gr.update(visible=False)
    
    ocr_files = f"{folderpath}/ocr_files"
    try:
        with open(f'{folderpath}/summary/chart.json', 'r') as file:
            json_data = json.load(file)
        
        extracted_info = extract_lforms_data(json.dumps(json_data))
        sex = extracted_info.get('sex', None)
        dob_str = extracted_info.get('date_of_birth', None)
        
        age = None
        if dob_str is not None:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - dob.year
                
                # Adjust age if birthday hasn't occurred this year
                if (today.month, today.day) < (dob.month, dob.day):
                    age -= 1
            except ValueError as e:
                print(f"Error parsing date: {e}")
        
        # Check if both age and sex are not None
        if age is not None and sex is not None:
            content = f"age = '{age}'\nsex = '{sex}'\n"
            file_path_variables2 = f"../variables/variables2.py"
            try:
                with open(file_path_variables2, 'w') as file:
                    file.write(content)
            except Exception as e:
                print(f"Error writing to variables2.py: {str(e)}")
                return None, None, gr.update(visible=False), gr.update(visible=False)
           
            return f"Age: {age}\n Sex: {sex}\n", "🟢 Ready to analyze", gr.update(visible=True), gr.update(visible=True)
        else:
            return None, "🔴 Please update your age and sex in Darnahi Chartit", gr.update(visible=False), gr.update(visible=False)
            
    except Exception as e:
        return None, f"An error occurred: {str(e)}", gr.update(visible=False), gr.update(visible=False)




    
####AI File server
def list_files(directory):
    files = []
    try:
        # List files in the main directory
        files.extend([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        
        # List files in the AI wordcloud subdirectory
        wordcloud_dir = os.path.join(directory, "wordclouds")
        if os.path.isdir(wordcloud_dir):
            wordcloud_files = [os.path.join("wordclouds", f) for f in os.listdir(wordcloud_dir) if os.path.isfile(os.path.join(wordcloud_dir, f))]
            files.extend(wordcloud_files)
        
        return files
    except OSError as e:
        #print(f"Pick a directory to list {directory}: {e}")
        return []

def display_file(filename):
    if not filename or isinstance(filename, gr.components.Dropdown):
        return None, None

    try:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return None, file_path
            else:
                with open(file_path, 'r') as file:
                    content = file.read()
                return content, None
        else:
            print(f"File not found: {file_path}")
            return None, None
    except Exception as e:
        print(f"Error displaying file {filename}: {e}")
        return None, None

def refresh_file_list(request: gr.Request):
    #checks for RAG dir and also refreshes list of files
    set_user_directory(request)
    
    file_choices = list_files(directory)
    
    if os.path.isdir(os.path.join(directory, "chroma_storage")):
        status = "🟢 RAG database successfully setup for Darnabot User"
    else:
        status = "🔴 RAG database needs to be set up for Darnabot User"
    
    return gr.Dropdown(choices=file_choices), status
    
def update_display(filename):
    if isinstance(filename, gr.components.Dropdown):
        filename = filename.value  
    if not filename:
        return gr.update(value="No file selected", visible=True), gr.update(value=None, visible=False)
    
    content, image_path = display_file(filename)
    if image_path:
        return gr.update(value=None, visible=False), gr.update(value=image_path, visible=True)
    elif content is not None:
        return gr.update(value=content, visible=True), gr.update(value=None, visible=False)
    else:
        return gr.update(value="Error displaying file", visible=True), gr.update(value=None, visible=False)


##SYMPTOM LOGGER

# Create a thread-local storage
local = threading.local()

# Function to get and connect to relevant database connection for current thread
def get_db():
    if folderpath is None:
        print("folderpath value is empty. Skipping. Please connect to your Darnahi Account.")
        return None
    
    try:
        db_path = f"{folderpath}/summary/medical_records.db"
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None
        

def close_db():
    if hasattr(local, "db") and local.db is not None:
        local.db.close()
        local.db = None
        
# Initialize the database
def init_db(request: gr.Request):
    
    if folderpath is None:
        print("folderpath value is empty. Skipping. Please connect to your Darnahi Account.")
        return
        
    global get_basic
    get_basic(folderpath)
          
    db = get_db()
    if db is None:
        return
        
    try:
        with db:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    age INTEGER,
                    sex TEXT,
                    symptom TEXT,
                    past_medical_history TEXT,
                    medications TEXT,
                    image BLOB,
                    comment TEXT
                )
            ''')
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        if db:
            db.close()


def get_basic(folderpath):
    # This function gets chartit summary
    with open(f'{folderpath}/summary/chart.json', 'r') as file:
        json_data = json.load(file)
        
    extracted_info = extract_lforms_data(json.dumps(json_data))
    json_output = json.dumps(extracted_info, indent=4)
    write_text_to_pdf(folderpath, str(extracted_info))
    with open(f'{folderpath}/ocr_files/fhir_output.json', 'w', encoding='utf-8') as f:
        f.write(json_output)
    return extracted_info

#duplicate as AI module but seems to relevant to keep
def calculate_age(dob):
    if dob is not None:
        today = datetime.now()
        born = datetime.strptime(dob, "%Y-%m-%d")
    
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return "Please update Chartit in you account"



#create PDF with container and margins
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Medical Record', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def create_pdf(record, image_data):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set margin so that the comments dont go past margin
    pdf.set_left_margin(10)
    
    for key, value in record.items():
        if key != 'image' and key != 'comment':
            pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, txt="Comment:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=record['comment'])
    
    if image_data:
        try:
            image_bytes = base64.b64decode(image_data)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name

            pdf.add_page()
            pdf.image(temp_file_path, x=10, y=30, w=190)
            
            os.unlink(temp_file_path)
        except Exception as e:
            pdf.ln(10)
            pdf.cell(0, 10, txt=f"Error processing image: {e}", ln=True)
    
    summary_dir = os.path.join(folderpath, "summary")
    ocr_dir = os.path.join(folderpath, "ocr_files")
    
    
    filename = os.path.join(summary_dir, f"record_{record['date'].replace(':', '-')}.pdf")
    filename2 = os.path.join(ocr_dir, f"record_{record['date'].replace(':', '-')}.pdf")
    
    pdf.output(filename)
    pdf.output(filename2)
    return filename, filename2

def write_text_to_pdf(directory, text):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    text_object = c.beginText(72, 750)  # Start 1 inch from top
    for line in text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    
    # Save the PDF
    with open(f'{directory}/ocr_files/fhir_data.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())

def submit_record(symptom, outputd, comment, file):
    basic_info = get_basic(folderpath)
    age = calculate_age(basic_info['date_of_birth'])
    final_comment = outputd if outputd is not None else (comment if comment is not None else "")
    
    record = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'age': age,
        'sex': basic_info['sex'],
        'symptom': symptom,
        'past_medical_history': json.dumps(basic_info['past_medical_history']),
        'medications': json.dumps(basic_info['medications']),
        'comment': final_comment
    }
    
    image_data = None
    if file:
        try:
            # Read /encode file as base64
            with open(file.name, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            return f"🔴 Error processing image: {e}"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO records (date, age, sex, symptom, past_medical_history, medications, image, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record['date'], record['age'], record['sex'], record['symptom'], record['past_medical_history'], record['medications'], image_data, final_comment))
        conn.commit()
    
    pdf_filename = create_pdf(record, image_data)
    
    return f"🟢 Record submitted successfully. {pdf_filename}"

def fetch_records():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, symptom FROM records ORDER BY date DESC")
        records = cursor.fetchall()
    if not records:
        return gr.Dropdown(choices=["No records available"], value="No records available")
    choices = [f"{r[0]} - {r[1]} - {r[2]}" for r in records]
    return gr.Dropdown(choices=choices, value=choices[0])

def display_record(selected_record):
    if not selected_record or selected_record == "No records available":
        return "Please select a record to display", None
    
    record_id = int(selected_record.split(' - ')[0])
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        record = cursor.fetchone()
    
    if not record:
        return "Record not found", None
    
    columns = ['id', 'date', 'age', 'sex', 'symptom', 'past_medical_history', 'medications', 'image', 'comment']
    record_dict = {columns[i]: record[i] for i in range(len(columns))}
    
    display_text = "\n".join([f"{k}: {v}" for k, v in record_dict.items() if k != 'image'])
    
    if record_dict['image']:
        try:
            image_data = base64.b64decode(record_dict['image'])
            img = Image.open(io.BytesIO(image_data))
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                img.save(temp_file.name, 'PNG')
                temp_file_path = temp_file.name
            return display_text, temp_file_path
        except Exception as e:
            return f"{display_text}\n\nError displaying image: {e}", None
    else:
        return display_text, None

#toggle visibility and connect to relevant DB
def toggle_visibility(choice, request: gr.Request):
    set_user_health_files_directory(request)
    close_db()
    init_db(request)
    
    if choice == "new":
        return gr.Row.update(visible=True), gr.Row.update(visible=False)
    else:
        return gr.Row.update(visible=False), gr.Row.update(visible=True)

#Using ai to write a note
class HealthMotivator:
    async def get_motivation(self, symptom_info):
        messages = [
            {"role": "system", "content": "You are Darnabot, medical transcriber. Write a brief note with input and suggested first aid management only. Suggest doctor if complicated."},
            {"role": "user", "content": f"Generate a brief note input: {symptom_info} only. Do not make up information."},
        ]

        try:    
            OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            async for part in await AsyncClient(host=OLLAMA_HOST).chat(model=f'{model}', messages=messages, stream=True):
                yield part['message']['content']
        except Exception as e:
            yield f"Remember to take care of your health. Please see links below! Also download {model} from ollama. (Error: {str(e)})"



motivator = HealthMotivator()

async def symptom_note(symptom, symptom_info):
    basic_info = get_basic(folderpath)
    age = calculate_age(basic_info['date_of_birth'])
    symptom_info = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'age': age,
        'sex': basic_info['sex'],
        'symptom': symptom,
        'past_medical_history': json.dumps(basic_info['past_medical_history']),
        'medications': json.dumps(basic_info['medications']),
        'comment': symptom_info
    }
    
    motivation = "See a doctor for Advice. This is only information. "   
    async for chunk in motivator.get_motivation(symptom_info):
        motivation += chunk
        yield motivation
    
#######################GRADIO UI

with gr.Blocks(theme='Taithrah/Minimal', css= "footer{display:none !important}") as demo:
    with open('motivation.json', 'r') as file:
        proverbs = json.load(file)
    random_key = random.choice(list(proverbs.keys()))
    proverb = proverbs[random_key]
    gr.Markdown(f"""<div style='text-align: center; font-size: 1rem;'>
<i>{proverb}</i>
</div>
""")
    with gr.Tab("DARNABOT"):
        chatbot = gr.Chatbot(label="DARNAHI CONCIERGE 🛎️")
        msg = gr.Textbox(label="Ask DARNABOT:", placeholder="How can I help?")
        with gr.Row():
            btn1 = gr.Button("Ask")
            Clear = gr.ClearButton([msg, chatbot])

    

        btn1.click(my_function, inputs=[msg, chatbot], outputs=[chatbot])
        Clear.click(clear_conversation, outputs=[msg, chatbot])
    

    with gr.Tab("RUN AI"):
        
            gr.Markdown("## This section will run AI tools (~5min) on your medical records and do the following\n 1. Calculate Age using Darnahi Chartit Data\n 2. Scan through your previously uploaded records once\n 3. Run Image recognition and AI vision on it once to generate AI metadata\n 4. Generate Age and Sex based Recommendations using USPTF recommendations\n 5. Create summaries from your uploaded records that you can explore or download from file server tab\n 6. Create Wordclouds\n 7. Create structured and Unstructured data/ RAG for Darnabot to use so as to tailor its answers using your uploaded chunked data. \n\n")
            with gr.Row():
                fetch_button = gr.Button("Fetch Age and Sex")
                with gr.Column(visible=False) as analysis_column:
                    deidentify_words = gr.Textbox(label="Enter information to deidentify", placeholder="names|email|address|phone")
                    analyze_button = gr.Button("RUN AI")
    
            output1 = gr.Textbox(label="Age and Sex")
            output2 = gr.Textbox(label="Alert")
    
            fetch_button.click(
                fn=fetch_age_sex,
                inputs=[],
                outputs=[output1, output2, analysis_column, analyze_button]
            )
    
            analyze_button.click(
                fn=analyze,
                inputs=[deidentify_words],
                outputs=[output2]
         )

            with gr.Accordion(label="EXPLORE AI FILES)", open=False):

                with gr.Row():
                    with gr.Row():
                        file_list = gr.Dropdown(label="Select a file", choices=list_files(directory))
                        refresh_button = gr.Button("Refresh List")
                    status_text = gr.Textbox(label="Database Status", interactive=False)
    
                with gr.Row():
                    display_area = gr.Textbox(label="Explore Content", visible=True)
                    display_area2 = gr.Image(label="Image", visible=True)
    

                file_list.change(
                fn=update_display,
                inputs=[file_list],
                outputs=[display_area, display_area2]
                )
    
                refresh_button.click(
                fn=refresh_file_list,
                inputs=[],
                outputs=[file_list, status_text]
                )
            with gr.Accordion(label="OTHER INFORMATIONAL LINKS)", open=False):
            
                gr.HTML("""
            <iframe src="https://www.uspreventiveservicestaskforce.org/webview/#!/" width="100%" height="580px"></iframe>
            """)
            
                gr.Markdown("## Are you up to date on Immunizations?\n See Immunization suggestions:")
                gr.HTML("""
        <iframe src="https://www.aafp.org/family-physician/patient-care/prevention-wellness/immunizations-vaccines/immunization-schedules/adult-immunization-schedule.html" 
        width="100%" height="500px"></iframe>
        """)

            

    
       
    with gr.Tab("⛨SYMPTOM LOGGER"): 
        with gr.Row():
            create_new = gr.Button("Create New")
            fetch_previous = gr.Button("Fetch Previous")
    
        with gr.Column(visible=False) as new_record_row:
            with gr.Row():
                symptom = gr.Dropdown(["pain", "rash", "diarrhea", "discharge", "wound", "other"], label="Symptom")
                comment = gr.Textbox(label="Details", placeholder="Rash since 2 days with discharge")
            with gr.Row():
                file = gr.File(label="Attach Image (optional)")
            result = gr.Textbox(label="Alert")
        
            outputd = gr.Markdown(label="Darnabot:")

                            
            with gr.Row():
                btnw = gr.Button("GENERATE")
                submit_btn = gr.Button("Save")
            btnw.click(symptom_note, inputs=(symptom, comment), outputs=[outputd])
        
        
        
    
        with gr.Column(visible=False) as explore_records_row:
            with gr.Row():
                records_dropdown = gr.Dropdown(label="Select Record", choices=["No records available"])
                with gr.Column():
                    fetch_btn = gr.Button("Refresh List")
                    display_btn = gr.Button("Display Selected Record")
            with gr.Row():
                record_display = gr.Textbox(label="Record Details")
                image_display = gr.Image(label="Attached Image")
    
        create_new.click(
        toggle_visibility, 
        inputs=gr.Text(value="new", visible=False), 
        outputs=[new_record_row, explore_records_row]
    )
    
        fetch_previous.click(
        toggle_visibility, 
        inputs=gr.Text(value="previous", visible=False), 
        outputs=[new_record_row, explore_records_row]
    )
    
        submit_btn.click(submit_record, inputs=[symptom, outputd, comment, file], outputs=result)
        fetch_btn.click(fetch_records, outputs=records_dropdown)
        display_btn.click(display_record, inputs=[records_dropdown], outputs=[record_display, image_display])     



if __name__ == "__main__":

    demo.launch(server_name='0.0.0.0', server_port=3012, pwa=True, share=False)
    

