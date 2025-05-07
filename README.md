# 🧾 AI-Powered Financial Document Auditor

**Audit smarter, not harder.**  
This full-stack AI application leverages AWS Textract and OpenAI's GPT-4o to automatically extract and audit financial documents — including invoices, expense reports, and purchase orders — for errors, inconsistencies, and compliance issues.

---

## ✨ Project Summary

Manual financial audits are time-consuming and error-prone. This AI-powered auditor solves that by:
- Extracting text and tabular data from scanned or uploaded financial documents using **AWS Textract**
- Automatically identifying **mathematical errors**, **missing approvals**, **typos**, and **data inconsistencies** with **GPT-4o**
- Supporting multiple document types, including PDFs, images, CSVs, Excel, and XML files
- Presenting a clean and modern frontend built with **React** and **TailwindCSS**
- Running entirely on the cloud via **Heroku**

---

## 📁 Tech Stack

| Layer       | Tools Used                              |
|-------------|------------------------------------------|
| Frontend    | React + TailwindCSS + ReactMarkdown      |
| Backend     | Flask + OpenAI API + AWS Textract        |
| Structured Data Parser | Pandas + xmltodict            |
| Deployment  | Docker + Heroku                          |

---

## 🚀 Features

✅ Upload scanned or structured financial documents  
✅ Automatic OCR extraction and data parsing  
✅ AI-powered audit summaries with discrepancy reports  
✅ Markdown-formatted results with professional tone  
✅ Full-stack deployment via Docker & Heroku

---

## 🛠️ How to Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/Inernesto/AI-Financial-Auditor.git
cd ai-financial-auditor
```
### 2. Set environment variables
Create a .env file inside the audit-backend folder:
```bash
AWS_REGION=your-region
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
OPENAI_API_KEY=your-openai-key
```
### 3. Install dependencies
Backend (Python)
```bash
cd audit-backend
pip install -r requirements.txt
```
Frontend (React)
```bash
cd ../audit-frontend
npm install
```
### 4. Build the frontend
```bash
npm run build
```
### 5. Run the backend server
```bash
cd ../audit-backend
python app.py
```
Visit: http://localhost:5000

## Deployment (Heroku)
This app is Heroku-ready with a Procfile, requirements.txt, and production-ready build.

### 1. Create a Heroku app:
```bash
heroku create your-app-name
```
### 2. Set config vars:
```bash
heroku config:set AWS_REGION=...
heroku config:set AWS_ACCESS_KEY_ID=...
heroku config:set AWS_SECRET_ACCESS_KEY=...
heroku config:set OPENAI_API_KEY=...
```
### 3. Push to Heroku:
```bash
git push heroku main
```
### 4. Open in browser:
```bash
heroku open
```
## 📄 Supported Document Types
PDF (scanned or digital)

JPG / PNG / TIFF

CSV

XLSX

XML

## 📊 Example Use Cases
Catch incorrect tax or commission calculations

Validate invoice totals and line item consistency

Flag suspicious approval patterns

Detect date or currency formatting errors

## 🤝 Contributions
Contributions, suggestions, and pull requests are welcome. Please open an issue first if you'd like to discuss major changes.

## 👨‍💻 Author
Built with care by Ernest Inyama
