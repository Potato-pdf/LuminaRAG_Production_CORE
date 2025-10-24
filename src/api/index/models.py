from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentToIndex(BaseModel):
    empresa: str
    titulo: str
    private : bool
    empresa: str = Field(..., description="Organization or company name")
    titulo: str = Field(..., description="Document title")
    private: Optional[bool] = Field(False, description="Is the document private?")

    class Config:
        schema_extra = {
            "example": {
                "empresa": "FINFERSSA",
                "titulo": "Contrato de servicio",
                "private": False,
            }
        }

