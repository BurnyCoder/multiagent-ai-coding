import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

class OsmosisAPI:
    """Client for interacting with the Osmosis Agent Improvement API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Osmosis API client
        
        Args:
            api_key: Optional API key. If not provided, will look for OSMOSIS_API_KEY env var
        """
        self.api_key = api_key or os.getenv('OSMOSIS_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set as OSMOSIS_API_KEY environment variable")
            
        self.base_url = "https://osmosis.gulp.dev"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

    def enhance_task(self, input_text: str, context: Optional[Dict[str, str]] = None, 
                    agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Enhance a task with relevant knowledge
        
        Args:
            input_text: The agent's input/query
            context: Optional context about agent's current state
            agent_type: Optional type of agent making request
            
        Returns:
            Dict containing enhanced response and metadata
        """
        payload = {
            "tenant_id": self.api_key,
            "input_text": input_text,
            "context": context or {},
            "agent_type": agent_type
        }
        
        response = requests.post(
            f"{self.base_url}/enhance_task",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()['response']
        return result

    def store_knowledge(self, query: str, turns: List[Dict[str, Any]], 
                       success: Optional[bool] = None,
                       agent_type: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store agent interactions and experiences
        
        Args:
            query: Original user query/instruction
            turns: Sequence of agent interaction turns
            success: Whether agent completed task successfully
            agent_type: Type of agent
            metadata: Additional metadata about interaction
            
        Returns:
            Dict containing storage confirmation and metadata
        """
        payload = {
            "tenant_id": self.api_key,
            "query": query,
            "turns": turns,
            "success": success,
            "agent_type": agent_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }
        
        response = requests.post(
            f"{self.base_url}/store_knowledge",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def delete_by_intent(self, intent: str, 
                        similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """Delete knowledge entries matching an intent
        
        Args:
            intent: Intent to match against
            similarity_threshold: Similarity threshold for matching (0-1)
            
        Returns:
            Dict containing deletion results
        """
        params = {
            "tenant_id": self.api_key,
            "intent": intent,
            "similarity_threshold": similarity_threshold
        }
        
        response = requests.post(
            f"{self.base_url}/delete_by_intent",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def test_api_features(self):
        """Test all features of the Osmosis API"""
        try:
            # Test enhance_task
            print("\nTesting enhance_task...")
            enhance_response = self.enhance_task(
                input_text="Find and purchase a red Nike running shoe in size 10",
                context={"user_type": "customer", "category": "shoes"},
                agent_type="shopping_assistant"
            )
            print("Enhance task response:", enhance_response)

            # Test store_knowledge
            print("\nTesting store_knowledge...")
            turns = [
                {
                    "turn": 1,
                    "inputs": "On shopping website homepage. Need to search for red Nike running shoes.",
                    "decision": json.dumps({
                        "action_type": "click",
                        "element_name": "search_bar",
                        "text": ["Nike red running shoes"]
                    }),
                    "result": "Clicked search bar and entered search terms",
                    "memory": "User wants red Nike running shoes"
                }
            ]
            store_response = self.store_knowledge(
                query="Find red Nike running shoes",
                turns=turns,
                success=True,
                agent_type="shopping_assistant",
                metadata={"browser": "chrome", "session_id": "123"}
            )
            print("Store knowledge response:", store_response)

            # Test delete_by_intent
            print("\nTesting delete_by_intent...")
            delete_response = self.delete_by_intent(
                intent="find shoes",
                similarity_threshold=0.7
            )
            print("Delete by intent response:", delete_response)

            print("\nAll API tests completed successfully!")
            return True

        except Exception as e:
            print(f"Error during API testing: {str(e)}")
            return False

            
if __name__ == "__main__":
    # Initialize API client
    api = OsmosisAPI()
    
    # Run tests
    api.test_api_features()
