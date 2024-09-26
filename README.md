
#### NOTE: IN PROCESS OF UPDATING. AVAILABLE FOR USE ON SEPT 29  ######
**DARNA HEALTH INTELLIGENCE V2.3**


**Self Hosted Health_Server is DARNA.HI V2.3**

**Darnahi's Vision:**
=================

This tool wants to be your personal health intelligent assistant. It aims to be built around AI core. The local running LLM will be able to understand your personal health information while being private and secure. For example you'll be able to ask Darnabot any health questions you have, and it will provide answers specifically based on your own health details. It's like having a knowledgeable health assistant available whenever you need, but the assitant is actually intelligent , local running program giving you personalized suggestions while protecting your privacy.

CAUTION: This tool is not a replacement for a Doctor. For medical advice, please consult with a Healthcare professional. Darnahi only aims to provide Health suggestions/information which might not be evidence based and has risk of hallucinations. Early stage. Beta and under development and isnt secure. Please take all steps to safeguard your data. 

**Key words:** 

- Self Hosted (This means you have to run this on your own linux computer and all your data stays on your computer; your data does not leave your computer and security is limited by your own computer security),
- Liinux,
- python,
- Open Source,
- Free,
- AI/ML,
- LLM (ollama, mistral-nemo)
- No Internet required to run it

DEMO version with features turned off: http://seapoe1809.pythonanywhere.com/login
ADMIN 
password'health' 
USER1 
password 'wellness'


"Forward looking open source Health server initiative! Put simply, it aspires to be your personal health assistant."

**Short VIDEO DEMO:**

VIDEO ABOUT DARNAHI LANDING PAGE

[darnahi_landing.webm](https://github.com/user-attachments/assets/a6f61b33-9b1e-4f46-bf83-9a35bfce4b3b)


1. Darnahi Home:

    1. Chartit to log your basic information in FHIR R4 format
    2. Ability to upload and save your files to your self hosted file server
    3. Ability to view dicom files, xml files, health suggestions for your age
    4. Ability to encrypt and zip your files securely and remotely

2. Darnabot

   VIDEO ABOUT DARNABOT IN ACTION
   
[darnabot2.webm](https://github.com/user-attachments/assets/cddca3d3-1012-4a01-9d09-cb1c2779978c)

New and improved Darnabot, Darnahi's AI engine
#requires ollama and mistral-nemo
    1. ask questions of your medical records that is stored as structured and unstructured RAG
    2. Local running LLM and Local running darnahi #privacy
    3. AI engine that uses NLP to analyze your health files to create health screening recommendations (USPTF based), wordclouds, RAG for darnabot
    4. Symptom logger (optional use of AI to generate notes) for storage in darnahi file server). Can be shared with your provider if you wish in pdf's 

3. Darnahi Optional Modules
   VIDEO ABOUT DARNAHI OPTIONAL MODULES IN ACTION
*CLICK HERE*
[darnahi optional modules](https://nostrcheck.me/media/49a2ed6afaabf19d0570adab526a346266be552e65ccbd562871a32f79df865d/ea9801cb687c5ff0e78d43246827d4f1692d4bccafc8c1d17203c0347482c2f9.mp4)


Darnahi optional modules include: 
1. weight/ bp/ glucose/ water tracker
    
2. IBS module- tracks your dietary and bowel habits; AI FODMAP engine; exercises to manage your IBS; know your IBS

3. Immunization passport- to track and keep record of your immunizations; AI travel advisor; travel map

4. Tailscale to allow remote access

5. Portal to share your encrypted zipped health docs securely

6. Remote docker container manager
    
##DARNA Healthy Intelligence v2.3- An open source, self hosted intiative - self custody of your health data

##Early stage. Beta and under development and isnt secure. Please take all steps to safeguard your data. 





**Vision: **

This is a forever open source, self hosted personal Health intelligent assistant.


What is this project?
======================
DARNA. HI v2.3 is a Forward looking project.

 <img src="https://github.com/seapoe1809/Health_server/blob/main/static/darnav2_mktg.png" width =300, height=550>

About Darnahi
=============
Darnahi is a self hosted app that allows you to securely self manage your medical records and can provide personalized health suggestions and answers using local running LLM's. To summarize:

- Darnahi is a personal health assistant that runs on Linux.
- Is Locally Self Hosted
- It keeps your medical data safe at home (as safe as you keep your computer). 
- It can suggest health screening (USPTF) based on your age and gender. 
- It stores your medication list and medical history in FHIR R4 format. 
- It analyzes your health information using natural language processing and AI. 
- It can answer simple questions about your saved health data using local LLM

**Disclaimer: **

Use at your own Risk. See License document. It is still in beta. Take all steps to safeguard your data. The security will be as safe as your computer is. Keep your computer encrypted. Dont share password.

This tool is not a replacement for a Doctor. For medical advice, please consult with a Healthcare professional. Darnahi only aims to provide Health suggestions/information which might not be evidence based. LLMs are known to hallucinate.

 
Who is it for:
==============
- If you want to take control of your medical information and share it easily with new doctors, this tool is for you. With this program you can create an encrypted health passport. 
- If you wish to Self Host
- You are privacy conscious.
- You have some computer skills and an ability to use Linux or set up a virtual Linux machine. 
- Support Open Source


This project is an Free and open-source local hostedd software that helps bring together your health data that is currently saved in different places like electronic health records, fitness apps, and wearable devices. Darnahi wishes to provide a way to aggregate your health data. One stop to bring all your health data together on your secure computer at home. When you visit a new doctor, you can choose to share your encrypted health data with them on demand through QR code, email, link etc. This way, you have full custody of your health data and can decide who to share it with and what to do with it. 
In not so distant future we hope to have specialized trained lightweight large language model (LLM) running on your laptop or phone to interpret your health data, generate relevant health intents and responses tailored to an individual's queries about their health. At this time we rely on Mistral-nemo running using Ollama.

**Disclaimer: **

Use at your own Risk. See License document. It is still beta. Take all steps to safeguard your data. The security will be as safe as your computer is. Keep your computer encrypted. Dont share password.
This tool is not a replacement for a Doctor. For medical advice, please consult with a Healthcare professional. Darnahi only aims to provide Health suggestions/information which might not be evidence based.

WHY I CARE ABOUT THIS:
I created this project because I had trouble moving my own health data when I switched healthcare providers. As someone who works in the healthcare space, I see that current EHR solutions make it difficult to port your data, even though there are regulatory requirements to do so. It's frustrating to see that some institutions still rely on fax and scan to move data around, which shows how outdated and hidden these data porting techniques are.

This is version 2.3 of the project, and I anticipate that there will be many more iterations and help from OSS community before it takes a good form. My goal is to make it easier for people to take ownership of their health data and store it in one place on their own computer. They can shoose to interact with local LLM or use their deidentified data to interact with powerful public LLM if they wish. Darnahi provides both- a way to interact with local LLM and also to deidentify their data seamlessly/ This way, they can decide who to share it with, how to use it and finally have more control over their own health.

License? 
========
This program is free software; you can redistribute it and/or modify it under the terms of the Darna modified GNU General Public License as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You would of course have to credit Darnahi.


basic requirements
=======================================
#linux os (Debian or Ubuntu distro preferred)
#ollama and model mistral-nemo
#GPU enabled computer (preferred for running local LLM)
#python3
#git
#docker (for optional docker apps)

SAFE AND SECURE
===============
We are trying to take all steps to keep it safe and secure. Please note this is still a beta version. The security will be as safe as your computer is. Keep your computer encrypted. Dont share password.
Darnahi is Self Hosted -This means you have to run this on your own linux computer and all your data stays on your computer; your data does not leave your computer and security is limited by your own computer security




**step 1: Git clone and install Health_server**
==============================================

Make sure you have python3. If not go to https://www.python.org/. Once done do the following:

*(Optional)* Install Git and git clone Darna_local repo: 
 (skip this step if git already installed)
 
    sudo apt-get install git


*(Optional)* Make sure pip is installed to help install python modules 
 (skip this step if pip is already installed)

    sudo apt-get install python3-pip
    
*(Optional)* Make sure venv is availabls 
 (skip this step if pip is already installed)

    sudo apt install python3.10-venv    



Git clone the Darna_local repo
              
    git clone https://github.com/seapoe1809/Health_server
    
Change directory into the Health_server directory
              
    cd Health_server

Now install 'distro' and subsequently run Setup. This should also start your Server.

    pip install pip-tools distro      
    python3 setup_darna.py

Once started the server should be active at port :3001. The browser should auto launch and take you there. You could easily access on the home computer at http://localhost:3001 .The flask server when launched will give you the IP address at which it launched. You could now navigate to that http://your_ip_adddress:3001 with any mobile device and access the server.

INSTALLING OLLAMA for Local LLM
===============================

Darnahi currently uses Ollama for its stable Local LLMs (https://ollama.com/download)

    curl -fsSL https://ollama.com/install.sh | sh
    
Time to get the model
    
    ollama pull mistral-nemo
    


SHUTDOWN THE SERVER
===================
The app allows you to shut down the server remotely from anywhere. Go to the 'INFORMATION' section and scroll to the bottom to find the 'kill switch' option. Using this will shut down the server and the local language model running on it. However, to restart the server, you need to be physically at your home computer.

Note: This might not shutdownt he docker containers from the sky store. You would have to remove them on your home computer individually.

RESTARTING THE SERVER
=====================
Click on the Darnahi icon from launcher. 
OR go to Health_server directory and type:

    cd Health_server
    ./darna_launch.sh


DELETING DARNAHI
================
All software runs in python Venv and dockerized containers.
If you don't want to use the health server app anymore, you can simply delete the entire 'Health_server' folder. Since the software is running in virtual environments, deleting that folder will completely remove it with just one click. No need for any special shutdown process, just delete the folder to get rid of it all.

FEEDBACK
========
        
To give feedback, please go to 'Information' card and click on last link that allows you to email me. Or you could start a debug thread on github itself.



**USING DARNAHI: Upload your health data in the health_server folder:**
=================================================================

a) Upload health files: On health app, search how to 'get your data', then choose "Export All Health Data" and save the file in iOS files. Then click on 'UPLOAD' icon (+) on your Darnahi server, choose file and upload to your server.
 
b) If you have data on EPIC MyChart or Cerner er Athena etc or your doctors gateway. Go to 'Sky App Store', click on the 'Portal Access Card', choose your EMR provider, login and go to Menu, search 'sharing' or 'export', click 'yourself' and download a zip file to 'files'.  Then click on 'UPLOAD' card on your flask server and download to your server.
 
c) PDF's and JPGS on mobile: 'UPLOAD' (+) icon on the Darnahi server and follow instructions to upload to your server.

d) Tips are in 'INFORMATION' card of server. 

e)  The default username password: ADMIN 'health' and USER1 'wellness'. You could change it 'Information' card if you wish. For Grafana is user:'admin', password:'health'.

f) Update Chartit with your basic demographic information that is stored in FHIR R4 format

RUN AI via Darnabot:
===================
Here it what the Run AI does. It might need you to enter words to de-identify separated by "|"
    -It generates a list of USPTF recommended medical screenings for your age/ sex based on US guidelines
    -It uses OCR to extract data from your uploaded files
    -It runs NLP to get medical data organized by type
    -It vectorizes and chunks up the data and creates a database
    -It creates a visual word cloud 
    -It creates a RAG for the local LLM which allows the local LLM to provide personalized answers to your health related questions

 <img src="https://github.com/seapoe1809/Health_server/blob/main/static/darna_information.png" width =300, height=550>


 <img src="https://github.com/seapoe1809/Health_server/blob/main/static/deidentify.png" width =300, height=550>


CHART IT CARD:
============== 
 It allows you to enter your personal basic demographics, allergies, past medical history and update your list of medications in a standard FHIR R4 format.
    This information gets stored in the 'summary' folder.
    When you share an encrypted zip file with your healthcare provider, they can access your past medical history and current medication list in a format compatible with electronic medical records (EMRs).


HEALTH FILES CARD:
==================
The dropdown menu provides several options:
    View health files stored in the 'summary' folder including visualizing data in dicom format.
    View the personalized health intents generated when you run the 'Analyze' function.
    View your de-identified data, which could be useful for interacting with public language models.
    View your word cloud visualization.
    Create Encrypted zip of the health files stored in the 'summary' folder.


VIEW FILES
==========
This card allows you to view the folders on your server. You can access and view XML files, PDF files as well as DICOM files. DICOM files are a standard format used for medical imaging data like X-rays, CT scans, etc. A sample DICOM file is included on the server for demonstration purposes.

So in simple terms, this gives you the ability to navigate the server's file system and open XML document files or medical imaging files in the DICOM format, with an example DICOM file provided.
Note: some XML health files need a supporting styles.xsl file alongwith to allow viewing.

**DARNA BOT**
============


Darnahi currenlty uses Ollama for local LLM's and specifically Mistral-Nemo:

Structured and Unstructured RAG architecture: This helps the LLM quickly find and understand the specific health information it needs from your medical data.
    
ChromaDB: This database that organizes and stores your health details in for Darnabot.



**OPTIONAL APPS:** 
==================
Install module includes optional apps that can be downloaded on Darnahi. They are dockerized apps and run in containers. Cheers! 
More information is available within Darnahi
1. weight/ bp/ glucose/ water tracker
2. IBS module- tracks your dietary and bowel habits; AI FODMAP engine; exercises to manage your IBS; know your IBS
3. Immunization passport- to track and keep record of your immunizations; AI travel advisor; travel map
4. Tailscale to allow remote access
5. Portal to share your encrypted zipped health docs securely
6. Remote docker container manager
7. A portal for you to be able to download your information from local health providers. It isnt exhaustive.

**Bookmark to your device iphone:**
=====================================
Navigate in the browser to Darnahi at <ip_address>:3001. Then click [^] and choose 'Add to Home Screen' and 'Add'.

**Update Install Module**
==========================
In the future as more optional modules are added, all you have to do is run update_install_module.sh and your folder will be updated to the latest git repo. This file serves this function

**Disclaimer: **

Use at your own Risk. See License document. It is still beta. Take all steps to safeguard your data. The security will be as safe as your computer is. Keep your computer encrypted. Dont share password.
This tool is not a replacement for a Doctor. For medical advice, please consult with a Healthcare professional. Darnahi only aims to provide Health suggestions/information which might not be evidence based.

**Troubleshooting**
===================

If you notice a newly installed module doesnt appear after installation. 

    Click refresh of the browser of the home page of optional module 

Newly installed Docker container is acting up

    docker restart <docker-optional-module>
    
If you encounter the missing module _sqlite3 error when you start venv. Its a known error with older python Venv. You might need to uninstall python3 and reinstall. Its preferred if you download directly from python.org. 

    sudo apt update
    sudo apt install libsqlite3-dev
    sudo apt install python3 python3-venv

You can check with:

    python3
    import sqlite3
 
OR 
Build python3 from source: https://github.com/seapoe1809/assets/blob/main/Python_from_source_LINUX


**
Venv error:** 
Error creating venv could mean venv need to be installed or upgraded

    python -m pip install --upgrade venv

If computer sleeps and wakes, the CUDA breaks while running Darnabot as part of its memory offload mechanism. Restarting fixes it. will add a fix next update. 






##FEEDBACK##
=============
 Hope you like it! Please share feedback and let me know if you would like to contribute to this project. You could send feedback by commenting on this repo or going to 'INFORMATiON' card and clicking on link saying 'email' the writer of repo.
 



