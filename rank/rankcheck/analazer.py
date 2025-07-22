import pdfplumber
import spacy
from groq import Groq
import json

def extract_text_from_pdf(pdf_path):
    text=""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text +=page.extract_text() + "\n"
    return text.strip()

API_KEY= "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"

def analy_resume_llm(resume_text:str,job_description:str)->dict:
    prompt =f"""
    Assistant for Resume Analysis.
    Given a Resme and job Description Extract the details:
    1.Identify All the Skilss
    2.Calculate Years of Experience
    3.Categorize the RPojects
    4.Rank the resume based on job Description  
      
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Provide the output in valid JSON Format with this structure
    {{
        "rank":"<percentage>",
        "skills":["skill1", "skill2",....],
        "total_experience":"<number of years of Experience>",
        "project_category":["category1", "category2",....]
    }}
    """
    
    try:
        client =Groq(api_key=API_KEY)
        response = client.chat.completions.create(
            model = "meta-llama/llama-4-scout-17b-16e-instruct",
            messages =[{"role":"user", "content":prompt}],
            temperature=0.7,
            response_format ={"type": "json_object"},
        )
        result=response.choices[0].message.content
        return json.loads(result)
    
    except Exception as e:
        print("LLM Erros" ,e)
        
def process_resume(pdf_path,job_description):
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        print("Extracted Resume Text:", resume_text[:500])
        data = analy_resume_llm(resume_text,job_description)
        return data
    except Exception as e:
        print(e)
        return None