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
num_epochs = 1  # Reduced epoch
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
def prepare_data():
    """Generates and prepares the financial sentiment dataset."""
    texts = [
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

    # Increase dataset size by repeating
    texts = texts * 20
    labels = labels * 20

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

# --- 3. Tokenizer and Dataset Class ---
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

# --- 4. Model and Trainer Setup ---
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

# --- 5. Training ---
# # %%
print("\n" + "=" * 50)
print("Starting training...")
print("=" * 50)

train_result = trainer.train()

print("Training completed!")

# Extract final metrics
train_loss = train_result.metrics['train_loss']
print(f"Final training loss: {train_loss:.4f}")

# --- 6. Evaluation and Analysis ---
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

# --- 7. Visualization ---
# # %%
# Confusion Matrix Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=[n.split(' ')[0] for n in label_names],
            yticklabels=[n.split(' ')[0] for n in label_names])
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

# Loss History Plot
training_loss_history = []
validation_loss_history = []

for log in trainer.state.log_history:
    if 'loss' in log and 'step' in log:
        training_loss_history.append((log['step'], log['loss']))
    if 'eval_loss' in log:
        validation_loss_history.append(log['eval_loss'])

if validation_loss_history:
    plt.figure(figsize=(12, 5))

    # Validation Loss per Epoch
    plt.subplot(1, 2, 1)
    epochs_plot = range(1, len(validation_loss_history) + 1)
    plt.plot(epochs_plot, validation_loss_history, 'o-', label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Validation Loss per Epoch')
    plt.grid(True)

    # Training Loss Progress
    if training_loss_history:
        plt.subplot(1, 2, 2)
        steps, losses = zip(*training_loss_history)
        plt.plot(steps, losses, label='Training Loss')
        plt.xlabel('Training Steps')
        plt.ylabel('Loss')
        plt.title('Training Loss Progress')
        plt.grid(True)

    plt.tight_layout()
    plt.show()
else:
    print("Could not generate loss plots (loss history is empty).")

# --- 8. Testing on New Examples ---
# # %%
def predict_sentiment(text, model, tokenizer, max_length, label_names, device):
    """Predicts the sentiment for a single text."""
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

        probs = torch.softmax(logits, dim=-1)

        predicted_class = torch.argmax(probs, dim=-1).item()
        confidence = torch.max(probs).item()

    print(f"\nText: {text}")
    print(f"Predicted class: {label_names[predicted_class]}")
    print(f"Confidence: {confidence:.4f}")

    print("All probabilities:")
    print(f"  Positive: {probs[0][0].item():.4f}")
    print(f"  Negative: {probs[0][1].item():.4f}")
    print(f"  Neutral: {probs[0][2].item():.4f}")

test_sentences = [
    "Tech company announces breakthrough, stock jumps 12%", # Expect Positive
    "Global recession fears cause market crash",            # Expect Negative
    "Company maintains steady growth as expected"           # Expect Neutral
]

print("\n" + "=" * 50)
print("Testing on New Examples (using the trained model)")
print("=" * 50)

# Extract only the class name for display
short_label_names = [n.split(' ')[0] for n in label_names] 
for sentence in test_sentences:
    predict_sentiment(sentence, model, tokenizer, max_length, short_label_names, device)

# --- 9. Model Saving and Loading Test ---
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

test_text = "Stock market shows positive momentum"
print("\n" + "=" * 50)
print("Test with Loaded Model")
print("=" * 50)
predict_sentiment(test_text, loaded_model, loaded_tokenizer, max_length, short_label_names, device)

# --- 10. Final Summary ---
# # %%
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
print("Code completed successfully!")