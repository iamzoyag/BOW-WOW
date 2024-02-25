import sqlite3
import requests
from bs4 import BeautifulSoup
import os
from youtube_transcript_api import YouTubeTranscriptApi
from collections import Counter
import math
import fitz
import json
import io
from PIL import Image
import hashlib
import pdfkit

pdf_file_name = "daa.pdf"

def databaseName(pdf_file_name):
    database_name = pdf_file_name.split('.')
    database_name = database_name[0] + '.db'
    return database_name

def create_table(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_sentences
                (sentence TEXT,
                 font_size INTEGER,
                 page_number INTEGER)''')
    conn.commit()
    conn.close()

def scrape(pdf_file_name):
    database_name = databaseName(pdf_file_name)
    create_table(database_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    pdf = fitz.open(pdf_file_name)
    for pageNum, page in enumerate(pdf):
        dict = page.get_text("dict")
        blocks = dict["blocks"]
        for block in blocks:
            if "lines" in block.keys():
                spans = block['lines']
                for span in spans:
                    data = span['spans']
                    for lines in data:
                        sentence = lines['text']
                        sentence = sentence.strip()
                        font_size = round(lines['size'])
                        if sentence == '' or sentence == ' ' or len(sentence) == 1:
                            continue
                        c.execute("INSERT INTO pdf_sentences (sentence, font_size, page_number) VALUES (?, ?, ?)", (sentence, font_size, pageNum+1))
                        conn.commit()
    conn.close()

def getNumberOfPages(pdf_file_name):
    pdf_file = fitz.open(pdf_file_name)
    num_pages = pdf_file.page_count
    return num_pages

def getHeading(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT sentence FROM pdf_sentences WHERE page_number = ? AND font_size = (SELECT MAX(font_size) FROM pdf_sentences WHERE page_number = ?)", (page_number, page_number))
    results = c.fetchall()
    conn.close()
    return results

def getPageContent(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT sentence FROM pdf_sentences WHERE page_number = ? AND font_size NOT IN (SELECT MAX(font_size) FROM pdf_sentences WHERE page_number = ? GROUP BY page_number)", (page_number, page_number))
    results = c.fetchall()
    conn.close()
    return results

def makeQuery(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    create_table(database_name)
    content = getPageContent(pdf_file_name, page_number)
    heading = getHeading(pdf_file_name, page_number)
    content_query = ''
    heading_query = ''
    for i in range(len(content)):
        content_query += content[i][0] + ' '
    for i in range(len(heading)):
        heading_query += heading[i][0] + ' '
    combined_query = "The slide topic is " + heading_query + " and the contents of the slides are " + content_query + "\nmake me brief study notes for this slide" 
    return heading_query, content_query, combined_query

def generate_problems_gemi(pdf_file_name, page_number):
    gemini_url = "https://documentai.googleapis.com"
    heading_query, content_query, _ = makeQuery(pdf_file_name, page_number)
    payload = {
        "slide_topic": heading_query,
        "slide_content": content_query,
        "num_problems": 3
    }
    try:
        response = requests.post(gemini_url, json=payload)
        if response.status_code == 200:
            print(response)
            problems = response.json()["problems"]
            return problems
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error generating problems via Gemini API: {str(e)}")
        return None

def generate_problem_set(problem_set_content, output_filename):
    html_content = "<html><body>"
    html_content += "<h1>Math Problems</h1>"
    for i, problem in enumerate(problem_set_content, start=1):
        html_content += f"<p><strong>Problem {i}:</strong><br>{problem}</p>"
    html_content += "</body></html>"

    pdfkit_config = pdfkit.configuration()
    try:
        pdfkit.from_string(html_content, output_filename, configuration=pdfkit_config)
        print(f"Problem set saved as {output_filename}")
    except Exception as e:
        print(f"Error generating problem set PDF: {str(e)}")

def generate_problem_set_pdf(pdf_file_name, output_filename):
    num_pages = getNumberOfPages(pdf_file_name)
    all_problems = []

    for i in range(1, num_pages):
        problems = generate_problems_gemi(pdf_file_name, i)
        print(problems)
        all_problems.extend(problems)

    generate_problem_set(all_problems, output_filename)
    
def generate_lecture_notes_pdf(lecture_content, output_filename):
    html_content = "<html><body>"
    html_content += "<h1>Lecture Notes</h1>"
    for i, content in enumerate(lecture_content, start=1):
        html_content += f"<div><strong>Slide {i}:</strong><br>{content}</div>"
    html_content += "</body></html>"

    pdfkit_config = pdfkit.configuration()
    try:
        pdfkit.from_string(html_content, output_filename, configuration=pdfkit_config)
        print(f"Lecture notes saved as {output_filename}")
    except Exception as e:
        print(f"Error generating lecture notes PDF: {str(e)}")

def generate_lecture_notes(pdf_file_name, output_filename):
    num_pages = getNumberOfPages(pdf_file_name)
    all_lecture_content = []

    for i in range(1, num_pages):
        heading, content, _ = makeQuery(pdf_file_name, i)
        problems = generate_problems_gemi(pdf_file_name, i)
        lecture_notes = f"Slide Topic: {heading}\n\nContent:\n{content}\n\nProblems:\n"
        lecture_notes += "\n".join(problems)
        all_lecture_content.append(lecture_notes)

    generate_lecture_notes_pdf(all_lecture_content, output_filename)
    
def extractImages(pdf_file_name):
    folder_name = pdf_file_name.split(".")[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    pdf_file = fitz.open(pdf_file_name)
    saved_hashes = set()
    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]
        image_list = page.get_images()
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_hash = hashlib.md5(image_bytes).hexdigest()
            if image_hash not in saved_hashes:
                image = Image.open(io.BytesIO(image_bytes))
                filename = f"{folder_name}/image{page_index+1}_{image_index}.{image_ext}"
                image.save(open(filename, "wb"))
                saved_hashes.add(image_hash)

def main():
    pdf_file_name = "daa.pdf"
    output_filename = "all_problems.pdf"
    lecture_notes_filename = "lecture_notes.pdf"
    extractImages(pdf_file_name)
    generate_problem_set_pdf(pdf_file_name, output_filename)
    generate_lecture_notes(pdf_file_name, lecture_notes_filename)
    lecture_data_1 = {
        'title': 'Machine Learning Lecture 1',
        'subtitle': 'Introduction to Machine Learning',
        'lecture_notes':'lecture_notes.pdf',
        'problem_set': 'all_problems.pdf'
    }
    return lecture_data_1

if __name__ == "__main__":
    main()
