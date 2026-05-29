from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    message: str = Field(..., description="The guest message/query to process", min_length=1)
    user_id: str = Field(default="default_user", description="The ID of the user for retrieving guest memory")

class ChatResponse(BaseModel):
    intent: str = Field(..., description="The classified intent, or 'clarification_required' if confidence is low")
    confidence: float = Field(..., description="The confidence score of the classification, between 0.0 and 1.0")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
