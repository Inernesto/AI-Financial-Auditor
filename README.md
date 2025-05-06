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
