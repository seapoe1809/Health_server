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


import gradio as gr
import os
from ollama import AsyncClient
import asyncio

model='gemma3:4b'

image_path = os.path.join(os.getcwd(), "uploads", "impetigo.jpeg")


class HealthMotivator:
    async def get_motivation(self, result):
        print('Result', result)
        messages = [
            {"role": "system", "content": "You are Darnabot, strep throat and rheumatic fever expert. Provide a brief message given context. No preamble."},
            {"role": "user", "content": f"Given clinical context: {result} give relevant information about strep throat, rheumatic fever "},
        ]
        
        #async for part in await AsyncClient().chat(model='mistral-nemo', messages=messages, stream=True):
            #chunk=part['message']['content']
            #yield chunk
        try:    
            OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            async for part in await AsyncClient(host=OLLAMA_HOST).chat(model, messages=messages, stream=True):
                yield part['message']['content']
        except Exception as e:
            yield f"Remember to take care of your health. Please see links below! (Error: {str(e)})"



motivator = HealthMotivator()

async def darnabot_says(result):
    motivation = "Please see a Doctor for advice! "   
    async for chunk in motivator.get_motivation(result):
        motivation += chunk
        yield motivation
        
# Questionnaire
def calculate_strep_risk(high_risk, age, exudate, nodes, fever, cough):
    score = 0
    
    # Add 1 point for each criterion
    if age == "3-14":  # Fixed: changed age_range to age
        score += 1
    
    if exudate:
        score += 1
        
    if nodes:
        score += 1
        
    if fever:
        score += 1
        
    if cough == "Absent":
        score += 1
    
    # Determine recommendation based on score
    if high_risk:
        likelihood = "Moderately High despite score given symptoms."
        recommendation = "Strep test advised as risk score is equivalent to 11-17%"
    elif score < 1:
        likelihood = "5%-10%"
        recommendation = "No testing advised as LOW RISK. Likely viral!"
    elif score == 2:
        likelihood = "11%-17%"
        recommendation = "Strep test advised given your risk "
    elif score == 3:
        likelihood = "28%-35%"
        recommendation = "Strep test advised given your risk"
    elif score >= 4:
        likelihood = ">50%"
        recommendation = "Testing advised strongly. Even consider empiric antibiotics. **Dosing of Amoxicillin** is 45 mg/kg/day split twice a day for 10 days OR **Azithromycin** 12 mg/kg once a day for 5 days in Penicillin allergy"
    else:  # score == 1
        likelihood = "5%-10%"
        recommendation = "No testing advised"
    
    return {
        "score": score,
        "likelihood": likelihood,
        "recommendation": recommendation,
        "summary": f"Risk Score: {score}/5 - {likelihood} likelihood of Strep. {recommendation}."
    }

# Fixed: Added the missing check_strep function
def check_strep(high_risk, age, exudate, nodes, fever, cough):
    result = calculate_strep_risk(high_risk, age, exudate, nodes, fever, cough)
    return result["summary"]

# Gradio interface
with gr.Blocks(theme='Taithrah/Minimal', css="footer{display:none !important}") as demo:
    gr.Markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center; height: 100%; color: #FFFFFF; background-color: #4c00b0; font-weight: bold;'>Strep Throat Checker</div>")
   
    Introduction = f"""Summary: 
    \n* Strep throat is a bacterial infection in the throat and tonsils, with long lasting effects in kids.
    \n* A quick test is available to see if you have strep throat.
    \n* Antibiotics can cure strep throat.

 \n**What is Strep Throat?**
\nStrep throat is a type of throat infection caused by bacteria called *Group A Streptococcus*. Unlike most sore throats, which are caused by viruses, strep throat is bacterial and requires antibiotics for treatment. While it can affect anyone, it's more common in school-aged children and spreads easily through coughing, sneezing, or sharing food and drinks. Only about 1 in 10 adults and 3 in 10 children with a sore throat actually have strep throat, so testing is often needed to tell the difference.

**Symptoms to Watch For**
\nSymptoms of strep throat usually appear 2 to 5 days after being exposed. Common signs include a sudden, severe sore throat, pain when swallowing, and a fever. You might also notice red and swollen tonsils, white patches or pus on the tonsils, or small red spots on the roof of the mouth. Swollen lymph nodes in the neck are also common. Children may also experience headaches, stomach pain, nausea, vomiting, or a red rash known as scarlet fever.


**Possible Complications**
\nIf left untreated, strep throat can lead to serious complications. The bacteria may spread and cause problems such as ear infections, sinus infections, or abscesses around the tonsils. In rare cases, it can lead to more severe conditions like rheumatic fever, which can affect the heart, joints, and nervous system, or a kidney disease called post-streptococcal glomerulonephritis. Prompt treatment with antibiotics usually prevents these complications.

**Who’s at Risk and How It Spreads**
\nStrep throat is most common in children between the ages of 5 and 15, but anyone in close contact with someone infected can get it. It spreads easily in crowded settings like schools, daycare centers, shelters, or military barracks. Adults who work with children or live with someone who has strep throat are also at higher risk. Because it's contagious, good hygiene—like frequent handwashing and not sharing utensils—is important to prevent its spread.


***Take the self assessment test to assess your risk!***
"""
    
    Rheumatic_fever = """Summary: 
    \n* Rheumatic fever is an inflammatory condition that can affect the heart, joints, brain, and skin few weeks after untreated strep throat or streep infection!    
   \n* Most worrisome symptom is heart involvement as it can damage heart valves.
   \n* Symptoms can include worsening neuropsychiatric symptoms called PANDAS- behavior tics/ ocd/ anxiety.
   \n* Treatment focuses on managing inflammation and symptoms. Ideally treat before you get there!

    
    \n**What Is Rheumatic Fever?**
\nRheumatic fever is a serious condition that can develop after a bacterial infection such as strep throat, scarlet fever, or impetigo caused by *Group A Streptococcus* (or group A strep). It’s not the infection itself that causes the illness, but rather the body’s immune system overreacting and attacking its own healthy tissues. This immune response can lead to inflammation in several parts of the body, including the heart, joints, brain, and skin. Rheumatic fever is most common in school-aged children and usually appears 1 to 5 weeks after a strep infection.

**Symptoms and Warning Signs**
\nSymptoms of rheumatic fever can vary widely. Common signs include painful, swollen joints (especially in the knees, ankles, elbows, or wrists), fever, fatigue, and a movement disorder called chorea, which causes involuntary jerking movements. Some people may also experience a rash with pink rings and a clear center, or small, painless lumps near the joints. When the heart is affected, symptoms may include chest pain, shortness of breath, or a rapid heartbeat. Doctors may also detect a new heart murmur, an enlarged heart, or fluid around the heart—all of which indicate a more serious problem.

**Complications and Risk Factors**
\nIf not treated properly, rheumatic fever can lead to long-term damage to the heart, a condition known as rheumatic heart disease. This occurs when the valves of the heart are scarred or weakened, making it harder for the heart to function properly. In severe cases, surgery may be needed, and untreated rheumatic heart disease can even be fatal. Children between the ages of 5 and 15 are most at risk, especially those who live in crowded environments like schools or shelters where strep infections can spread easily. People who’ve had rheumatic fever before are more likely to get it again if they get another strep infection.

**Related Condition: PANDAS**
\nAnother possible complication linked to strep infections in children is a condition called PANDAS, which stands for Pediatric Autoimmune Neuropsychiatric Disorders Associated with Streptococcal infections. In PANDAS, the immune system mistakenly affects the brain, leading to sudden onset of symptoms like obsessive-compulsive behaviors (OCD), anxiety, tics, or mood changes. These symptoms can appear almost overnight following a strep infection. While research is ongoing, early recognition and treatment of strep infections may help reduce the risk of both PANDAS and rheumatic fever.


**Arthritis: Painful and Swollen Joints**
\nOne of the most common symptoms of rheumatic fever is arthritis, which causes painful, tender, and swollen joints. It usually starts in the larger joints, such as the knees, ankles, elbows, and wrists. The pain may move from one joint to another over time, and though uncomfortable, this type of joint inflammation usually doesn’t cause permanent damage if treated early. However, recurring joint pain is a signal to seek medical care, especially if it follows a recent strep infection.


**Heart Involvement: A Serious Concern**
\nRheumatic fever can seriously affect the heart, particularly the valves, which help blood flow in the correct direction through the heart. This can lead to rheumatic heart disease. Symptoms might include chest pain, a rapid or irregular heartbeat, shortness of breath, and fatigue. In some cases, doctors may hear a new heart murmur or detect fluid around the heart. Long-term damage can be life-threatening and may require medications or even surgery. That's why early treatment is essential to protect the heart.


**Kidney Effects: A Rare but Serious Complication**
\nAlthough not as common, rheumatic fever can sometimes lead to a condition called **post-streptococcal glomerulonephritis**, which affects the kidneys. This occurs when the immune system's response to a strep infection causes inflammation in the small filters of the kidneys. Symptoms may include dark or reddish-colored urine, swelling (especially in the face, hands, or feet), and high blood pressure. Kidney issues are more often linked to strep skin infections but can be a complication of rheumatic fever as well.


**Skin Changes: Rash and Nodules**
\nRheumatic fever can also show up on the skin. Some people develop a unique rash called **erythema marginatum**, which appears as pink rings with a clear center, usually on the torso or limbs. Others might get **subcutaneous nodules**, which are small, painless lumps under the skin near joints like elbows or knees. These skin signs are less common but are important clues for doctors when diagnosing the condition.


**Related Condition: PANDAS**
\nAnother rare complication that can follow a strep infection in children is **PANDAS** (Pediatric Autoimmune Neuropsychiatric Disorders Associated with Streptococcal infections). In this condition, the immune system mistakenly affects the brain, leading to sudden behavioral changes such as obsessive-compulsive tendencies, tics, or anxiety. Symptoms often appear quickly after a strep infection. While still being studied, PANDAS highlights the wide-reaching effects strep bacteria can have beyond a sore throat.


"""
    
    Diagnosis_treatment = """Summary: 
    \n* Diagnosis is by Rapid Strep test and culture    
   \n* Treatment is antibiotics- Amoxicillin/ Clauvanate or Azithromycin
   \n* Please see a doctor. This is informational only.

    \n**Diagnosis of Strep Throat**
\nDiagnosing strep throat typically starts with review of symptoms and a physical exam. Since many sore throats are caused by viruses—not bacteria—it’s important to confirm whether *Group A Streptococcus* is actually the cause. A simple throat swab can be used to collect a sample from the back of the throat, which is then tested for strep bacteria using a Strep test or/ and culture.

**The Rapid Strep Test**
\nThe rapid strep test is a quick and commonly used method to detect strep bacteria. This test can provide results within minutes. If the test is positive, antibiotics can be started right away after consulting with a clinician. If the test is negative but the doctor still suspects strep based on symptoms, a throat culture may be sent to a lab for confirmation.

**Treatment Options and Antibiotic Choices**
\nThe first choice for treating strep throat is usually **penicillin** or **amoxicillin**, taken for 10 days. For people allergic to penicillin, alternatives like **cephalexin**, **clindamycin**, or **azithromycin** may be used, depending on the type of allergy. It’s very important to complete the entire course of antibiotics, even if symptoms improve early, to fully clear the infection and avoid complications like rheumatic fever.

**Dosing of Amoxicillin** is 45 mg/kg/day every 12 hours OR 40 mg/kg/day every 8 hours for 10 days
\n**Dosing of Azithromycin** is 12 mg/kg once daily for 5 days in Penicillin allergy.

**Important Note**
\nPlease see a doctor for treatment advice. The intent is only informational in this app!
"""
    
    with gr.Tab("SYMPTOM CHECKER"):
        with gr.Accordion(label="SELF ASSESSMENT 📋: Do I have Strep Throat?", open=True):
            with gr.Column():
                high_risk = gr.Checkbox(label="Worsening neuropsychiatric symptoms!! Do you have history of Rheumatic fever, Tics, neuropsychiatric symptoms (OCD, severe anxiety, eating disorder etc)")
                age = gr.Radio(choices=["3-14", "15-44", ">45"], label="What is your Age Range", value=None)
                exudate = gr.Checkbox(label="Do you have any swelling or whitis exudate on tonsils on self examination?")
                nodes = gr.Checkbox(label="Do you have painful swollen neck lymphnodes?")
                fever = gr.Checkbox(label="Do you have a fever >100.4F or >38C?")
                cough = gr.Radio(choices=["Absent", "Present"], label="Do you have a cough?", value=None)
                check_btn = gr.Button("Check")
                result = gr.Textbox(label="Summary by Darnabot:")
                outputd = gr.Markdown(label="Darnabot:")

                check_btn.click(fn=check_strep, inputs=[high_risk, age, exudate, nodes, fever, cough], outputs=result).then(fn=darnabot_says, inputs=result, outputs=outputd)
                
                """
                def combined_check(high_risk, age, exudate, nodes, fever, cough):
                    result = check_strep(high_risk, age, exudate, nodes, fever, cough)
                    bot_response = darnabot_says(strep_result)
    
                    return result1, bot_response

                check_btn.click(fn=combined_check, inputs=[high_risk, age, exudate, nodes, fever, cough], outputs=[result, outputd])
                """
    gr.Markdown("# Quick Chapters")
    gr.Markdown("Click on any chapter to expand it.")
        
    with gr.Accordion("Chapter 1: Introduction", open=False) as chapter1:
            gr.Markdown("## Chapter 1 Introduction")
            gr.Markdown(Introduction)
            with gr.Group():
                gr.Image("uploads/impetigo.jpeg", show_label=True)
                gr.Markdown("**Figure 1:** Impetigo - a highly contagious skin infection causing red sores that can spread quickly")
                gr.Image("uploads/strep_throat.jpg", show_label=False)
                gr.Markdown("**Figure 2:** Strep throat - Sore throat accompanied by swollen tonsils and whitish exudates. May be accompanied by reddist splotches on palate and tongue")
        
    with gr.Accordion("Chapter 2: Understanding Rheumatic Fever and Complications", open=False) as chapter2:
            gr.Markdown("## Chapter 2 Untreated Complications")
            gr.Markdown(Rheumatic_fever)
            with gr.Group():
                gr.Image("uploads/rheumatic_fever.jpeg", show_label=True)
                gr.Markdown("**Figure 1:** Rheumatic Fever - Clinical features few weeks after a active Strep Infection")
        
    with gr.Accordion("Chapter 3: What should I do?", open=False) as chapter3:
            gr.Markdown("## Chapter 3 Diagnosis and Treatment")
            gr.Markdown(Diagnosis_treatment)
            
    
        
    
    
    with gr.Accordion("Chapter4: Buy Test: Where to get it?", open=False) as chapter4:
            gr.Markdown("## Buy strep test")
            gr.HTML("""
        <a href="https://thedigitalhealthstore.com/products/strepaim-73025-strep-a-25-tests" target="_blank">Buy my strep test in US</a>
    """)
            gr.HTML("""
        <a href="hhttps://www.doccheckshop.eu/laboratory/tests/more-tests/13924/stera-healthcare-stera-strep-a-quick-test" target="_blank">Buy my strep test in elsewhere</a>
    """)
            gr.HTML("""
        <a href="https://www.ganeshdiagnostic.com/group-a-streptococcal-test" target="_blank">Buy my strep test in India</a>
    """)
            
    gr.Markdown("# OTHER INFORMATIONAL LINKS")
    gr.HTML("""
        <a href="https://www.cdc.gov/group-a-strep/about/strep-throat.html" target="_blank">Understanding Strep Throat</a>
    """)
    gr.HTML("""
        <a href="https://www.cdc.gov/group-a-strep/about/rheumatic-fever.html" target="_blank">Understanding Rheumatic Fever</a>
    """)
    gr.HTML("""
        <a href="https://www.mdcalc.com/calc/104/centor-score-modified-mcisaac-strep-pharyngitis" target="_blank">Centor Criteria for Strep Throat</a>
    """)

# Fixed: Corrected the if __name__ == "__main__" syntax
if __name__ == "__main__":
    demo.launch(server_name='0.0.0.0', server_port=3026, pwa=True, share=False)



"""""

"""""
