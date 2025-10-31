"""
🎯 SELECCIÓN DE MODELO DE EMBEDDINGS
====================================

Módulo para seleccionar y configurar el modelo de embeddings apropiado.
"""

from typing import Any
import logging
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from src.config import EMBEDDING_CONFIG

logger = logging.getLogger(__name__)


class CustomEmbeddingModel:
    """Modelo de embeddings personalizado para modelos no registrados en sentence-transformers"""

    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Cargar el modelo desde Hugging Face"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Modelo {self.model_name} cargado exitosamente desde transformers")
        except Exception as e:
            raise RuntimeError(f"Error cargando modelo {self.model_name}: {e}")

    def encode(self, texts, convert_to_numpy=True, **kwargs):
        """Generar embeddings para textos"""
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        with torch.no_grad():
            for text in texts:
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                      max_length=512, padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                outputs = self.model(**inputs)
                # Usar mean pooling sobre las últimas capas ocultas
                embeddings_tensor = outputs.last_hidden_state.mean(dim=1)
                # Normalizar
                embeddings_tensor = F.normalize(embeddings_tensor, p=2, dim=1)

                if convert_to_numpy:
                    embeddings.append(embeddings_tensor.cpu().numpy().flatten())
                else:
                    embeddings.append(embeddings_tensor.cpu().flatten())

        return embeddings[0] if len(embeddings) == 1 else embeddings

    def get_sentence_embedding_dimension(self):
        """Obtener la dimensión de los embeddings"""
        return self.model.config.hidden_size


def get_embedding_model():
    """
    Obtener el modelo de embeddings configurado.

    Returns:
        Modelo de embeddings (SentenceTransformer o CustomEmbeddingModel)
    """
    model_name = EMBEDDING_CONFIG["model_name"]
    device = EMBEDDING_CONFIG["device"]

    try:
        # Intentar cargar como modelo de sentence-transformers primero
        model = SentenceTransformer(model_name, device=device)
        logger.info(f"Modelo {model_name} cargado exitosamente como SentenceTransformer")
        return model
    except Exception as e:
        logger.warning(f"No se pudo cargar {model_name} como SentenceTransformer: {e}")
        logger.info(f"Intentando cargar {model_name} como modelo transformers personalizado...")

        try:
            # Si falla, intentar cargar como modelo transformers personalizado
            model = CustomEmbeddingModel(model_name, device=device)
            logger.info(f"Modelo {model_name} cargado exitosamente como CustomEmbeddingModel")
            return model
        except Exception as e2:
            raise RuntimeError(f"Error cargando modelo de embeddings {model_name}: {e2}")


def get_text_embedding(text: str) -> list[float]:
    """
    Generar embedding para un texto dado.

    Args:
        text: Texto a embedder

    Returns:
        Lista de floats con el embedding
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=False)

    # Convertir a lista si es tensor
    if hasattr(embedding, 'tolist'):
        return embedding.tolist()
    elif hasattr(embedding, 'numpy'):
        return embedding.numpy().tolist()
    else:
        return list(embedding)