import os
from openai import AsyncOpenAI
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    """Service for generating conversational responses using OpenAI."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"
    
    def _get_system_prompt(self, current_state: str, context: Dict) -> str:
        """Generate system prompt based on current conversation state."""
        
        base_prompt = """You are a friendly, professional insurance onboarding assistant. Your role is to collect information from users in a conversational way. Be concise but warm.

IMPORTANT RULES:
1. Stay focused on collecting the required information
2. If the user seems frustrated, upset, or asks to speak with a human, respond with empathy and include the phrase [FRUSTRATED_USER] at the start of your response
3. Validate inputs naturally (e.g., if email looks invalid, politely ask them to check it)
4. Keep responses brief - one or two sentences when asking for information
5. Don't repeat information the user has already provided
"""
        
        state_prompts = {
            "zip_code": "Ask for their ZIP code. Validate it's a 5-digit number.",
            "full_name": "Ask for their full name.",
            "email": "Ask for their email address.",
            "vehicle_choice": "Ask if they want to provide a VIN number OR enter Year, Make, and Body Type manually.",
            "vehicle_vin": "Ask for their vehicle's VIN (17 characters).",
            "vehicle_year": "Ask for the vehicle's year.",
            "vehicle_make": "Ask for the vehicle's make (e.g., Toyota, Ford, Honda).",
            "vehicle_body": "Ask for the vehicle's body type (e.g., Sedan, SUV, Truck, Coupe).",
            "vehicle_use": "Ask how they use this vehicle. Options: Commuting, Commercial, Farming, or Business.",
            "blind_spot_warning": "Ask if the vehicle has blind spot warning equipment (Yes/No).",
            "commute_days": "Ask how many days per week they use this vehicle for commuting.",
            "commute_miles": "Ask about one-way miles to work/school.",
            "annual_mileage": "Ask for estimated annual mileage.",
            "add_another_vehicle": "Ask if they want to add another vehicle to their policy.",
            "license_type": "Ask about their US license type. Options: Foreign, Personal, or Commercial.",
            "license_status": "Ask about their license status: Valid or Suspended.",
            "complete": "Thank them and let them know their information has been collected successfully."
        }
        
        state_instruction = state_prompts.get(current_state, "Continue the conversation naturally.")
        
        context_str = ""
        if context:
            context_str = f"\n\nCollected information so far:\n"
            for key, value in context.items():
                if value:
                    context_str += f"- {key}: {value}\n"
        
        return f"{base_prompt}\n\nCurrent task: {state_instruction}{context_str}"
    
    async def generate_response(
        self,
        current_state: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict,
        additional_context: Optional[str] = None
    ) -> str:
        """Generate a response using OpenAI."""
        
        system_prompt = self._get_system_prompt(current_state, context)
        
        if additional_context:
            system_prompt += f"\n\nAdditional context: {additional_context}"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history (last 10 messages for context)
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback response if OpenAI fails
            fallback_responses = {
                "zip_code": "Could you please provide your ZIP code?",
                "full_name": "What is your full name?",
                "email": "What is your email address?",
                "vehicle_choice": "Would you like to enter a VIN or provide Year, Make, and Body Type?",
                "vehicle_vin": "Please enter the 17-character VIN.",
                "vehicle_year": "What year is the vehicle?",
                "vehicle_make": "What is the make of the vehicle?",
                "vehicle_body": "What is the body type?",
                "vehicle_use": "How do you use this vehicle? (Commuting, Commercial, Farming, Business)",
                "blind_spot_warning": "Does this vehicle have blind spot warning? (Yes/No)",
                "commute_days": "How many days per week do you commute?",
                "commute_miles": "How many miles is your one-way commute?",
                "annual_mileage": "What is your estimated annual mileage?",
                "add_another_vehicle": "Would you like to add another vehicle?",
                "license_type": "What type of US license do you have? (Foreign, Personal, Commercial)",
                "license_status": "What is your license status? (Valid/Suspended)",
                "complete": "Thank you! Your information has been collected successfully."
            }
            return fallback_responses.get(current_state, "I'm sorry, could you repeat that?")
    
    async def check_frustration(self, message: str) -> bool:
        """Check if user message indicates frustration."""
        frustration_keywords = [
            "frustrated", "angry", "annoyed", "speak to human", "talk to someone",
            "real person", "agent", "representative", "this is ridiculous",
            "hate this", "stupid", "useless", "waste of time", "give up",
            "help me", "not working", "doesn't work", "broken"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in frustration_keywords)

