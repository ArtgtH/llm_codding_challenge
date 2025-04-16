from datetime import date as Date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import json


class AgriculturalOperation(BaseModel):
    """
    Model representing agricultural operation data with daily and cumulative metrics.
    """
    date: Date = Field(description="Дата проведения операции")
    subdivision: str = Field(description="Подразделение, выполняющее операцию")
    operation: str = Field(description="Тип проводимой операции")
    crop: str = Field(description="Сельскохозяйственная культура")
    daily_area: Optional[float] = Field(description="За день, га", default=None)
    total_area: Optional[float] = Field(description="С начала операции, га", default=None) 
    daily_yield: Optional[float] = Field(description="Вал за день, ц", default=None)
    total_yield: Optional[float] = Field(description="Вал с начала, ц", default=None)
    
    def to_json(self) -> str:
        """Convert the model instance to a JSON string."""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgriculturalOperation":
        """Create a model instance from a JSON string."""
        data = json.loads(json_str)
        return cls.model_validate(data)
        
    @classmethod
    def get_schema_for_prompt(cls) -> str:
        """
        Returns a formatted JSON schema representation of the model,
        useful for inclusion in AI prompts.
        """
        schema = cls.model_json_schema()
        return json.dumps(schema, ensure_ascii=False, indent=2)
