#sentiment_analysis.py



import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json
import re
import sys  # NEW

def split_into_sentences(text):
    """Split text into sentences and return with character positions."""
    sentences_with_positions = []
    current_pos = 0

    # Split sentences using regex
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)

    for sentence in sentences:
        if sentence.strip():
            # Find the actual position in original text
            start_pos = text.find(sentence, current_pos)
            end_pos = start_pos + len(sentence)

            sentences_with_positions.append({
                'text': sentence,
                'start': start_pos,
                'end': end_pos
            })

            current_pos = end_pos

    return sentences_with_positions

def analyze_sentiment(text, tokenizer, model):
    """Analyze sentiment using FinBERT model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_score = predictions[0].tolist()

    # FinBERT labels: positive, negative, neutral
    labels = ['positive', 'negative', 'neutral']
    sentiment_class = labels[sentiment_score.index(max(sentiment_score))]

    return sentiment_class, sentiment_score

def main():
    # Choose model (CLI arg > FINBERT_MODEL env > default)
    cli_model = sys.argv[1].strip() if len(sys.argv) > 1 else None
    model_name = cli_model or os.getenv("FINBERT_MODEL", "ProsusAI/finbert")

    # Load FinBERT model and tokenizer
    print(f"Loading FinBERT model: {model_name} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Read input file
    input_file = "output/company_paragraphs_sample.txt"
    print(f"Reading file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split into sentences
    sentences = split_into_sentences(text)
    print(f"Found {len(sentences)} sentences")

    # Analyze sentiment for each sentence
    results = []
    for idx, sentence_data in enumerate(sentences, start=1):
        print(f"Processing sentence {idx}/{len(sentences)}")
        sentiment_class, scores = analyze_sentiment(sentence_data['text'], tokenizer, model)

        results.append({
            "sentence": sentence_data['text'],
            "class": sentiment_class,
            "position": {
                "start": sentence_data['start'],
                "end": sentence_data['end']
            },
            "confidence_scores": {
                "positive": scores[0],
                "negative": scores[1],
                "neutral": scores[2]
            }
        })

    # Save results
    output_file = "output/sentiment_analysis_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # NEW: ensure folder exists
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSentiment analysis completed!")
    print(f"Model used: {model_name}")
    print(f"Results saved to: {output_file}")
    print(f"Total sentences analyzed: {len(results)}")

if __name__ == "__main__":
    main()