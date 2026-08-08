# Model weights

Drop trained model artifacts here, one folder per model:

| Folder                 | Model                          | Source dataset                         |
|------------------------|--------------------------------|----------------------------------------|
| `spam-classifier/`     | DistilBERT (transformers)      | email-spam-detection                   |
| `econ-forecaster/`     | FT-Transformer (torch/joblib)  | economie-maroc-rasd                    |
| `waste-classifier/`    | ViT (transformers)             | realwaste-classification               |

Each folder must contain the full model files required by the loader in
`models/__init__.py` (e.g. `config.json`, `pytorch_model.bin`, `tokenizer`
files, or `model.pkl` + `scaler.pkl` for the tabular forecaster).

Predictions are cached in Redis (key `rasd:model:<name>:<sha256>`), so
repeated identical queries return in <1ms instead of running inference.
Set `MODEL_CACHE_TTL` (seconds) to control how long results stay cached.
