"""
Model registry for the RASD-Maroc API.

Serves the three Transformer-family models trained on Kaggle:

  1. spam-classifier   - DistilBERT fine-tuned on email-spam-detection
  2. econ-forecaster   - FT-Transformer on economie-maroc-rasd
  3. waste-classifier  - ViT fine-tuned on realwaste-classification

Weights are loaded lazily and only if present on disk under
`models/weights/<model_name>/`. If a model is not available, the registry
returns a structured 503 payload instead of crashing the API.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .model_cache import cached_predict

MODELS_DIR = Path(__file__).resolve().parent / "weights"

# Model name -> (framework, input type, description)
REGISTRY: Dict[str, Dict[str, Any]] = {
    "spam-classifier": {
        "framework": "transformers",
        "input": "text",
        "description": "DistilBERT fine-tuned for email spam detection (binary).",
        "classes": ["ham", "spam"],
    },
    "econ-forecaster": {
        "framework": "pytorch",
        "input": "tabular",
        "description": "FT-Transformer forecasting Morocco economic indicators.",
        "classes": ["value", "lower", "upper"],
    },
    "waste-classifier": {
        "framework": "transformers",
        "input": "image",
        "description": "Vision Transformer (ViT) for RealWaste 9-class image classification.",
        "classes": [
            "Cardboard", "Food Organics", "Glass", "Metal", "Miscellaneous Trash",
            "Paper", "Plastic", "Textile Trash", "Vegetation",
        ],
    },
}


def available_models() -> List[str]:
    return [name for name in REGISTRY if _weights_present(name)]


def model_info(name: str) -> Optional[Dict[str, Any]]:
    info = REGISTRY.get(name)
    if not info:
        return None
    return {**info, "name": name, "loaded": _weights_present(name)}


def _weights_present(name: str) -> bool:
    return (MODELS_DIR / name).exists()


def _missing_payload(name: str) -> Dict[str, Any]:
    return {
        "model": name,
        "status": "model_not_available",
        "error": (
            f"Trained weights for '{name}' not found. "
            f"Place them in models/weights/{name}/ or train on Kaggle first."
        ),
    }


@cached_predict("spam-classifier")
def _predict_spam(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = payload.get("text", "")
    try:
        from transformers import pipeline
        model_path = MODELS_DIR / "spam-classifier"
        clf = pipeline("text-classification", model=str(model_path), tokenizer=str(model_path))
        out = clf(text, truncation=True)[0]
        return {"model": "spam-classifier", "label": out["label"], "score": out["score"], "text": text}
    except ImportError:
        return {"model": "spam-classifier", "status": "dependencies_missing", "error": "transformers not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"model": "spam-classifier", "status": "inference_error", "error": str(exc)}


@cached_predict("econ-forecaster")
def _predict_econ(payload: Dict[str, Any]) -> Dict[str, Any]:
    code = payload.get("code", "")
    try:
        import joblib
        import pandas as pd
        model_path = MODELS_DIR / "econ-forecaster"
        model = joblib.load(model_path / "model.pkl")
        scaler = joblib.load(model_path / "scaler.pkl")
        feats = payload.get("features", [])
        df = pd.DataFrame([feats])
        X = scaler.transform(df)
        pred = model.predict(X)[0]
        return {"model": "econ-forecaster", "code": code, "forecast": float(pred)}
    except ImportError:
        return {"model": "econ-forecaster", "status": "dependencies_missing", "error": "joblib/pandas not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"model": "econ-forecaster", "status": "inference_error", "error": str(exc)}


@cached_predict("waste-classifier")
def _predict_waste(payload: Dict[str, Any]) -> Dict[str, Any]:
    image_path = payload.get("image", "")
    try:
        from transformers import pipeline
        model_path = MODELS_DIR / "waste-classifier"
        clf = pipeline("image-classification", model=str(model_path))
        out = clf(image_path)
        return {"model": "waste-classifier", "predictions": out}
    except ImportError:
        return {"model": "waste-classifier", "status": "dependencies_missing", "error": "transformers not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"model": "waste-classifier", "status": "inference_error", "error": str(exc)}


PREDICTORS = {
    "spam-classifier": _predict_spam,
    "econ-forecaster": _predict_econ,
    "waste-classifier": _predict_waste,
}


def predict(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run a cached prediction for the given model, or return a 503-style payload."""
    if name not in REGISTRY:
        return {"model": name, "status": "unknown_model", "error": f"Unknown model '{name}'"}
    if not _weights_present(name):
        return _missing_payload(name)
    predictor = PREDICTORS.get(name)
    if predictor is None:
        return {"model": name, "status": "not_implemented", "error": f"No predictor wired for '{name}'"}
    result = predictor(payload)
    return result
