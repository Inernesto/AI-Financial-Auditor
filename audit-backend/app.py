import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import pandas as pd
import xmltodict
from io import BytesIO

# Load environment variables from .env
load_dotenv()

# Serve from a dist folder inside your backend (adjust if different)
static_dir = os.path.join(os.path.dirname(__file__), '../audit-frontend/dist')

app = Flask(__name__, static_folder=static_dir, static_url_path='')

CORS(app)  # Allow requests from frontend

# Initialize AWS Textract client
textract = boto3.client(
    'textract',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    byte_data = file.read()

    try:
        response = textract.analyze_document(
            Document={'Bytes': byte_data},
            FeatureTypes=['FORMS', 'TABLES']
        )

        blocks = response['Blocks']

        lines = [
            block['Text'] for block in blocks
            if block['BlockType'] == 'LINE'
        ]

        key_values = {}
        key_map = {}
        value_map = {}
        block_map = {}

        for block in blocks:
            block_id = block.get('Id')
            block_map[block_id] = block
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block

        def get_text_for_ids(ids):
            text = []
            for id_ in ids:
                word_block = block_map.get(id_)
                if word_block and 'Text' in word_block:
                    text.append(word_block['Text'])
            return ' '.join(text)

        for key_id, key_block in key_map.items():
            value_ids = []
            for rel in key_block.get('Relationships', []):
                if rel['Type'] == 'VALUE':
                    value_ids.extend(rel['Ids'])
            key_text = get_text_for_ids(key_block.get('Relationships', [])[0].get('Ids', []))
            value_text = get_text_for_ids(value_ids)
            if key_text:
                key_values[key_text] = value_text

        tables = []
        current_table = []
        for block in blocks:
            if block['BlockType'] == 'CELL':
                row = block['RowIndex']
                col = block['ColumnIndex']
                text = ''
                for rel in block.get('Relationships', []):
                    if rel['Type'] == 'CHILD':
                        text = get_text_for_ids(rel['Ids'])
                current_table.append({
                    'row': row,
                    'col': col,
                    'text': text
                })

        return jsonify({
            'text_lines': lines,
            'form_fields': key_values,
            'table_cells': current_table
        })

    except Exception as e:
        print("\n ERROR:", e)
        traceback.print_exc()
        return jsonify({'error': 'Something went wrong during OCR.'}), 500

@app.route('/convert', methods=['POST'])
def convert_structured_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename.lower()
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file)
        elif filename.endswith('.xml'):
            xml_data = xmltodict.parse(file.read())
            return jsonify({"structuredData": xml_data})
        else:
            return jsonify({'error': 'Unsupported structured file type'}), 400

        structured_data = df.to_dict(orient='records')
        return jsonify({"structuredData": structured_data})

    except Exception as e:
        print("\n CONVERSION ERROR:", e)
        traceback.print_exc()
        return jsonify({'error': 'Failed to convert structured document.'}), 500

@app.route('/audit', methods=['POST'])
def audit_documents():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'error': 'Expected a list of documents'}), 400

        formatted_docs = []
        for doc in data:
            file_name = doc.get("fileName", "Unknown File")

            if "structuredData" in doc:
                lines = "\n".join([str(row) for row in doc["structuredData"]])
                doc_text = f"FILE: {file_name}\n--- STRUCTURED DATA ---\n{lines}\n"
            else:
                lines = "\n".join(doc.get("textLines", []))
                fields = "\n".join(f"{k}: {v}" for k, v in doc.get("formFields", {}).items())
                table = "\n".join(
                    f"Row {cell['row']} Col {cell['col']}: {cell['text']}"
                    for cell in doc.get("tableCells", [])
                )
                doc_text = f"FILE: {file_name}\n--- TEXT ---\n{lines}\n\n--- FORM FIELDS ---\n{fields}\n\n--- TABLE CELLS ---\n{table}\n"

            formatted_docs.append(doc_text)

        prompt = (
            "You are a professional financial auditor. You are given multiple structured document extracts, "
            "such as invoices, purchase orders, expense reports, and commission summaries. "
            "For each document, do the following:\n"
            "- Identify the type of document (invoice, PO, report, etc.).\n"
            "- Recalculate totals, taxes, and commissions based on the line-item data.\n"
            "- Flag discrepancies if the totals do not match expected calculations.\n"
            "- Highlight typographical errors (e.g., date or figure formatting mistakes).\n"
            "- Identify missing approvals, inconsistent entries, or unusual financial behavior.\n"
            "- If the document does not include any financial, procurement, or expense-related data, state: "
            "'**No financial audit is required for the provided documents.**'\n"
            "- Format your response using clear Markdown with headers and bullet points.\n\n"
            "Do not guess — base your assessment strictly on the data in the documents.\n\n"
            f"{chr(10).join(formatted_docs)}\n\nAudit Summary:"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional financial auditing assistant. "
                        "You are reviewing structured document data (e.g., invoices, purchase orders, commission sheets, and expense reports). "
                        "Your responsibilities are:\n"
                        "- Detect mathematical errors (e.g., incorrect totals, taxes, or commission percentages).\n"
                        "- Detect missing approvals, misaligned values, or inconsistencies across entries.\n"
                        "- Highlight typos that affect dates or financial correctness.\n"
                        "- Format your audit report cleanly in Markdown (e.g., `## Document Name`, bullet lists, bold totals).\n"
                        "- Do not include emojis, casual tone, or promotional content.\n"
                        "- If a document has no financial relevance, respond with: '**No financial audit is required for the provided documents.**'\n"
                        "You must always remain objective, accurate, and formal in your tone."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        audit_result = response.choices[0].message.content.strip()
        return jsonify({"summary": audit_result})

    except Exception as e:
        print("\nAUDIT ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to generate audit summary"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
