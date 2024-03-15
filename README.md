Health_Server is DARNA.HI V2

DEMO version with features turned off: http://seapoe1809.pythonanywhere.com/login
ADMIN 'health', USER1 'wellness'; swipe left to navigate

"No Fear! Forward looking open source Health server initiative!"

##DARNA Healthy Intent v2- An open source intiative - self custody of your health data
##Early stage. Beta and under development and isnt secure. Please take all steps to safeguard your data. 

What is this project?
======================
DARNA. HI v2 is a Forward looking project.

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/darnav2_mktg.png" width =300, height=550>

We are getting ready for the day when powerful Language models would run locally on your device and you can ask it in a very Privacy centered questions very specific to your health . In Darnahi v2.2 a language model (llama 1B) is being used to process personal health data and provide answers to questions specific to an individual's health situation. Additionally, natural language preprocessing (NLP) techniques are being used, along with a retrieval augmented architecture (RAG) to process and understand the health data by the local LLM.

In future we hope to have a trained lightweight large language model (LLM) being employed to interpret the processed data and generate relevant health intents or responses tailored to an individual's queries about their health. To summarize Darnahi aims to leverage advanced language AI capabilities to give personalized health insights and recommendations by analyzing someone's specific health information and answering their questions in that context.

The core components are NLP for understanding natural language, a RAG model for retrieving and processing relevant data, and a local LLM that ties it together by mapping the data to the queries and providing contextualized health-related output.

This project is an Free and open-source software that helps bring together your health data that is currently saved in different places like electronic health records, fitness apps, and wearable devices. We wish to provide a way to aggregate your health data. One stop to bring all your health data together on your secure computer at home. When you visit a new doctor, you can choose to share your encrypted health data with them on demand through QR code, email, link etc. This way, you have full custody of your health data and can decide who to share it with and what to do with it.

WHY I CARE ABOUT THIS:
I created this project because I had trouble moving my own health data when I switched healthcare providers. As someone who works in the healthcare space, I see that current EHR solutions make it difficult to port your data, even though there are regulatory requirements to do so. It's frustrating to see that some institutions still rely on fax and scan to move data around, which shows how outdated and hidden these data porting techniques are. Given this pain point, I also see an exciting oppportunity with LLM's. I look forward to the day when superior Language models will run on your device at home.

This is version 2.2 of the project, and I anticipate that there will be many more iterations and help from OSS community before it takes a good form. My goal is to make it easier for people to take ownership of their health data and store it in one place on their own computer. They can shoose to interact with local LLM or use their deidentified data to interact with powerful public LLM if they wish. Darnahi provides both- a way to interact with local LLM and also to deidentify their data seamlessly/ This way, they can decide who to share it with, how to use it and finally have more control over their own health.

License? 
========
This program is free software; you can redistribute it and/or modify it under the terms of the Darna modified GNU General Public License as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You would of course have to credit Darnahi.


basic requirements
=======================================
#linux os (Debian or Ubuntu distro preferred)
#GPU enabled computer (preferred for running local LLM)
#python3
#git
#docker (if you wish to use dockerized apps in sky market)

SAFE AND SECURE
===============
We are trying to take all steps to keep it safe and secure. Please note this is still a beta version. All software runs in python Virtual Env and dockerized containers. To delete it, delete the Health_server folder and thats it!

Please note that this is only the second version of the project, and I plan on adding more features and making improvements in the future. You can expect constant improvement in the future.

**step 1: Git clone and install Health_server**
==============================================

Make sure you have python3. If not go to https://www.python.org/. Once done do the following:

(Optional) Install Git and git clone Darna_local repo: 
 (skip this step if git already installed)
 
    sudo apt-get install git

 Git clone the Darna_local repo
              
    git clone https://github.com/seapoe1809/Health_server

(Optional) Make sure pip is installed to help install python modules 
 (skip this step if pip is already installed)

    sudo apt-get install python3-pip

Change directory into the Health_server directory
              
    cd Health_server

Now install 'distro' and subsequently run Setup. This should also start your Server.

    pip install pip-tools distro      
    python3 setup_darna.py

Once started the server should be active at port :3001. The browser should auto launch and take you there. You could easily access on the home computer at http://localhost:3001 .The flask server when launched will give you the IP address at which it launched. You could now navigate to that http://your_ip_adddress:3001 with any mobile device and access the server.  

SHUTDOWN THE SERVER
===================
The app allows you to shut down the server remotely from anywhere. Go to the 'INFORMATION' section and scroll to the bottom to find the 'kill switch' option. Using this will shut down the server and the local language model running on it. However, to restart the server, you need to be physically at your home computer.

Note: This might not shutdownt he docker containers from the sky store. You would have to remove them on your home computer.

RESTART THE SERVER
==================
Click on the Darnahi icon from launcher. 
OR go to Health_server directory and type:

    cd Health_server
    ./darna_launch.sh

DELETE THE SERVER
=================
If you don't want to use the health server app anymore, you can simply delete the entire 'Health_server' folder. Since the software is running in virtual environments, deleting that folder will completely remove it with just one click. No need for any special shutdown process, just delete the folder to get rid of it all.

FEEDBACK
========
        
To give feedback, please go to 'Information' card and click on last link that allows you to email me. Or you could start a debug thread on github itself.

**Step 2: Upload your health data in the health_server folder:**
=================================================================

a) Upload health files: On health app, search how to 'get your data', then choose "Export All Health Data" and save the file in iOS files. Then click on 'UPLOAD' icon (+) on your Darnahi server, choose file and upload to your server.
 
b) If you have data on EPIC MyChart or Cerner er Athena etc or your doctors gateway. Go to 'Sky App Store', click on the 'Portal Access Card', choose your EMR provider, login and go to Menu, search 'sharing' or 'export', click 'yourself' and download a zip file to 'files'.  Then click on 'UPLOAD' card on your flask server and download to your server.
 
c) PDF's and JPGS on mobile: 'UPLOAD' (+) icon on the Darnahi server and follow instructions to upload to your server.

d) Tips are in 'INFORMATION' card of server. 

e)  The default username password: ADMIN 'health' and USER1 'wellness'. You could change it 'Information' card if you wish. For Grafana is user:'admin', password:'health'.


**Troubleshooting**
===================
If you encounter the missing module _sqlite3 error when you start venv. Its a known error with older python Venv. You might need to uninstall python3 and reinstall. Its preferred if you download directly from python.org. 

    sudo apt update
    sudo apt install libsqlite3-dev
    sudo apt install python3 python3-venv

You can check with:

    python3
    import sqlite3
 
OR 
Build python3 from source: https://github.com/seapoe1809/assets/blob/main/Python_from_source_LINUX

The default username password: ADMIN 'health' and USER1 'wellness'. You could change it 'Information' card if you wish.

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/1-2-3.png" width =300, height=550>
**
Venv error:** 
Error creating venv could mean venv need to be installed or upgraded

    python -m pip install --upgrade venv



Snapshots:
=============


<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5864.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5865.png" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5866.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5867.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5868.png" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5869.jpeg" width =300, height=550>
<img src="https://user-images.githubusercontent.com/82007659/243430051-478d54cd-5e25-4134-ba6c-21a67220b5f7.jpg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5870.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5871.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5872.png" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5873.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5874.png" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5877.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5878.png" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/darna_information.png" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/deidentify.png" width =300, height=550>

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5879.jpeg" width =300, height=550>

**Code for Install Module is at : **
========================================

https://github.com/pnmeka/install_module/

Install Module is a set of **dockerized container apps** that you could add to the 'Pie in Sky'. It is completely optional.
It is maintained by another user.

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5880.png" width =300, height=550>

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5881.jpeg" width =300, height=550>

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5884.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5895.png" width =300, height=550>

****Why XMR here?****
=====================

In the realm of financial privacy, the use of cryptocurrencies like Monero can play a role in enhancing users' security. Monero is a privacy-focused cryptocurrency that provides anonymity and obfuscation of transaction details. This can be particularly relevant in healthcare contexts.

You could choose to support the XMR network by running a node on your computer. More nodes make the network more resilient and futureproofs it.

========================================================================================

<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5885.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5892.jpeg" width =300, height=550>




<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5887.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/IMG_5894.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/DARNA_HI_v2_assets/pic11.png" width =300, height=550>




**PIE IN SKY:** I imagine it a way download external dockerized apps to run on your server. It adds more functionalities and dimensions to our server. Cheers! 
 
 Hope you like it! Please share feedback and let me know if you woudl like to contribute to this project. You could send feedback by commenting on this repo or going to 'INFORMATiON' card and clicking on link saying 'email' the writer of repo.
 



