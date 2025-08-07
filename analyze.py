#!/usr/bin/env python3
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

import asyncio
import base64
import json
import mimetypes
import os
import re
import shutil
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple

import chromadb
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import pytesseract
import pydicom
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pdf2image import convert_from_path
from PIL import Image, ImageFile
from tqdm import tqdm
from unidecode import unidecode
from wordcloud import WordCloud

from variables import variables, variables2

ImageFile.LOAD_TRUNCATED_IMAGES = True

HS_path = os.getcwd()

print(HS_path)
folderpath = os.environ.get('FOLDERPATH')

print("folderpath is", folderpath)


if folderpath:
    ocr_files = f"{folderpath}/ocr_files"
else:
    print("Session FOLDERPATH environment variable not set.")

APP_dir = f"{HS_path}/install_module"
ocr_files = f"{folderpath}/ocr_files"
upload_dir = f"{folderpath}/upload"
summary_dir = f"{folderpath}/summary"
ip_address = variables.ip_address
age = variables2.age
sex = variables2.sex
try:
    formatted_ignore_words = variables2.ignore_words if hasattr(variables2, 'ignore_words') else None
except NameError:
    formatted_ignore_words = None


# Path to the Tesseract OCR executable (change this if necessary)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

ocr_files_dir = f'{ocr_files}/'

output_dir = os.path.join(ocr_files_dir, 'Darna_tesseract')
os.makedirs(output_dir, exist_ok=True)

# Define the patterns to identify and deidentify
KEYWORDS_REGEX = r'(?i)(?:Name|DOB|Date of birth|Birth|Address|Phone|PATIENT|Patient|MRN|Medical Record Number|APT|House|Street|ST|zip|pin):.*?(\n|$)'
# remove specific words
IGNORE_REGEX = rf'(?i)(?<!\bNO\b[-.,])(?:NO\b[-.]|[Nn][Oo]\b[-.,]|{formatted_ignore_words})'
KEYWORDS_REPLACE = r'\1REDACT'
DOB_REGEX = r'\b(?!(?:NO\b|NO\b[-.]|[Nn][Oo]\b[-.,]))(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2]\d|3[0-1])-\d{4}\b'
SSN_REGEX = r'\b(?!(?:NO\b|NO\b[-.]|[Nn][Oo]\b[-.,]))(\d{3})-(\d{4})\b'
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
ZIP_REGEX = r'\b(?!(?:NO\b|NOb[-.]|[Nn][Oo]\b[-.,]))([A-Z]{2}) (\d{5})\b'


def perform_ocr(image_path, model="gemma3:4b"):
    """Perform OCR and correct grammar in chunks for long texts"""
    try:
        import requests
        
        # Perform OCR using Tesseract
        raw_text = pytesseract.image_to_string(image_path)
        
        if not raw_text.strip():
            return "No text detected in image"
        
        # If text is short, process normally
        if len(raw_text) < 500:
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": f"Fix grammar and coherence without commentary and preamble in errorprone text: {raw_text}\nCorrected:",
                        "stream": False,
                        "temperature": 0.4
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    corrected = response.json().get("response", "").strip()
                    return corrected or raw_text
            except:
                pass
        
        # For longer texts, process in chunks
        else:
            sentences = raw_text.split('. ')
            chunk_size = 15  # Process 5 sentences at a time
            corrected_chunks = []
            
            for i in range(0, len(sentences), chunk_size):
                chunk = '. '.join(sentences[i:i+chunk_size])
                if not chunk.strip():
                    continue
                    
                try:
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": model,
                            "prompt": f"Fix grammar and coherence without commentary and preamble in error prone text: {chunk}\nCorrected:",
                            "stream": False,
                            "temperature": 0.4
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        corrected = response.json().get("response", "").strip()
                        corrected_chunks.append(corrected or chunk)
                    else:
                        corrected_chunks.append(chunk)
                except:
                    corrected_chunks.append(chunk)
            
            return '. '.join(corrected_chunks)
        
        return raw_text
        
    except Exception as e:
        print(f"OCR error: {str(e)}")
        return None
        


def convert_pdf_to_images(file_path):
    # Implementation of the convert_pdf_to_images function
    try:
        # Convert PDF to images using pdf2image library
        images = convert_from_path(file_path)
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {file_path}")
        print(f"Error message: {str(e)}")
        return None


def process_ocr_files(directory, age):
    output_file = os.path.join(directory, 'ocr_results.txt') 
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(directory):
            # Skip any paths that include the 'tesseract' directory
            if 'tesseract' in root.split(os.sep):
                continue

            for file_name in files:
                # Skip hidden files and non-image/non-PDF files explicitly
                if file_name.startswith('.') or not file_name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                    continue

                file_path = os.path.join(root, file_name)
                if os.path.isfile(file_path):
                    if file_name.lower().endswith('.pdf'):
                        images = convert_pdf_to_images(file_path)
                        if images is not None:
                            for i, image in enumerate(images):
                                text = perform_ocr(image)
                                if text:
                                    f.write(f"File: {file_name}, Page: {i+1}\n")
                                    f.write(text)
                                    f.write('\n\n')
                                image.close()
                    else:
                        # Assuming perform_ocr can handle image files directly
                        text = perform_ocr(file_path)
                        if text:
                            f.write(f"File: {file_name}\n")
                            f.write(text)
                            f.write('\n\n')
    try:
        shutil.copy(output_file, os.path.join(directory, 'Darna_tesseract', 'ocr_results.txt'))
    except shutil.Error as e:
        print(f"Error occurred while copying file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    else:
        print('OCR completed. Results saved in', output_file)


def add_deidentification_tags(text):
    return f'Deidentified Entry | {datetime.now().strftime("%m/%d/%Y")}\n{text}'

def generate_fake_text(match):
    return re.sub(KEYWORDS_REGEX, KEYWORDS_REPLACE, match.group())

def redact_zip_and_words(match):
    words = match.group(1)
    zip_code = match.group(2)
    redacted_words = 'XX ' * min(4, len(words.split()))
    redacted_zip = re.sub(r'\b\d{5}\b', '11111', zip_code)
    return redacted_words + redacted_zip

def deidentify_records(ocr_files, formatted_ignore_words):
    try:
        os.makedirs(os.path.dirname(f'{ocr_files}/ocr_results.txt'), exist_ok=True)
        try:
            with open(f'{ocr_files}/ocr_results.txt') as f:
                text = f.read()
        except FileNotFoundError:
            with open(f'{ocr_files}/ocr_results.txt', 'w') as f:
                pass
            text = ""

        # remove specific words
        IGNORE_REGEX = rf'(?i)(?<!\bNO\b[-.,])(?:NO\b[-.]|[Nn][Oo]\b[-.,]|{formatted_ignore_words})'


        redacted = re.sub(KEYWORDS_REGEX, generate_fake_text, text, flags=re.IGNORECASE)
        redacted = re.sub(IGNORE_REGEX, '', redacted)
        redacted = re.sub(DOB_REGEX, '', redacted)
        redacted = re.sub(SSN_REGEX, '', redacted)
        redacted = re.sub(EMAIL_REGEX, '', redacted)
        redacted = re.sub(ZIP_REGEX, redact_zip_and_words, redacted)

        tagged = add_deidentification_tags(redacted)

        with open(f'{ocr_files}/Darna_tesseract/deidentified_records.txt', 'w') as f:
            f.write(tagged)
        print("Deidentified records printed with user input")
    except Exception as e:
        return f"Error in deidentification process: {str(e)}"


def collate_images(input_dir, output_dir):
    images = []
    for root, dirs, files in os.walk(input_dir):
        # Skip processing files in the '<tesseract>' subdirectory
        if os.path.basename(root) == 'Darna_tesseract':
            continue

        for file in files:
            # Skip all .txt files
            if file.lower().endswith('.txt'):
                continue

            file_path = os.path.join(root, file)
            try:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    img = Image.open(file_path)
                    if img.size[0] > 0 and img.size[1] > 0:  # Check if the image is not empty
                        images.append(img)
                        img.close()
                elif file.lower().endswith(('.pdf', '.PDF')):
                    pdf_images = convert_pdf_to_images(file_path)
                    if pdf_images is not None:
                        for pdf_img in pdf_images:
                            if pdf_img.size[0] > 0 and pdf_img.size[1] > 0:  # Check if the image is not empty
                                images.append(pdf_img)
                                # No need to close PIL Images created from bytes
            except Exception as e:
                print(f"Error processing image: {file_path}")
                print(f"Error message: {str(e)}")
                continue

def get_recommendations(age=None, sex=None, ancestry=None, pack_years=None, smoking=None, quit_within_past_15_years=None, overweight_or_obesity=None, cardiovascular_risk=None, cardiovascular_risk_7_5_to_10=None, rh_d_negative=None, pregnant=None, new_mother=None, substance_abuse_risk=None, skin_type=None):
    recommendations = []
    # Set default values when not specified
    if ancestry is None:
        ancestry = "not None"
    if pack_years is None:
        pack_years = 5
    if smoking is None:
        smoking = "not None"
    if quit_within_past_15_years is None:
        quit_within_past_15_years = "not None"
    if overweight_or_obesity is None:
        overweight_or_obesity = "not None"
    if cardiovascular_risk is None:
        cardiovascular_risk = "not None"
    if rh_d_negative is None:
        rh_d_negative = "not None"
    if cardiovascular_risk_7_5_to_10 is None:
        cardiovascular_risk_7_5_to_10 = "not None"
    if substance_abuse_risk is None:
        substance_abuse_risk = "not None"
    if skin_type is None:
        skin_type = "not None"

    # B - Recommended (39)
    if (sex == 'female') and (age is not None) and (age >= 21 and age <= 65):
    	recommendations.append("Pap Smear: Cervical Cancer: Screening -- Women aged 21 to 65 years")
    if age is not None and (age >= 50 and age <= 75):
        recommendations.append("Colonoscopy: Colorectal Cancer: Screening -- Adults aged 50 to 75 years")
    if age is not None and (age >= 18):
        recommendations.append("BP: Blood pressure screening in office screening -- Adults aged 18 years and above")
    if sex == 'female' and age >= 45:
        recommendations.append("Coronary Risk: Screening women aged 45 and older for lipid disorders if they are at increased risk for coronary heart disease.")
    if sex == 'male' and age >= 35:
        recommendations.append("Fasting Lipid: Screening Men aged 35 and older for lipid disorders with fasting lipid profile.")
    if sex == 'female' and (ancestry is not None):
        recommendations.append("BRCA: BRCA-Related Cancer: Risk Assessment, Genetic Counseling, and Genetic Testing -- Women with a personal or family history of breast, ovarian, tubal, or peritoneal cancer or an ancestry associated with BRCA1/2 gene mutation")
    if sex == 'female' and age >= 35:
        recommendations.append("Breast Cancer: Medication Use to Reduce Risk -- Women at increased risk for breast cancer aged 35 years or older")
    if (sex == 'female') and age is not None and (age >= 50 and age <= 74):
        recommendations.append("Mammogram: Breast Cancer: Screening -- Women aged 50 to 74 years")
    if (sex == 'female' or (new_mother is not None and new_mother)):
        recommendations.append("Breastfeeding: Primary Care Interventions -- Pregnant women, new mothers, and their children")
    if sex == 'female':
        recommendations.append("Sti screen: Chlamydia and Gonorrhea: Screening -- Sexually active women, including pregnant persons")
    if age is not None and (age >= 45 and age <= 49):
        recommendations.append("Colonoscopy: Colorectal Cancer: Screening -- Adults aged 45 to 49 years")
    if age is not None and (age >= 8 and age <= 18):
        recommendations.append("Anxiety Questionnaire: Anxiety in Children and Adolescents: Screening -- Children and adolescents aged 8 to 18 years")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Aspirin for High Risk: Aspirin Use to Prevent Preeclampsia and Related Morbidity and Mortality: Preventive Medication -- Pregnant persons at high risk for preeclampsia")
    if sex == 'pregnant':
        recommendations.append("Urinalysis: Asymptomatic Bacteriuria in Adults: Screening -- Pregnant persons")
    if sex == 'male' and (ancestry is not None):
        recommendations.append("Brca Gene Test: BRCA-Related Cancer: If screen positive, risk Assessment, Genetic Counseling, and Genetic Testing -- Men with a personal or family history of breast, ovarian, tubal, or peritoneal cancer or an ancestry associated with BRCA1/2 gene mutation")
    if sex == 'male' and age >= 65 and (pack_years is not None and pack_years > 0):
        recommendations.append("Ultrasound Doppler Abdomen: Abdominal Aortic Aneurysm: Screening -- Men aged 65 to 75 years who have ever smoked")
    if age is not None and (age >= 12 and age <= 18):
        recommendations.append("Depression Screen Questionnaire: Depression and Suicide Risk in Children and Adolescents: Screening -- Adolescents aged 12 to 18 years")
    if age is not None and (age >= 65):
        recommendations.append("Falls Screen Questionnaire: Falls Prevention in Community-Dwelling Older Adults: Interventions -- Adults 65 years or older")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)) and (age is not None and (age >= 24)):
        recommendations.append("Fasting Blood Glucose: Gestational Diabetes: Screening -- Asymptomatic pregnant persons at 24 weeks of gestation or after")
    if overweight_or_obesity is not None:
        recommendations.append("Bmi screen: If elevated BMI consider Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults With Cardiovascular Risk Factors: Behavioral Counseling Interventions -- Adults with cardiovascular disease risk factors")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Weight Trend: Healthy Weight and Weight Gain In Pregnancy: Behavioral Counseling Interventions -- Pregnant persons")
    if sex == 'female' and (age is not None and (age >= 18)):
        recommendations.append("Hepatitis B Blood Test: Hepatitis B Virus Infection in Adolescents and Adults: Screening -- Adolescents and adults at increased risk for infection")
    if sex == 'male' and (age is not None and (age >= 18 and age <= 79)):
        recommendations.append("Hepatitis C Blood Test: Hepatitis C Virus Infection in Adolescents and Adults: Screening -- Adults aged 18 to 79 years")
    if sex == 'female' and (age is not None and (age >= 14)):
        recommendations.append("Violence Questionnaire screen: Intimate Partner Violence, Elder Abuse, and Abuse of Vulnerable Adults: Screening -- Women of reproductive age")
    if age is not None and (age >= 6 and age <= 60):
        recommendations.append("Tb Screen Test/ Questionnaire: Latent Tuberculosis Infection in Adults: Screening -- Asymptomatic adults at increased risk of latent tuberculosis infection (LTBI)")
    if (sex == 'male' or (sex == 'female' and (pregnant is not None and pregnant))) and (age is not None and (age >= 50 and age <= 80) and (pack_years is not None) and (smoking is not None)):
        recommendations.append("Ct Chest: Lung Cancer screening if you smoked more that 20 pack years: Screening -- Adults aged 50 to 80 years who have a 20 pack-year smoking history and currently smoke or have quit within the past 15 years")
    if age is not None and (age >= 6 and age <= 18):
        recommendations.append("Bmi Screen: Obesity in Children and Adolescents: Screening -- Children and adolescents 6 years and older")
    if sex == 'female' and (age is not None and (age < 65)):
        recommendations.append("Dexa Bone Test: Osteoporosis to Prevent Fractures: Screening -- Postmenopausal women younger than 65 years at increased risk of osteoporosis")
    if sex == 'female' and (age is not None and (age >= 65)):
        recommendations.append("Dexa Bone Test: Osteoporosis to Prevent Fractures: Screening -- Women 65 years and older")
    if (sex == 'pregnant' or (pregnant is not None and pregnant) or (new_mother is not None)):
        recommendations.append("Depression Questionnaire: Perinatal Depression: Preventive Interventions -- Pregnant and postpartum persons")
    if age is not None and (age >= 35 and age <= 70):
        recommendations.append("Fasting Blood Glucose: Prediabetes and Type 2 Diabetes: Screening -- Asymptomatic adults aged 35 to 70 years who have overweight or obesity")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Bp, Questionnaire and Urine test: Preeclampsia: Screening -- Pregnant woman")
    if age is not None and (age < 5):
        recommendations.append("Oral Exam: Prevention of Dental Caries in Children Younger Than 5 Years: Screening and Interventions -- Children younger than 5 years")
    if (sex == 'female' or (pregnant is not None and pregnant)) or (new_mother is not None):
        recommendations.append("Oral Exam: Prevention of Dental Caries in Children Younger Than 5 Years: Screening and Interventions -- Children younger than 5 years")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)) and (rh_d_negative is not None):
        recommendations.append("Rh Blood Test: Rh(D) Incompatibility especially with Rh negative: Screening -- Unsensitized Rh(D)-negative pregnant women")
    if sex == 'male' or (sex == 'female' and (pregnant is not None and pregnant) or (new_mother is not None and new_mother)):
        recommendations.append("Depression Questionnaire: Screening for Depression in Adults -- General adult population")
    if sex == 'male' or (sex == 'female' and (pregnant is not None and pregnant)) or (new_mother is not None):
        recommendations.append("Sti Screen: Sexually Transmitted Infections: Behavioral Counseling -- Sexually active adolescents and adults at increased risk")
    if (age is not None and (age >= 25)) or (new_mother is not None) or (sex == 'male' and (substance_abuse_risk is not None)):
        recommendations.append("Skin Exam: Skin Cancer Prevention: Behavioral Counseling -- Adults, Young adults, adolescents, children, and parents of young children")
    if (age is not None and (age >= 40 and age <= 75)) and (cardiovascular_risk is not None) and (cardiovascular_risk_7_5_to_10 is not None):
        recommendations.append("Heart Disease Questionnaire: Screen for CV risk and consider Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: Preventive Medication -- Adults aged 40 to 75 years who have 1 or more cardiovascular risk factors and an estimated 10-year cardiovascular disease (CVD) risk of 10% or greater")
    if sex == 'female' and (pregnant is not None and pregnant) and (ancestry is not None and ancestry == 'BRCA1/2 gene mutation'):
        recommendations.append("Family History and Brca Test: BRCA-Related Cancer: Risk Assessment, Genetic Counseling, and Genetic Testing -- Women with a personal or family history of breast, ovarian, tubal, or peritoneal cancer or an ancestry associated with BRCA1/2 gene mutation")
    if (age is not None and (age >= 6 and age <= 18)) or (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Tobacco Questionnaire: Tobacco Use in Children and Adolescents: Primary Care Interventions -- School-aged children and adolescents who have not started to use tobacco")
    if age is not None and (age >= 18) and (substance_abuse_risk is not None):
        recommendations.append("Alcohol Questionnaire: Unhealthy Alcohol Use in Adolescents and Adults: Screening and Behavioral Counseling Interventions -- Adults 18 years or older, including pregnant women")
    if age is not None and (age >= 13):
        recommendations.append("Drug Abuse Questionnaire: Unhealthy Drug Use: Screening -- Adults age 13 years or older")
    if age is not None and (age > 2 and age < 24) and skin_type is not None:
        recommendations.append("Skin Exam: Skin Cancer: Counseling -- Fair-skinned individuals aged 6 months to 24 years with a family history of skin cancer or personal history of skin cancer, or who are at increased risk of skin cancer")
        
    return recommendations


def generate_recommendations(age=None, sex=None):
    age = f"{age}"
    try:
        age = int(age)
    except ValueError:
        print("Invalid age value. Age must be a valid integer.")

    sex = f"{sex}"

    recommendations = get_recommendations(age, sex)
    # Adding subheading
    subheading = f"The USPTF recommendations for {age}/{sex} are:"
    subheading = f"RECOMMENDATIONS:"
    recommendations_with_subheading = [subheading] + recommendations

    with open(f'{ocr_files}/Darna_tesseract/USPTF_Intent.txt', 'w') as file:
        file.write('\n\n\n'.join(recommendations_with_subheading))
    doc = fitz.open()  # Create a new PDF
    page = doc.new_page()  
    text = "\n\n\n".join(recommendations_with_subheading) 
    page.insert_text((72, 72), text)
    doc.save(f'{ocr_files}/USPTF.pdf')  # Save the PDF
    doc.close()

#extract data from the updated fhir file - mychart       
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


###nlp_process.py functions


# Ensure NLTK components are downloaded
#nltk.download('punkt')
#nltk.download('stopwords')

#convert text to lowercase and remove fillers
def normalize_text(text):
    # Convert text to lowercase and remove ':' and '-'
    return re.sub('[: -]', '', text.lower())

def condense_summary_to_tokens(text, token_limit=300):
    tokens = word_tokenize(text)
    # Select the first 'token_limit' tokens
    limited_tokens = tokens[:token_limit]
    # Reconstruct the text from these tokens
    condensed_text = ' '.join(limited_tokens)
    return condensed_text

#write all to a json summary file    
def wordcloud_summary(keys, texts, directory):
    output_file = f'{directory}/wordcloud_summary.json'
    wordcloud_dir = f'{directory}/wordclouds'
    
    try:
        with open(output_file, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}
    
    # Ensure the directories exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(wordcloud_dir, exist_ok=True)
    
    for i, key in enumerate(keys):
        if i < len(texts):
            text = texts[i]
            # Check if the text contains any words
            if text.strip():
                existing_data[key] = text
                
                # Attempt to generate word cloud
                try:
                    # Split the text into words
                    words = text.split()
                    
                    # Check if there are enough words
                    if len(words) > 1:
                        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                        
                        # Save the word cloud
                        plt.figure(figsize=(10, 5))
                        plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis('off')
                        plt.title(f'Word Cloud for {key}')
                        plt.savefig(f'{wordcloud_dir}/{key}_wordcloud.png')
                        plt.close()
                        
                        print(f"Generated word cloud for key: {key}")
                    else:
                        print(f"Not enough words to generate word cloud for key: {key}")
                except Exception as e:
                    print(f"Error generating word cloud for key {key}: {str(e)}")
            else:
                print(f"Skipping empty text for key: {key}")
        else:
            print(f"No text available for key: {key}")
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
               

#generate list of meds from the files         
def load_text_from_json_meds(json_file_path, keys):
    normalized_keys = [normalize_text(key) for key in keys]
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        text = []
        for json_key, value in data.items():
            normalized_json_key = normalize_text(json_key)
            if any(normalized_key in normalized_json_key for normalized_key in normalized_keys):
                if isinstance(value, str):
                    text.append(value)
                elif isinstance(value, list):
                    text.extend(str(item) for item in value if item)
                elif isinstance(value, dict):
                    text.extend(str(item) for item in value.values() if item)
                else:
                    text.append(str(value))
        
        combined_text = ' '.join(text)
        combined_text = condense_summary_to_tokens(combined_text, 300)
    return combined_text

#generate a list of past medical history from the files

def load_text_from_json_pmh(json_file_path, keys):
    normalized_keys = [normalize_text(key) for key in keys]
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        text = []
        for json_key, value in data.items():
            normalized_json_key = normalize_text(json_key)
            if any(normalized_key in normalized_json_key for normalized_key in normalized_keys):
                if isinstance(value, str):
                    text.append(value)
                elif isinstance(value, list):
                    text.extend(str(item) for item in value if item)
                elif isinstance(value, dict):
                    text.extend(str(item) for item in value.values() if item)
                else:
                    text.append(str(value))
        
        combined_text = ' '.join(text)
        combined_text = condense_summary_to_tokens(combined_text, 300)
    return combined_text
    
#generate a list of screening items from the USPTF file    
def load_text_from_json_screening(json_file_path, keys):
    normalized_keys = [normalize_text(key) for key in keys]
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        text = []
        for json_key, value in data.items():
            normalized_json_key = normalize_text(json_key)
            if any(normalized_key in normalized_json_key for normalized_key in normalized_keys):
                text.append(value)
        combined_text_screening=' '.join(text)
        #print (combined_text_screening)
        
    return combined_text_screening
        
def load_text_from_json_summary(json_file_path, keys):
    normalized_keys = [normalize_text(key) for key in keys]
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        text = []
        for json_key, value in data.items():
            normalized_json_key = normalize_text(json_key)
            if any(normalized_key in normalized_json_key for normalized_key in normalized_keys):
                if isinstance(value, str):
                    text.append(value)
                elif isinstance(value, list):
                    text.extend(str(item) for item in value if item)
                elif isinstance(value, dict):
                    text.extend(str(item) for item in value.values() if item)
                else:
                    text.append(str(value))
        
        combined_text = ' '.join(text)
        combined_text = condense_summary_to_tokens(combined_text, 300)
    return combined_text

#iterate json files in directory and call function above
def process_directory_summary(directory, keys):
    combined_texts = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            print(file_path)
            combined_text = load_text_from_json_summary(file_path, keys)
            if combined_text:  # Only add non-empty strings
                combined_texts.append(combined_text)
            
    
    # Combine all texts into one
    final_combined_text = ' '.join(combined_texts)
    return final_combined_text

#iterate json files in directory and summarize meds
def process_directory_meds(directory, keys):
    combined_texts = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            print(file_path)
            combined_text = load_text_from_json_meds(file_path, keys)
            combined_texts.append(combined_text)
            
    
    # Combine all texts into one
    final_combined_text = ' '.join(combined_texts)
    return final_combined_text

#iterate json files in directory and summarize past medical
def process_directory_pmh(directory, keys):
    combined_texts = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            print(file_path)
            combined_text = load_text_from_json_pmh(file_path, keys)
            combined_texts.append(combined_text)
            
    
    # Combine all texts into one
    final_combined_text = ' '.join(combined_texts)
    return final_combined_text

def preprocess_and_create_wordcloud(text, directory):
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.isalnum() and word.lower() not in stop_words]
    
    # Check if there are any words left after filtering
    if not filtered_words:
        print("No words left after preprocessing. Skipping word cloud creation.")
        return
    
    processed_text = ' '.join(filtered_words)
    
    # Create and display the word cloud
    wordcloud = WordCloud(width=800, height=800, background_color='white').generate(processed_text)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.tight_layout(pad = 0)

    # Display the word cloud
    #plt.show()

    # Save the word cloud image
    plt.savefig(f'{directory}darnahi_ocr.png')
    
#############

pattern = r"\d+\..+?(\d{4};\d+\(\d+\):\d+–\d+\. DOI: .+?\.|.+?ed\., .+?: .+?; \d{4}\. \d+–\d+\.)"

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def process_pdf(file_path, chunk_size=350):
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            text_blocks = page.get_text("dict")["blocks"]
            for block in text_blocks:
                if 'text' in block:
                    text = block['text'].strip()
                    if text:
                        full_text += text + "\n"
        chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
        return chunks
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

def process_json(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return []
    semantic_snippets = []
    for heading, content in existing_data.items():
        metadata = {'heading': heading, 'file': input_file}
        doc = Document(page_content=content, metadata=metadata)
        semantic_snippets.append(doc)
    return semantic_snippets

def process_files(directory):
    all_semantic_snippets = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.pdf'):
            snippets = process_pdf(file_path)
            all_semantic_snippets.extend(snippets)
        elif filename.endswith('.json'):
            semantic_snippets = process_json(file_path)
            all_semantic_snippets.extend(semantic_snippets)
    return all_semantic_snippets

def chromadb_embed(directory, collection_name="documents_collection"):
    persist_directory = os.path.join(directory, 'Darna_tesseract', 'chroma_storage')
    os.makedirs(persist_directory, exist_ok=True)
    all_semantic_snippets = str(process_files(directory))
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(name=collection_name)
    count = collection.count()
    print(f"Collection already contains {count} documents")
    ids = [str(i) for i in range(count, count + len(all_semantic_snippets))]
    for i in tqdm(range(0, len(all_semantic_snippets), 100), desc="Adding documents"):
        batch_snippets = all_semantic_snippets[i:i+100]
        batch_metadatas = []
        for snippet in batch_snippets:
            metadata = {"filename": "summary", "heading": "summary_heading"} if not isinstance(snippet, Document) else snippet.metadata
            batch_metadatas.append(metadata)
        collection.add(ids=ids[i:i+100], documents=[s if isinstance(s, str) else s.page_content for s in batch_snippets], metadatas=batch_metadatas)
    new_count = collection.count()
    print(f"Added {new_count - count} documents")


#########pdf_sectionreader.py

global_heading_content_dict = {}  # Global dictionary to accumulate data

def process_pdf_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            with fitz.open(file_path) as doc:
                print(f"Processing {filename}...")
                extract_and_tag_text(doc)

    # Generate and save output after processing all files
    generate_output(global_heading_content_dict, directory)

def extract_and_tag_text(doc):
    block_dict, page_num = {}, 1
    for page in doc:
        file_dict = page.get_text('dict')
        block = file_dict['blocks']
        block_dict[page_num] = block
        page_num += 1

    rows = []
    for page_num, blocks in block_dict.items():
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        xmin, ymin, xmax, ymax = list(span['bbox'])
                        font_size = span['size']
                        text = unidecode(span['text'])
                        span_font = span['font']
                        is_upper = text.isupper()
                        is_bold = "bold" in span_font.lower()

                        if text.strip() != "":
                            rows.append((xmin, ymin, xmax, ymax, text, is_upper, is_bold, span_font, font_size))

    span_df = pd.DataFrame(rows, columns=['xmin', 'ymin', 'xmax', 'ymax', 'text', 'is_upper', 'is_bold', 'span_font', 'font_size'])
    common_font_size = span_df['font_size'].mode().iloc[0]
    span_df['tag'] = span_df.apply(assign_tag, axis=1, common_font_size=common_font_size)

    update_global_dict(span_df)

def assign_tag(row, common_font_size):
    if any(char.isdigit() for char in row['text']):
        return 'p'
    elif row['font_size'] > common_font_size and row['is_bold'] and row['is_upper']:
        return 'h1'
    elif row['is_bold'] or row['is_upper'] or row['font_size'] > common_font_size:
        return 'h2'
    else:
        return 'p'

def update_global_dict(span_df):
    tmp = []
    current_heading = None

    for index, span_row in span_df.iterrows():
        text, tag = span_row.text.strip(), span_row.tag
        if 'h' in tag:
            if current_heading is not None:
                existing_text = global_heading_content_dict.get(current_heading, "")
                global_heading_content_dict[current_heading] = existing_text + '\n'.join(tmp).strip()
            current_heading = text
            tmp = []
        else:
            tmp.append(text)

    if current_heading is not None:
        existing_text = global_heading_content_dict.get(current_heading, "")
        global_heading_content_dict[current_heading] = existing_text + '\n'.join(tmp).strip()
    


def generate_output(heading_content_dict, directory):
    text_df = pd.DataFrame(list(heading_content_dict.items()), columns=['heading', 'content'])
    #text_df.to_excel(f'{directory}/combined_output.xlsx', index=False, engine='openpyxl')
    
    json_data = json.dumps(heading_content_dict, indent=4, ensure_ascii=False)
    with open(f'{directory}/Darna_tesseract/combined_output.json', 'w', encoding='utf-8') as f:
        f.write(json_data)
    with open(f'{directory}/combined_output.json', 'w', encoding='utf-8') as f:
        f.write(json_data)



def whitelist_directory(directory, whitelist):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename not in whitelist:
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")


##########################################
#AI ASSISTANCE TO TAG AND SAVE FILES
###########################################


#imports with availability checks
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from ollama import AsyncClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import pydicom  # PyMuPDF
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False

class AsyncFileProcessor:
    """Async file processor for metadata extraction and AI analysis"""
    
    def __init__(self, db_path: str = f"{summary_dir}/medical_records.db", model: str = "gemma3:4b", use_vision_for_images: bool = True):
        self.db_path = db_path
        self.model = model
        self.use_vision_for_images = use_vision_for_images
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                upload_date TIMESTAMP,
                embedded_metadata TEXT,
                ai_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster searches
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)
        ''')
        
        conn.commit()
        conn.close()
    
    def _is_dicom_file(self, file_path: Path) -> bool:
        """Check if file is DICOM by reading header"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(132)
                return b'DICM' in header
        except:
            return False
    
    async def process_folder(self, folder_path: str, extensions: Optional[List[str]] = None, exclude_extensions: Optional[List[str]] = None) -> Dict:
        """
        Process all files in a folder asynchronously
        """
        results = {
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "files": [],
            "error": None
        }
        
        try:
            folder_path = Path(folder_path)
            if not folder_path.exists():
                results["error"] = f"Folder {folder_path} does not exist"
                return results
            
            # Default excluded extensions if not specified
            if exclude_extensions is None:
                exclude_extensions = ['.db', '.sqlite', '.sqlite3', '.tmp', '.temp', '.cache', '.lock', '.DS_Store']
            
            # Get all files in folder
            files = []
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    file_ext = file_path.suffix.lower()
                    
                    # Skip excluded extensions
                    if file_ext in exclude_extensions:
                        continue
                    
                    # Skip hidden files and system files
                    if file_path.name.startswith('.') or file_path.name.startswith('~'):
                        continue
                    
                    # If specific extensions are requested, only include those
                    if extensions is not None:
                        if file_ext in extensions:
                            files.append(file_path)
                    else:
                        # Include all non-excluded files
                        files.append(file_path)
            
            if not files:
                results["error"] = f"No files found in {folder_path}"
                return results
            
            # Process files in batches for better performance
            batch_size = 5
            for i in range(0, len(files), batch_size):
                batch = files[i:i+batch_size]
                batch_results = await asyncio.gather(
                    *[self.process_file(str(file_path)) for file_path in batch],
                    return_exceptions=True
                )
                
                for file_path, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        results["errors"] += 1
                        results["files"].append({
                            "filename": file_path.name,
                            "status": "error",
                            "message": str(result)
                        })
                    else:
                        if result.get("status") == "success":
                            results["processed"] += 1
                        elif result.get("status") == "skipped":
                            results["skipped"] += 1
                        else:
                            results["errors"] += 1
                        results["files"].append(result)
            
        except Exception as e:
            results["error"] = f"Error processing folder: {str(e)}"
        
        return results
    
    async def process_file(self, file_path: str) -> Dict:
        """
        Process a single file: extract metadata and generate AI summary

        """
        file_path = Path(file_path)
        
        # Check if file already exists in database
        if self._file_exists_in_db(str(file_path)):
            return {
                "filename": file_path.name,
                "status": "skipped",
                "message": "Already in database"
            }
        
        try:
            # Get file stats
            stats = file_path.stat()
            file_info = {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size": stats.st_size,
                "file_type": file_path.suffix.lower(),
                "upload_date": datetime.now()
            }
            
            # Extract embedded metadata
            embedded_metadata = await self._extract_embedded_metadata(file_path)
            file_info["embedded_metadata"] = json.dumps(embedded_metadata)
            
            # Generate AI metadata if Ollama is available
            if OLLAMA_AVAILABLE:
                content = await self._extract_content(file_path)
                ai_metadata = await self._generate_ai_metadata(file_path.name, content)
                file_info["ai_metadata"] = ai_metadata
            else:
                file_info["ai_metadata"] = json.dumps({"error": "Ollama not available"})
            
            # Save to database
            self._save_to_database(file_info)
            
            return {
                "filename": file_path.name,
                "status": "success",
                "embedded_metadata": embedded_metadata,
                "ai_metadata": json.loads(file_info["ai_metadata"]) if file_info["ai_metadata"] else None
            }
            
        except Exception as e:
            raise Exception(f"Error processing {file_path.name}: {str(e)}")
    
    async def _analyze_image_with_vision(self, file_path: Path, max_chars: int = 3000) -> str:
        """
        Analyze image using vision LLM model

        """
        try:
            import requests
            
            # Encode image to base64
            with open(str(file_path), "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Create analysis prompt
            prompt = """Analyze this image and provide concise summary and relevant keywords in json format. No preamble or commentary". Provide JSON: {{\"summary\": \"...\", \"keywords\": [\"...\", \"...\"]}}"
            s"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [encoded_image],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1000
                }
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                if result:
                    return result[:max_chars]
            
            # If vision fails, note it
            return f"Vision analysis failed for {file_path.name}"
            
        except Exception as e:
            return f"Error analyzing image {file_path.name}: {str(e)}"
    
    async def _extract_content(self, file_path: Path, max_chars: int = 3000) -> str:
        """Extract text content from file for AI analysis"""
        content = ""
        ext = file_path.suffix.lower()
        
        # PDF and similar documents
        if PYMUPDF_AVAILABLE and ext in ['.pdf', '.xps', '.epub', '.mobi', '.fb2', '.cbz']:
            try:
                doc = fitz.open(str(file_path))
                for page_num in range(min(3, doc.page_count)):  # First 3 pages
                    content += doc[page_num].get_text()
                doc.close()
                return content[:max_chars]
            except:
                pass
        
        # Office documents - .docx, .xlsx, .pptx
        elif ext in ['.docx', '.xlsx', '.pptx']:
            try:
                if ext == '.docx':
                    # Extract text from docx
                    with zipfile.ZipFile(str(file_path), 'r') as zip_file:
                        if 'word/document.xml' in zip_file.namelist():
                            xml_content = zip_file.read('word/document.xml')
                            root = ET.fromstring(xml_content)
                            # Extract text from all text elements
                            texts = []
                            for elem in root.iter():
                                if elem.text:
                                    texts.append(elem.text)
                            content = ' '.join(texts)
                            return content[:max_chars]
                elif ext == '.xlsx':
                    # Basic Excel text extraction
                    with zipfile.ZipFile(str(file_path), 'r') as zip_file:
                        for name in zip_file.namelist():
                            if name.startswith('xl/sharedStrings'):
                                xml_content = zip_file.read(name)
                                root = ET.fromstring(xml_content)
                                texts = []
                                for elem in root.iter():
                                    if elem.text:
                                        texts.append(elem.text)
                                content = ' '.join(texts)
                                return content[:max_chars]
                elif ext == '.pptx':
                    # PowerPoint text extraction
                    with zipfile.ZipFile(str(file_path), 'r') as zip_file:
                        texts = []
                        for name in zip_file.namelist():
                            if name.startswith('ppt/slides/slide'):
                                xml_content = zip_file.read(name)
                                root = ET.fromstring(xml_content)
                                for elem in root.iter():
                                    if elem.text:
                                        texts.append(elem.text)
                        content = ' '.join(texts)
                        return content[:max_chars]
            except:
                pass
        
        # Legacy .doc files (if python-docx is available)
        elif ext == '.doc':
            try:
                # Try using LibreOffice/OpenOffice command line tool if available
                import subprocess
                temp_txt = str(file_path) + '.txt'
                result = subprocess.run(
                    ['soffice', '--headless', '--convert-to', 'txt:Text', str(file_path)],
                    capture_output=True,
                    timeout=10
                )
                if os.path.exists(temp_txt):
                    with open(temp_txt, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:max_chars]
                    os.remove(temp_txt)
                    return content
            except:
                # If conversion fails, return file info
                pass
        
        # Text-based files
        elif ext in ['.txt', '.md', '.py', '.js', '.jsx', '.ts', '.tsx', 
                     '.html', '.htm', '.css', '.scss', '.sass', '.less',
                     '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
                     '.csv', '.tsv', '.log', '.sql', '.sh', '.bash', '.zsh',
                     '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.go', '.rs', '.swift',
                     '.r', '.m', '.php', '.rb', '.pl', '.lua', '.vim', '.el']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:max_chars]
                return content
            except:
                pass
        
        # RTF files
        elif ext == '.rtf':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    rtf_content = f.read()
                    # Simple RTF stripping (removes most RTF formatting)
                    import re
                    # Remove RTF commands
                    content = re.sub(r'\\[a-z]+\d*\s?', '', rtf_content)
                    content = re.sub(r'[{}]', '', content)
                    return content[:max_chars]
            except:
                pass
        
        # Images with Vision LLM or OCR
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.bmp', '.webp', '.ico']:
            # Use vision model if enabled
            if self.use_vision_for_images:
                vision_result = await self._analyze_image_with_vision(file_path, max_chars)
                if vision_result and "failed" not in vision_result.lower():
                    return vision_result
            
            # Fallback to OCR
            if TESSERACT_AVAILABLE and PIL_AVAILABLE:
                try:
                    image = Image.open(str(file_path))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    content = pytesseract.image_to_string(image)
                    if content.strip():
                        return content[:max_chars]
                except:
                    pass
            
            return f"Image file: {file_path.name}, Type: {ext}, Size: {file_path.stat().st_size} bytes"
        
        # DICOM medical imaging files
        elif ext in ['.dcm', '.dicom'] or self._is_dicom_file(file_path):
            if PYDICOM_AVAILABLE:
                try:
                    from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
            
                    # Read DICOM file
                    ds = pydicom.dcmread(str(file_path))
            
                    # Extract metadata
                    metadata = {
                        "patient_id": getattr(ds, 'PatientID', 'Unknown'),
                        "study_date": getattr(ds, 'StudyDate', 'Unknown'),
                        "modality": getattr(ds, 'Modality', 'Unknown'),
                        "body_part": getattr(ds, 'BodyPartExamined', 'Unknown')
                    }
            
                    # Convert to image if pixel data exists
                    if hasattr(ds, 'pixel_array'):
                        pixel_array = ds.pixel_array
                
                        # Apply LUT transformations if needed
                        if 'RescaleSlope' in ds or 'RescaleIntercept' in ds:
                            pixel_array = apply_modality_lut(pixel_array, ds)
                
                        if 'WindowCenter' in ds and 'WindowWidth' in ds:
                            pixel_array = apply_voi_lut(pixel_array, ds)
                
                        # Convert to PIL Image for vision analysis
                        if len(pixel_array.shape) == 2:  # Grayscale
                            # Normalize to 0-255 range
                            pixel_array = ((pixel_array - pixel_array.min()) * 255.0 / 
                                        (pixel_array.max() - pixel_array.min())).astype(np.uint8)
                            image = Image.fromarray(pixel_array, mode='L').convert('RGB')
                    
                            # Now use vision analysis
                            if self.use_vision_for_images:
                                # Convert PIL image back to base64 for vision analysis
                                import io
                                img_buffer = io.BytesIO()
                                image.save(img_buffer, format='PNG')
                                encoded_image = base64.b64encode(img_buffer.getvalue()).decode()
                        
                                # Use your existing vision analysis with the encoded image
                                vision_result = await self._analyze_dicom_with_vision(
                                    encoded_image, metadata, max_chars
                                )
                                if vision_result:
                                    return vision_result
            
                    # Fallback to metadata only
                    return f"DICOM file: {file_path.name}, Modality: {metadata['modality']}, Body Part: {metadata['body_part']}, Patient ID: {metadata['patient_id']}"
            
                except Exception as e:
                    return f"Error reading DICOM file {file_path.name}: {str(e)}"
    
            return f"DICOM file: {file_path.name} (pydicom not available for analysis)"
        
        # Audio/Video files - just return metadata
        elif ext in ['.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wav', '.flac', '.ogg', '.webm', '.m4a', '.aac']:
            return f"Media file: {file_path.name}, Type: {ext}, Size: {file_path.stat().st_size} bytes"
        
        # Default: return basic file info
        return f"File: {file_path.name}, Type: {ext}, Size: {file_path.stat().st_size} bytes"
    
    async def _extract_embedded_metadata(self, file_path: Path) -> Dict:
        """Extract native file metadata"""
        stats = file_path.stat()
        metadata = {
            "size": stats.st_size,
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat()
        }
        
        mime_type, _ = mimetypes.guess_type(str(file_path))
        ext = file_path.suffix.lower()
        
        # PDF and ebook metadata
        if PYMUPDF_AVAILABLE and ext in ['.pdf', '.xps', '.epub', '.mobi', '.fb2', '.cbz']:
            try:
                doc = fitz.open(str(file_path))
                meta = doc.metadata
                if meta:
                    for key in ['author', 'title', 'subject', 'keywords', 'creator', 'producer']:
                        if meta.get(key):
                            metadata[key.capitalize()] = meta[key]
                    metadata['Pages'] = doc.page_count
                doc.close()
            except:
                pass
        
        # Image metadata
        elif PIL_AVAILABLE and ext in ['.png', '.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.bmp', '.webp', '.ico']:
            try:
                image = Image.open(str(file_path))
                metadata['Format'] = image.format
                metadata['Dimensions'] = f"{image.width}x{image.height}"
                metadata['Mode'] = image.mode
                
                # EXIF data for photos
                if hasattr(image, 'getexif'):
                    exifdata = image.getexif()
                    if exifdata:
                        for tag_id in exifdata:
                            tag = TAGS.get(tag_id, tag_id)
                            data = exifdata.get(tag_id)
                            if tag in ['Artist', 'Copyright', 'DateTime', 'DateTimeOriginal', 
                                      'Software', 'Make', 'Model', 'LensModel', 'GPSInfo']:
                                try:
                                    metadata[tag] = str(data)
                                except:
                                    pass
            except:
                pass
        
        # Office documents
        elif ext in ['.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp']:
            try:
                with zipfile.ZipFile(str(file_path), 'r') as zip_file:
                    # Microsoft Office
                    if 'docProps/core.xml' in zip_file.namelist():
                        core_xml = zip_file.read('docProps/core.xml')
                        root = ET.fromstring(core_xml)
                        
                        namespaces = {
                            'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                            'dc': 'http://purl.org/dc/elements/1.1/',
                            'dcterms': 'http://purl.org/dc/terms/'
                        }
                        
                        elements = {
                            'Creator': './/dc:creator',
                            'Title': './/dc:title',
                            'Subject': './/dc:subject',
                            'Keywords': './/cp:keywords',
                            'Description': './/dc:description',
                            'LastModifiedBy': './/cp:lastModifiedBy',
                            'Revision': './/cp:revision'
                        }
                        
                        for name, xpath in elements.items():
                            elem = root.find(xpath, namespaces)
                            if elem is not None and elem.text:
                                metadata[name] = elem.text
                    
                    # OpenDocument format
                    elif 'meta.xml' in zip_file.namelist():
                        meta_xml = zip_file.read('meta.xml')
                        root = ET.fromstring(meta_xml)
                        # Extract OpenDocument metadata
                        for elem in root.iter():
                            if 'title' in elem.tag.lower() and elem.text:
                                metadata['Title'] = elem.text
                            elif 'creator' in elem.tag.lower() and elem.text:
                                metadata['Creator'] = elem.text
            except:
                pass
        
        # Audio files metadata (if mutagen is available)
        elif ext in ['.mp3', '.mp4', '.m4a', '.flac', '.ogg', '.wav']:
            try:
                from mutagen import File
                audio = File(str(file_path))
                if audio:
                    if audio.info:
                        metadata['Duration'] = str(audio.info.length) + ' seconds'
                        metadata['Bitrate'] = str(getattr(audio.info, 'bitrate', 'N/A'))
                    for key in ['title', 'artist', 'album', 'date', 'genre']:
                        if key in audio:
                            metadata[key.capitalize()] = str(audio[key][0])
            except ImportError:
                pass
            except:
                pass
        
        return metadata
    
    async def _generate_ai_metadata(self, filename: str, content: str) -> str:
        """Generate AI metadata using Ollama"""
        if not OLLAMA_AVAILABLE:
            return json.dumps({"error": "Ollama not available"})
        
        messages = [
            {
                "role": "system", 
                "content": "You are a document analyst. Provide concise summary and relevant keywords."
            },
            {
                "role": "user", 
                "content": f"File: {filename}\nContent: {content[:2000]}\n\nProvide JSON: {{\"date\": \"...\", \"summary\": \"...\", \"keywords\": [\"...\", \"...\"]}}"
            }
        ]
        
        try:
            client = AsyncClient(host=self.ollama_host)
            response = await client.chat(
                model=self.model,
                messages=messages,
                stream=False
            )
            
            result = response['message']['content']
            
            # Try to extract JSON
            try:
                json_start = result.index('{')
                json_end = result.rindex('}') + 1
                json_str = result[json_start:json_end]
                parsed = json.loads(json_str)
                return json.dumps(parsed)
            except:
                return json.dumps({"summary": result, "keywords": []})
                
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _file_exists_in_db(self, file_path: str) -> bool:
        """Check if file already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def _save_to_database(self, file_info: Dict):
        """Save file information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO files (
                filename, file_path, file_size, file_type,
                upload_date, embedded_metadata, ai_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_info["filename"],
            file_info["file_path"],
            file_info["file_size"],
            file_info["file_type"],
            file_info["upload_date"],
            file_info["embedded_metadata"],
            file_info["ai_metadata"]
        ))
        
        conn.commit()
        conn.close()

# Calling AI assistance usage
async def main():
    # Initialize processor with vision enabled for images
    processor = AsyncFileProcessor(
        db_path=f"{summary_dir}/medical_records.db",
        model="gemma3:4b", 
        use_vision_for_images=True 
    )
    
    # Process ALL files except database and temp files (recommended)
    results = await processor.process_folder(
        f"{summary_dir}",
        exclude_extensions=['.db', '.sqlite', '.tmp', '.temp', '.cache']
    )
    
    
    # Check for errors first
    if results.get("error"):
        print(f"Error: {results['error']}")
    else:
        print(f"Processed: {results['processed']} files")
        print(f"Skipped: {results['skipped']} files")
        print(f"Errors: {results['errors']} files")
        
        # Show details for any errors
        if results['errors'] > 0:
            print("\nError details:")
            for file_info in results['files']:
                if file_info.get('status') == 'error':
                    print(f"  - {file_info['filename']}: {file_info.get('message', 'Unknown error')}")
    
###########################################

#write files to pdf
def write_text_to_pdf(directory, text):
    doc = fitz.open()  # Create a new PDF
    page = doc.new_page()  # Add a new page
    page.insert_text((72, 72), text)  # Position (x, y) and text
    doc.save(f'{directory}/fhir_data.pdf')  # Save the PDF
    doc.close()
def run_analyzer(age, sex, ocr_files, formatted_ignore_words):
    try:
    
        # Process OCR files with provided input
        print("Processing OCR files")
        process_ocr_files(ocr_files, age)

        # Create collated file
        collate_images(ocr_files, f"{ocr_files}/Darna_tesseract")

        # Deidentify records
        print("Deidentifying records")
        deidentify_records(ocr_files, formatted_ignore_words)
        

        # Generate recommendations with provided age and sex
        print("Generating recommendations")
        recommendations = generate_recommendations(age=age, sex=sex)

        # Extract data from FHIR file and create PDF
        directory = ocr_files
        #folderpath is global directory

        with open(f'{folderpath}/summary/chart.json', 'r') as file:
            json_data = json.load(file)

        extracted_info = extract_lforms_data(json.dumps(json_data))
        print(extracted_info)

        json_output = json.dumps(extracted_info, indent=4)
        write_text_to_pdf(directory, str(extracted_info))

        final_directory = f'{directory}/Darna_tesseract/'

        # Process PDF files
        process_pdf_files(directory)

        # Write the JSON output to a file
        with open(f'{directory}/fhir_output.json', 'w', encoding='utf-8') as f:
            f.write(json_output)

        # NLP Processing for summary, past medical history, medications, and screening
        json_file_path = f'{directory}/combined_output.json'
        keys_pmh = ['PMH', 'medical', 'past medical history', 'surgical', 'past']
        keys_meds = ['medications', 'MEDICATIONS:', 'medicine', 'meds']
        keys_summary = ['HPI', 'history', 'summary']
        keys_screening = ['RECS', 'RECOMMENDATIONS']

        # Process text data and create word clouds
        text_summary = process_directory_summary(directory, keys_summary)
        preprocess_and_create_wordcloud(text_summary, final_directory)

        text_meds = process_directory_meds(directory, keys_meds)
        text_screening = load_text_from_json_screening(json_file_path, keys_screening)
        text_pmh = process_directory_pmh(directory, keys_pmh)

        # Write processed texts to JSON
        keys = ("darnahi_summary", "darnahi_past_medical_history", "darnahi_medications", "darnahi_screening")
        texts = (text_summary, text_pmh, text_meds, text_screening)
        wordcloud_summary(keys, texts, final_directory)

        # CHROMA embedding
        chromadb_embed(directory)

        # Cleanup OCR files, but leave Darna_tesseract files
        whitelist = ["combined_output.json"]       
        whitelist_directory(directory, whitelist)
    
    except Exception as e:
        print(f"Error during processing: {e}")

##CALL ANALYZER AND AI ANALYSIS->SQLITE
if __name__ == "__main__":
            asyncio.run(main())
run_analyzer(age, sex, ocr_files, formatted_ignore_words)


