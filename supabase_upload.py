import streamlit as st
from config import SEARCH_WORD
import pandas as pd
import numpy as np
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    return create_client(url, key)
supabase = get_client()

LOCAL_FOLDER_PATH = f"./articles-{SEARCH_WORD}" 
SUPABASE_BUCKET_NAME = "DTSC_project"
SUPABASE_FOLDER_PATH = "txt/"

def upload_contents(local_dir,supa_folder_path,supa_bkname):
    for file in os.listdir(local_dir):
        local_file_path = os.path.join(local_dir,file)
        if not os.path.isfile(local_file_path):
            continue
        if not file.endswith('.txt'):
            print(f'{file} not a .txt')
            continue
        

        
        supabase_file_path = os.path.join(supa_folder_path, file).replace('\\', '/')
        with open(local_file_path,'rb') as file_body:
            try:
                res = supabase.storage.from_(supa_bkname).upload(
                    path=supabase_file_path,
                    file=file_body,
                    file_options={"content-type": "text/plain","upsert": "true"},
                )
                if res.status_code == "200":
                    print("good, uploaded")
            except Exception as e:
                print(f"error: {e}")
            


def main():
    upload_contents(LOCAL_FOLDER_PATH,SUPABASE_FOLDER_PATH,SUPABASE_BUCKET_NAME)
    

if __name__ == "__main__":
    main()

            


