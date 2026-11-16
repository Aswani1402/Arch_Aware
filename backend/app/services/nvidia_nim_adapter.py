"""
NVIDIA NIM (NVIDIA Inference Microservices) Hosted API Adapter for Architect AI.
Official Documentation: https://docs.api.nvidia.com/
Implements a modular, decoupled integration for visual material identification,
multimodal architectural reasoning, and search reranking.
Gracefully falls back to local rule-based engineering analysis if NVIDIA_API_KEY is not configured.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.error

logger = logging.getLogger("architect_ai.nvidia_nim")

# Official Hosted NVIDIA NIM Endpoints
NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Evaluated NIM Models for Architectural Discovery
NIM_MODELS = {
    "vision_primary": "meta/llama-3.2-90b-vision-instruct",
    "vision_fast": "meta/llama-3.2-11b-vision-instruct",
    "reranker": "nvidia/nv-rerankqa-mistral-4b-v3",
    "embeddings": "nvidia/nv-embedqa-e5-v5"
}

class NvidiaNimAdapter:
    """
    Decoupled adapter for NVIDIA NIM hosted endpoints.
    Provides visual material identification and semantic search reranking.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY", "").strip()
        self.base_url = NVIDIA_NIM_BASE_URL

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def analyze_architectural_image(
        self,
        image_url: str,
        context_title: str = "",
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits an image to NVIDIA NIM Vision models (e.g. Llama-3.2-90b-Vision or 11b-Vision)
        to identify visible architectural elements, candidate materials, and uncertainty caveats.
        """
        if not self.is_configured:
            return {
                "configured": False,
                "provider": "nvidia_nim",
                "message": "NVIDIA_API_KEY is not configured. Using rule-based engineering inspection."
            }

        selected_model = model_name or NIM_MODELS["vision_fast"]
        
        system_prompt = (
            "You are an architectural materials inspector for Architect AI. "
            "Analyze the provided image of an architectural design or building component. "
            "Identify: 1) Visible structural elements; 2) Candidate material types; "
            "3) Visual evidence; 4) Technical uncertainty caveats (what CANNOT be confirmed from photos). "
            "CRITICAL: Never invent manufacturer brand names, exact product SKUs, prices, or structural load ratings. "
            "Use qualified labels like 'Possible natural stone', 'Tile — exact material unconfirmed', 'Concrete finish — mix unconfirmed'. "
            "Return valid JSON only."
        )

        user_content = [
            {
                "type": "text",
                "text": f"Inspect this architectural image ({context_title}). What building materials and construction elements are visible?"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ]

        payload = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 800,
            "temperature": 0.2,
            "top_p": 0.7
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=15) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                choice_text = res_data["choices"][0]["message"]["content"]
                return {
                    "configured": True,
                    "provider": "nvidia_nim",
                    "model_used": selected_model,
                    "raw_response": choice_text
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            logger.warning(f"[NVIDIA NIM] HTTP {e.code} error: {error_body}")
            return {
                "configured": True,
                "provider": "nvidia_nim",
                "error": f"NVIDIA NIM API error ({e.code})",
                "detail": error_body
            }
        except Exception as e:
            logger.warning(f"[NVIDIA NIM] Connection failure: {e}")
            return {
                "configured": True,
                "provider": "nvidia_nim",
                "error": str(e)
            }

    def rerank_search_results(
        self,
        query: str,
        documents: List[str]
    ) -> Dict[str, Any]:
        """
        Reranks retrieved architectural items using NVIDIA NIM nv-rerankqa-mistral-4b-v3.
        """
        if not self.is_configured or not documents:
            return {"configured": False, "provider": "nvidia_nim", "ranked_indices": list(range(len(documents)))}

        payload = {
            "model": NIM_MODELS["reranker"],
            "query": {"text": query},
            "passages": [{"text": doc} for doc in documents]
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url}/ranking",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                rankings = res_data.get("rankings", [])
                ranked_indices = [r["index"] for r in sorted(rankings, key=lambda x: x["logit"], reverse=True)]
                return {
                    "configured": True,
                    "provider": "nvidia_nim",
                    "ranked_indices": ranked_indices
                }
        except Exception as e:
            logger.info(f"[NVIDIA NIM] Reranking fallback: {e}")
            return {"configured": True, "error": str(e), "ranked_indices": list(range(len(documents)))}
