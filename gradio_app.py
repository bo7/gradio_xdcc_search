import gradio as gr
import subprocess
import pandas as pd
import json

def get_raw_data_from_go():
    # Call the Go binary and capture output
    result = subprocess.run(["xdcc-cli", "getdata"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Check for errors
    if result.returncode != 0:
        return None, None, f"Error: {result.stderr}"
    
    # Assuming the Go program outputs JSON
    try:
        data = json.loads(result.stdout)
        headers = data['headers']
        rows = data['rows']
        return headers, rows
    except json.JSONDecodeError:
        return None, None, "Failed to parse Go output."

def search_xdcc(query):
    # Call the Go function to get raw data
    headers, rows, error = get_raw_data_from_go()
    
    if error:
        return None, None, error
    
    # Convert the raw data into a DataFrame
    if headers and rows:
        df_cleaned = pd.DataFrame(rows, columns=headers)
        
        # Add a column for checkboxes (initially all False)
       df_cleaned['Select'] = False

        # Limit the results to the top 10 rows
        df_cleaned = df_cleaned.head(10)

        # Reorder the columns as Select, Size, and File Name
        df_display = df_cleaned[['Select', 'Size', 'File Name']]

        return df_display, df_cleaned, "Search successful!"
    else:
        return None, None, "No data returned."

def download_selected(selection):
    # selection will be a DataFrame with the updated checkbox states
    if selection is None or selection.empty:
        return "No files selected for download."

    selected_rows = selection[selection['Select']]

    if selected_rows.empty:
        return "No files selected for download."

    messages = []
    
    for _, row in selected_rows.iterrows():
        file_name = row['File Name']
        url = row['URL']
        
        try:
            # Construct the download command
            command = ["xdcc-cli", "download", url]
            
            # Run the download command
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check if the download was successful
            if result.returncode == 0:
                messages.append(f"Downloaded {file_name} successfully.")
            else:
                messages.append(f"Failed to download {file_name}. Error: {result.stderr}")
        
        except Exception as e:
            messages.append(f"An error occurred while downloading {file_name}: {str(e)}")
    
    return "\n".join(messages)

# Define your Gradio interface
def interface():
    with gr.Blocks() as demo:
        query = gr.Textbox(label="Search Query")
        search_btn = gr.Button("Search")
        results = gr.DataFrame(label="Search Results", interactive=True)
        download_btn = gr.Button("Download Selected")
        output = gr.Textbox(label="Output", interactive=False)

        # Store both the displayed DataFrame and the one with URLs
        search_btn.click(search_xdcc, inputs=query, outputs=[results, output])
        download_btn.click(download_selected, inputs=[results], outputs=output)

    # Launching the Gradio app on 0.0.0.0 to allow external connections
    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    interface()
