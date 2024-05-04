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
#modules torch, sentence transformers, gradio, json
#uses chromaminer to chunk and embed and then uses function to extract relevant component
import torch
import os
import re
import json
import random
import requests
import gradio as gr
import chromadb

from transformers import pipeline

#this could be modified to include a LLM of your choice. In this case I picked TinyLLama due to it size for effectiveness

#pip install --upgrade transformers
#gemma wouldnt answer medical questions but is useful for other things
#pipe = pipeline("text-generation", model="google/gemma-2b-it", device_map="auto", torch_dtype=torch.bfloat16, token="{hf_access_token_from_your_hf_profile_settings}")

#Currently set to use tiny llama
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")


#this truncates the content words for use by Chroma search to build context for queries
def truncate_words(documents):
    truncated_documents = []
    for doc in documents:
        doc=str(doc)
        words = doc.split()[:300]  # Truncate each document to 300 words
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
        # Check if persist_directory exists; if not, skip attempting to create a client.
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
        result += existing_data.get(key, " ")[:150]
    if med_value is not None:
        print(med_value)
        key = 'darnahi_medications'
        result += existing_data.get(key, " ")[:350]
    if summary_value is not None:
        print(summary_value)
        key = 'darnahi_summary'
        result += existing_data.get(key, "No data found for 'summary' key.")[:350]
    if past_medical_history_value is not None:
        print(past_medical_history_value)
        key = 'darnahi_past_medical_history'
        result += existing_data.get(key, " ")[:150]  
    if xmr_value is not None:
        print(xmr_value)
        key = 'darnahi_xmr'
        result += existing_data.get(key, " ")[:150]

     # Check if no pattern matched
    if not (darna_match or med_match or summary_match or xmr_match or past_medical_history_match):
        # Your logic here for when no pattern matches, currently placeholder
        collection_name="documents_collection"
        context, sources = generate_context_and_sources(query, collection_name, os.path.join(directory, 'chroma_storage'))

        print(context, sources)
        result = context[:150]
    if result is None:
        result={''}
   
    print(result)
    return result

#generate a chat function using the query and context
def my_function(query, request: gr.Request):
    #pass userID
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
    #context, sources=generate_context_and_sources("past medical history")
    #print(context, sources)
    #use this for original llama1b chat
    messages = [
        {"role": "user", "content": "You are Darnabot?"},
        {"role": "assistant", "content": "I am 'Darnabot', AI health assistant with domain expertise"},
        {"role": "user", "content": f"'Darnabot' Answer query:{query}:{context}"},
        ]
    
    #print(messages)
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    outputs = pipe(prompt, max_new_tokens=300, do_sample=False, top_k=50)
    
    generated_text=outputs[0]["generated_text"]
    last_user_message = messages[-1]["content"]
    try:

        end_of_last_user_message = generated_text.rindex(last_user_message) + len(last_user_message)
        final_output = generated_text[end_of_last_user_message:].strip()
    except ValueError:
        final_output = generated_text
    
    
    return final_output
    
    
    
    return outputs

"""#def function to download url pdf and add to data repository to vectorize it
def download_url(input_text):
    try:
        # Process the input in some way
        os.makedirs("data_darna", exist_ok=True)
        r=input_text
        file_path = os.path.join("data_darna", input_text.rpartition("/")[2])
        r = requests.get(input_text, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(r.content)
            #chunk it up
            #the cmd allows launch of venv called nlpv that has the modules needed for chroma_mminer
            cmd = "/bin/bash -c 'source ../darnavenv/bin/activate && python chroma_miner.py'"
            os.system(cmd)
            return "Downloaded and Added to Chroma Vector Store embeddings: " + input_text
        else:
            return f"Failed to retrieve {input_text}"
    except Exception as e:
            return f"An error occurred: {str(e)}" """

#set up the UI
with gr.Blocks(theme=gr.themes.Soft(primary_hue=gr.themes.colors.orange)) as demo:
    with open('motivation.json', 'r') as file:
        proverbs = json.load(file)
    random_key = random.choice(list(proverbs.keys()))
    proverb = proverbs[random_key]
    gr.Markdown(f"""<div style='text-align: center; font-size: 1rem;'>
<i>{proverb}</i>
</div>
""")
    with gr.Tab("Ask Me:"):
        initial_state={'input1': ""}
        input1 = gr.Textbox(label="ASK :", value=initial_state['input1'])
        output1 = gr.Textbox(label="DARNABOT :")
        title="Ask DarnaBot"
        btn1 = gr.Button("GO")
        btn1.click(my_function, inputs=[input1], outputs=output1)

    """with gr.Tab("Add to Knowledge Database"):
        input2 = gr.Textbox(label="Please enter url for PDF file:")
        output2 = gr.Textbox(label="Process Message:")
        btn2 = gr.Button("Download and Embed")
        btn2.click(download_url, inputs=input2, outputs=output2)"""



if __name__ == "__main__":
    # Launch the interface
    #make it accessible on local network
    demo.launch(server_name='0.0.0.0', server_port=3012, share=False)
    
    
#graveyard

