from typing import TypedDict, List, Dict, Optional, Literal

class FileState(TypedDict):
    file_path: str 
    content: str 
    status: Literal["pending", "generated", "patched", "validated", "failed"]
    retry_count: int 
    last_error: Optional[str]
    content_hash: Optional[str]
    source: Literal["llm", "memory", "patched"]

class AgentState(TypedDict):
    user_prompt: str
    user_id: str
    project_name: str
    project_root: str
    project_plan_markdown: str
    tech_stack: Dict[str, str]
    approved: bool
    backend_files: Dict[str, FileState]
    frontend_files: Dict[str, FileState]
    current_file: Optional[str]
    error_message: Optional[str]
    error_summary: Optional[str]
    retry_count: int
    max_retries: int
    build_status: str
    iteration_count: int
