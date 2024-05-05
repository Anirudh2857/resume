import streamlit as st
import openai
import PyPDF2

# Set up OpenAI API
openai.api_key = "Enter you Key"

# Function to extract text from PDF file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to process CV and job description and generate score and explanation
def process_cv_job(cv_text, job_description):
    # Split text into smaller chunks to fit within the maximum context length
    max_context_length = 4096
    max_input_length = max_context_length - len("The candidate's CV:\n\nThe job description:\n\nProvide a score from 1 to 10 indicating the suitability of the candidate for the specified role and an explanation of the score (2-4 sentences).")
    
    cv_chunks = [cv_text[i:i+max_input_length//2] for i in range(0, len(cv_text), max_input_length//2)]
    job_chunks = [job_description[i:i+max_input_length//2] for i in range(0, len(job_description), max_input_length//2)]
    
    # Initialize variables for score and explanation
    total_score = 0
    total_explanation = ''
    
    # Process each chunk separately
    for cv_chunk, job_chunk in zip(cv_chunks, job_chunks):
        prompt = f"The candidate's CV:\n{cv_chunk}\n\nThe job description:\n{job_chunk}\n\nProvide a score from 1 to 10 indicating the suitability of the candidate for the specified role and an explanation of the score (2-4 sentences)."
        
        # Use OpenAI to generate response
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=max_context_length  # Limit the number of tokens to avoid exceeding the maximum context length
        )
        
        # Extract score and explanation from OpenAI response
        score_explanation = response.choices[0].message['content'].strip()
        print("Score explanation:", score_explanation)  # Add this line for debugging
        
        # Find the first word that can be converted to an integer (this assumes the score is the first integer encountered)
        score_str = next((word for word in score_explanation.split() if word.isdigit()), None)
        if score_str:
            score = int(score_str)
        else:
            # Handle case where no score is found
            score = 0  # Set a default score or handle it as appropriate for your application
        
        explanation = ' '.join(score_explanation.split()[1:])
        
        # Accumulate total score and explanation
        total_score += score
        total_explanation += explanation + ' '
    
    # Calculate average score
    average_score = total_score / len(cv_chunks)
    
    return average_score, total_explanation.strip()

# Streamlit web interface
def main():
    st.title("AI CV Screening System")
    st.write("Upload a candidate's CV and a job description to get a suitability score.")
    
    # Upload CV and job description
    cv_file = st.file_uploader("Upload Candidate's CV", type=['txt', 'pdf'])
    job_description_file = st.file_uploader("Upload Job Description", type=['txt', 'pdf'])
    
    if cv_file is not None and job_description_file is not None:
        try:
            # Read text from uploaded files
            if cv_file.type == 'application/pdf':
                cv_text = extract_text_from_pdf(cv_file)
            else:
                cv_text = cv_file.read().decode("utf-8", errors="ignore")
                
            if job_description_file.type == 'application/pdf':
                job_description = extract_text_from_pdf(job_description_file)
            else:
                job_description = job_description_file.read().decode("utf-8", errors="ignore")
            
            # Process CV and job description
            score, explanation = process_cv_job(cv_text, job_description)
            
            # Display score and explanation
            st.write(f"Suitability Score: {score:.2f}")
            st.write("Explanation:")
            st.write(explanation)
        except Exception as e:
            st.error(f"Error: {str(e)}")
        

if __name__ == "__main__":
    main()
