import torch
from model_loader import ModelLoader

class TextFilterService:
    def __init__(self, model_loader: ModelLoader):
        self.model_loader = model_loader

    def process_text(self, final_text: str) -> dict:
        hf_tokenizer = self.model_loader.hf_tokenizer
        hf_model = self.model_loader.hf_model
        identity_model = self.model_loader.identity_model
        identity_tokenizer = self.model_loader.identity_tokenizer
        device = self.model_loader.device

        # Toxic-BERT inference
        hf_inputs = hf_tokenizer(final_text, return_tensors="pt", padding=True, truncation=True)
        hf_inputs = {k: v.to(device) for k, v in hf_inputs.items()}
        with torch.no_grad():
            hf_outputs = hf_model(**hf_inputs)
        hf_probs = torch.sigmoid(hf_outputs.logits)[0]
        hf_labels = hf_model.config.id2label
        results = {hf_labels.get(i, f"Label {i}"): float(prob) for i, prob in enumerate(hf_probs)}

        # Identity hate classifier
        identity_inputs = identity_tokenizer(final_text, return_tensors="pt", padding=True, truncation=True)
        identity_inputs.pop("token_type_ids", None)
        identity_inputs = {k: v.to(device) for k, v in identity_inputs.items()}
        with torch.no_grad():
            identity_outputs = identity_model(**identity_inputs)
        identity_probs = torch.sigmoid(identity_outputs.logits)
        identity_prob = identity_probs[0][1].item()
        not_identity_prob = identity_probs[0][0].item()

        results["identity_hate_custom"] = identity_prob
        results["not_identity_hate_custom"] = not_identity_prob

        results["safe"] = (
            all(results.get(label, 0) < 0.5 for label in ['toxic', 'severe_toxic', 'obscene', 'insult', 'identity_hate']) 
            and identity_prob < 0.5
        )

        return results
