from flask import Flask, request, jsonify
import PyPDF2
import requests

app = Flask(__name__)

# Load and extract text from PDF at startup
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Change this to your PDF file name
PDF_PATH = "media_to_upload1717413506"
textbook_text = extract_text_from_pdf(PDF_PATH)

# Gemini API details
GEMINI_API_KEY = "AIzaSyCi8vKotcmREaHIKU4k84XKpzHWa6hPSHA"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY

def ask_gemini(question, context):
    prompt = f"Use the following Social Science textbook content to answer the question:\n\n{context}\n\nQuestion: {question}\nAnswer:"
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(GEMINI_API_URL, json=data)
    if response.status_code == 200:
        result = response.json()
        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "Sorry, I couldn't find the answer."
    else:
        return "Sorry, there was an error with the Gemini API."

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    question = req['queryResult']['queryText']
    # For now, use the whole textbook. (Can improve with search later)
    answer = ask_gemini(question, textbook_text)
    return jsonify({'fulfillmentText': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)