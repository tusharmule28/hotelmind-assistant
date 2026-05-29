import json
import re
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.logger import logger
from app.services.retry_handler import get_ollama_retry_decorator

class IntentClassifierService:
    def __init__(self):
        # Initialize LangChain Ollama chat model
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.0,
            format="json"  # Forces JSON output mode in Ollama
        )
        self.allowed_intents = {
            "BOOK_ROOM",
            "SEARCH_HOTEL",
            "CANCEL_BOOKING",
            "GUEST_REQUEST",
            "REVIEW_QUERY",
            "PRICING_QUERY",
            "OTHER"
        }

    @get_ollama_retry_decorator()
    async def _call_llm(self, message: str) -> str:
        """
        Invokes Ollama using LangChain. Wrapped in tenacity retry logic.
        """
        system_prompt = (
            "You are an AI assistant for a hotel reservation and guest services system. "
            "Your task is to classify the intent of a guest's query.\n\n"
            "Supported intents:\n"
            "- BOOK_ROOM: The guest wants to book a room, make a reservation, check availability, or start a booking.\n"
            "- SEARCH_HOTEL: The guest is looking for hotels, locations, amenities, or browsing options.\n"
            "- CANCEL_BOOKING: The guest wants to cancel an existing booking or reservation.\n"
            "- GUEST_REQUEST: The guest is asking for room service, extra towels, maintenance, housekeeping, wake-up calls, check-in/out times, or other guest services.\n"
            "- REVIEW_QUERY: The guest is asking about reviews, ratings, feedback, or guest experiences.\n"
            "- PRICING_QUERY: The guest is asking about room rates, prices, costs, fees, discounts, or pricing details.\n"
            "- OTHER: General greeting, chit-chat, or questions unrelated to hotels.\n\n"
            "You MUST respond ONLY with a JSON object matching this schema:\n"
            '{"intent": "<one of the intents above>", "confidence": <float between 0.0 and 1.0>}\n'
            "Do not include any other text, markdown formatting, or explanation."
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Query to classify: '{message}'")
        ]
        
        logger.info("calling_ollama_llm", model=settings.OLLAMA_MODEL, query=message)
        response = await self.llm.ainvoke(messages)
        return str(response.content)

    def _parse_and_validate_json(self, raw_output: str) -> Dict[str, Any]:
        """
        Safely extracts and parses JSON block, validating required keys and structures.
        """
        raw_output_clean = raw_output.strip()
        parsed_data = None

        # Try standard JSON parsing
        try:
            parsed_data = json.loads(raw_output_clean)
        except json.JSONDecodeError:
            logger.warning("direct_json_parse_failed", raw_output=raw_output)

        # Fallback: Regex extraction for JSON object block
        if not parsed_data:
            match = re.search(r"\{.*\}", raw_output_clean, re.DOTALL)
            if match:
                try:
                    parsed_data = json.loads(match.group(0))
                except json.JSONDecodeError as e:
                    logger.error("regex_json_parse_failed", raw_output=raw_output, error=str(e))
            else:
                logger.error("json_block_not_found", raw_output=raw_output)

        if not parsed_data:
            raise ValueError(f"Failed to parse any JSON from LLM output: {raw_output}")

        # Validate structure
        if "intent" not in parsed_data or "confidence" not in parsed_data:
            raise ValueError(f"Missing required fields 'intent' or 'confidence' in parsed JSON: {parsed_data}")

        # Normalize intent string
        intent = str(parsed_data["intent"]).upper().strip()
        
        # Validate intent matches allowed list
        if intent not in self.allowed_intents:
            logger.warn("unsupported_intent_returned", intent=intent, allowed=list(self.allowed_intents))
            intent = "OTHER"

        # Validate confidence is float
        try:
            confidence = float(parsed_data["confidence"])
            # Normalize confidence range
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            logger.error("invalid_confidence_format", confidence=parsed_data.get("confidence"))
            confidence = 0.0

        return {
            "intent": intent,
            "confidence": confidence
        }

    async def classify_intent(self, message: str) -> Dict[str, Any]:
        """
        Public classification method coordinating LLM call, parsing, and threshold logic.
        """
        try:
            raw_output = await self._call_llm(message)
            result = self._parse_and_validate_json(raw_output)
            
            logger.info(
                "intent_classification_completed",
                query=message,
                detected_intent=result["intent"],
                confidence=result["confidence"]
            )
            return result
        except Exception as e:
            logger.exception("intent_classification_failed", query=message, error=str(e))
            # Safe production fallback
            return {
                "intent": "OTHER",
                "confidence": 0.0,
                "error": str(e)
            }
