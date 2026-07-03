---
metrics:
- accuracy
base_model:
- unitary/toxic-bert
---
Use Model
```bash
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
identity_model = AutoModelForSequenceClassification.from_pretrained("Mridul2003/identity-hate-detector").to(device)
identity_tokenizer = AutoTokenizer.from_pretrained("Mridul2003/identity-hate-detector")
identity_inputs = identity_tokenizer(final_text, return_tensors="pt", padding=True, truncation=True)
    if 'token_type_ids' in identity_inputs:
        del identity_inputs['token_type_ids']
    identity_inputs = {k: v.to(device) for k, v in identity_inputs.items()}
    with torch.no_grad():
        identity_outputs = identity_model(**identity_inputs)
    identity_probs = torch.sigmoid(identity_outputs.logits)
    identity_prob = identity_probs[0][1].item()
    not_identity_prob = identity_probs[0][0].item()

    results["identity_hate_custom"] = identity_prob
    results["not_identity_hate_custom"] = not_identity_prob

```

# Offensive Language Classifier (Fine-Tuned on Custom Dataset)

This repository contains a fine-tuned version of the [`unitary/toxic-bert`](https://huggingface.co/unitary/toxic-bert) model for binary classification of offensive language (labels: `Offensive` vs `Not Offensive`). The model has been specifically fine-tuned on a custom dataset due to limitations observed in the base model's performance — particularly with `identity_hate` related content.

---

## 🔍 Problem with Base Model (`unitary/toxic-bert`)

The original `unitary/toxic-bert` model is trained for multi-label toxicity detection with 6 categories:
- toxic
- severe toxic
- obscene
- threat
- insult
- identity_hate

While it performs reasonably well on generic toxicity, **it struggles with edge cases involving identity-based hate speech** — often:
- Misclassifying subtle or sarcastic identity attacks
- Underestimating offensive content with identity-specific slurs

---

## ✅ Why Fine-Tune?

We fine-tuned the model on a custom annotated dataset with two clear labels:
- `0`: Not Identity Hate 
- `1`: Identity Hate

The new model simplifies the task into a **binary classification problem**, allowing more focused training for real-world moderation scenarios.

---

## 📊 Dataset Overview

- Total examples: ~4,000+
- Balanced between offensive and non-offensive labels
- Contains high proportions of `identity_hate`, `obscene`, `insult`, and more nuanced samples

---

## 🧠 Model Details

- **Base model**: [`unitary/toxic-bert`](https://huggingface.co/unitary/toxic-bert)
- **Fine-tuned using**: Hugging Face 🤗 `Trainer` API
- **Loss function**: CrossEntropyLoss (via `num_labels=2`)
- **Batch size**: 8
- **Epochs**: 3
- **Learning rate**: 2e-5

---

## 🔬 Performance (Binary Classification)

| Metric   | Value   |
|----------|---------|
| Accuracy | ~92%    |
| Precision / Recall | Balanced |

---

