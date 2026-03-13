# 📋 Document Validation Assistant

A Streamlit-based app to validate and cross-check Purchase Orders (PO),
Goods Received Notes (GRN), and Invoices.

## 🚀 Features

-   Upload PDF files for PO, GRN, and Invoice.
-   Automatically extract text and run validation workflow.
-   Displays step-by-step validation results.
-   Download a detailed JSON report.

## ⚙️ Installation

1.  Clone this repository.

2.  Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

3.  Add your OpenAI API key in `.env` file:

        OPENAI_API_KEY=your_api_key_here

## ▶️ Run the App

``` bash
streamlit run app.py
```

## 📖 Usage

1.  Upload PO, GRN, and Invoice PDFs.
2.  Start validation process.
3.  View results and download report.
