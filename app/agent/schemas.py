from typing import List, Dict
from pydantic import BaseModel

class ProjectPlan(BaseModel):
    project_name: str
    description: str
    backend_structure: List[str]
    frontend_structure: List[str]
    api_endpoints: List[Dict[str, str]]
    database_models: List[Dict[str, str]]

class FileGeneration(BaseModel):
    file_path: str
    code: str

class ErrorFixResponse(BaseModel):
    explanation: str
    corrected_code: str
