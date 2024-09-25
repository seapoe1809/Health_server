#/* DARNA.HI
# * Copyright (c) 2023 Seapoe1809   <https://github.com/seapoe1809>
# * 
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
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import json
from datetime import datetime, timedelta
import calendar
from ollama import AsyncClient
import asyncio

# Ensure the upload directory exists
#UPLOADS_DIR = "/workspace/uploads"
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

def initialize_database():
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS food_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id INTEGER,
                    meal_type TEXT,
                    food_item TEXT,
                    timestamp DATETIME,
                    FOREIGN KEY (persona_id) REFERENCES personas (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS bm_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id INTEGER,
                    bm_type INTEGER,
                    urgency BOOLEAN,
                    timestamp DATETIME,
                    FOREIGN KEY (persona_id) REFERENCES personas (id))''')
    conn.commit()
    conn.close()

def create_persona(persona_name):
    if persona_name and persona_name != "None":
        initialize_database()  # Ensure the database and tables exist
        conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
        c = conn.cursor()
    
        try:
            # Check if the persona already exists
            c.execute("SELECT name FROM personas WHERE name = ?", (persona_name,))
            if c.fetchone():
                conn.close()
                return (
                    gr.update(value=""),  # Clear the input
                    gr.update(choices=get_personas(), value=persona_name),
                    gr.update(visible=True),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    f"Persona '{persona_name}' already exists. Selected for use."
                )
            
            # If the persona doesn't exist, create it
            c.execute("INSERT INTO personas (name) VALUES (?)", (persona_name,))
            conn.commit()
        except sqlite3.Error as e:
            conn.close()
            return (
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                f"An error occurred: {str(e)}"
            )
        
        conn.close()
        
        # Get updated list of personas
        updated_personas = get_personas()
        
        return (
            gr.update(value=""),  # Clear the input
            gr.update(choices=updated_personas, value=persona_name),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            f"Persona '{persona_name}' created successfully!"
        )
    else:
        return (
            gr.update(),
            gr.update(choices=get_personas()),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            "List Refreshed."
        )

def get_personas():
    initialize_database()  # Ensure the database and tables exist
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
    c = conn.cursor()
    c.execute("SELECT name FROM personas")
    personas = [row[0] for row in c.fetchall()]
    conn.close()
    return ["None"] + personas if personas else ["None"]

def save_food_entry(persona, meal_type, food_item):
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
    c = conn.cursor()
    c.execute("SELECT id FROM personas WHERE name = ?", (persona,))
    persona_id = c.fetchone()[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:00:00")
    c.execute("INSERT INTO food_entries (persona_id, meal_type, food_item, timestamp) VALUES (?, ?, ?, ?)",
              (persona_id, meal_type, food_item, timestamp))
    conn.commit()
    conn.close()
    return create_ibs_graph_and_table(persona)

def save_bm_entry(persona, bm_type, urgency):
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
    c = conn.cursor()
    c.execute("SELECT id FROM personas WHERE name = ?", (persona,))
    persona_id = c.fetchone()[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:00:00")
    c.execute("INSERT INTO bm_entries (persona_id, bm_type, urgency, timestamp) VALUES (?, ?, ?, ?)",
              (persona_id, str(bm_type), urgency, timestamp))
    conn.commit()
    conn.close()
    return create_ibs_graph_and_table(persona)

def on_persona_select(persona):
    if persona and persona != "None":
        fig, df, message = create_ibs_graph_and_table(persona)
        return (
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True, value=fig),
            gr.update(visible=True, value=df),
            message
        )
    else:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            "Please select a persona."
        )

def delete_ibs_and_update(persona_name):
    # Connect to the database
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
    c = conn.cursor()

    # Retrieve the persona_id
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]

    # Get the current time and calculate the time for 1 hour ago
    current_time = datetime.now()
    one_hour_ago = current_time - timedelta(hours=1)

    # Convert the times to a string format that matches your DB timestamp format
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    one_hour_ago_str = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')

    # Delete entries from food_entries within the last hour for this persona
    c.execute("""
        DELETE FROM food_entries 
        WHERE persona_id = ? AND timestamp BETWEEN ? AND ?
    """, (persona_id, one_hour_ago_str, current_time_str))

    # Delete entries from bm_entries within the last hour for this persona
    c.execute("""
        DELETE FROM bm_entries 
        WHERE persona_id = ? AND timestamp BETWEEN ? AND ?
    """, (persona_id, one_hour_ago_str, current_time_str))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    return create_ibs_graph_and_table(persona_name)

def create_ibs_graph_and_table(persona_name):
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'ibs.db'))
    c = conn.cursor()
    
    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    
    # Fetch food records for the persona
    c.execute("""
        SELECT 'Food' as entry_type, meal_type as subtype, food_item as description, timestamp
        FROM food_entries
        WHERE persona_id = ?
        UNION ALL
        SELECT 'BM' as entry_type, bm_type as subtype, 
               CASE WHEN urgency = 1 THEN 'Urgent' ELSE 'Not Urgent' END as description, 
               timestamp
        FROM bm_entries
        WHERE persona_id = ?
        ORDER BY timestamp
    """, (persona_id, persona_id))
    
    readings = c.fetchall()
    conn.close()

    # Create a DataFrame
    df = pd.DataFrame(readings, columns=['Entry Type', 'Subtype', 'Description', 'Timestamp'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Weekday'] = df['Timestamp'].dt.day_name()
    df['Hour'] = df['Timestamp'].dt.hour

    if df.empty:
        fig = go.Figure()
        fig.update_layout(title=f"No data available for {persona_name}")
        return fig, df, f"No data available for {persona_name}"

    # Define markers
    markers = {
        'Snack': '🥐☕️', 'Breakfast': '🥞🍳', 'Lunch': '🍛🍝', 'Dinner': '🍲🥘',
        '1': '⓵', '2': '⓶', '3': '⓷', '4': '⓸', '5': '⓹', '6': '⓺', '7': '⓻'
    }

    # Create the graph
    fig = go.Figure()

    # Add food entries
    for meal_type in ['Snack', 'Breakfast', 'Lunch', 'Dinner']:
        meal_data = df[(df['Entry Type'] == 'Food') & (df['Subtype'] == meal_type)]
        fig.add_trace(go.Scatter(
            x=meal_data['Timestamp'],
            y=[1]*len(meal_data),
            mode='text',
            text=[markers[meal_type]]*len(meal_data),
            name=meal_type,
            textposition="middle center",
            textfont=dict(size=36),  # Increase font size to make icons bigger
            hovertext=meal_data['Description'] + '<br>' + meal_data['Weekday'] + ' ' + meal_data['Timestamp'].dt.strftime('%H:%M'),
            hoverinfo='text'
        ))

    # Add BM entries
    bm_data = df[df['Entry Type'] == 'BM']
    fig.add_trace(go.Scatter(
        x=bm_data['Timestamp'],
        y=[0]*len(bm_data),
        mode='text',
        text=[markers[str(subtype)] for subtype in bm_data['Subtype']],
        name='BM',
        textposition="middle center",
        textfont=dict(size=36),  # Increase font size to make icons bigger
        hovertext=bm_data['Description'] + '<br>' + bm_data['Weekday'] + ' ' + bm_data['Timestamp'].dt.strftime('%H:%M'),
        hoverinfo='text'
    ))

    # Add urgency markers
    urgent_data = df[(df['Entry Type'] == 'BM') & (df['Description'] == 'Urgent')]
    fig.add_trace(go.Scatter(
        x=urgent_data['Timestamp'],
        y=[-0.1]*len(urgent_data),
        mode='text',
        text=['🗦  🗧']*len(urgent_data),
        name='Urgency',
        textposition="middle center",
        textfont=dict(size=36),  # Increase font size to make icons bigger
        hovertext=urgent_data['Weekday'] + ' ' + urgent_data['Timestamp'].dt.strftime('%H:%M'),
        hoverinfo='text'
    ))

    # Create custom x-axis ticks
    unique_dates = df['Timestamp'].dt.date.unique()
    tick_values = []
    tick_text = []
    for date in unique_dates:
        for hour in [6, 12, 18, 0]:  # morning, noon, evening, night
            tick_values.append(pd.Timestamp.combine(date, pd.Timestamp(f"{hour:02d}:00:00").time()))
            weekday = calendar.day_name[date.weekday()]
            if hour == 6:
                tick_text.append(f"{weekday} morning")
            elif hour == 12:
                tick_text.append(f"{weekday} noon")
            elif hour == 18:
                tick_text.append(f"{weekday} evening")
            else:
                tick_text.append("night")

    fig.update_layout(
        title=f'IBS Tracker for {persona_name}',
        yaxis=dict(
            ticktext=['BM', 'Food'],
            tickvals=[0, 1],
            range=[-0.2, 1.2]
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=tick_values,
            ticktext=tick_text,
            tickangle=45
        ),
        showlegend=False
    )

    return fig, df, f"Updated chart and table for {persona_name}"


#Questionnaire
def check_ibs(diagnosis, colonoscopy, blood_tests, sibo_test, constipation, diarrhea):
    base_conditions = [diagnosis, colonoscopy, blood_tests, sibo_test]
    
    if all(base_conditions):
        if constipation and diarrhea:
            return "You might have IBS-M (Mixed IBS)."
        elif constipation:
            return "You might have predominantly IBS-C (Constipation-predominant IBS)."
        elif diarrhea:
            return "You might have predominantly IBS-D (Diarrhea-predominant IBS)."
        else:
            return "You might have IBS, but the subtype is unclear."
    else:
        return "You might not have IBS. Please see a doctor to be tested."

##Exercise
# Function to display exercise details
def display_exercise(exercise):
    exercises = {
        "Breathing Exercise": {
            "text": "**STEPS: Diaphragmatic Breathing**:\n1. Choose a comfortable and quiet place to do your breathing exercise. \n2. Don't force it. This can make you feel more stressed. \n3. Focus on your belly to help with diaphragmatic breathing.\n 4. Click Start when ready.",
            "gif": "breathing2.webp"
        },
        "Vagal Gut Exercise": {
            "text": "**STEPS: This works by activating your vagal system.**\n1. Choose a comfortable and quiet place to do your exercise. \n2. Lie down. \n3. Inhale deeply.\n4. Bear down with your throat closed for few seconds and let go.\n 4. Repeat. \n5. Click Start when ready.",
            "gif": "boston_breath.webp"
        },
        "Boston Clasp Exercise": {
            "text": "**STEPS: This works by taking your mind of the gut discomfort.**\n1. Choose a comfortable and quiet place to do your exercise. \n2. Clasp your hands as shown. \n3. Pull apart for 15 seconds.\n 4. Let go. Repeat. \n5.Click Start when ready.",
            "gif": "clasp.webp"
        }
    }
    
    text = exercises[exercise]["text"]
    gif_path = os.path.join(UPLOADS_DIR, exercises[exercise]["gif"])
    return text, gif_path

# Timer function for 30s reverse countdown
def timer(exercise):
    if not exercise:
        return "<div style='font-size: 30px; text-align: center;'>Please select an exercise first!</div>"
   
    for i in range(60, -1, -1):
        time.sleep(1)
        yield f"<div style='font-size: 30px; text-align: center;'>{i} seconds left</div>" if i > 0 else "<div style='font-size: 30px; text-align: center;'>Great Work!</div>"


##DARNABOT FODMAP CHECKER
# Load the FODMAP repository JSON file
file_path_fodmap = os.path.join(UPLOADS_DIR, "fodmap_repo.json")
with open(file_path_fodmap) as f:
    fodmap_data = json.load(f)

# Function to search the FODMAP data based on the input term (partial match)
def fodmap_checker(food_name):
    results = []
    for item in fodmap_data:
        if food_name.lower() in item['name'].lower():  # Partial match check
            details = item['details']
            result = (
                f"{item['name']} food has\n"
                f"FODMAP: {item['fodmap']},\n"
                f"Category: {item['category']},\n"
                f"Details - Oligos: {details['oligos']}, "
                f"Fructose: {details['fructose']}, "
                f"Polyols: {details['polyols']}, "
                f"Lactose: {details['lactose']}\n"
            )
            results.append(result)
    
    if results:
        return "\n".join(results)
    else:
        return f" Try to estimate FODMAP safety in {food_name}. "

class HealthMotivator:
    async def get_motivation(self, food_info):
        messages = [
            {"role": "system", "content": "You are Darnabot, Irritable Bowel Syndrome expert. Provide a brief message about fodmap using relevant information on foods listed."},
            {"role": "user", "content": f"Give fodmap content to your best knowledge {food_info}."},
        ]
        
        #async for part in await AsyncClient().chat(model='mistral-nemo', messages=messages, stream=True):
            #chunk=part['message']['content']
            #yield chunk
        try:    
            OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            async for part in await AsyncClient(host=OLLAMA_HOST).chat(model='mistral-nemo', messages=messages, stream=True):
                yield part['message']['content']
        except Exception as e:
            yield f"Remember to take care of your health. Please see links below! Also download mistral-nemo from ollama. (Error: {str(e)})"



motivator = HealthMotivator()

async def fodmap_health(food_item):
    food_info=fodmap_checker(food_item)
    motivation = "This is an estimate. "   
    async for chunk in motivator.get_motivation(food_info):
        motivation += chunk
        yield motivation
        
##GRADIO APP
initialize_database()

# Gradio interface
with gr.Blocks(theme='Taithrah/Minimal', css="footer{display:none !important}") as demo:
    gr.Markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center; height: 100%; color: #FFFFFF; background-color: #4c00b0; font-weight: bold;'>IBS Tracker</div>")
    with gr.Tab("LOG TRACKER"):
        with gr.Row():
            persona_dropdown = gr.Dropdown(label="Select Persona", choices=get_personas())
            with gr.Row():
                persona_input = gr.Textbox(label="Create Persona")
                create_button = gr.Button("Add 👥 / Refresh ⟳")

        with gr.Row():
            with gr.Accordion("FOOD LOG", visible=False) as food_accordion:
                meal_type = gr.Dropdown(choices=["Breakfast", "Lunch", "Dinner", "Snack"], label="Meal Type")
                food_item = gr.Textbox(label="Food Item")
                with gr.Row():
                    save_food_button = gr.Button("SAVE LOG")

            with gr.Accordion("BM LOG", visible=False) as bm_accordion:
                gr.HTML("""
        <a href="https://pediatricsurgery.stanford.edu/Conditions/BowelManagement/bristol-stool-form-scale.html" target="_blank">🅸 Info </a>
        """)
                bm_type = gr.Dropdown(choices=["1", "2", "3", "4", "5", "6", "7"], label="BM Type (Bristol Score)")
                urgency = gr.Checkbox(label="Urgency")
                with gr.Row():
                    save_bm_button = gr.Button("SAVE LOG")
                    delete_button= gr.Button("DELETE LOG (1hr)")

        ibs_graph = gr.Plot(label="Daily Chart", visible=False)
        ibs_table = gr.DataFrame(label="Daily records", visible=False)
        output = gr.Textbox(label="ALERT:")

        create_button.click(
            create_persona,
            inputs=[persona_input],
            outputs=[persona_input, persona_dropdown, food_accordion, bm_accordion, ibs_graph, ibs_table, output]
        )

        persona_dropdown.change(
            on_persona_select,
            inputs=[persona_dropdown],
            outputs=[food_accordion, bm_accordion, ibs_graph, ibs_table, output]
        )

        save_food_button.click(
            save_food_entry,
            inputs=[persona_dropdown, meal_type, food_item],
            outputs=[ibs_graph, ibs_table, output]
        )

        save_bm_button.click(
            save_bm_entry,
            inputs=[persona_dropdown, bm_type, urgency],
            outputs=[ibs_graph, ibs_table, output]
        )
        
        delete_button.click(
            delete_ibs_and_update,
            inputs=[persona_dropdown],
            outputs=[ibs_graph, ibs_table, output]
        )
    
    
    with gr.Tab("FOOD CHECKER"):
    
        
        outputd = gr.Markdown(label="Darnabot:")
        inputt = gr.Textbox(label="ASK DARNABOT TO CHECK FOOD:")
                            
        btnw = gr.Button("CHECK IT")
        btnw.click(fodmap_health, inputs=inputt, outputs=[outputd])
        
        gr.Markdown("# OTHER INFORMATIONAL LINKS\n ## More about FODMAP:")
        gr.HTML("""
        <a href="https://fodmapchecker.com/" target="_blank">FODMAP Checker on Web</a>
    """)
        gr.HTML("""
        <a href="https://www.monashfodmap.com/about-fodmap-and-ibs/high-and-low-fodmap-foods/">MONASH FODMAP</a>
    """)
    
    with gr.Tab("TIPS"):
        
            """
            gr.Markdown("# Are you traveling?\n ## See travel health suggestions:\n\n")
            
            with gr.Row():
                inputt = gr.Textbox(label="Where are you traveling to mate!")
                btnw = gr.Button("Enter Country")
                
            outputd = gr.Markdown(label="Darnabot:")
  
    
            btnw.click(travel_health, inputs=inputt, outputs=[outputd])
            """
            
            with gr.Accordion(label="SELF ASSESSMENT 📋: Do I have IBS?", open=False):
                with gr.Column():
                    diagnosis = gr.Checkbox(label="Have you been given a diagnosis by your doctor?")
                    colonoscopy = gr.Checkbox(label="Have you undergone Colonoscopy?")
                    blood_tests = gr.Checkbox(label="Do you have unremarkable blood tests?")
                    sibo_test = gr.Checkbox(label="Did you undergo SIBO test?")
                    constipation = gr.Checkbox(label="Are you predominantly constipated?")
                    diarrhea = gr.Checkbox(label="Do you have diarrhea?")
                    check_btn = gr.Button("Check")
                    result = gr.Textbox(label="Result")
                    check_btn.click(
                        fn=check_ibs,
                        inputs=[diagnosis, colonoscopy, blood_tests, sibo_test, constipation, diarrhea],
                        outputs=result
                    )
                
            
    
            with gr.Accordion(label="STRESS/ ANXIETY EXERCISES (1 min)", open=False):
                with gr.Row():
                    with gr.Column():
                        dropdown = gr.Dropdown(
                        choices=["Breathing Exercise", "Vagal Gut Exercise", "Boston Clasp Exercise"], 
                        value=None, 
                        interactive=True, 
                        label="Stress/Anxiety Exercises (1 min)"
            
                    )
                        text_output = gr.Markdown()
            
                    with gr.Column():
                        #image_output = gr.Image(type="filepath", label="Exercise Animation", width=300, height=300)
                        image_output = gr.Image(type="filepath", label="Exercise:")
                        timer_output = gr.HTML(label="60s Reverse Timer")
    
                        submit_button = gr.Button("Start Exercise", interactive=False)
        
                def enable_submit(exercise):
                    if exercise:
                        return gr.update(interactive=True)
    
                # Update text and display the exercise GIF when the dropdown changes
                dropdown.change(display_exercise, inputs=dropdown, outputs=[text_output, image_output])
                dropdown.change(enable_submit, inputs=dropdown, outputs=submit_button)
    
                # When the button is clicked, start the 30-second timer and display the countdown
                submit_button.click(timer, inputs=dropdown, outputs=timer_output)
           

            
           
    
            gr.Markdown("# OTHER INFORMATIONAL LINKS\n ## Guided Meditation:")
            gr.HTML("""
        <a href="https://www.uclahealth.org/programs/uclamindful/free-guided-meditations/guided-meditations" target="_blank">UCLA Guided Meditation Links</a>
    """)

            gr.HTML("""
        <a href="https://insighttimer.com/guided-meditations" target="_blank">Insight Timer Guided Meditation</a>
        """)
            gr.HTML("""
        <a href="https://www.nhs.uk/conditions/irritable-bowel-syndrome-ibs/diet-lifestyle-and-medicines/" target="_blank">Other Do's and Donts</a>
        """)


    
    demo.launch(server_name='0.0.0.0', server_port=3024, share=False, allowed_paths=[UPLOADS_DIR])

if __name__ == "__main__":
    demo.launch()
