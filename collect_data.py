print("Installing all required libraries...")

!pip install google-generativeai -q
!pip install google-api-python-client -q
!pip install beautifulsoup4| -q
!pip install requests -q
!pip install pandas -q
!pip install transformers peft trl bitsandbytes accelerate datasets -U -q

print("All libraries installed.")

import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import google.generativeai as genai
import time

# Key for Google Search
os.environ["GOOGLE_API_KEY"] = ""
# ID for Google Search
os.environ["GOOGLE_CSE_ID"] = ""
# Key for Gemini "Teacher" Model
os.environ["GEMINI_API_KEY"] = ""
# --------------------------------

if "YOUR_GOOGLE_CLOUD_API_KEY_HERE" in os.environ.get("GOOGLE_API_KEY", "") or \
   "YOUR_GOOGLE_AI_STUDIO_KEY_HERE" in os.environ.get("GEMINI_API_KEY", ""):
    print("ERROR: Please paste your API keys in Cell 2 before running.")
else:
    print("API keys found.")
    try:
        google_search_service = build("customsearch", "v1", developerKey=os.environ["GOOGLE_API_KEY"])
        print("Google Search client initialized.")

        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        print("Gemini client initialized successfully.")
    except Exception as e:
        print(f"Error initializing API clients. Check your keys. Error: {e}")

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

print("**Children's** Topic Bank and Query Templates are loaded.")

def search_google(topic):
    """
    Searches Google for a topic and returns a list of URLs.
    """
    print(f"  > Searching Google for: '{topic}'")
    try:
        result = google_search_service.cse().list(
            q=topic,
            cx=os.environ["GOOGLE_CSE_ID"],
            num=5
        ).execute()

        urls = [item['link'] for item in result.get('items', [])]
        print(f"    - Found {len(urls)} URLs.")
        return urls
    except Exception as e:
        print(f"    - Error searching Google: {e}")
        return []

def scrape_and_clean_text(url, min_words=500, max_words=4000):
    """
    Scrapes a URL, cleans the text.
    Skips if < min_words.
    Truncates if > max_words.
    """
    print(f"    - Attempting to scrape: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"    - Failed to fetch URL (Status {response.status_code})")
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
            print(f"    - SKIPPED: Only found {word_count} words. (Min: {min_words})")
            return None

        if word_count > max_words:
            print(f"    - TRUNCATING: Found {word_count} words, limiting to {max_words}.")
            final_text = " ".join(words[:max_words])
            final_word_count = max_words
        else:
            final_text = cleaned_text
            final_word_count = word_count

        print(f"    - SUCCESS: Scraped {final_word_count} words.")
        return final_text

    except Exception as e:
        print(f"    - Error scraping: {e}")
        return None

import google.generativeai as genai

print("Listing all available Gemini models that support 'generateContent'...\n")

found_model_name = None

try:
    for m in genai.list_models():
      if 'generateContent' in m.supported_generation_methods:
          print(f"Found model: {m.name}")

          if "1.5-flash" in m.name:
              found_model_name = m.name
          elif "gemini-pro" in m.name and not found_model_name:
              found_model_name = m.name

    if found_model_name:
        print(f"\n---")
        print(f"Recommended model to use: {found_model_name}")
        print(f"---")
    else:
        print("\nCould not find a suitable model. Please check your API key and permissions.")

except Exception as e:
    print(f"An error occurred while listing models: {e}")
    print("Please make sure your GEMINI_API_KEY in Cell 2 is correct and active.")

MODEL_TO_USE = "models/gemini-flash-latest"

if "PASTE_RECOMMENDED_MODEL_NAME_HERE" in MODEL_TO_USE:
    print("ERROR: Please update the 'MODEL_TO_USE' variable in this cell with a model name from the cell above.")
else:
    print(f"Using model: {MODEL_TO_USE}")

try:
    gemini_model = genai.GenerativeModel(MODEL_TO_USE)

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

    generation_config = genai.GenerationConfig(response_mime_type="application/json")

    def generate_synthetic_data(text_block):
        """
        Calls the Gemini API to generate learning objectives for a text.
        """
        print(f"    - Sending {len(text_block.split())} words to 'Teacher' (Gemini)...")
        full_prompt = f"{SYSTEM_PROMPT}\n\n{text_block}"

        try:
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            result_json = json.loads(response.text)
            print(f"    - SUCCESS: 'Teacher' generated {len(result_json['generated_learning_objectives'])} objectives.")
            return result_json

        except Exception as e:
            print(f"    - Error generating objectives with Gemini: {e}")
            return None

except Exception as e:
    print(f"Error initializing model '{MODEL_TO_USE}'. Did you paste the name correctly?")
    print(f"Full error: {e}")

import pandas as pd
import os

output_filename = "dynamic_LO_dataset.csv"

def load_processed_topics(filename):
    """
    Checks if the CSV exists and returns a set of all
    topics that have already been processed.
    """
    if not os.path.exists(filename):
        return set()

    try:
        df = pd.read_csv(filename)
        if 'topic' in df.columns:
            return set(df['topic'].unique())
        else:
            return set()
    except pd.errors.EmptyDataError:
        return set()
    except Exception as e:
        print(f"Error loading processed topics: {e}")
        return set()

def append_to_csv(data_point, filename):
    """
Appends a single new data point (as a dictionary)
    to the CSV file. This is our "checkpoint."
    """
    df_new = pd.DataFrame([data_point])

    file_exists = os.path.exists(filename)

    try:
        if not file_exists:
            df_new.to_csv(filename, index=False, encoding='utf-8')
        else:
            df_new.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8')
    except Exception as e:
        print(f"    -  Error saving checkpoint: {e}")

print("Checkpoint helper functions are ready.")

import random
print("--- STARTING DYNAMIC DATASET GENERATION ---")

processed_topics = load_processed_topics(output_filename)
print(f"Loaded {len(processed_topics)} previously processed topics from checkpoint file.")

new_data_this_session = 0

try:
    while True:
        random_category_key = random.choice(list(TOPIC_BANK.keys()))
        random_sub_topic = random.choice(TOPIC_BANK[random_category_key])
        random_template = random.choice(QUERY_TEMPLATES)

        search_query = random_template.format(random_sub_topic)

        if search_query in processed_topics:
            print(f"\nSkipping already processed query: {search_query}")
            continue

        print(f"\nProcessing new query: {search_query}")

        urls = search_google(search_query)
        if not urls:
            continue

        got_one_for_this_topic = False

        for url in urls:
            if got_one_for_this_topic:
                break


            text = scrape_and_clean_text(url, min_words=500)

            if text:

                data_point = generate_synthetic_data(text)

                if data_point:
                    data_point['topic'] = search_query
                    append_to_csv(data_point, output_filename)
                    processed_topics.add(search_query)
                    new_data_this_session += 1
                    print(f"SUCCESS: Checkpoint saved for query: {search_query}")
                    got_one_for_this_topic = True


except KeyboardInterrupt:
    print("\n\n---  SCRIPT STOPPED MANUALLY ---")
    print("Loop interrupted by user. Progress has been saved.")

finally:
    print("\n--- Generation Complete ---")
    print(f"Successfully generated {new_data_this_session} new data points in this session.")
    print(f"Total topics processed in CSV: {len(processed_topics)}")
