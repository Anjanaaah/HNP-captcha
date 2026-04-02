import pandas as pd
import json
import os
import numpy as np

# --- USER CONFIGURATION (CHECK THESE CAREFULLY) ---
# 1. Where is the CSV?
CSV_PATH = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\dataset\labels.csv"

# 2. Where are the images? (Check if it is 'Anjan_proj' or 'Anjan_pro')
# Based on your logs, it seems to be 'Anjan_proj'
IMAGES_DIR = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\dataset\pictures"

# 3. Where to save the chunks?
OUTPUT_DIR = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\dataset_chunks"

NUM_CHUNKS = 5

def fix_dataset():
    print(f"Checking paths...")
    if not os.path.exists(CSV_PATH):
        print(f"❌ ERROR: CSV not found at {CSV_PATH}")
        return
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ ERROR: Image folder not found at {IMAGES_DIR}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Reading CSV...")
    df = pd.read_csv(CSV_PATH)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    valid_entries = []
    missing_count = 0
    
    print("Validating images...")
    for index, row in df.iterrows():
        file_name = row['image_path']
        label = str(row['captcha_text'])
        
        # Create absolute path
        full_image_path = os.path.join(IMAGES_DIR, file_name)
        full_image_path = os.path.abspath(full_image_path) # Force absolute path
        
        # KEY FIX: Ensure path exists before adding
        if os.path.exists(full_image_path):
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
            valid_entries.append(entry)
        else:
            missing_count += 1
            if missing_count < 5: # Print first 5 missing to help debug
                print(f"⚠️ Missing file: {full_image_path}")

    print(f"\nSummary:")
    print(f"✅ Valid Images: {len(valid_entries)}")
    print(f"❌ Missing Images: {missing_count}")
    
    if len(valid_entries) == 0:
        print("CRITICAL ERROR: No valid images found! Check your IMAGES_DIR path.")
        return

    # Split and Save
    chunks = np.array_split(valid_entries, NUM_CHUNKS)
    
    for i, chunk_data in enumerate(chunks):
        part_num = i + 1
        output_file = os.path.join(OUTPUT_DIR, f"train_part_{part_num}.json")
        
        # Convert numpy array back to list for JSON
        chunk_list = chunk_data.tolist()
        
        with open(output_file, 'w') as f:
            json.dump(chunk_list, f, indent=2)
        print(f"Saved {output_file} ({len(chunk_list)} images)")

    # VERIFICATION
    print("\n--- FINAL CHECK ---")
    with open(os.path.join(OUTPUT_DIR, "train_part_1.json"), 'r') as f:
        test_data = json.load(f)
        first_image = test_data[0]['messages'][0]['content'][0]['image']
        print(f"Sample Image Path: {first_image}")
        if first_image is None:
            print("❌ TEST FAILED: Image path is still None!")
        else:
            print("✅ TEST PASSED: Image path is valid.")

if __name__ == "__main__":
    fix_dataset()