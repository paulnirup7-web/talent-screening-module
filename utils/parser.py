import re
import PyPDF2

# A standard set of English stop words to filter out common structural words
STOP_WORDS = {
    'the', 'and', 'of', 'to', 'in', 'is', 'for', 'a', 'an', 'on', 'at', 'by', 
    'with', 'from', 'as', 'about', 'into', 'through', 'during', 'including', 
    'until', 'against', 'among', 'throughout', 'up', 'over', 'after', 
    'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
    'does', 'did', 'but', 'or', 'if', 'because', 'while', 'this', 'that', 
    'these', 'those', 'then', 'there', 'here', 'all', 'any', 'both', 'each', 
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 
    'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 
    'now', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'my', 'your', 
    'his', 'her', 'their', 'its', 'we', 'our', 'us', 're'
}

def extract_text_from_pdf(pdf_file):
    """
    Extracts and merges all text content from a PDF file using PyPDF2.
    
    Parameters:
        pdf_file: A path to a PDF file or a file-like object (e.g., BytesIO from Streamlit).
        
    Returns:
        str: The extracted text from the PDF.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def clean_and_tokenize(text):
    """
    Utility function to preprocess text by:
    1. Converting to lowercase.
    2. Removing punctuation (while retaining symbols like +, #, . for programming language tokens e.g. C++, C#, .NET).
    3. Splitting into tokens.
    
    Parameters:
        text (str): The raw text to process.
        
    Returns:
        list: A list of cleaned word tokens.
    """
    if not text:
        return []
    
    # Lowercase the input string
    text = text.lower()
    
    # Replace punctuation characters with spaces, except '+', '#', '.', '-'
    # This keeps terms like "c++", "c#", ".net", "multi-threading" intact
    cleaned_text = re.sub(r'[^\w\s\+#\.-]', ' ', text)
    
    # Tokenize by splitting on whitespace
    raw_tokens = cleaned_text.split()
    
    # Strip any trailing/leading dots or dashes that might be grammatical, e.g. "python." -> "python"
    # while preserving symbols inside words (like ".net")
    tokens = []
    for token in raw_tokens:
        cleaned_token = token.strip(".,-")
        if cleaned_token:
            tokens.append(cleaned_token)
            
    return tokens

def calculate_fit_score(resume_text, jd_text):
    """
    Compares resume text against a job description input using a keyword-based approach.
    
    Calculation formula:
    Fit Score = (number of unique JD keywords found in resume / total unique JD keywords) * 100
    
    Parameters:
        resume_text (str): Extracted text from the candidate's resume.
        jd_text (str): The job description text.
        
    Returns:
        tuple: (score_percentage, matched_keywords, missing_keywords)
            - score_percentage (float): The match percentage (0 to 100).
            - matched_keywords (list): Keywords from JD present in the resume.
            - missing_keywords (list): Keywords from JD absent from the resume.
    """
    # Preprocess and tokenize both texts
    resume_tokens = set(clean_and_tokenize(resume_text))
    jd_tokens = clean_and_tokenize(jd_text)
    
    # Extract unique JD keywords, filtering out stop words and short numbers
    unique_jd_keywords = set()
    for token in jd_tokens:
        # Ignore common stop words and purely numeric strings under 3 digits
        if token not in STOP_WORDS and not (token.isdigit() and len(token) < 3):
            unique_jd_keywords.add(token)
            
    # If the job description has no keywords after filtering, return 0
    if not unique_jd_keywords:
        return 0.0, [], []
        
    matched_keywords = []
    missing_keywords = []
    
    # Check match presence for each unique JD keyword
    for keyword in sorted(list(unique_jd_keywords)):
        if keyword in resume_tokens:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
            
    # Calculate fit score percentage
    score = (len(matched_keywords) / len(unique_jd_keywords)) * 100
    
    return round(score, 2), matched_keywords, missing_keywords
