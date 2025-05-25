from pydantic import BaseModel
from typing import List, Optional

class ClothingItem(BaseModel):
    type: str  # 'tops', 'bottoms', 'shoes'
    sub_type: Optional[str]
    color: Optional[str]
    pattern: Optional[str]
    material: Optional[str]
    style: Optional[str]
    season: Optional[str]
    mood: Optional[str]
    brand: Optional[str]

class AgentClothingAnalysis(BaseModel):
    scenario: str
    selected_categories: List[str]
    requested_categories: List[str]