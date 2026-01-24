import os
import json
import time
import random
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# It's better to set these as environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_TO_USE = "models/gemini-1.5-flash"
OUTPUT_FILENAME = "dynamic_LO_dataset.csv"

TOPIC_BANK = {
    "Science & Nature": [
        "How Rainbows Are Made", "The Life Cycle of a Butterfly", "What are Planets",
        "The Water Cycle", "Dinosaurs and Fossils", "How Plants Grow",
        "Types of Animals", "Why We Need Sleep", "Volcanoes Explained",
        "Exploring the Ocean"
    ],
    "Math & Logic": [
        "Introduction to Counting", "Basic Shapes and Geometry", "Simple Addition and Subtraction",
        "Telling Time", "Understanding Money", "Patterns in Math",
        "Measuring Length and Weight", "Solving Simple Puzzles", "Fractions for Beginners",
        "Symmetry"
    ],
    "History & Culture": [
        "The Pyramids of Egypt", "Life in Ancient Rome", "Famous Explorers",
        "Different Countries and Flags", "How People Traveled Long Ago", "Holidays Around the World",
        "What is a Community", "The First Day of School History",
        "How a Seed Becomes Food", "Castles and Knights"
    ],
    "Art & Creativity": [
        "Mixing Colors", "Drawing Basic Shapes", "Famous Artists for Kids",
        "Making Music and Rhythm", "What is a Story", "Simple Crafts and DIY",
        "The Power of Imagination", "Creating Simple Poems",
        "Learning About Photography", "Puppet Making"
    ],
    "Technology & Safety": [
        "How Computers Work Simply", "Internet Safety Rules", "Introduction to Coding Games",
        "Traffic Rules and Safety", "First Aid Basics for Kids", "How a Lightbulb Works",
        "What is Recycling", "Types of Simple Machines (Lever, Wheel)",
        "The Importance of Brushing Teeth", "Stranger Danger"
    ]
}

QUERY_TEMPLATES = [
    "comprehensive guide to {}",
    "explain {} like I'm a beginner",
    "core concepts of {}",
    "in-depth article on {}",
    "{} explained for students",
    "the science behind {}",
    "{} lecture notes",
    "how does {} actually work",
    "technical explanation of {}",
    "academic paper on {}"
]

SYSTEM_PROMPT = """
You are an expert instructional designer. Your task is to read the provided educational text
and generate 5-15 high-quality learning objectives for it based on the text length. The objectives must clearly
state what a learner should be able to do after reading the text (e.g., "Describe the process...",
"Analyze the relationship...", "Define the term...").

You MUST provide the output as a single, valid JSON object with two keys:
1. "educational_text": The full, original text that was provided to you.
2. "generated_learning_objectives": A list of strings, where each string is a
   learning objective you created.

Do not include any text, backticks, or explanations outside of the JSON object.
"""

def initialize_clients():
    """Initializes Google Search and Gemini API clients."""
    if not GOOGLE_API_KEY or not GEMINI_API_KEY or not GOOGLE_CSE_ID:
        logger.error("API keys or CSE ID not found. Please set GOOGLE_API_KEY, GOOGLE_CSE_ID, and GEMINI_API_KEY environment variables.")
        return None, None

    try:
        search_service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL_TO_USE)
        logger.info("API clients initialized successfully.")
        return search_service, model
    except Exception as e:
        logger.error(f"Error initializing API clients: {e}")
        return None, None

def search_google(search_service, topic):
    """Searches Google for a topic and returns a list of URLs."""
    logger.info(f"Searching Google for: '{topic}'")
    try:
        result = search_service.cse().list(
            q=topic,
            cx=GOOGLE_CSE_ID,
            num=5
        ).execute()
        urls = [item['link'] for item in result.get('items', [])]
        logger.info(f"Found {len(urls)} URLs.")
        return urls
    except Exception as e:
        logger.error(f"Error searching Google: {e}")
        return []

def scrape_and_clean_text(url, min_words=500, max_words=4000):
    """Scrapes a URL and cleans the text content."""
    logger.info(f"Attempting to scrape: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch URL (Status {response.status_code})")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            element.decompose()

        text_chunks = [p.get_text() for p in soup.find_all('p')]
        full_text = " ".join(text_chunks).strip()
        cleaned_text = " ".join(full_text.split())
        words = cleaned_text.split()
        word_count = len(words)

        if word_count < min_words:
            logger.info(f"Skipped: Only found {word_count} words. (Min: {min_words})")
            return None

        if word_count > max_words:
            logger.info(f"Truncating: Found {word_count} words, limiting to {max_words}.")
            cleaned_text = " ".join(words[:max_words])

        logger.info(f"Successfully scraped {len(cleaned_text.split())} words.")
        return cleaned_text
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None

def generate_learning_objectives(model, text_block):
    """Calls the Gemini API to generate learning objectives for a text."""
    logger.info(f"Sending text to Gemini for LO generation...")
    full_prompt = f"{SYSTEM_PROMPT}\n\n{text_block}"
    try:
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        result_json = json.loads(response.text)
        logger.info(f"Successfully generated {len(result_json['generated_learning_objectives'])} objectives.")
        return result_json
    except Exception as e:
        logger.error(f"Error generating objectives with Gemini: {e}")
        return None

def load_processed_topics(filename):
    """Loads already processed topics from the CSV file."""
    if not os.path.exists(filename):
        return set()
    try:
        df = pd.read_csv(filename)
        return set(df['topic'].unique()) if 'topic' in df.columns else set()
    except Exception as e:
        logger.error(f"Error loading processed topics: {e}")
        return set()

def save_data_point(data_point, filename):
    """Appends a single data point to the CSV file."""
    df_new = pd.DataFrame([data_point])
    try:
        file_exists = os.path.exists(filename)
        df_new.to_csv(filename, mode='a' if file_exists else 'w', 
                      header=not file_exists, index=False, encoding='utf-8')
    except Exception as e:
        logger.error(f"Error saving data point: {e}")

def main():
    search_service, gemini_model = initialize_clients()
    if not search_service or not gemini_model:
        return

    processed_topics = load_processed_topics(OUTPUT_FILENAME)
    logger.info(f"Loaded {len(processed_topics)} previously processed topics.")

    new_count = 0
    try:
        while True:
            category = random.choice(list(TOPIC_BANK.keys()))
            sub_topic = random.choice(TOPIC_BANK[category])
            template = random.choice(QUERY_TEMPLATES)
            query = template.format(sub_topic)

            if query in processed_topics:
                continue

            logger.info(f"Processing query: {query}")
            urls = search_google(search_service, query)
            
            for url in urls:
                text = scrape_and_clean_text(url)
                if text:
                    data_point = generate_learning_objectives(gemini_model, text)
                    if data_point:
                        data_point['topic'] = query
                        save_data_point(data_point, OUTPUT_FILENAME)
                        processed_topics.add(query)
                        new_count += 1
                        logger.info(f"Data point saved for query: {query}")
                        break # Move to next query after one successful scrape
            
            time.sleep(1) # Respectful delay
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
    finally:
        logger.info(f"Session complete. Generated {new_count} new data points.")

if __name__ == "__main__":
    main()
