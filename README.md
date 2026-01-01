# Automated Learning Objectives (LOs) Dataset Creation


## 1. Project Overview

This repository presents a powerful Python script designed to **automate the creation of high-quality educational datasets**. The core function is to dynamically generate **Learning Objectives (LOs)** from educational text content sourced from the web. This process is crucial for developing AI models focused on educational technology (EdTech) and instructional design.

The script combines web scraping techniques with advanced generative AI capabilities, specifically leveraging the **Google Gemini model**, to transform raw text into structured, instructional design-compliant learning objectives.

## 2. Key Features

The automated dataset generation process is built around several key features:

| Feature | Description | Technologies Used |
| :--- | :--- | :--- |
| **Dynamic Topic Selection** | The script uses a predefined `TOPIC_BANK` covering subjects like Science, Math, History, Art, and Technology to ensure diverse and relevant educational content is targeted. | Python `random` module |
| **Intelligent Web Search** | It utilizes the Google Custom Search API to find relevant educational articles and resources for the selected topics, ensuring the data is current and authoritative. | Google API Client |
| **Robust Web Scraping** | The script employs `BeautifulSoup` to scrape and clean text from the identified URLs, removing boilerplate content (headers, footers, navigation) to isolate the core educational text. | `BeautifulSoup4`, `requests` |
| **AI-Powered LO Generation** | The cleaned text is passed to the Gemini AI model, which acts as an "expert instructional designer" to generate 5-15 high-quality, measurable learning objectives in a structured JSON format. | Google Generative AI SDK (Gemini) |
| **Data Management & Checkpointing** | All generated data (original text and LOs) is saved to a CSV file (`dynamic_LO_dataset.csv`). A checkpoint system is implemented to track processed topics, allowing the script to be stopped and resumed without duplicating work. | `pandas`, Python `os` |

## 3. Workflow and Methodology

The `collect_data.py` script executes a continuous loop to build the dataset:

1.  **Topic Selection:** A random topic and a query template are selected from the predefined banks.
2.  **Search Query Generation:** A search query is dynamically created (e.g., "comprehensive guide to [sub-topic]").
3.  **Search Execution:** The Google Custom Search API is queried to retrieve a list of relevant URLs.
4.  **Content Scraping:** Each URL is visited, and the text content is scraped, cleaned, and filtered to ensure it meets minimum and maximum word count requirements (500 to 4000 words).
5.  **AI Processing:** The cleaned text is sent to the Gemini model with a detailed system prompt instructing it to generate learning objectives based on the text.
6.  **Data Storage:** The resulting JSON object, containing the original text and the generated learning objectives, is parsed and appended as a new row to the `dynamic_LO_dataset.csv` file.

## 4. Installation and Setup

### Prerequisites
*   Python 3.x
*   Access to Google Custom Search API and a CSE ID.
*   Access to Google Gemini API.

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/SeifEldenOsama/Creating_LOs_dataset_using_pythonscript.git
    cd Creating_LOs_dataset_using_pythonscript
    ```
2.  Install the required Python libraries:
    ```bash
    pip install google-generativeai google-api-python-client beautifulsoup4 requests pandas
    ```
3.  **API Key Configuration:** The script requires your API keys to be set as environment variables or directly in the script's configuration block:
    *   `GOOGLE_API_KEY` (for Google Custom Search)
    *   `GOOGLE_CSE_ID` (for Google Custom Search)
    *   `GEMINI_API_KEY` (for Gemini Model)

## 5. Usage

To start the automated dataset generation process, simply run the main script:

```bash
python collect_data.py
```

The script will run continuously, generating new data points and saving them to `dynamic_LO_dataset.csv` until manually stopped.

## 6. Repository Contents

| File/Folder | Description |
| :--- | :--- |
| `collect_data.py` | The main Python script containing the entire workflow for data collection and LO generation. |
| `Building-Child-Friendly-Educational-Datasets.pdf` | A supplementary document likely detailing the theoretical background or methodology for building child-friendly educational datasets. |
| `dynamic_LO_dataset.csv` | The output file where the generated dataset is stored. |
