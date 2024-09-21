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
import sqlite3
import os
from datetime import datetime, date
import plotly.graph_objs as go
import pandas as pd

# Function to initialize the database and create the personas table if not exists
def initialize_database():
    if not os.path.exists('personas.db'):
        conn = sqlite3.connect('personas.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS personas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE)''')
        conn.commit()
        conn.close()

# Function to create a persona with linked tables for glucose, BP, and weight
def create_persona(persona_name):
    if persona_name is not None:
        conn = sqlite3.connect('personas.db')
        c = conn.cursor()
    
        # Check if the persona already exists
        c.execute("SELECT name FROM personas WHERE name = ?", (persona_name,))
        if c.fetchone():
            conn.close()
            return gr.update(), gr.update(choices=get_personas(), visible=True, value=None)
    
        # Insert new persona
        c.execute("INSERT INTO personas (name) VALUES (?)", (persona_name,))
        persona_id = c.lastrowid
    
        # Create linked tables for glucose, BP, and weight
        c.execute(f'''CREATE TABLE IF NOT EXISTS glucose_{persona_id} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value REAL,
                    date TEXT,
                    time TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
        c.execute(f'''CREATE TABLE IF NOT EXISTS bp_{persona_id} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    systolic REAL,
                    diastolic REAL,
                    date TEXT,
                    time TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
        c.execute(f'''CREATE TABLE IF NOT EXISTS weight_{persona_id} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value REAL,
                    unit TEXT,
                    date TEXT,
                    time TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
        conn.commit()
        conn.close()
    
        return gr.update(value=""), gr.update(choices=get_personas(), visible=True, value=None)

# Function to get all personas
def get_personas():
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    c.execute("SELECT name FROM personas")
    personas = [row[0] for row in c.fetchall()]
    conn.close()
    return personas

# Function to select persona and show measurement options
def select_persona(persona_name):
    return gr.update(choices=['Glucose', 'BP', 'Weight'], value=None)

# Function to add glucose measurement
def add_glucose(persona_name, glucose_value, date, time):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        # If the date is invalid, return without saving
        print(f"Invalid date {date}. Entry not saved.")
        return
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    
    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    
    # Insert glucose measurement with date and time
    c.execute(f"INSERT OR REPLACE INTO glucose_{persona_id} (value, date, time) VALUES (?, ?, ?)", 
              (glucose_value, date, time))
    conn.commit()
    conn.close()

# Function to add blood pressure measurement
def add_bp(persona_name, systolic_value, diastolic_value, date, time):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        # If the date is invalid, return without saving
        print(f"Invalid date {date}. Entry not saved.")
        return
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    
    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    
    # Insert BP measurement with date and time
    c.execute(f"INSERT OR REPLACE INTO bp_{persona_id} (systolic, diastolic, date, time) VALUES (?, ?, ?, ?)", 
              (systolic_value, diastolic_value, date, time))
    conn.commit()
    conn.close()

# Function to add weight measurement
def add_weight(persona_name, weight_value, weight_unit, date, time):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        # If the date is invalid, return without saving
        print(f"Invalid date {date}. Entry not saved.")
        return
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    
    # Convert weight to kg
    if weight_unit.lower() == 'lbs':
        weight_value = weight_value * 0.45359237
    elif weight_unit.lower() == 'g':
        weight_value = weight_value / 1000
    elif weight_unit.lower() != 'kg':
        raise ValueError("Unsupported weight unit. Please use 'kg', 'lbs', or 'g'.")
    
    # Round to 2 decimal places
    weight_value = round(weight_value, 2)
    
    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    
    # Insert weight measurement with date and time
    c.execute(f"INSERT OR REPLACE INTO weight_{persona_id} (value, unit, date, time) VALUES (?, ?, ?, ?)", 
              (weight_value, 'kg', date, time))
              
    conn.commit()
    conn.close()

# Function to populate current date and time
def populate_now():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    return date_str, time_str

#GRAPHING FUNCTIONS

def create_weight_graph_and_table(persona_name):
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    
    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    
    # Fetch weight readings for the persona
    c.execute(f"SELECT date, time, value FROM weight_{persona_id} ORDER BY date ASC, time ASC")
    readings = c.fetchall()
    
    conn.close()
    
    if not readings:
        return None, None  # Return None for both graph and table if no data is available
    
    # Create DataFrame for table
    df = pd.DataFrame(readings, columns=['Date', 'Time', 'Weight (kg)'])
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.sort_values('DateTime')  # Ensure sorting by the combined datetime column
    
    # Prepare data for graph
    dates = df['DateTime']
    weights = df['Weight (kg)']
    
    # Create graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers', name='Weight', line=dict(color='#2AAA8A'),
    marker=dict(color='#2AAA8A')))
    fig.update_layout(
        title=f'Weight Readings Over Time for {persona_name}',
        xaxis_title='Date',
        yaxis_title='Weight (kg)',
        hovermode='closest',
        xaxis=dict(
            showgrid=False,
            tickangle=-45),
        yaxis=dict(showgrid=False),
        annotations=[
            dict(
                x=x,
                y=y,
                text='🔵',
                showarrow=False,
                font=dict(size=20),
                xref='x',
                yref='y'
            ) for x, y in zip(dates, weights)
        ]
    )
    
    return fig, df[['Date', 'Time', 'Weight (kg)']] 
    
def update_weight_graph_and_table(persona_name, measure):
            if measure == 'Weight':
                fig, df = create_weight_graph_and_table(persona_name)
                if fig and df is not None:
                    return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True)
                else:
                    return gr.Plot(visible=False), gr.DataFrame(visible=False)
            else:
                return gr.Plot(visible=False), gr.DataFrame(visible=False)

def submit_weight_and_update_graph(persona_name, weight_value, weight_unit, date, time):
            add_weight(persona_name, weight_value, weight_unit, date, time)
            fig, df = create_weight_graph_and_table(persona_name)
            if fig and df is not None:
                return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True)
            else:
                return gr.Plot(visible=False), gr.DataFrame(visible=False)
                                

##GRAPHING BP

def get_blood_pressure_data(persona_id):
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    c.execute(f"SELECT systolic, diastolic, date, time FROM bp_{persona_id} ORDER BY date, time")
    readings = c.fetchall()
    conn.close()

    df = pd.DataFrame(readings, columns=['Systolic', 'Diastolic', 'Date', 'Time'])
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.sort_values('DateTime')

    # Create Ohlc chart
    trace = go.Ohlc(
        x=df['DateTime'],
        open=df['Systolic'],
        high=df['Systolic'],
        low=df['Diastolic'],
        close=df['Diastolic'],
        increasing=dict(line=dict(color='#2AAA8A')),  
        decreasing=dict(line=dict(color='#2AAA8A')) 
    )

    # Create the layout
    layout = go.Layout(
        title='Blood Pressure Over Time',
        yaxis_title='Blood Pressure (mmHg)',
        xaxis_title='Date and Time',
        xaxis_rangeslider_visible=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    # Create the figure and add shapes for normal ranges
    fig = go.Figure(data=[trace], layout=layout)

    # Add light green band for normal systolic range
    fig.add_shape(type="rect",
                  xref="paper", yref="y",
                  x0=0, x1=1, y0=100, y1=140,
                  fillcolor="lightgreen", opacity=0.3, layer="below", line_width=0)

    # Add light green band for normal diastolic range
    fig.add_shape(type="rect",
                  xref="paper", yref="y",
                  x0=0, x1=1, y0=70, y1=90,
                  fillcolor="lightgreen", opacity=0.3, layer="below", line_width=0)

    return fig, df[['Date', 'Time', 'Systolic', 'Diastolic']]

def update_BP_graph_and_table(persona_name, measure):
    if measure == 'BP':
        conn = sqlite3.connect('personas.db')
        c = conn.cursor()
        c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
        persona_id = c.fetchone()[0]
        conn.close()

        fig, df = get_blood_pressure_data(persona_id)
        if not df.empty:
            return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True)
        else:
            return gr.Plot(visible=False), gr.DataFrame(visible=False)
    else:
        return gr.Plot(visible=False), gr.DataFrame(visible=False)

def submit_BP_and_update_graph(persona_name, systolic_value, diastolic_value, date, time):
    add_bp(persona_name, systolic_value, diastolic_value, date, time)
    
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    conn.close()

    fig, df = get_blood_pressure_data(persona_id)
    if not df.empty:
        return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True)
    else:
        return gr.Plot(visible=False), gr.DataFrame(visible=False)

###GLUCOSE GRAPHING

def get_glucose_data(persona_id):
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    c.execute(f"SELECT value, date, time FROM glucose_{persona_id} ORDER BY date, time")
    readings = c.fetchall()
    conn.close()

    df = pd.DataFrame(readings, columns=['Glucose', 'Date', 'Time'])
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.sort_values('DateTime')

    times_of_day = df['DateTime'].apply(lambda x: (x.hour * 60 + x.minute) / 1440)
    hover_texts = [f"Value: {value} mg/dL<br>Date: {date}<br>Time: {time}" 
                   for value, date, time in zip(df['Glucose'], df['Date'], df['Time'])]

    trace = go.Scatter(
        x=times_of_day,
        y=df['Glucose'],
        mode='markers',
        marker=dict(
            size=10,
            color=df['Glucose'],
            colorscale='Viridis',
            showscale=False,
            colorbar=dict(title="Glucose (mg/dL)")
        ),
        text=hover_texts,
        hoverinfo='text'
    )

    normal_range = go.Scatter(
        x=[0, 1, 1, 0],
        y=[70, 70, 150, 150],
        fill='toself',
        fillcolor='rgba(0,255,0,0.2)',
        line=dict(color='rgba(0,255,0,0)'),
        hoverinfo='skip',
        showlegend=False
    )

    layout = go.Layout(
        title='Glucose Readings by Time of Day',
        xaxis=dict(
            title='Time of Day',
            tickmode='array',
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=['Midnight', 'Morning', 'Noon', 'Evening', 'Midnight'],
            showticklabels=True,
            range=[0, 1]
        ),
        yaxis=dict(
            title='Glucose Value (mg/dL)',
            range=[max(0, df['Glucose'].min() - 20) if not df.empty else 0, 
                   df['Glucose'].max() + 20 if not df.empty else 200]
        ),
        hovermode='closest',
        shapes=[
            dict(type="line", x0=0.25, x1=0.25, y0=0, y1=1, yref="paper", line=dict(color="rgba(0,0,0,0.2)", dash="dash")),
            dict(type="line", x0=0.5, x1=0.5, y0=0, y1=1, yref="paper", line=dict(color="rgba(0,0,0,0.2)", dash="dash")),
            dict(type="line", x0=0.75, x1=0.75, y0=0, y1=1, yref="paper", line=dict(color="rgba(0,0,0,0.2)", dash="dash"))
        ]
    )

    fig = go.Figure(data=[normal_range, trace], layout=layout)
    return fig, df[['Date', 'Time', 'Glucose']]


def update_glucose_graph_and_table(persona_name, measure):
    if measure == 'Glucose':
        conn = sqlite3.connect('personas.db')
        c = conn.cursor()
        c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
        persona_id = c.fetchone()[0]
        conn.close()

        fig, df = get_glucose_data(persona_id)
        if not df.empty:
            return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True)
        else:
            return gr.Plot(visible=False), gr.DataFrame(visible=False)
    else:
        return gr.Plot(visible=False), gr.DataFrame(visible=False)

def submit_glucose_and_update_graph(persona_name, glucose_value, date, time):
    add_glucose(persona_name, glucose_value, date, time)
    
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    conn.close()

    fig, df = get_glucose_data(persona_id)
    if not df.empty:
        return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True)
    else:
        return gr.Plot(visible=False), gr.DataFrame(visible=False)


##WATER TRACKER

class WaterTracker:
    def __init__(self):
        self.glasses = 0
        self.last_reset = date.today()

    def drink_water(self):
        today = date.today()
        if today > self.last_reset:
            self.glasses = 0
            self.last_reset = today
        
        if self.glasses < 8:
            self.glasses += 1
        
        return f"You've had {self.glasses} glass{'es' if self.glasses != 1 else ''} of water today. {'Great Job!' if self.glasses == 8 else ''}"

tracker = WaterTracker()

##using ollama to generate message
from ollama import AsyncClient
import asyncio
class HealthMotivator:
    async def get_motivation(self):
        messages = [
            {"role": "system", "content": "You are a health motivator. Provide a short, encouraging message about staying healthy."},
            {"role": "user", "content": "Give me a motivational health tip."},
        ]
        
        #async for part in await AsyncClient().chat(model='mistral-nemo', messages=messages, stream=True):
            #chunk=part['message']['content']
            #yield chunk
        try:    
            OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            async for part in await AsyncClient(host=OLLAMA_HOST).chat(model='mistral-nemo', messages=messages, stream=True):
                yield part['message']['content']
        except Exception as e:
            yield f"Remember to take care of your health! (Error: {str(e)})"



motivator = HealthMotivator()

async def update_water_and_motivation():
    water_status = tracker.drink_water()
    motivation = ""
    async for chunk in motivator.get_motivation():
        motivation += chunk
        yield water_status, motivation
    

###GRADIO INTERFACE

def create_gradio_interface():
    initialize_database()
    
    with gr.Blocks(theme='Taithrah/Minimal', css= "footer{display:none !important}") as demo:
        gr.Markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center; height: 100%; color: #FFFFFF; background-color: #4c00b0; font-weight: bold;'>DARNAHI TRACKER</div>")
        
        with gr.Tab("TRACKER"):
            
        
            with gr.Row():
                persona_name_input = gr.Textbox(label="Add Persona", placeholder="Add Persona")
                create_button = gr.Button("Add 👥 / Refresh ⟳")
        
            personas_available = bool(get_personas())
            with gr.Row():
                persona_dropdown = gr.Dropdown(label="Select Persona to View", choices=get_personas(), visible=personas_available)
                measure_dropdown = gr.Dropdown(label="Measure", choices=[], visible=personas_available)
        
            with gr.Row():
                glucose_input = gr.Number(label="Enter Glucose", visible=False, minimum=1, value=90)
                bp_systolic_input = gr.Number(label="Enter Systolic", visible=False, minimum=1, value=120)
                bp_diastolic_input = gr.Number(label="Enter Diastolic", visible=False, minimum=1, value=80)
                weight_input = gr.Number(label="Enter Weight", visible=False, minimum=1, value=80)
                weight_unit_dropdown = gr.Dropdown(label="Unit", choices=["kg", "lbs"], visible=False, value="kg")
        
                date_input = gr.Textbox(label="Enter Date", placeholder="YYYY-MM-DD", visible=False)
                time_input = gr.Dropdown(label="Select Time", choices=[f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 30)], allow_custom_value=True, visible=False)
        
                with gr.Row(visible=True) as now_and_submit_row:
                    now_button = gr.Button("Now", visible=False)
                    submit_glucose_button = gr.Button("Submit Glucose", visible=False)
                    submit_bp_button = gr.Button("Submit BP", visible=False)
                    submit_weight_button = gr.Button("Submit Weight", visible=False)
        
            # Add weight graph component
            weight_graph = gr.Plot(label="Weight Trend", visible=False)
            weight_table = gr.DataFrame(label="Weight Readings", visible=False)
        
            # Add BP graph component
            bp_graph = gr.Plot(label="BP Trend", visible=False)
            bp_table = gr.DataFrame(label="BP Readings", visible=False)
        
            # Add Glucose graph component
            glucose_graph = gr.Plot(label="Glucose Trend", visible=False)
            glucose_table = gr.DataFrame(label="Glucose Readings", visible=False)
        
        
            create_button.click(create_persona, inputs=persona_name_input, outputs=[persona_name_input, persona_dropdown])
            persona_dropdown.change(select_persona, inputs=persona_dropdown, outputs=measure_dropdown)
        
            def show_measure_inputs(measure):
                glucose_visible = gr.update(visible=False)
                bp_systolic_visible = gr.update(visible=False)
                bp_diastolic_visible = gr.update(visible=False)
                weight_visible = gr.update(visible=False)
                weight_unit_visible = gr.update(visible=False)
                date_visible = gr.update(visible=False)
                time_visible = gr.update(visible=False)
                now_button_visible = gr.update(visible=False)
                submit_glucose_visible = gr.update(visible=False)
                glucose_graph_visible = gr.update(visible=False)
                glucose_table_visible = gr.update(visible=False)
                submit_bp_visible = gr.update(visible=False)
                bp_graph_visible = gr.update(visible=False)
                bp_table_visible = gr.update(visible=False)
                submit_weight_visible = gr.update(visible=False)
                weight_graph_visible = gr.update(visible=False)
                weight_table_visible = gr.update(visible=False)

                if measure == 'Glucose':
                    glucose_visible = gr.update(visible=True)
                    submit_glucose_visible = gr.update(visible=True)
                    glucose_graph_visible = gr.update(visible=True)
                    glucose_table_visible = gr.update(visible=True)
                elif measure == 'BP':
                    bp_systolic_visible = gr.update(visible=True)
                    bp_diastolic_visible = gr.update(visible=True)
                    submit_bp_visible = gr.update(visible=True)
                    bp_graph_visible = gr.update(visible=True)
                    bp_table_visible = gr.update(visible=True)
                elif measure == 'Weight':
                    weight_visible = gr.update(visible=True)
                    weight_unit_visible = gr.update(visible=True)
                    submit_weight_visible = gr.update(visible=True)
                    weight_graph_visible = gr.update(visible=True)
                    weight_table_visible = gr.update(visible=True)

                if measure in ['Glucose', 'BP', 'Weight']:
                    date_visible = gr.update(visible=True)
                    time_visible = gr.update(visible=True)
                    now_button_visible = gr.update(visible=True)

                return (
                    glucose_visible,
                    bp_systolic_visible,
                    bp_diastolic_visible,
                    weight_visible,
                    weight_unit_visible,
                    date_visible,
                    time_visible,
                    now_button_visible,
                    submit_glucose_visible,
                    glucose_graph_visible,
                    glucose_table_visible,
                    submit_bp_visible,
                    bp_graph_visible,
                    bp_table_visible,
                    submit_weight_visible,
                    weight_graph_visible,
                    weight_table_visible
                )
                                         
                                         

            measure_dropdown.change(
        show_measure_inputs, 
        inputs=measure_dropdown, 
        outputs=[
            glucose_input, 
            bp_systolic_input, 
            bp_diastolic_input, 
            weight_input, 
            weight_unit_dropdown, 
            date_input, 
            time_input, 
            now_button, 
            submit_glucose_button,
            glucose_graph,
            glucose_table, 
            submit_bp_button, 
            bp_graph,
            bp_table,
            submit_weight_button,
            weight_graph,
            weight_table
        ]
    )

            
            
            #button click functions   

            submit_glucose_button.click(submit_glucose_and_update_graph, inputs=[persona_dropdown, glucose_input, date_input, time_input], outputs=[glucose_graph, glucose_table])
            submit_bp_button.click(submit_BP_and_update_graph, inputs=[persona_dropdown, bp_systolic_input, bp_diastolic_input, date_input, time_input], outputs=[bp_graph, bp_table])
        
            submit_weight_button.click(submit_weight_and_update_graph, 
                                   inputs=[persona_dropdown, weight_input, weight_unit_dropdown, date_input, time_input], 
                                   outputs=[weight_graph, weight_table])

        

            #refreshes if the persona is changed        

            persona_dropdown.change(update_weight_graph_and_table, inputs=[persona_dropdown, measure_dropdown], outputs=[weight_graph, weight_table])
            measure_dropdown.change(update_weight_graph_and_table, inputs=[persona_dropdown, measure_dropdown], outputs=[weight_graph, weight_table])
        
            persona_dropdown.change(update_BP_graph_and_table, inputs=[persona_dropdown, measure_dropdown], outputs=[bp_graph, bp_table])
            measure_dropdown.change(update_BP_graph_and_table, inputs=[persona_dropdown, measure_dropdown], outputs=[bp_graph, bp_table])
        
            persona_dropdown.change(update_glucose_graph_and_table, inputs=[persona_dropdown, measure_dropdown], outputs=[glucose_graph, glucose_table])
            measure_dropdown.change(update_glucose_graph_and_table, inputs=[persona_dropdown, measure_dropdown], outputs=[glucose_graph, glucose_table])


            now_button.click(populate_now, inputs=[], outputs=[date_input, time_input])
    
    
        with gr.Tab("TIPS"):
            with gr.Row():
                outputw = gr.Textbox(label="Drink 8 mate!")
                btnw = gr.Button("Drink Water Today!")
                
            outputd = gr.Textbox(label="Darnabot:")
  
    
            btnw.click(update_water_and_motivation, outputs=[outputw, outputd])
            
            
            gr.Markdown("## Some Tips for Healthy Living:\n\n")
            gr.HTML("""<iframe src="https://www.wellnesseveryday.org/images/stigma-reduction/wellness-tips/EveryDayWellnessTips.pdf" 
                width="100%" height="500px//"></iframe>""")
            
            
            #gr.HTML("""<iframe src="https://www.baycrest.org/Baycrest_Centre/media/content/101_HealthTips.pdf" width="100%" height="500px//"></iframe>""")
            
            

                    

        
        
    demo.launch(server_name='0.0.0.0', server_port=3020, share=False)

if __name__ == "__main__":
    create_gradio_interface()
