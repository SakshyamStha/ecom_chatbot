import json
import re
import os
import math
from collections import defaultdict, Counter
import random

# Set the path to the intents JSON file within the 'shop' app
json_file_path = os.path.join(os.path.dirname(__file__), 'data', 'intents.json')

def preprocess_text(text):
    """
    Preprocesses text by converting it to lowercase and removing non-alphanumeric characters.
    Returns a list of words.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.split()

def train_naive_bayes(intents):
    """
    Trains a Naive Bayes model by creating word frequency counts for each intent.
    Returns word counts, intent counts, and total word count.
    """
    word_counts = defaultdict(Counter)
    intent_counts = Counter()
    total_words = 0
    
    for intent in intents:
        tag = intent['tag']
        for pattern in intent['patterns']:
            words = preprocess_text(pattern)
            word_counts[tag].update(words)
            intent_counts[tag] += 1
            total_words += len(words)
    
    return word_counts, intent_counts, total_words

def classify_intent(user_input, word_counts, intent_counts, total_words):
    """
    Classifies the intent of the user input using the Naive Bayes algorithm.
    Returns the most probable intent.
    """
    words = preprocess_text(user_input)
    print(f"Processed Words: {words}")  # Debugging: Check the words
    best_intent = None
    max_prob = -float('inf')

    
    for intent, count in intent_counts.items():
        # Start with the prior probability of the intent
        log_prob = math.log(count / total_words)
        
        # Add the probabilities of each word given the intent
        for word in words:
            word_prob = (word_counts[intent][word] + 1) / (sum(word_counts[intent].values()) + len(word_counts[intent]))
            log_prob += math.log(word_prob)
        
        # Debugging: Print the log probabilities for each intent
        print(f"Intent: {intent}, Log Probability: {log_prob}")

        # Choose the intent with the highest probability
        if log_prob > max_prob:
                max_prob = log_prob
                best_intent = intent

    return best_intent


    """
    Generates a response based on the user's input by classifying its intent.
    Returns an appropriate response or a default message.
    """
from .models import Product

def generate_response(user_input):
    # Load intents from the JSON file
    with open(json_file_path, 'r') as file:
        intents = json.load(file)["intents"]
    
    # Train the Naive Bayes model on the loaded intents
    word_counts, intent_counts, total_words = train_naive_bayes(intents)
    
    # Classify the user's input to determine intent
    intent = classify_intent(user_input, word_counts, intent_counts, total_words)

    print(f"Detected Intent: {intent}")  # Debugging: Check detected intent
    
    # Handle product search intent separately
    if intent == "product_search":
        product_name = extract_product_name(user_input)
        print(f"Detected Product: {product_name}") 
        if product_name:
            product_details = get_product_details(product_name)
            return product_details
        else:
            return "Sorry, I couldn't understand the product you're asking about."

    # Default response if intent is not recognized
    for intent_data in intents:
        if intent_data['tag'] == intent:
            return random.choice(intent_data['responses'])  # Pick the first response for simplicity
    
    return "I'm not sure how to respond to that."

def extract_product_name(user_input):
    """
    Extract the product name from the user's input, considering keywords in a sentence.
    Handles cases where the product name is mentioned with spaces, and
    converts spaces into underscores for multi-word product names to match the database.
    """
    # Convert the user input to lowercase and split it into words
    words = preprocess_text(user_input)

    # Keywords to look for in the sentence
    keywords = ["about", "product", "item", "is", "want"]

    # Case 1: Look for a keyword in the input
    for keyword in keywords:
        if keyword in words:
            # Get the next word after the keyword
            product_name_start_index = words.index(keyword) + 1
            if product_name_start_index < len(words):
                # The product name starts from the next word after the keyword
                product_name = " ".join(words[product_name_start_index:]).strip()
                # Convert spaces to underscores for multi-word product names
                product_name = product_name.replace(" ", "_").capitalize()
                return product_name

    # Case 2: If no keyword found, check if the input is a single product name
    # For example, user directly types "watch"
    product_name = " ".join(words).strip()
    # For multi-word product names, convert spaces to underscores
    product_name = product_name.replace(" ", "_").capitalize()
    
    return product_name

def get_product_details(product_name):
    """
    Fetch product details from the database based on the product name.
    It handles both single-word and multi-word product names.
    """
    try:
        # Try to fetch the product with the exact name (handling underscores for multi-word names)
        product = Product.objects.get(name__iexact=product_name.replace(" ", "_"))  # Case insensitive search with underscore
        product_details = f"Product: {product.name}\nPrice: {product.price}\n"
        if product.imageURL:
            product_details +=  f"<img src='{product.imageURL}' width='100' height='100' alt='{product.name}' />"
        return product_details
    except Product.DoesNotExist:
        return f"Sorry, we couldn't find a product named '{product_name}'."
