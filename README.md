# Automated Learning Objectives (LOs) Dataset Creation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Generative AI](https://img.shields.io/badge/AI-Gemini-orange.svg)](https://ai.google.dev/)

A professional Python-based framework for automating the creation of high-quality educational datasets. This tool dynamically generates **Learning Objectives (LOs)** from web-sourced educational content using Google Search and Gemini AI.

## 🌟 Project Overview

In the rapidly evolving field of EdTech, high-quality structured data is essential for training specialized AI models. This repository provides a robust pipeline to:
1.  **Discover** relevant educational content across diverse subjects.
2.  **Extract** and clean text from authoritative web sources.
3.  **Synthesize** measurable, instructional-design-compliant learning objectives using state-of-the-art LLMs.

The resulting dataset is ideal for fine-tuning models like Llama, Mistral, or Gemini for educational applications.

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Dynamic Topic Discovery** | Utilizes a multi-disciplinary `TOPIC_BANK` (Science, Math, History, Art, Technology) for broad coverage. |
| **Intelligent Search** | Integrates Google Custom Search API for high-relevance source discovery. |
| **Automated Scraping** | Clean, boilerplate-free text extraction using `BeautifulSoup4`. |
| **AI Synthesis** | Leverages **Google Gemini 1.5 Flash** for expert-level instructional design output. |
| **Fault-Tolerant** | Built-in checkpointing and logging to ensure continuous progress without data loss. |

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Google Cloud Project with [Custom Search API](https://developers.google.com/custom-search/v1/overview) enabled
- [Google AI Studio](https://aistudio.google.com/) API Key for Gemini

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/SeifEldenOsama/Creating_LOs_dataset_using_pythonscript.git
   cd Creating_LOs_dataset_using_pythonscript
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Set your API keys as environment variables:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key"
   export GOOGLE_CSE_ID="your_cse_id"
   export GEMINI_API_KEY="your_gemini_api_key"
   ```

## 📖 Usage

Run the main script to start the automated collection process:
```bash
python collect_data.py
```

The script will:
- Randomly select topics and search queries.
- Scrape and clean content from the web.
- Generate LOs and save them to `dynamic_LO_dataset.csv`.
- Log all activities to `dataset_generation.log`.

## 📁 Project Structure

```text
├── collect_data.py          # Main execution script
├── requirements.txt         # Project dependencies
├── LICENSE                  # MIT License
├── README.md                # Project documentation
├── .gitignore               # Git ignore rules
└── Building-Child-Friendly-Educational-Datasets.pdf # Theoretical background
```

## 📝 Dataset Format

The generated `dynamic_LO_dataset.csv` contains the following columns:
- `topic`: The search query used to find the content.
- `educational_text`: The raw, cleaned text extracted from the source.
- `generated_learning_objectives`: A JSON-formatted list of learning objectives.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
