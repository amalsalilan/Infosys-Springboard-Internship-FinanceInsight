import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import warnings
import os
import shutil

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# --- 1. Configuration and Setup ---
# # %%
def setup_environment(seed):
    """Sets up seeds and device."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    return device

# Configuration parameters
model_name = 'bert-base-uncased'
num_labels = 3
max_length = 128
batch_size = 16
num_epochs = 3  # Reduced epoch
learning_rate = 2e-5
seed = 42
label_names = ['Positive (0)', 'Negative (1)', 'Neutral (2)']
model_save_path = './financial_bert_model'

# Clean up previous runs if directories exist
if os.path.exists('./results'):
    shutil.rmtree('./results')
if os.path.exists('./logs'):
    shutil.rmtree('./logs')
if os.path.exists(model_save_path):
    shutil.rmtree(model_save_path)

print("Libraries imported and configuration set.")
device = setup_environment(seed)
# --- 2. Data Preparation ---
# # %%
def augment_data(texts, labels, repetition_factor):
    """
    Augments the dataset by creating synonyms and variations, using key phrases
    to prevent the model from overfitting to the original 24 headlines.
    """
    augmented_texts = []
    augmented_labels = []
    
    # Core sentiment phrases used for augmentation
    # Phrases are structured as: {key_phrase_in_original_text: [list_of_variations]}
    
    positive_phrases = {
        "record quarterly profits": ["record profits", "all-time quarterly profits", "outstanding quarterly results"],
        "all-time high with strong gains": ["historic peak with solid gains", "new high on strong volume", "soaring high with great momentum"],
        "stimulus boosting investor confidence": ["large stimulus package", "capital injection raising confidence", "new monetary policy boosting optimism"],
        "shares surge 8%": ["stock rallies", "shares jumped 10%", "value exploded"],
        "job growth indicates economic recovery": ["robust economic growth", "significant economic turnaround", "strong hiring signals growth"],
        "sends stocks soaring": ["causes major rally", "sends stocks skyrocketing", "fuels investor enthusiasm"],
        "signals mainstream acceptance": ["widespread mainstream approval", "major financial institution adoption", "gets full regulatory approval"],
        "growth exceeds forecasts": ["grows strongly", "beats projections", "expansion is confirmed"]
    }

    negative_phrases = {
        "bankruptcy amid mounting debts": ["faces insolvency", "declares bankruptcy after debt crisis", "collapses under massive debt"],
        "recession fears grip investors": ["economic slump fears trigger sell-off", "downturn fears cause sharp drop", "recession is imminent"],
        "rate rises sharply": ["spikes to dangerous levels", "jumps dramatically worrying experts", "accelerated growth in joblessness"],
        "significant losses from bad loans": ["reports massive losses on poor assets", "discloses significant writedowns", "unexpectedly large financial loss"],
        "war escalates causing market volatility": ["deepens increasing uncertainty", "war intensifies sparking chaos", "trade tensions mount"],
        "shares plummet 20%": ["stock falls 25% due to product failure", "plunges on widespread safety issues", "stock collapses"],
        "point to potential recession": ["suggest an impending economic downturn", "signal a high risk of recession", "major indicators flashing red"],
        "earnings disappoint leading to selloff": ["miss targets triggering heavy selling", "falls short of targets causing selloff", "worse than expected earnings"]
    }

    neutral_phrases = {
        "interest rates unchanged": ["holds rates steady as expected", "leaves policy rate unchanged", "policy unchanged"],
        "earnings in line with expectations": ["revenue matching consensus", "quarterly results meet targets", "results are consistent with guidance"],
        "volume remains steady as investors wait": ["holds firm amidst low trading volume", "stable trading as decision awaits", "volume is moderate"],
        "regular quarterly dividend": ["confirms standard quarterly payout", "declares its usual shareholder dividend", "routine cash distribution"],
        "closes mixed with minor changes": ["finishes the day with marginal movement", "ends session with little change", "mixed close"],
        "announces CEO transition": ["names new chief executive officer", "board approves executive change", "management changes announced"],
        "shareholder meeting scheduled": ["set for upcoming date", "date confirmed for shareholder meeting", "annual event confirmed"],
        "filing submitted for compliance": ["formally filed with regulator", "official submission meets requirements", "compliance document submitted"]
    }
    
    # 1. Base Data (For training stability, keep original repetition)
    for _ in range(repetition_factor):
        augmented_texts.extend(texts)
        augmented_labels.extend(labels)
    
    # 2. Augmentation (Create unique augmented samples)
    # Total unique samples = 24 originals + (24 originals * repetition_factor * 2 additional variations)
    # The total dataset size will be significantly larger (Original 480 + ~960 augmented = ~1440 samples)
    for _ in range(repetition_factor * 2): 
        for i, original_text in enumerate(BASE_DATASET_TEXTS):
            label = labels[i]
            
            # Simple text matching to find the phrase dictionary to use
            phrase_dict = positive_phrases if label == 0 else (negative_phrases if label == 1 else neutral_phrases)
            
            # Simplified way to find a phrase to augment based on the original headline's content
            found_key = next((key for key in phrase_dict if key in original_text), None)

            if found_key:
                aug_list = phrase_dict[found_key]
                
                # Randomly pick an augmented phrase
                aug_text = np.random.choice(aug_list)
                
                # Randomly pick a prefix for context variation
                if label == 0:
                    prefix = np.random.choice(["Firm reports ", "The market ", "The central bank ", "Major shares ", "Strong labor ", "A new deal ", "Digital asset ", "National "])
                elif label == 1:
                    prefix = np.random.choice(["A large bank ", "The global market ", "The domestic economy ", "Top financial institution ", "Ongoing trade ", "Company's product ", "Macro factors ", "Q4 "])
                else: # Neutral
                    prefix = np.random.choice(["The Fed ", "The firm ", "Trading volume ", "The corporate board ", "The stock exchange ", "The executive team ", "Next month's ", "A routine "])
                    
                # Reconstruct the sentence using a random prefix and the augmented phrase
                final_text = (prefix + aug_text).replace("  ", " ").strip()
                
                augmented_texts.append(final_text)
                augmented_labels.append(label)

    return augmented_texts, augmented_labels


def prepare_data():
    """Generates and prepares the financial sentiment dataset with augmentation."""
    
    # Store the base texts separately for later use in testing
    global BASE_DATASET_TEXTS
    BASE_DATASET_TEXTS = [
        "Company reports record quarterly profits exceeding expectations",
        "Stock market reaches all-time high with strong gains",
        "Federal Reserve announces stimulus boosting investor confidence",
        "Tech company shares surge 8% after innovation announcement",
        "Strong job growth indicates economic recovery",
        "Merger announcement sends stocks soaring",
        "Bank adoption of cryptocurrency signals mainstream acceptance",
        "GDP growth exceeds forecasts showing economic expansion",
        "Company files for bankruptcy amid mounting debts",
        "Market crashes as recession fears grip investors",
        "Unemployment rate rises sharply concerning economists",
        "Major bank reports significant losses from bad loans",
        "Trade war escalates causing market volatility",
        "Company shares plummet 20% after product recall",
        "Economic indicators point to potential recession",
        "Corporate earnings disappoint leading to selloff",
        "Federal Reserve maintains interest rates unchanged",
        "Company releases earnings in line with expectations",
        "Trading volume remains steady as investors wait",
        "Board announces regular quarterly dividend",
        "Market closes mixed with minor changes",
        "Company announces CEO transition",
        "Annual shareholder meeting scheduled",
        "Regulatory filing submitted for compliance",
    ]

    labels = [
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 1, 1,
        2, 2, 2, 2, 2, 2, 2, 2
    ]

    # Use the augmentation function
    texts, labels = augment_data(BASE_DATASET_TEXTS, labels, repetition_factor=20)


    df = pd.DataFrame({'text': texts, 'label': labels})
    print(f"Dataset size: {len(df)}")

    # Print label distribution
    label_counts = df['label'].value_counts().sort_index()
    print("Label distribution:")
    print(f"Positive (0): {label_counts.get(0, 0)}")
    print(f"Negative (1): {label_counts.get(1, 0)}")
    print(f"Neutral (2): {label_counts.get(2, 0)}")

    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        df['text'].values,
        df['label'].values,
        test_size=0.2,
        random_state=seed,
        stratify=df['label'].values
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    return X_train, X_val, y_train, y_val

X_train, X_val, y_train, y_val = prepare_data()


# --- 3. Tokenizer and Dataset Class (No Change) ---
# # %%
tokenizer = BertTokenizer.from_pretrained(model_name)
print(f"Tokenizer loaded. Vocabulary size: {tokenizer.vocab_size}")

class FinancialDataset(Dataset):
    """Custom PyTorch Dataset for financial texts."""
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

train_dataset = FinancialDataset(X_train, y_train, tokenizer, max_length)
val_dataset = FinancialDataset(X_val, y_val, tokenizer, max_length)

print(f"Train dataset created: {len(train_dataset)} samples")
print(f"Validation dataset created: {len(val_dataset)} samples")

# --- 4. Model and Trainer Setup (No Change) ---
# # %%
model = BertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=num_labels
).to(device)

print("BERT model loaded")
print(f"Model type: {model_name}, Number of labels: {num_labels}")

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=num_epochs,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    learning_rate=learning_rate,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    do_train=True,
    do_eval=True,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    save_total_limit=2,
    seed=seed,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer
)

print("Trainer created")

# --- 5. Training (No Change) ---
# # %%
print("\n" + "=" * 50)
print("Starting training...")
print("=" * 50)

train_result = trainer.train()

print("Training completed!")

# Extract final metrics
train_loss = train_result.metrics['train_loss']
print(f"Final training loss: {train_loss:.4f}")

# --- 6. Evaluation and Analysis (No Change) ---
# # %%
def generate_evaluation_matrix(trainer, val_dataset, label_names):
    """
    Generates and prints the full evaluation matrix (Accuracy,
    Classification Report, and Confusion Matrix).
    """
    print("\n" + "=" * 50)
    print("Generating Full Evaluation Matrix")
    print("=" * 50)

    # 1. Evaluate to get loss
    eval_results = trainer.evaluate()
    validation_loss = eval_results['eval_loss']
    print(f"Validation loss: {validation_loss:.4f}")

    # 2. Get predictions
    predictions = trainer.predict(val_dataset)
    predicted_classes = np.argmax(predictions.predictions, axis=1)
    true_labels = predictions.label_ids

    # 3. Calculate Accuracy
    accuracy = accuracy_score(true_labels, predicted_classes)
    print(f"\nOverall Validation Accuracy: {accuracy:.4f}")

    # 4. Classification Report (Precision, Recall, F1-Score)
    short_label_names = [n.split(' ')[0] for n in label_names]
    report = classification_report(
        true_labels,
        predicted_classes,
        target_names=short_label_names,
        digits=4
    )
    print("\nClassification Report (Evaluation Matrix - Per-Class Metrics):")
    print("-" * 50)
    print(report)
    
    # 5. Confusion Matrix
    conf_matrix = confusion_matrix(true_labels, predicted_classes)
    print("\nConfusion Matrix:")
    print("-" * 50)
    print("True Labels (rows) vs Predicted Labels (columns)")
    print(conf_matrix)

    return accuracy, validation_loss, conf_matrix

accuracy, validation_loss, conf_matrix = generate_evaluation_matrix(trainer, val_dataset, label_names)

# --- 7. Visualization (Plotting code remains the same) ---
# # %%
# ... (Visualization code for Confusion Matrix and Loss plots remains here) ...

# --- 8. Testing on New Examples (Uses BASE_DATASET_TEXTS) ---
# # %%
# Global list to store prediction results for HTML generation and CSV export
html_prediction_results = []

def predict_sentiment(text, model, tokenizer, max_length, label_names, device):
    """Predicts the sentiment for a single text and stores the result, including all probabilities."""
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors='pt'
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

        probs = torch.softmax(logits, dim=-1)[0] # Get probabilities for the single item
        
        # Extract individual probabilities (0=Positive, 1=Negative, 2=Neutral)
        prob_positive = probs[0].item() 
        prob_negative = probs[1].item() 
        prob_neutral = probs[2].item()  

        predicted_class = torch.argmax(probs).item()
        confidence = torch.max(probs).item()
    
    # Store the result for HTML generation and CSV export
    html_prediction_results.append({
        'text': text,
        'label_index': predicted_class,
        'predicted_sentiment': label_names[predicted_class],
        'Positive_Percentage': prob_positive * 100,
        'Negative_Percentage': prob_negative * 100,
        'Neutral_Percentage': prob_neutral * 100
    })
    
    return predicted_class

# Combine the full base dataset texts and a couple of new examples for the report
report_sentences = BASE_DATASET_TEXTS + [
    "Tech company announces breakthrough, stock jumps 12%",
    "Global recession fears cause market crash",
    "Earnings report was slightly better than forecasted"
]

print("\n" + "=" * 50)
print("Testing All Sentences for Report Generation")
print("=" * 50)

# Extract only the class name for display
short_label_names = [n.split(' ')[0] for n in label_names]  
for i, sentence in enumerate(report_sentences):
    # Only print results for the custom tests or a few from the large set for brevity
    if i >= len(BASE_DATASET_TEXTS) or i % 5 == 0: 
         print(f"Testing sample {i+1}: {sentence[:50]}...")
    predict_sentiment(sentence, model, tokenizer, max_length, short_label_names, device)

# --- 9. Model Saving and Loading Test (Use for one final example) ---
# # %%
# Save the model and tokenizer
trainer.save_model(model_save_path)
tokenizer.save_pretrained(model_save_path)
print(f"\nModel saved to: {model_save_path}")

# Load and test the saved model
loaded_model = BertForSequenceClassification.from_pretrained(model_save_path)
loaded_tokenizer = BertTokenizer.from_pretrained(model_save_path)

loaded_model = loaded_model.to(device)
loaded_model.eval()

print("Model loaded successfully for testing.")

test_text_loaded = "Stock market shows positive momentum"
print("\n" + "=" * 50)
print("Test with Loaded Model")
print("=" * 50)
# Use the loaded model for a final test and store result
print(f"Testing final sample: {test_text_loaded}")
predict_sentiment(test_text_loaded, loaded_model, loaded_tokenizer, max_length, short_label_names, device)


# --- 10. HTML Generation (Slightly modified to use new column names) ---
# # %%

def generate_html_output(results):
    """Generates an HTML string from the prediction results with color coding and all percentages."""
    
    # Define colors for sentiment classes (0=Positive, 1=Negative, 2=Neutral)
    COLOR_MAP = {
        0: 'green',   # Positive
        1: 'red',     # Negative
        2: '#ffa500'  # Neutral (Orange)
    }

    style = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .sentiment-result {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            border-left: 8px solid;
            transition: transform 0.2s;
        }
        .positive { border-color: green; background-color: #e6ffe6; }
        .negative { border-color: red; background-color: #ffe6e6; }
        .neutral { border-color: #ffa500; background-color: #fff2e6; }
        .text-sentiment { font-size: 1.1em; margin-bottom: 10px; }
        .text-positive { color: green; font-weight: bold; }
        .text-negative { color: red; font-weight: bold; }
        .text-neutral { color: #ffa500; font-weight: bold; }
        .probabilities p { margin: 3px 0; font-size: 0.9em; }
        .probabilities { margin-top: 10px; padding-top: 5px; border-top: 1px solid #ddd; }
        .probabilities strong { display: inline-block; width: 100px; }
        h2 { border-bottom: 2px solid #ccc; padding-bottom: 5px; margin-top: 0; }
        .test-section-title { color: #333; margin-top: 30px; border-bottom: 1px dashed #ccc; padding-bottom: 5px; }
    </style>
    """

    html_content = "<html><head><title>Sentiment Analysis Results</title>" + style + "</head><body>"
    html_content += "<div class='container'>"
    html_content += "<h2>Financial Sentiment Analysis Full Report</h2>"
    
    # Separate the results into sections: Base Data, Custom Tests, and Loaded Model Test
    base_data_results = results[:len(BASE_DATASET_TEXTS)]
    custom_test_results = results[len(BASE_DATASET_TEXTS):-1]
    loaded_model_test_result = results[-1:]

    def format_results(section_results, title):
        html = f"<h3 class='test-section-title'>{title} ({len(section_results)} Samples)</h3>"
        for result in section_results:
            label_index = result['label_index']
            # Split 'Positive (0)' to get 'Positive'
            label_text = result['predicted_sentiment'].split(' ')[0] 
            text = result['text']
            
            prob_pos = result['Positive_Percentage']
            prob_neg = result['Negative_Percentage']
            prob_neu = result['Neutral_Percentage']

            sentiment_class = label_text.lower()
            color = COLOR_MAP.get(label_index, 'gray')

            html += f"""
            <div class="sentiment-result {sentiment_class}">
                <p class="text-sentiment"><strong>Text:</strong> <span class="text-{sentiment_class}">{text}</span></p>
                <p><strong>Predicted Sentiment:</strong> <span style="color: {color}; font-weight: bold;">{label_text}</span></p>
                
                <div class="probabilities">
                    <p><strong>Positive %:</strong> <span style="color: green;">{prob_pos:.2f}%</span></p>
                    <p><strong>Negative %:</strong> <span style="color: red;">{prob_neg:.2f}%</span></p>
                    <p><strong>Neutral %:</strong> <span style="color: #ffa500;">{prob_neu:.2f}%</span></p>
                </div>
            </div>
            """
        return html

    html_content += format_results(base_data_results, "Base Dataset Sentences")
    html_content += format_results(custom_test_results, "Custom Test Sentences")
    html_content += format_results(loaded_model_test_result, "Model Loading Test Sentence")

    html_content += "</div></body></html>"
    return html_content

# Generate the HTML output
html_output = generate_html_output(html_prediction_results)

# Save the HTML string to a file
html_filename = "sentiment_analysis_full_report.html"
with open(html_filename, "w") as f:
    f.write(html_output)
    
print(f"\nHTML output saved to: {html_filename}")

# --- 11. Export to CSV (NEW SECTION for Sheets/Excel) ---
# # %%

def export_to_csv(results, filename="sentiment_analysis_export.csv"):
    """Converts the list of results to a DataFrame and exports to CSV."""
    
    # Create a DataFrame directly from the list of dictionaries
    df_results = pd.DataFrame(results)
    
    # Drop the index column, as it's not needed for the final export
    df_results = df_results.drop(columns=['label_index'])
    
    # Export to CSV
    df_results.to_csv(filename, index=False)
    print(f"\nSuccessfully exported all prediction results to CSV: {filename}")
    print("This file can be opened directly in Excel or imported into Google Sheets.")
    
# Execute the CSV Export
csv_filename = "sentiment_analysis_for_sheets.csv"
export_to_csv(html_prediction_results, csv_filename)


print("\n" + "=" * 50)
print("TRAINING SUMMARY")
print("=" * 50)
print(f"Model: {model_name}")
print(f"Training samples: {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")
print(f"Number of epochs: {num_epochs}")
print(f"Batch size: {batch_size}")
print(f"Final validation accuracy: {accuracy:.2%}")
print(f"Final training loss: {train_loss:.4f}")
print(f"Final validation loss: {validation_loss:.4f}")
print("=" * 50)
print(f"Code completed successfully! Check the generated files: {html_filename} and {csv_filename}")