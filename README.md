**Scrutinization of Tender Document Using AI**
An AI-driven automation platform developed for NLC India Limited (NLCIL) to streamline the industrial procurement process. This system automates the evaluation of technical and financial bids, transforming unstructured tender PDFs into structured, verifiable data.

🚀 Impact
Efficiency: Reduced average document evaluation time by 60%.
Accuracy: Achieved over 90% accuracy in structured data extraction.
Scalability: Successfully tested on 50 sample tenders within a live industrial environment.

🛠️ Key Features
Intelligent Data Extraction: Uses Google Gemini API for semantic analysis of complex tender clauses.
OCR Capability: Employs Tesseract OCR and OpenCV to process scanned legacy documents.

Automated Verification:
EMD Verification: Extracts amount, type, and validity of Earnest Money Deposits.
PQR Validation: Automatically checks vendor eligibility against Pre-Qualification Requirements.
Udyam Integration: Cross-verifies registration details via official government portals.
Workflow Orchestration: Managed by n8n to coordinate data flow between AI models and storage.

💻 Technology Stack
Language: Python 
Web Framework: Flask 
Frontend: HTML, JavaScript 
Automation: n8n 
AI/NLP: Google Gemini API 
OCR: Tesseract OCR 
Storage: Google Sheets API 

🏗️ System Architecture
The solution follows a three-tier architecture:
Frontend Layer: A Flask web interface for file uploading and merging.
Automation Layer: n8n workflows that trigger Gemini AI for deep document analysis.
Data Storage Layer: Google Sheets for structured records and Word for automated report generation.


Developed by: Suriyaprakashar A Internship Organization: NLC India Limited (Material Management Complex)  
Guide: Mr. S.K. Suresh, Chief Manager / Computer Services
