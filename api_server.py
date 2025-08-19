from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import traceback
import sys
import os
import base64
import json
from io import BytesIO
from PIL import Image

# Add the current directory to Python path to import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import RAG functions from app.py
from app import createMultiQueryChain, kb_retriever, generateRRF, generateResponse, MultiQuery, llm

app = FastAPI(title="Nyantar AI API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    chatHistory: List[dict]
    feature: str = "chat"
    language: str = "english"
    image_url: Optional[str] = None  # Base64 encoded image
    document_url: Optional[str] = None  # Base64 encoded document

class DraftingRequest(BaseModel):
    document_type: str
    subject: str
    parties: List[str]
    key_terms: Dict[str, str]
    jurisdiction: str = "India"
    language: str = "english"
    additional_context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    error: Optional[str] = None

class DraftingResponse(BaseModel):
    document: str
    document_type: str
    sections: List[str]
    language: str

# Legal drafting templates
DRAFTING_TEMPLATES = {
    "employment_contract": {
        "sections": [
            "Parties and Position",
            "Term of Employment",
            "Duties and Responsibilities",
            "Compensation and Benefits",
            "Working Hours and Conditions",
            "Termination Clauses",
            "Confidentiality and Non-Compete",
            "Dispute Resolution"
        ],
        "prompt": "Draft a comprehensive employment contract in {language} for the position of {position} with the following terms: {key_terms}. Include all standard legal clauses and ensure compliance with Indian labor laws."
    },
    "rental_agreement": {
        "sections": [
            "Parties and Property",
            "Term of Lease",
            "Rent and Payment Terms",
            "Security Deposit",
            "Maintenance and Repairs",
            "Utilities and Services",
            "Restrictions and Rules",
            "Termination and Renewal"
        ],
        "prompt": "Draft a comprehensive rental agreement in {language} for {property_type} with the following terms: {key_terms}. Include all standard legal clauses and ensure compliance with Indian rental laws."
    },
    "legal_notice": {
        "sections": [
            "Sender and Recipient Details",
            "Subject Matter",
            "Facts and Circumstances",
            "Legal Basis",
            "Demands and Relief Sought",
            "Time Limit for Response",
            "Consequences of Non-Compliance"
        ],
        "prompt": "Draft a professional legal notice in {language} regarding {subject} with the following details: {key_terms}. Use appropriate legal language and ensure all necessary elements are included."
    },
    "business_contract": {
        "sections": [
            "Parties and Purpose",
            "Scope of Work",
            "Terms and Conditions",
            "Payment Terms",
            "Delivery and Performance",
            "Intellectual Property",
            "Confidentiality",
            "Termination and Dispute Resolution"
        ],
        "prompt": "Draft a comprehensive business contract in {language} for {subject} with the following terms: {key_terms}. Include all standard business contract clauses and ensure legal compliance."
    }
}

@app.on_event("startup")
async def startup_event():
    print("Starting Nyantar AI API Server...")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Nyantar AI API is running"}

async def process_image_with_gpt4_vision(image_data: str, question: str, language: str):
    """Process image using GPT-4 Vision API"""
    try:
        import openai
        
        vision_prompt = f"""
        Analyze this legal document image and answer the user's question: {question}
        
        Provide a comprehensive legal analysis including:
        1. Document type identification
        2. Key legal points and terms
        3. Relevant legal provisions
        4. Practical implications
        5. Recommendations or warnings
        
        Respond in {language} language with proper legal terminology.
        Structure your response with clear headings and bullet points.
        """
        
        # Call OpenAI Vision API
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are a legal expert specializing in Indian law. Provide accurate, helpful legal analysis."},
                {"role": "user", "content": [
                    {"type": "text", "text": vision_prompt},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]}
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in GPT-4 Vision processing: {e}")
        return f"Error processing image: {str(e)}"

def build_drafting_prompt(request: DraftingRequest, template: dict) -> str:
    """Build the drafting prompt based on request and template"""
    
    # Extract key terms as formatted text
    key_terms_text = "\n".join([f"- {key}: {value}" for key, value in request.key_terms.items()])
    
    # Build the prompt
    prompt = template["prompt"].format(
        language=request.language,
        position=request.key_terms.get("position", "the specified position"),
        property_type=request.key_terms.get("property_type", "the property"),
        subject=request.subject,
        key_terms=key_terms_text
    )
    
    # Add additional context if provided
    if request.additional_context:
        prompt += f"\n\nAdditional Context: {request.additional_context}"
    
    # Add parties information
    if request.parties:
        parties_text = ", ".join(request.parties)
        prompt += f"\n\nParties involved: {parties_text}"
    
    return prompt

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Received chat request: {request.message}")
        print(f"Chat history length: {len(request.chatHistory)}")
        print(f"Language: {request.language}")
        print(f"Feature: {request.feature}")
        print(f"Has image: {request.image_url is not None}")
        print(f"Has document: {request.document_url is not None}")
        
        # Handle image analysis
        if request.image_url:
            print("Processing image with GPT-4 Vision...")
            image_response = await process_image_with_gpt4_vision(
                request.image_url, 
                request.message, 
                request.language
            )
            return ChatResponse(response=image_response)
        
        # Handle document analysis (similar to image)
        if request.document_url:
            print("Processing document with GPT-4 Vision...")
            document_response = await process_image_with_gpt4_vision(
                request.document_url, 
                request.message, 
                request.language
            )
            return ChatResponse(response=document_response)
        
        # Process chat history
        processed_history = []
        for msg in request.chatHistory:
            role = msg.get("role")
            content = msg.get("content")
            if role and content:
                processed_history.append({"role": role, "content": content})
            else:
                print(f"Warning: Invalid message format: {msg}")
        
        print(f"Chat history: {processed_history}")
        
        # Create multi-query chain
        multi_query_chain = createMultiQueryChain(MultiQuery, llm)
        
        # Generate multiple queries
        multi_query_resp = multi_query_chain.invoke({"user_query": request.message, "chat_history": processed_history})
        print(f"Multi-query response: {multi_query_resp}")
        
        # Check if document retrieval is required
        if multi_query_resp.get('documentRetrievalRequired', False):
            print("Document retrieval required - using vector database")
            
            # Get the queries from the response
            queries = multi_query_resp.get('generatedQueries', [])
            print(f"Generated queries: {queries}")
            
            # Retrieve documents for each query
            all_retrieved_docs = []
            for query in queries:
                docs = kb_retriever.invoke(query)
                print(f"Retrieved {len(docs)} documents for query: {query}")
                all_retrieved_docs.append(docs)
            
            # Rank documents using RRF
            ranked_documents = generateRRF(all_retrieved_docs)
            print(f"Ranked {len(ranked_documents)} documents after RRF")
            
            # Log document details for debugging
            for i, doc in enumerate(ranked_documents[:3]):
                print(f"Document {i+1} metadata: {doc.metadata}")
                print(f"Document {i+1} content preview: {doc.page_content[:100]}...")
            
            # Generate response with context
            print("Generating response with context...")
            resp = generateResponse(
                request.message, 
                ranked_documents, 
                processed_history,
                request.language  # Pass language to generateResponse
            )
            print(f"Generated response: {resp[:200]}...")
            
            # Extract sources with deduplication
            sources = []
            seen_sources = set()
            if ranked_documents:
                for doc in ranked_documents[:3]:  # Top 3 sources
                    source_name = None
                    if hasattr(doc, 'metadata'):
                        source_name = doc.metadata.get('source') or doc.metadata.get('file_path') or doc.metadata.get('filename')
                    if source_name:
                        # Clean the source name
                        source_name = source_name.replace('data/', '').replace('.pdf', '').replace('_', ' ')
                        if source_name not in seen_sources:
                            sources.append(source_name)
                            seen_sources.add(source_name)
                            print(f"Added source: {source_name}")
            
            print(f"Final sources being returned: {sources}")
            
            return ChatResponse(
                response=resp,
                sources=sources
            )
        else:
            print("No document retrieval required - but this appears to be a legal question")
            print("Generating response without context but providing general legal information")
            
            # Generate response without document retrieval but still provide legal guidance
            resp = generateResponse(
                request.message, 
                [], 
                processed_history,
                request.language  # Pass language to generateResponse
            )
            print(f"Generated response without context: {resp[:200]}...")
            
            return ChatResponse(
                response=resp,
                sources=[]
            )
            
    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/api/draft", response_model=DraftingResponse)
async def draft_document(request: DraftingRequest):
    try:
        print(f"Received drafting request for: {request.document_type}")
        print(f"Subject: {request.subject}")
        print(f"Language: {request.language}")
        
        # Get template for document type
        template = DRAFTING_TEMPLATES.get(request.document_type)
        if not template:
            raise HTTPException(status_code=400, detail=f"Unsupported document type: {request.document_type}")
        
        # Build drafting prompt
        drafting_prompt = build_drafting_prompt(request, template)
        print(f"Drafting prompt: {drafting_prompt[:200]}...")
        
        # Call OpenAI API for drafting
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert legal drafter specializing in Indian law. Create professional, legally sound documents with proper structure and formatting."},
                {"role": "user", "content": drafting_prompt}
            ],
            max_tokens=3000,
            temperature=0.3
        )
        
        # Process and structure the response
        drafted_document = response.choices[0].message.content
        print(f"Drafted document length: {len(drafted_document)} characters")
        
        return DraftingResponse(
            document=drafted_document,
            document_type=request.document_type,
            sections=template["sections"],
            language=request.language
        )
        
    except Exception as e:
        print(f"Error in drafting: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error drafting document: {str(e)}")

@app.get("/api/drafting-templates")
async def get_drafting_templates():
    """Get available drafting templates"""
    return {
        "templates": list(DRAFTING_TEMPLATES.keys()),
        "template_details": DRAFTING_TEMPLATES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
