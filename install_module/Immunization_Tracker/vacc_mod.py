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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
import shutil
import urllib.parse
from ollama import AsyncClient
import asyncio


# Ensure the upload directory exists
#UPLOADS_DIR = "/workspace/uploads"
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

## TO DO ##can pass down base url from flask to make it work
BASE_URL= "http://localhost:3022"


# Function to initialize the database and create the personas table if not exists
def initialize_database():
    if not os.path.exists(os.path.join(UPLOADS_DIR, 'vaccine.db')):
        conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'vaccine.db'))
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS personas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE)''')
        conn.commit()
        conn.close()

# Function to create a persona with linked table for vaccines
def create_persona(persona_name):
    if persona_name is not None:
        conn = None
        try:
            conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'vaccine.db'))
            c = conn.cursor()
        
            # Check if the persona already exists
            c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
            existing_persona = c.fetchone()
            
            if existing_persona:
                persona_id = existing_persona[0]
            else:
                # Insert new persona
                c.execute("INSERT INTO personas (name) VALUES (?)", (persona_name,))
                persona_id = c.lastrowid
            
                # Create linked table for vaccines
                c.execute(f'''CREATE TABLE IF NOT EXISTS vaccine_{persona_id} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            vaccine TEXT,
                            date TEXT,
                            file_name TEXT,
                            file_path TEXT)''')
            
            conn.commit()
            
            return (
                gr.update(value=""),  # Clear the input
                gr.update(choices=get_personas(), value=persona_name, visible=True),
                gr.update(choices=['Add/View', 'Delete'], visible=True)
            )
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return (
                gr.update(value=persona_name),  # Keep the input value
                gr.update(choices=get_personas(), visible=True),
                gr.update(choices=['Add/View', 'Delete'], visible=True)
            )
        finally:
            if conn:
                conn.close()
    else:
        # When the field value is None (cleared), update the list of personas
        updated_personas = get_personas()
        return (
            gr.update(value=""),  # Keep the input clear
            gr.update(choices=updated_personas, value=None, visible=True),
            gr.update(choices=['Add/View', 'Delete'], visible=True)
        )



        
# Function to get all personas
def get_personas():
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'vaccine.db'))
    c = conn.cursor()
    c.execute("SELECT name FROM personas")
    personas = [row[0] for row in c.fetchall()]
    conn.close()
    return personas

# Function to select persona and show measurement options
def select_persona(persona_name):
    if persona_name:
        return gr.update(choices=['Add/View', 'Delete'], visible=True, value=None)
    return gr.update(choices=[], visible=False, value=None)



# Function to add vaccine with file
def add_vaccine(persona_name, vaccine_name, date, files):
    try:
        datetime.datetime.strptime(date, "%Y-%m")
    except ValueError:
        print(f"Invalid date {date}. Entry not saved.")
        return

    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'vaccine.db'))
    c = conn.cursor()

    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]

    # Insert the vaccine info into the database, even if no files are attached
    if not files:
        c.execute(f"INSERT INTO vaccine_{persona_id} (vaccine, date, file_name, file_path) VALUES (?, ?, ?, ?)", 
                  (vaccine_name, date, None, None))
                  
    # Save the files if provided
    else:
        file_names = []
        file_paths = []

        
        for file in files:
                file_name = os.path.basename(file.name)
                destination_path = os.path.join(UPLOADS_DIR, file_name)
                
                # Copy the file to the UPLOADS_DIR
                shutil.copy(file, destination_path)
            
                # Store the correct path in the database
                file_names.append(file_name)
                file_paths.append(destination_path)

     

        # Insert vaccine with date and file info
        for file_name, file_path in zip(file_names, file_paths):
            c.execute(f"INSERT INTO vaccine_{persona_id} (vaccine, date, file_name, file_path) VALUES (?, ?, ?, ?)", 
                  (vaccine_name, date, file_name, file_path))
    conn.commit()
    conn.close()

#delete a vaccine
def delete_vaccine_and_update(persona_name, vaccine_name, measure):
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'vaccine.db'))
    c = conn.cursor()
    
    try:
        #for case-insensitive comparison
        persona_name_lower = persona_name.lower()
        vaccine_name_lower = vaccine_name.lower()
        
        # Get the persona's ID (case-insensitive)
        c.execute("SELECT id FROM personas WHERE LOWER(name) = ?", (persona_name_lower,))
        result = c.fetchone()
        if result is None:
            print(f"No persona found with name: {persona_name}")
            return None, None, None
        persona_id = result[0]
        
        # Fetch all records for the given vaccine (case-insensitive)
        c.execute(f"SELECT id, file_path FROM vaccine_{persona_id} WHERE LOWER(vaccine) = ?", (vaccine_name_lower,))
        records = c.fetchall()
        
        if not records:
            print(f"No records found for vaccine: {vaccine_name}")
            return None, None, None
        
        # Delete associated files
        for record in records:
            file_path = record[1]
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete the records from the database (case-insensitive)
        c.execute(f"DELETE FROM vaccine_{persona_id} WHERE LOWER(vaccine) = ?", (vaccine_name_lower,))
        
        conn.commit()
        print(f"Deleted {len(records)} record(s) for vaccine: {vaccine_name}")
        
        graph, table_data, files = update_vaccine_graph_and_table(persona_name, measure)
        return graph, table_data, files
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None, None, None
    
    finally:
        conn.close()

"""
# Function to create vaccine graph and table
def broken_bars(xstart, xwidth, ystart, yh, colors):
    
    if len(xstart) != len(xwidth) or len(xstart) != len(colors):
        raise ValueError('xstart, xwidth and colors must have the same length')
    
    shapes = []
    
    for k in range(len(xstart)):
        shapes.append(dict(type="rect",
                           x0=xstart[k],
                           y0=ystart,
                           x1=xstart[k] + xwidth[k],
                           y1=ystart+yh,
                           fillcolor=colors[k],
                           line_color=colors[k]))
    return shapes
"""
# Function to create vaccine graph and table
def broken_bars(xstart, xwidth, ystart, yh, colors, radius=0.1):
    if len(xstart) != len(xwidth) or len(xstart) != len(colors):
        raise ValueError('xstart, xwidth, and colors must have the same length')
    
    shapes = []
    for k in range(len(xstart)):
        x0 = xstart[k]
        x1 = xstart[k] + xwidth[k]
        y0 = ystart
        y1 = ystart + yh
        
        path = f'M {x0+radius},{y0} L {x1-radius},{y0} Q {x1},{y0} {x1},{y0+radius} L {x1},{y1-radius} Q {x1},{y1} {x1-radius},{y1} L {x0+radius},{y1} Q {x0},{y1} {x0},{y1-radius} L {x0},{y0+radius} Q {x0},{y0} {x0+radius},{y0} Z'
        
        shapes.append(dict(
            type="path",
            path=path,
            fillcolor=colors[k],
            line_color=colors[k]
        ))
    
    return shapes

    
def create_vaccine_graph_and_table(persona_name):
    conn = sqlite3.connect(os.path.join(UPLOADS_DIR, 'vaccine.db'))
    c = conn.cursor()
    
    # Get the persona's ID
    c.execute("SELECT id FROM personas WHERE name = ?", (persona_name,))
    persona_id = c.fetchone()[0]
    
    # Fetch vaccine records for the persona
    c.execute(f"SELECT date, vaccine, file_name FROM vaccine_{persona_id} ORDER BY date ASC")
    readings = c.fetchall()
    
    conn.close()
    
    if not readings:
        return None, None
    
    # Create DataFrame for table
    df = pd.DataFrame(readings, columns=['Date', 'Vaccine', 'File'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['YearMonthly'] = df['Date'].dt.to_period('M')
    df = df.sort_values('YearMonthly')
    #df['File'] = df['File'].apply(lambda file: f'[{file}](http://localhost:8000/file={UPLOADS_DIR}/{file})' if file else "")
   
    
    ##create graph
    
    df['Year'] = df['Date'].dt.year
    df['MonthFraction'] = (df['Date'].dt.month - 1) / 12
    df['YearMonth'] = df['Year'] + df['MonthFraction']

    # Generate colors using a colorscale
    num_vaccines = len(df)
    color_scale = px.colors.sequential.Viridis
    if num_vaccines == 1:
        colors = [color_scale[len(color_scale) // 2]]  # Middle color for single vaccine
    else:
        colors = [color_scale[int(i/(num_vaccines-1) * (len(color_scale)-1))] for i in range(num_vaccines)]


    # Create shapes for broken bars, grouped by vaccine name
    shapes = []
    unique_vaccines = df['Vaccine'].unique()

    for vaccine in unique_vaccines:
        vaccine_rows = df[df['Vaccine'] == vaccine]
        y_position = list(unique_vaccines).index(vaccine)
        for i, row in vaccine_rows.iterrows():
            shapes.extend(broken_bars([row['YearMonth']], [2], y_position, 0.8, [colors[i]]))

    # Create the figure
    fig = go.Figure()

    # Add invisible scatter trace for hover information
    fig.add_trace(go.Scatter(
        x=df['YearMonth'],
        y=df['Vaccine'],
        mode='markers',
        marker=dict(size=0),
        hoverinfo='text',
        text=df['Date'].dt.strftime('%Y %B'),
        showlegend=False
    ))

    # Add the broken bar shapes to the figure
    for shape in shapes:
        fig.add_shape(shape)

    # Update layout
    fig.update_layout(
        title=f'Vaccine Timeline for {persona_name}',
        xaxis=dict(
            title='Year',
            tickmode='linear',
            showgrid=False,
            dtick=3,  # Show labels every 5 years
            tick0=df['Year'].min(),  # Start ticks at the first year
            tickvals=[year for year in range(df['Year'].min(), df['Year'].max() + 1)],  # Show all years
            ticktext=[str(year) if year % 5 == 0 else '' for year in range(df['Year'].min(), df['Year'].max() + 1)],  # Only show label every 5 years
            ticks='outside',
            ticklen=10,
            range=[df['YearMonth'].min() - 0.5, df['YearMonth'].max() + 0.5]
    ),
        yaxis=dict(
            title='Vaccines',
            showgrid=False,
            categoryorder='array',
            categoryarray=unique_vaccines.tolist()  # Ensure unique vaccines are in the same row
        ),
        height=max(500, len(unique_vaccines) * 30),  # Adjust height based on number of unique vaccines
        hovermode='closest'
)

    
    return fig, df[['YearMonthly', 'Vaccine', 'File']]


def update_vaccine_graph_and_table(persona_name, measure):
    fig, df = create_vaccine_graph_and_table(persona_name)
    
    if df is not None and not df.empty:
        # Extract file information and create Markdown content
        file_info = df['File'].dropna().unique()

        
        # Process each file name to create proper Markdown links
        processed_file_info = []
        for file_name in file_info:
            if file_name:  # Check if file_name is not empty
                # Encode the file path
                encoded_file_path = urllib.parse.quote(f"{UPLOADS_DIR}/{file_name}")
                # Construct the full URL
                file_url = f"{BASE_URL}/file={encoded_file_path}"
                # Create the Markdown link
                markdown_link = f"[{file_name}]({file_url})"
                processed_file_info.append(markdown_link)
        
        # Join the processed file links with double newlines for separation
        markdown_content = "### Attached Files\n\n #### (Links work locally. Use File Server to download)\n\n" + "\n\n".join(processed_file_info)
        
        if measure == 'Add/View':
            return (
                gr.Plot(value=fig, visible=True),
                gr.DataFrame(value=df, visible=True),
                gr.Markdown(value=markdown_content, visible=True)
            )
        elif measure == 'Delete':
            return (
                gr.Plot(visible=False),
                gr.DataFrame(value=df, visible=True),
                gr.Markdown(value=markdown_content, visible=True)
            )
    
    # If there's no data or measure is neither 'Add' nor 'Delete'
    return (
        gr.Plot(visible=False),
        gr.DataFrame(visible=False),
        gr.Markdown(visible=False)
    )



def submit_vaccine_and_update_graph(persona_name, vaccine, date, files):
    add_vaccine(persona_name, vaccine, date, files)
    fig, df = create_vaccine_graph_and_table(persona_name)
    if fig is not None and df is not None:
        return gr.Plot(value=fig, visible=True), gr.DataFrame(value=df, visible=True), gr.update(visible=True)
    return gr.Plot(visible=False), gr.DataFrame(visible=False),  gr.update(visible=False)

def populate_now():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m")
    
####File server
def list_files(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except OSError as e:
        print(f"Error listing files in {directory}: {e}")
        return []

def display_file(filename):
    try:
        file_path = os.path.join(UPLOADS_DIR, filename)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return file_path, file_path
        else:
            return file_path, None
    except Exception as e:
        print(f"Error displaying file {filename}: {e}")
        return None, None

def refresh_file_list():
    return gr.Dropdown(choices=list_files(UPLOADS_DIR))

class HealthMotivator:
    async def get_motivation(self, country):
        messages = [
            {"role": "system", "content": "You are Darnabot, travel health expert. Provide a brief message about traveling healthy, vaccines if needed and comment on location provided."},
            {"role": "user", "content": f"Give health suggestions regarding traveling to country {country}."},
        ]
        
        #async for part in await AsyncClient().chat(model='mistral-nemo', messages=messages, stream=True):
            #chunk=part['message']['content']
            #yield chunk
        try:    
            OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            async for part in await AsyncClient(host=OLLAMA_HOST).chat(model='mistral-nemo', messages=messages, stream=True):
                yield part['message']['content']
        except Exception as e:
            yield f"Remember to take care of your health. Please see links below! (Error: {str(e)})"



motivator = HealthMotivator()

async def travel_health(country):
    motivation = "Please see a Doctor for advice! "   
    async for chunk in motivator.get_motivation(country):
        motivation += chunk
        yield motivation

####GRADIO APP
def create_gradio_interface():
    initialize_database()
    
    with gr.Blocks(theme='Taithrah/Minimal', css="footer{display:none !important}") as demo:
        gr.Markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center; height: 100%; color: #FFFFFF; background-color: #4c00b0; font-weight: bold;'>IMMUNIZATIONS LOG</div>")
        
        with gr.Tab("IMMUNIZATION TRACKER"):
            with gr.Row():
                persona_name_input = gr.Textbox(label="Add Person", placeholder="Add Person")
                create_button = gr.Button("Add 👥 / Refresh ⟳")
        
            with gr.Row():
                persona_dropdown = gr.Dropdown(label="Select Person to View", choices=get_personas(), visible=bool(get_personas()))
                measure_dropdown = gr.Dropdown(label="Task", choices=['Add/View', 'Delete'], visible=False)
        
            with gr.Row():
                vaccine_input = gr.Textbox(label="Enter Immunization", visible=False, placeholder="e.g., Flu Shot")
                date_input = gr.Textbox(label="Enter Date", placeholder="YYYY-MM", visible=False)
                file_input = gr.File(label="Click to Upload a File", file_types=["image", "pdf", "text"], file_count="multiple", visible=False)
         
            with gr.Row(visible=True) as now_and_submit_row:
                now_button = gr.Button("Now", visible=False)
                submit_vaccine_button = gr.Button("Submit Immunization", visible=False)
                delete_vaccine_button = gr.Button("Delete Immunization", visible=False)
           
            vaccine_graph = gr.Plot(label="Immunization Chart", visible=False)
            vaccine_table = gr.DataFrame(label="💉 IMMUNIZATION RECORDS 💉 ", visible=False)
            file_explorer = gr.Markdown(label="View Uploaded Files", visible=False)

            def create_and_update(persona_name):
                result = create_persona(persona_name)
                personas = get_personas()
                personas_available = bool(personas)
                return (
                    *result,
                    gr.update(visible=personas_available),  # For persona_dropdown
                    gr.update(visible=False),  # For measure_dropdown
                    gr.update(visible=False),  # For vaccine_input
                    gr.update(visible=False),  # For date_input
                    gr.update(visible=False),  # For file_input
                    gr.update(visible=False),  # For now_button
                    gr.update(visible=False),  # For submit_vaccine_button
                    gr.update(visible=False),  # For delete_vaccine_button
                    gr.update(visible=False),  # For vaccine_graph
                    gr.update(visible=False),  # For vaccine_table
                    gr.update(visible=False),  # For file_explorer
                )

            create_button.click(
                create_and_update,
                inputs=persona_name_input,
                outputs=[
                    persona_name_input,
                    persona_dropdown,
                    measure_dropdown,
                    persona_dropdown,  # Additional output for visibility
                    measure_dropdown,
                    vaccine_input,
                    date_input,
                    file_input,
                    now_button,
                    submit_vaccine_button,
                    delete_vaccine_button,
                    vaccine_graph,
                    vaccine_table,
                    file_explorer,
                ]
            )
            
            persona_dropdown.change(select_persona, 
                                    inputs=persona_dropdown, 
                                    outputs=measure_dropdown)
        
            def show_measure_inputs(measure):
                vaccine_visible = gr.update(visible=measure in ['Add/View', 'Delete'])
                date_visible = gr.update(visible=measure == 'Add/View')
                file_visible = gr.update(visible=measure == 'Add/View')
                now_button_visible = gr.update(visible=measure == 'Add/View')
                submit_vaccine_visible = gr.update(visible=measure == 'Add/View')
                delete_vaccine_visible = gr.update(visible=measure == 'Delete')
                vaccine_graph_visible = gr.update(visible=measure == 'Add/View')
                vaccine_table_visible = gr.update(visible=measure in ['Add/View', 'Delete'])
                file_explorer_visible = gr.update(visible=measure in ['Add/View', 'Delete'])

                return (
                    vaccine_visible,
                    date_visible,
                    file_visible,
                    now_button_visible,
                    submit_vaccine_visible,
                    delete_vaccine_visible,
                    vaccine_graph_visible,
                    vaccine_table_visible,
                    file_explorer_visible,
                )

            measure_dropdown.change(
                show_measure_inputs, 
                inputs=measure_dropdown, 
                outputs=[
                    vaccine_input, 
                    date_input,
                    file_input,
                    now_button, 
                    submit_vaccine_button,
                    delete_vaccine_button,
                    vaccine_graph,
                    vaccine_table,
                    file_explorer 
                ]
            )

            submit_vaccine_button.click(
                submit_vaccine_and_update_graph, 
                inputs=[persona_dropdown, vaccine_input, date_input, file_input], 
                outputs=[vaccine_graph, vaccine_table, file_explorer]
            )
            
            delete_vaccine_button.click(
                delete_vaccine_and_update, 
                inputs=[persona_dropdown, vaccine_input, measure_dropdown],
                outputs=[vaccine_graph, vaccine_table, file_explorer]
            )

            persona_dropdown.change(
                update_vaccine_graph_and_table, 
                inputs=[persona_dropdown, measure_dropdown], 
                outputs=[vaccine_graph, vaccine_table, file_explorer]
            )

            measure_dropdown.change(
                update_vaccine_graph_and_table, 
                inputs=[persona_dropdown, measure_dropdown], 
                outputs=[vaccine_graph, vaccine_table, file_explorer]
            )
            
            

            now_button.click(populate_now, inputs=[], outputs=[date_input])
    
        with gr.Tab("TIPS"):
        
            gr.Markdown("# Are you traveling?\n ## See travel health suggestions:\n\n")
            
            with gr.Row():
                inputt = gr.Textbox(label="Where are you traveling to mate!")
                btnw = gr.Button("Darnabot Answers")
                
            outputd = gr.Markdown(label="Darnabot:")
  
    
            btnw.click(travel_health, inputs=inputt, outputs=[outputd])
            
            gr.HTML("""
            <iframe src="https://www.vaccinehub.com.au/map/travel" 
            width="100%" height="580px"></iframe>
            """)
            
            gr.Markdown("## Are you up to date on Immunizations?\n See Immunization suggestions:")
            gr.HTML("""
        <iframe src="https://www2a.cdc.gov/nip/adultimmsched/#print" 
        width="100%" height="500px"></iframe>
        """)
    
            gr.Markdown("# Informational Links?\n ## See Immunization suggestions:")
            gr.HTML("""
        <a href="https://www.cdc.gov/vaccines/imz-schedules/adult-easyread.html" target="_blank">Vaccine by Age - CDC</a>
    """)

            gr.HTML("""
        <a href="https://www.travelvax.com.au/holiday-traveller/vaccination-requirements" target="_blank">Travelax.com Health App</a>
        """)
            gr.HTML("""
        <a href="https://www.cdc.gov/travel" target="_blank">CDC Travelers' Health</a>
        """)

                
        with gr.Tab("FILE SERVER"):
            with gr.Row():
                file_list = gr.Dropdown(choices=list_files("uploads"), label="Select a file")
                display_area = gr.File(label="File Download")
                refresh_button = gr.Button("Refresh File List")
            display_area2 = gr.Image(label="File Viewer")
    
            def refresh_dropdown():
                file_list.choices = update_file_list()
                
            file_list.change(
                        fn=display_file,
                        inputs=[file_list],
                        outputs=[display_area, display_area2]
                )
            
            refresh_button.click(
                fn=refresh_file_list,
                inputs=[],
                outputs=[file_list]
            )

            # Update file list when dropdown is clicked
            file_list.select(
                fn=refresh_file_list,
                inputs=[],
                outputs=[file_list]
            )
            
    demo.launch(server_name='0.0.0.0', server_port=3022, share=False, allowed_paths=[UPLOADS_DIR])

if __name__ == "__main__":
    create_gradio_interface()
