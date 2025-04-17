import json
import logging
from mistralai import Mistral
from ai_agent.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class MistralAnalysisClient:
    def __init__(self, api_key: str, rate_limiter: RateLimiter):
        self.client = Mistral(api_key=api_key)
        self.rate_limiter = rate_limiter
        self.model = "mistral-large-latest"

    def analyze(self, text: str, prompt: str) -> dict:
        """
        Send analysis request with structured error handling.

        Args:
            text: Text content to analyze
            prompt: Instruction prompt for the analysis

        Returns:
            Parsed JSON response or error information dictionary
        """
        self.rate_limiter.wait()

        try:
            full_prompt = f"{prompt}\n\nText: {text}"
            messages = [{"role": "user", "content": full_prompt}]

            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
            )

            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {"error": "parsing_error", "details": str(e)}
            except (IndexError, AttributeError) as e:
                logger.error(f"Unexpected response format: {e}")
                return {"error": "format_error", "details": str(e)}

        except Exception as e:
            logger.error(f"API error during analysis: {e}")
            return {"error": "api_error", "details": str(e)}
