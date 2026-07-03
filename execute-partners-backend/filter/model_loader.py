import os
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODELS_DIR = Path(os.getenv("MODELS_DIR", "/app/models"))
TOXIC_HUB_ID = "unitary/toxic-bert"
IDENTITY_HUB_ID = "Mridul2003/identity-hate-detector"


def _resolve_model_source(local_name: str, hub_id: str) -> str:
    local_path = MODELS_DIR / local_name
    if local_path.is_dir() and (local_path / "config.json").exists():
        return str(local_path)
    return hub_id


class ModelLoader:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_models()

    def _load_models(self):
        toxic_source = _resolve_model_source("toxic-bert", TOXIC_HUB_ID)
        identity_source = _resolve_model_source("identity-hate-detector", IDENTITY_HUB_ID)

        self.hf_model = AutoModelForSequenceClassification.from_pretrained(
            toxic_source
        ).to(self.device)
        self.hf_tokenizer = AutoTokenizer.from_pretrained(toxic_source)

        self.identity_model = AutoModelForSequenceClassification.from_pretrained(
            identity_source
        ).to(self.device)

        try:
            self.identity_tokenizer = AutoTokenizer.from_pretrained(identity_source)
        except Exception:
            self.identity_tokenizer = self.hf_tokenizer
