import xgboost as xgb
from backend.file_manager import download_file

BUCKET_NAME = "modelos"

# Rutas de los modelos
FERTILIDAD_MODEL_PATH = "fertilidad_model.json"
CULTIVO_MODEL_PATH = "cultivo_model.json"

def load_models():
    """Descarga y carga los modelos de fertilidad y cultivo."""
    try:
        download_file(BUCKET_NAME, "fertilidad_model.json", FERTILIDAD_MODEL_PATH)
        download_file(BUCKET_NAME, "cultivo_model.json", CULTIVO_MODEL_PATH)

        fertilidad_model = xgb.XGBClassifier()
        fertilidad_model.load_model(FERTILIDAD_MODEL_PATH)

        cultivo_model = xgb.XGBClassifier()
        cultivo_model.load_model(CULTIVO_MODEL_PATH)

        return fertilidad_model, cultivo_model
    except Exception as e:
        raise RuntimeError(f"Error al cargar los modelos: {e}")
