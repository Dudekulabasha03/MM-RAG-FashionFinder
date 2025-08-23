"""
Service for interacting with local Ollama LLM models.
"""

import logging
import requests
import json
import base64
from typing import Optional
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaService:
    """
    Provides methods to interact with local Ollama LLM models.
    """
    
    def __init__(self, model_name="llama3.2:3b", 
                 base_url="http://localhost:11434",
                 temperature=0.2, top_p=0.6, max_tokens=2000):
        """
        Initialize the service with the specified Ollama model and parameters.
        
        Args:
            model_name (str): Name of the Ollama model to use
            base_url (str): Base URL for the Ollama API
            temperature (float): Controls randomness in generation
            top_p (float): Nucleus sampling parameter
            max_tokens (int): Maximum tokens in the response
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        
        # Test connection to Ollama
        self._test_connection()
    
    def _test_connection(self):
        """Test the connection to Ollama service."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Successfully connected to Ollama at {self.base_url}")
                # Check if our model is available
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                if self.model_name in model_names:
                    logger.info(f"Model {self.model_name} is available")
                else:
                    logger.warning(f"Model {self.model_name} not found. Available models: {model_names}")
            else:
                logger.error(f"Failed to connect to Ollama: {response.status_code}")
        except Exception as e:
            logger.error(f"Error connecting to Ollama: {e}")
    
    def generate_response(self, prompt: str, image_base64: Optional[str] = None) -> str:
        """
        Generate a response from the Ollama model based on a prompt and optionally an image.
        
        Args:
            prompt (str): Text prompt to guide the model's response
            image_base64 (str, optional): Base64-encoded image string
            
        Returns:
            str: Model's response
        """
        try:
            logger.info(f"Sending request to Ollama model {self.model_name} with prompt length: {len(prompt)}")
            
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_predict": self.max_tokens
                }
            }
            
            # Add image if provided
            if image_base64:
                payload["images"] = [image_base64]
            
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "")
                
                # Check if response appears to be truncated
                if result.get("done", False) and len(content) < 100:
                    logger.warning("Response appears to be truncated or too short")
                
                logger.info(f"Successfully generated response with {len(content)} characters")
                return content
            else:
                logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                return f"Error generating response: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {e}"
    
    def generate_fashion_response(self, user_image_base64, matched_row, all_items, 
                                 similarity_score, threshold=0.8):
        """
        Generate a fashion-specific response using role-based prompts.
        
        Args:
            user_image_base64: Base64-encoded user-uploaded image
            matched_row: The closest match row from the dataset
            all_items: DataFrame with all items related to the matched image
            similarity_score: Similarity score between user and matched images
            threshold: Minimum similarity for considering an exact match
            
        Returns:
            str: Detailed fashion response
        """
        try:
            # Generate a list of items with prices and links
            items_list = []
            for _, item in all_items.iterrows():
                item_info = f"* {item.get('Item Name', 'Unknown Item')}"
                if 'Price' in item and pd.notna(item['Price']):
                    item_info += f" - Price: {item['Price']}"
                if 'Brand' in item and pd.notna(item['Brand']):
                    item_info += f" - Brand: {item['Brand']}"
                if 'Image URL' in item and pd.notna(item['Image URL']):
                    item_info += f" - [View Image]({item['Image URL']})"
                items_list.append(item_info)
            
            # Join items with clear separators
            items_text = "\n".join(items_list)
            
            # Create prompt based on similarity threshold
            if similarity_score >= threshold:
                match_quality = "excellent match"
                confidence = "high confidence"
            else:
                match_quality = "similar item"
                confidence = "moderate confidence"
            
            # Create the fashion analysis prompt
            prompt = f"""You are a fashion expert analyzing a user's uploaded image. 

The user's image has been matched with {match_quality} in our database with {confidence} (similarity score: {similarity_score:.2f}).

MATCHED ITEM DETAILS:
- Item Name: {matched_row.get('Item Name', 'Unknown')}
- Brand: {matched_row.get('Brand', 'Unknown')}
- Price: {matched_row.get('Price', 'Unknown')}
- Category: {matched_row.get('Category', 'Unknown')}

RELATED ITEMS IN DATABASE:
{items_text}

Please provide a detailed fashion analysis including:
1. Description of the main item in the user's image
2. Style analysis (colors, patterns, fit, occasion)
3. Fashion recommendations and styling tips
4. Similar alternatives from our database

Keep the response informative, engaging, and fashion-focused. Use markdown formatting for better readability."""

            # Send the prompt to the model
            response = self.generate_response(prompt, user_image_base64)
            
            # Check if response is incomplete and create basic response if needed
            if not response or len(response.strip()) < 100:
                logger.warning("Generated response is too short, creating fallback response")
                response = f"""## Fashion Analysis Results

Based on your image, I've identified a {match_quality} in our database:

**Matched Item:** {matched_row.get('Item Name', 'Unknown')}
**Brand:** {matched_row.get('Brand', 'Unknown')}
**Price:** {matched_row.get('Price', 'Unknown')}
**Similarity Score:** {similarity_score:.2f}

## Related Items Found

{items_text}

*Note: The AI analysis was incomplete, but here are the items we found in our database that match your image.*"""

            # Ensure the items list is included
            if "RELATED ITEMS" not in response and "Related Items" not in response:
                response += f"\n\n## Related Items Found\n\n{items_text}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating fashion response: {e}")
            return f"Error generating fashion analysis: {e}"