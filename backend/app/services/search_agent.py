import json
import re
from typing import Dict, Any, List
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.logger import logger
from app.services.retry_handler import get_ollama_retry_decorator

class SearchAgentService:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.0,
            format="json"
        )
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection("hotels")
        # Load embedding model (should ideally be loaded once at startup)
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)

    @get_ollama_retry_decorator()
    async def extract_parameters(self, query: str, guest_memory: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extracts location, price range, and amenities from the natural language query.
        """
        memory_context = ""
        if guest_memory:
            memory_context = f"\nGuest Memory Context:\nPreferences: {guest_memory.get('preferences', {})}\nBooking History: {guest_memory.get('booking_history_cache', [])}\nUse this context if the query implies using past preferences or locations."
            
        system_prompt = (
            "You are an AI assistant for a hotel search system. "
            "Extract search parameters from the user's query.\n"
            f"{memory_context}\n\n"
            "Output ONLY a JSON object with these keys:\n"
            "- location (string, or null if not specified)\n"
            "- max_price (float, or null if not specified)\n"
            "- amenities (list of strings, empty list if none specified)\n"
            "Example output: {\"location\": \"Pune\", \"max_price\": 3000.0, \"amenities\": [\"pool\"]}"
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        logger.info("extracting_search_parameters", query=query)
        response = await self.llm.ainvoke(messages)
        
        try:
            parsed_data = json.loads(response.content.strip())
            return parsed_data
        except Exception as e:
            logger.error("failed_to_parse_extraction", error=str(e), content=response.content)
            return {"location": None, "max_price": None, "amenities": []}

    def _calculate_score(self, hotel: Dict[str, Any], query_params: Dict[str, Any]) -> float:
        """
        Custom ranking formula:
        Rating (30%), Price (25%), Amenities (20%), Location (15%), Recency (10%)
        """
        # Rating score (0-1)
        rating_score = (hotel.get("rating", 0) / 5.0) * 0.30
        
        # Price score (0-1), favors cheaper but valid prices
        max_price = query_params.get("max_price")
        price = hotel.get("price_per_night", float('inf'))
        if max_price:
            if price <= max_price:
                price_score = 0.25
            else:
                price_score = max(0, 0.25 - ((price - max_price) / max_price) * 0.25)
        else:
            price_score = (15000 - min(price, 15000)) / 15000 * 0.25
            
        # Amenities score
        requested_amenities = [a.lower() for a in query_params.get("amenities", [])]
        if not requested_amenities:
            amenity_score = 0.20
        else:
            hotel_amenities = [a.lower() for a in hotel.get("amenities", [])]
            match_count = sum(1 for a in requested_amenities if any(a in ha for ha in hotel_amenities))
            amenity_score = (match_count / len(requested_amenities)) * 0.20
            
        # Location score
        req_location = (query_params.get("location") or "").lower()
        if not req_location:
            location_score = 0.15
        else:
            hotel_loc = hotel.get("location", "").lower()
            location_score = 0.15 if req_location in hotel_loc else 0.0
            
        # Recency score
        recency_score = hotel.get("recency_score", 0) * 0.10
        
        return rating_score + price_score + amenity_score + location_score + recency_score

    @get_ollama_retry_decorator()
    async def generate_explanation(self, hotel: Dict[str, Any], query: str) -> str:
        """Generates a brief explanation for why this hotel is recommended."""
        # Using a simpler chat ollama without json format for this
        explainer_llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.3
        )
        prompt = f"User asked for: '{query}'. You are recommending {hotel['name']} (Rating: {hotel['rating']}, Price: {hotel['price_per_night']}). In one short sentence, explain why this is a good match."
        response = await explainer_llm.ainvoke(prompt)
        return response.content.strip()

    async def search(self, query: str, top_k: int = 5, guest_memory: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # 1. Extract params
        params = await self.extract_parameters(query, guest_memory=guest_memory)
        
        # 2. Vector Search
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=20 # Get top 20, then rank down to 5
        )
        
        # 3. Custom Ranking
        candidates = []
        if results and results["metadatas"] and results["metadatas"][0]:
            for i, meta in enumerate(results["metadatas"][0]):
                # Needs to fetch full amenities from db ideally, but we can search for it in doc
                # For simplicity, we just use the metadata
                doc = results["documents"][0][i] if "documents" in results else ""
                amenities = [a.strip() for a in doc.split("Amenities include: ")[-1].split(",") if "Amenities include:" in doc]
                
                hotel = {
                    "id": meta["id"],
                    "name": meta["name"],
                    "location": meta["location"],
                    "price_per_night": meta["price_per_night"],
                    "rating": meta["rating"],
                    "recency_score": meta["recency_score"],
                    "amenities": amenities
                }
                score = self._calculate_score(hotel, params)
                hotel["search_score"] = score
                candidates.append(hotel)
                
        # Sort by score descending
        candidates.sort(key=lambda x: x["search_score"], reverse=True)
        top_candidates = candidates[:top_k]
        
        # 4. Generate Explanations
        for hotel in top_candidates:
            hotel["explanation"] = await self.generate_explanation(hotel, query)
            
        return top_candidates
