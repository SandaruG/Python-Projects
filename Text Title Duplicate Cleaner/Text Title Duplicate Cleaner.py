import os
import difflib
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data (run once)
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

# Specify the directory
directory = r"C:\Users\Sandaru\OneDrive\Desktop\New folder\Done"

def get_sentences(content):
    """Extract sentences, handling title and newlines explicitly."""
    # Split by newlines first to preserve title line
    lines = content.split('\n')
    sentences = []
    for i, line in enumerate(lines):
        # Treat the first line (title) as a single sentence
        if i == 0 and line.strip().startswith("Title:"):
            sentences.append(line.strip())
        else:
            # Tokenize other lines into sentences
            try:
                sentences.extend(sent_tokenize(line.strip()))
            except Exception as e:
                print(f"Error tokenizing line '{line}': {e}")
                if line.strip():
                    sentences.append(line.strip())
    return sentences

def has_title(content):
    """Check if the file starts with a 'Title:' and return the title."""
    lines = content.strip().split('\n')
    if lines and lines[0].strip().startswith("Title:"):
        return True, lines[0].strip()
    return False, ""

def similarity_score(text1, text2):
    """Calculate similarity between two texts using difflib."""
    seq = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
    return seq.ratio() * 100

def clean_file_content(content, title):
    """Remove sentences in the first three that are >=90% similar to the title."""
    sentences = get_sentences(content)
    if not sentences:
        print("No sentences found in content.")
        return content
    
    title_text = title.replace("Title:", "").strip()
    cleaned_sentences = []
    title_kept = False
    sentence_count = 0
    within_first_three = True

    print("\nProcessing sentences:")
    for sentence in sentences:
        # Track if we're in the first three sentences
        if sentence_count < 3:
            sentence_count += 1
        else:
            within_first_three = False
        
        # Keep the title line
        if not title_kept and sentence.strip().startswith("Title:"):
            cleaned_sentences.append(sentence)
            title_kept = True
            print(f"Kept title: {sentence}")
        # Remove duplicates in the first three sentences
        elif within_first_three and (sentence.strip() == title_text or similarity_score(sentence.strip(), title_text) >= 90):
            print(f"Removing duplicate sentence: {sentence} (Similarity: {similarity_score(sentence.strip(), title_text)}%)")
            continue
        # Keep all other sentences
        else:
            cleaned_sentences.append(sentence)
            print(f"Kept sentence: {sentence}")
    
    return '\n'.join(cleaned_sentences)

def process_file(file_path):
    """Process a single .txt file to remove redundant title sentences."""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"\nOriginal content of {file_path} (first 3 lines/sentences):")
        original_sentences = get_sentences(content)[:3]
        for i, sentence in enumerate(original_sentences, 1):
            print(f"  {i}. {sentence}")
        
        # Check for title
        has_title_flag, title = has_title(content)
        if not has_title_flag:
            print(f"No title found in {file_path}, skipping.")
            return
        
        # Clean the content
        cleaned_content = clean_file_content(content, title)
        
        # Save the cleaned content
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
        print(f"Saved cleaned file: {file_path}")
        
        # Verify the first three sentences
        with open(file_path, 'r', encoding='utf-8') as file:
            saved_content = file.read()
        sentences = get_sentences(saved_content)[:3]
        title_text = title.replace("Title:", "").strip()
        
        print(f"\nVerification for {file_path}:")
        print("First three sentences after cleaning:")
        for i, sentence in enumerate(sentences, 1):
            print(f"  {i}. {sentence}")
            if sentence.strip() != title and similarity_score(sentence.strip(), title_text) >= 90:
                print(f"  Warning: Sentence {i} ('{sentence}') is still similar to title ({similarity_score(sentence.strip(), title_text)}%)")
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_directory(directory):
    """Process all .txt files in the directory."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return
    
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    if not txt_files:
        print(f"No .txt files found in {directory}.")
        return
    
    for file_name in txt_files:
        file_path = os.path.join(directory, file_name)
        print(f"\nProcessing file: {file_path}")
        process_file(file_path)
    
    print("\nProcessing complete.")

# Run the process
if __name__ == "__main__":
    process_directory(directory)