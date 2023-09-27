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
import pytesseract
from pdf2image import convert_from_path
import os
import variables
import variables2
import re
from PIL import Image, ImageFile
from datetime import datetime

ImageFile.LOAD_TRUNCATED_IMAGES = True

HS_path = os.getcwd()
folderpath = os.environ.get('FOLDERPATH')
if folderpath:
    ocr_files = f"{folderpath}/ocr_files"
else:
    print("Session FOLDERPATH environment variable not set.")

APP_dir = f"{HS_path}/install_module"
ocr_files = f"{folderpath}/ocr_files"
upload_dir = f"{folderpath}/upload"
ip_address = variables.ip_address
age = variables2.age
sex = variables2.sex
formatted_ignore_words = variables2.ignore_words


# Path to the Tesseract OCR executable (change this if necessary)
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

ocr_files_dir = f'{ocr_files}/'

output_dir = os.path.join(ocr_files_dir, 'Darna_tesseract')
os.makedirs(output_dir, exist_ok=True)

# Define the patterns to identify and deidentify
# remove anything after keyword
KEYWORDS_REGEX = r'(?i)(?:Name|DOB|Date of birth|Birth|Address|Phone|PATIENT|Patient|MRN|Medical Record Number|APT|House|Street|ST|zip|pin):.*?(\n|$)'

# remove specific words
IGNORE_REGEX = rf'(?i)(?<!\bNO\b[-.,])(?:NO\b[-.]|[Nn][Oo]\b[-.,]|{formatted_ignore_words})'

KEYWORDS_REPLACE = r'\1REDACT'
# NAME_REGEX = r'\b(?!(?:NO\b|NO\b[-.]|[Nn][Oo]\b[-.,]))(?:[A-Z][a-z]+\s){1,2}(?:[A-Z][a-z]+)(?<!\b[A-Z]{2}\b)\b'

DOB_REGEX = r'\b(?!(?:NO\b|NO\b[-.]|[Nn][Oo]\b[-.,]))(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2]\d|3[0-1])-\d{4}\b'
SSN_REGEX = r'\b(?!(?:NO\b|NO\b[-.]|[Nn][Oo]\b[-.,]))(\d{3})-(\d{4})\b'
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
ZIP_REGEX = r'\b(?!(?:NO\b|NOb[-.]|[Nn][Oo]\b[-.,]))([A-Z]{2}) (\d{5})\b'

def perform_ocr(image_path):
    # Implementation of the perform_ocr function
    try:
        # Perform OCR using Tesseract
        text = pytesseract.image_to_string(image_path)
        return text
    except pytesseract.TesseractError as e:
        print(f"Error processing image: {image_path}")
        print(f"Error message: {str(e)}")
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
    
    output_file = os.path.join(output_dir, 'ocr_results.txt')
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(directory):
            if os.path.basename(root) == 'Darna_tesseract':
                # Skip processing files in the 'Darna_tesseract' subdirectory
                continue

            for file_name in files:
                file_path = os.path.join(root, file_name)
                if os.path.isfile(file_path) and not file_name.startswith('.'):
                    if file_name.lower().endswith('.pdf'):
                        images = convert_pdf_to_images(file_path)
                        if images is not None:
                            for i, image in enumerate(images):
                                text = perform_ocr(image)
                                if text is not None:
                                    f.write(f"File: {file_name}, Page: {i+1}\n")
                                    f.write(text)
                                    f.write('\n\n')
                                image.close()
                    else:
                        text = perform_ocr(file_path)
                        if text is not None:
                            f.write(f"File: {file_name}\n")
                            f.write(text)
                            f.write('\n\n')

    print('OCR completed. Results saved in', output_file)

def add_deidentification_tags(text):
    return f'Deidentified Entry | {datetime.now().strftime("%m/%d/%Y")}\n{text}'

def generate_fake_text(match):
    return re.sub(KEYWORDS_REGEX, KEYWORDS_REPLACE, match.group())

def redact_zip_and_words(match):
    words = match.group(1)
    zip_code = match.group(2)
    redacted_words = 'ZZ ' * min(4, len(words.split()))
    redacted_zip = re.sub(r'\b\d{5}\b', '11111', zip_code)
    return redacted_words + redacted_zip

def deidentify_records():
    with open(f'{ocr_files}/Darna_tesseract/ocr_results.txt') as f:
        text = f.read()

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

#Collate images
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
                                pdf_img.close()
            except Exception as e:
                print(f"Error processing image: {file_path}")
                print(f"Error message: {str(e)}")
                continue

    if images:
        collated_file_name = f"collated_images_{datetime.now().strftime('%Y%m%d')}.png"
        output_collated_file = os.path.join(output_dir, collated_file_name)
        images[0].save(output_collated_file, save_all=True, append_images=images[1:], optimize=True)
        print(f"Images collated into {output_collated_file}")
    else:
        print("No valid images or PDFs found in the input directory.")



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
    	recommendations.append("Cervical Cancer: Screening -- Women aged 21 to 65 years")
    if age is not None and (age >= 50 and age <= 75):
        recommendations.append("Colorectal Cancer: Screening -- Adults aged 50 to 75 years")
    if age is not None and (age >= 18):
        recommendations.append("Blood pressure screening in office screening -- Adults aged 18 years and above")
    if sex == 'female' and age >= 45:
        recommendations.append("Screening women aged 45 and older for lipid disorders if they are at increased risk for coronary heart disease.")
    if sex == 'male' and age >= 35:
        recommendations.append("Screening Men aged 35 and older for lipid disorders with fasting lipid profile.")
    if sex == 'female' and (ancestry is not None):
        recommendations.append("BRCA-Related Cancer: Risk Assessment, Genetic Counseling, and Genetic Testing -- Women with a personal or family history of breast, ovarian, tubal, or peritoneal cancer or an ancestry associated with BRCA1/2 gene mutation")
    if sex == 'female' and age >= 35:
        recommendations.append("Breast Cancer: Medication Use to Reduce Risk -- Women at increased risk for breast cancer aged 35 years or older")
    if (sex == 'female') and age is not None and (age >= 50 and age <= 74):
        recommendations.append("Breast Cancer: Screening -- Women aged 50 to 74 years")
    if (sex == 'female' or (new_mother is not None and new_mother)):
        recommendations.append("Breastfeeding: Primary Care Interventions -- Pregnant women, new mothers, and their children")
    if sex == 'female':
        recommendations.append("Chlamydia and Gonorrhea: Screening -- Sexually active women, including pregnant persons")
    if age is not None and (age >= 45 and age <= 49):
        recommendations.append("Colorectal Cancer: Screening -- Adults aged 45 to 49 years")
    if age is not None and (age >= 8 and age <= 18):
        recommendations.append("Anxiety in Children and Adolescents: Screening -- Children and adolescents aged 8 to 18 years")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Aspirin Use to Prevent Preeclampsia and Related Morbidity and Mortality: Preventive Medication -- Pregnant persons at high risk for preeclampsia")
    if sex == 'pregnant':
        recommendations.append("Asymptomatic Bacteriuria in Adults: Screening -- Pregnant persons")
    if sex == 'male' and (ancestry is not None):
        recommendations.append("BRCA-Related Cancer: If screen positive, risk Assessment, Genetic Counseling, and Genetic Testing -- Men with a personal or family history of breast, ovarian, tubal, or peritoneal cancer or an ancestry associated with BRCA1/2 gene mutation")
    if sex == 'male' and age >= 65 and (pack_years is not None and pack_years > 0):
        recommendations.append("Abdominal Aortic Aneurysm: Screening -- Men aged 65 to 75 years who have ever smoked")
    if age is not None and (age >= 12 and age <= 18):
        recommendations.append("Depression and Suicide Risk in Children and Adolescents: Screening -- Adolescents aged 12 to 18 years")
    if age is not None and (age >= 65):
        recommendations.append("Falls Prevention in Community-Dwelling Older Adults: Interventions -- Adults 65 years or older")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)) and (age is not None and (age >= 24)):
        recommendations.append("Gestational Diabetes: Screening -- Asymptomatic pregnant persons at 24 weeks of gestation or after")
    if overweight_or_obesity is not None:
        recommendations.append("If elevated BMI consider Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults With Cardiovascular Risk Factors: Behavioral Counseling Interventions -- Adults with cardiovascular disease risk factors")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Healthy Weight and Weight Gain In Pregnancy: Behavioral Counseling Interventions -- Pregnant persons")
    if sex == 'female' and (age is not None and (age >= 18)):
        recommendations.append("Hepatitis B Virus Infection in Adolescents and Adults: Screening -- Adolescents and adults at increased risk for infection")
    if sex == 'male' and (age is not None and (age >= 18 and age <= 79)):
        recommendations.append("Hepatitis C Virus Infection in Adolescents and Adults: Screening -- Adults aged 18 to 79 years")
    if sex == 'female' and (age is not None and (age >= 14)):
        recommendations.append("Intimate Partner Violence, Elder Abuse, and Abuse of Vulnerable Adults: Screening -- Women of reproductive age")
    if age is not None and (age >= 6 and age <= 60):
        recommendations.append("Latent Tuberculosis Infection in Adults: Screening -- Asymptomatic adults at increased risk of latent tuberculosis infection (LTBI)")
    if (sex == 'male' or (sex == 'female' and (pregnant is not None and pregnant))) and (age is not None and (age >= 50 and age <= 80) and (pack_years is not None) and (smoking is not None)):
        recommendations.append("Lung Cancer screening if you smoked more that 20 pack years: Screening -- Adults aged 50 to 80 years who have a 20 pack-year smoking history and currently smoke or have quit within the past 15 years")
    if age is not None and (age >= 6 and age <= 18):
        recommendations.append("Obesity in Children and Adolescents: Screening -- Children and adolescents 6 years and older")
    if sex == 'female' and (age is not None and (age < 65)):
        recommendations.append("Osteoporosis to Prevent Fractures: Screening -- Postmenopausal women younger than 65 years at increased risk of osteoporosis")
    if sex == 'female' and (age is not None and (age >= 65)):
        recommendations.append("Osteoporosis to Prevent Fractures: Screening -- Women 65 years and older")
    if (sex == 'pregnant' or (pregnant is not None and pregnant) or (new_mother is not None)):
        recommendations.append("Perinatal Depression: Preventive Interventions -- Pregnant and postpartum persons")
    if age is not None and (age >= 35 and age <= 70):
        recommendations.append("Prediabetes and Type 2 Diabetes: Screening -- Asymptomatic adults aged 35 to 70 years who have overweight or obesity")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Preeclampsia: Screening -- Pregnant woman")
    if age is not None and (age < 5):
        recommendations.append("Prevention of Dental Caries in Children Younger Than 5 Years: Screening and Interventions -- Children younger than 5 years")
    if (sex == 'female' or (pregnant is not None and pregnant)) or (new_mother is not None):
        recommendations.append("Prevention of Dental Caries in Children Younger Than 5 Years: Screening and Interventions -- Children younger than 5 years")
    if (sex == 'pregnant' or (pregnant is not None and pregnant)) and (rh_d_negative is not None):
        recommendations.append("Rh(D) Incompatibility especially with Rh negative: Screening -- Unsensitized Rh(D)-negative pregnant women")
    if sex == 'male' or (sex == 'female' and (pregnant is not None and pregnant) or (new_mother is not None and new_mother)):
        recommendations.append("Screening for Depression in Adults -- General adult population")
    if sex == 'male' or (sex == 'female' and (pregnant is not None and pregnant)) or (new_mother is not None):
        recommendations.append("Sexually Transmitted Infections: Behavioral Counseling -- Sexually active adolescents and adults at increased risk")
    if (age is not None and (age >= 25)) or (new_mother is not None) or (sex == 'male' and (substance_abuse_risk is not None)):
        recommendations.append("Skin Cancer Prevention: Behavioral Counseling -- Adults, Young adults, adolescents, children, and parents of young children")
    if (age is not None and (age >= 40 and age <= 75)) and (cardiovascular_risk is not None) and (cardiovascular_risk_7_5_to_10 is not None):
        recommendations.append("Screen for CV risk and consider Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: Preventive Medication -- Adults aged 40 to 75 years who have 1 or more cardiovascular risk factors and an estimated 10-year cardiovascular disease (CVD) risk of 10% or greater")
    if sex == 'female' and (pregnant is not None and pregnant) and (ancestry is not None and ancestry == 'BRCA1/2 gene mutation'):
        recommendations.append("BRCA-Related Cancer: Risk Assessment, Genetic Counseling, and Genetic Testing -- Women with a personal or family history of breast, ovarian, tubal, or peritoneal cancer or an ancestry associated with BRCA1/2 gene mutation")
    if (age is not None and (age >= 6 and age <= 18)) or (sex == 'pregnant' or (pregnant is not None and pregnant)):
        recommendations.append("Tobacco Use in Children and Adolescents: Primary Care Interventions -- School-aged children and adolescents who have not started to use tobacco")
    if age is not None and (age >= 18) and (substance_abuse_risk is not None):
        recommendations.append("Unhealthy Alcohol Use in Adolescents and Adults: Screening and Behavioral Counseling Interventions -- Adults 18 years or older, including pregnant women")
    if age is not None and (age >= 13):
        recommendations.append("Unhealthy Drug Use: Screening -- Adults age 13 years or older")
    if age is not None and (age > 2 and age < 24) and skin_type is not None:
        recommendations.append("Skin Cancer: Counseling -- Fair-skinned individuals aged 6 months to 24 years with a family history of skin cancer or personal history of skin cancer, or who are at increased risk of skin cancer")
        
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
    recommendations_with_subheading = [subheading] + recommendations

    with open(f'{ocr_files}/Darna_tesseract/USPTF_Intent.txt', 'w') as file:
        file.write('\n\n\n'.join(recommendations_with_subheading))
        
        
# Process OCR files with provided input
process_ocr_files(ocr_files, age)


#create collated file
#collate_images(ocr_files, f"{ocr_files}/Darna_tesseract")


# Deidentify records
deidentify_records()


# Generate recommendations with provided age and sex
recommendations = generate_recommendations(age=age, sex=sex)




