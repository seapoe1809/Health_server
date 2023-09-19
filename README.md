# Health_server for Linux
The new DARNA. HI Version2. This allows you to self custody your health data on Linux Device accessible from ios, android or any device of your choice.

Health_Server is DARNA.HI V2

"Forward looking open source initiative preparing for the future!"

##DARNA Healthy Intent v2- An open source intiative - self custody of your health data
##Early stage. Beta and under development and isnt secure. Please take all steps to safeguard your data. 

What is this project?
======================
DARNA. HI v2 is a Forward looking project.

We are getting ready for the day the superior Language models would run locally on your device and you can ask it in a very Privacy centered way to give its 'Health-intents'(c) on your medical information . This project is an open-source software that helps bring together your health data that is currently saved in different places like electronic health records, fitness apps, and wearable devices. 

Now we hope with this software, you can bring all your health data together in one place on your computer at home. When you visit a new doctor, you can choose to share your health data with them on demand through email, link etc. This way, you have full custody of your health data and can decide who to share it with.


I created this project because I had trouble moving my own health data when I switched healthcare providers. As someone who works in the healthcare space, I see that current EHR solutions make it difficult to port your data, even though there are regulatory requirements to do so. It's frustrating to see that some institutions still rely on fax and scan to move data around, which shows how outdated and hidden these data porting techniques are. Given this pain point, I also see an exciting oppportunity with LLM's. I look forward to the day when superior Language models will run on your device at home.

This is version 2 of the project, and I anticipate that there will be many more iterations before it takes a good form. But my goal is to make it easier for people to take ownership of their health data and store it in one place on their own computer. They can shoose to interact with LLM's with their deidentified data if they wis. This way, they can decide who to share it with and have more control over their own health.

License?
========
This program is free software; you can redistribute it and/or modify it under the terms of the Darna modified GNU General Public License as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


basic requirements
=======================================
#linux os (Debian or Ubuntu distro preferred)
#python3
#git
#docker

Please note that this is only the second version of the project, and I plan on adding more features and making improvements in the future.

**step 1: Git clone and install Health_server**
=======================================

a) Make sure you have python3. If not go to https://www.python.org/ and update your Python. Once done do the following:

 Install Git and git clone Darna_local repo:
 
    sudo apt-get install git

 Git clone the Darna_local repo
              
    git clone https://github.com/seapoe1809/Health_server

 Make sure pip is installed to help install python modules

    sudo apt-get install python3-pip

Change directory into the Git repo directory
              
    cd Health_server

Now run Setup of Darna. HI. This should also start your Server.
              
              
    python3 setup_darna.py

The server should be active at port :3001. The flask server when launched will give you the IP address at which it launched. You could now navigate to that http://your_ip_adddress:3001 with any mobile device and access the server.             
        
To give feedback, please go to 'Information' card and send email to me. Or you could start a debug here itself.



**Troubleshooting**
===================
If you have trouble launching with $python3 darna.py, you might have to speciy the version of python. eg. in venv 

    python3.6 darna.py 


The default username password: ADMIN 'health' and USER1 'wellness'. You could change it 'Information' card if you wish.



**Step3: Download your health data in the health_server folder:**
=================================================================

a) Download ios health files: On apple health app, click the profile icon, then choose "Export All Health Data" and save the zip file in files. Then click on 'UPLOAD' card on your flask server and download to your server.
 
b) If you have data on EPIC MyChart or your doctors gateway, login and go to Menu, search 'sharing' or 'export', click 'yourself' and download a zip file to 'files'.  Then click on 'UPLOAD' card on your flask server and download to your server.
 
c) PDF's and JPGS on mobile: 'UPLOAD' card of server and follow instructions to download to your server.

d) Once files are downloaded, to UPLOAD directory, click tha 'RUN SYNC' card to move files and start Grafana.

e) Tips are in 'INFORMATION' card of server. 

f)  The default username password: ADMIN 'health' and USER1 'wellness'. You could change it 'Information' card if you wish. For Grafana is user:'admin', password:'health'.

Snapshots:
=============


<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5771.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5772.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5781.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5773.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5782.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5774.jpeg" width =300, height=550>
<img src="https://user-images.githubusercontent.com/82007659/243430051-478d54cd-5e25-4134-ba6c-21a67220b5f7.jpg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5775.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5783.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5778.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5785.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5786.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5779.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5777.jpeg" width =300, height=550>


<img src="https://github.com/seapoe1809/Darna/assets/82007659/f1c26f0c-fb38-48e1-8551-5b36de750c91" width =300, height=550>
<img src="https://github.com/seapoe1809/Darna/assets/82007659/f718336b-e545-43e5-aa50-aa004c274954" width =300, height=550>
<img src="https://github.com/seapoe1809/Darna/assets/82007659/86ab0bce-a0da-4330-9849-2d1600262f27" width =300, height=550>
<img src="https://github.com/seapoe1809/Darna/assets/82007659/c8272ff2-69db-4984-8ebe-469cb02ee7ab" width =300, height=550>

<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5787.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5789.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5790.jpeg" width =300, height=550>
<img src="https://github.com/seapoe1809/assets/blob/main/darna_local_assets/IMG_5791.jpeg" width =300, height=550>

 
**PIE IN SKY:** Is still under construction. I imagine it a way download external apps to run on your server. It adds more functionalities and dimensions to our server. Cheers! 
 
 Hope you like it! Please share feedback and let me know if you woudl like to contribute to this project. You could send feedback by commenting on this repo or going to 'INFORMATiON' card and clicking on link saying 'email' the writer of repo.
 


