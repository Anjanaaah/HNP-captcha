import pandas as pd
import json
import os
import numpy as np

# --- CONFIGURATION ---
CSV_PATH = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\dataset\labels.csv"
IMAGES_DIR = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\dataset\pictures"
OUTPUT_DIR = "dataset_chunks" # Where we save the JSON parts
NUM_CHUNKS = 5  # Splits 100k into 5 parts of 20k each

os.makedirs(OUTPUT_DIR, exist_ok=True)

def split_data():
    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Shuffle the data so each chunk is random
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split into chunks
    chunks = np.array_split(df, NUM_CHUNKS)
    
    for i, chunk_df in enumerate(chunks):
        part_num = i + 1
        formatted_data = []
        
        print(f"Processing Part {part_num} ({len(chunk_df)} images)...")
        
        for index, row in chunk_df.iterrows():
            file_name = row['image_path']
            label = str(row['captcha_text'])
            full_image_path = os.path.join(IMAGES_DIR, file_name)
            
            # Skip missing files
            if not os.path.exists(full_image_path):
                continue

            # Qwen-VL Format
            entry = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": full_image_path},
                            {"type": "text", "text": "Read the text in this image."}
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": label}]
                    }
                ]
            }
            formatted_data.append(entry)
        
        # Save this chunk
        output_file = os.path.join(OUTPUT_DIR, f"train_part_{part_num}.json")
        with open(output_file, 'w') as f:
            json.dump(formatted_data, f, indent=2)
            
        print(f"Saved {output_file}")

if __name__ == "__main__":
    split_data()