"""
LangChain and OpenAI integration service
"""
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings


class LangChainService:
    """Service for LangChain and OpenAI operations"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. LangChain features will be disabled.")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.7
            )
    
    async def generate_deal_summary(self, deal_data: Dict[str, Any]) -> str:
        """
        Generate a deal summary using LangChain
        
        Args:
            deal_data: Dictionary containing deal information
            
        Returns:
            Generated summary text
        """
        if not self.llm:
            return "LangChain service not available"
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert automotive deal analyst."),
            HumanMessage(content=f"Summarize this deal: {deal_data}")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = await chain.ainvoke({})
        return result.get("text", "")
    
    async def analyze_vehicle_price(
        self,
        make: str,
        model: str,
        year: int,
        mileage: int,
        condition: str,
        asking_price: float
    ) -> Dict[str, Any]:
        """
        Analyze vehicle pricing using AI
        
        Args:
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            mileage: Vehicle mileage
            condition: Vehicle condition
            asking_price: Asking price
            
        Returns:
            Dictionary with analysis results
        """
        if not self.llm:
            return {"error": "LangChain service not available"}
        
        prompt = f"""
        Analyze the following vehicle pricing:
        - Make: {make}
        - Model: {model}
        - Year: {year}
        - Mileage: {mileage} miles
        - Condition: {condition}
        - Asking Price: ${asking_price:,.2f}
        
        Provide:
        1. Fair market value estimate
        2. Price assessment (fair, overpriced, underpriced)
        3. Key factors affecting the price
        4. Negotiation recommendations
        """
        
        messages = [
            SystemMessage(content="You are an expert automotive pricing analyst."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return {
            "analysis": response.content,
            "vehicle": {
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "condition": condition,
                "asking_price": asking_price
            }
        }
    
    async def generate_customer_response(
        self,
        customer_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate customer response using AI
        
        Args:
            customer_query: Customer's question or query
            context: Optional context information
            
        Returns:
            Generated response text
        """
        if not self.llm:
            return "AI service not available"
        
        system_prompt = """
        You are AutoDealGenie, a helpful automotive deal assistant.
        Provide accurate, friendly, and professional responses to customer queries.
        """
        
        context_str = f"\nContext: {context}" if context else ""
        user_prompt = f"{customer_query}{context_str}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content


langchain_service = LangChainService()
