import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset, ClassLabel, load_metric

# Load the dataset with the specified encoding
data = pd.read_csv('dataset.csv', encoding='latin1')

# Encode labels as integers
label_encoder = LabelEncoder()
data['labels'] = label_encoder.fit_transform(data['Category'])

# Split the dataset
train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)

# Load the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples['Items_name'], padding="max_length", truncation=True)

# Create Hugging Face Dataset
train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Ensure the labels are in the correct format
train_dataset = train_dataset.cast_column('labels', ClassLabel(num_classes=len(label_encoder.classes_)))
test_dataset = test_dataset.cast_column('labels', ClassLabel(num_classes=len(label_encoder.classes_)))

# Load the model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(label_encoder.classes_))

# Define training arguments
training_args = TrainingArguments(
    output_dir='results',
    evaluation_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=10,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

# Create Trainer instance
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Train the model
trainer.train()

# Evaluate the model
eval_results = trainer.evaluate()

# Print evaluation results
print(f"Evaluation results: {eval_results}")

# Save the model explicitly
trainer.save_model('results')
tokenizer.save_pretrained('results')
