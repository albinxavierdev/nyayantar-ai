## set up environment
## set up environment
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['COHERE_API_KEY'] = os.getenv("COHERE_API_KEY")

## langchain dependencies
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
# from langchain_cohere import ChatCohere
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from langchain.load import loads, dumps

## other dependencies
from typing import List
import time
import traceback


## supress langchain warning
import warnings
from langchain_core._api import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)

## setting up file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "data")
persistent_directory = os.path.join(current_dir, "data-ingestion-local")

## instantiate embedding model
embedF = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

## load local vector DB
vectorDB = Chroma(embedding_function=embedF, persist_directory=persistent_directory)

## set up retriever
kb_retriever = vectorDB.as_retriever(search_type="similarity",search_kwargs={"k": 5})

## initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.15)

## main RAG prompt template
with open("prompts/mainRAG-prompt.md", "r", encoding="utf-8") as f:
    mainRAGPrompt = f.read()

## multiquery schema
class MultiQuery(BaseModel):
    documentRetrievalRequired: bool = Field(
        default=False, 
        description="Flag indicating whether the user query requires document retrieval from the knowledge base. Set to False for conversational queries like greetings, confirmations, or chitchat that don't need external information."
    )
    generatedQueries: List[str] = Field(
        default=[], 
        description="List of semantically equivalent query variations for improved retrieval coverage. Empty list if documentRetrievalRequired is False. Contains only the original query if it's straightforward, or 5 alternative phrasings if the query is complex/ambiguous."
    )

def createMultiQueryChain(output_pydantic_object, llm):
    # llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.15)
    with open("prompts/multiQuery-prompt.md", "r", encoding="utf-8") as f:
        template = f.read()
    parser = JsonOutputParser(pydantic_object=output_pydantic_object)
    prompt = PromptTemplate(
        template=template,
        input_variables=["chat_history", "user_query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm | parser
    return chain

def generateRRF(all_docs: List[List[Document]], k: int = 60) -> List[Document]:
    rrf_scores = dict()
    for docs in all_docs:
        for rank, doc in enumerate(docs, start=1):
            rrf_rank = 1/(k+rank)
            rrf_scores[dumps(doc)] = rrf_scores.get(dumps(doc), 0) + rrf_rank
    sorted_rrf_score = sorted(rrf_scores.items(), key=(lambda x: x[1]), reverse=True)
    best_docs = [loads(doc) for doc, _ in sorted_rrf_score][:3] ## only top 3 documents
    return best_docs

def generateResponse(user_query, documents, chat_history, language="english"):
    """
    Generate a response based on user query, retrieved documents, and chat history.
    
    Args:
        user_query (str): The user's question
        documents (list): Retrieved documents from vector database
        chat_history (list): Previous conversation history
        language (str): Language preference ("hindi" or "english")
    
    Returns:
        str: Generated response
    """
    try:
        print(f"generateResponse called with language: {language}")
        print(f"Number of documents: {len(documents)}")
        
        # Load the main RAG prompt
        with open("prompts/mainRAG-prompt.md", "r", encoding="utf-8") as f:
            main_prompt = f.read()
        
        # Add language instruction to the prompt
        language_instruction = ""
        if language == "hindi":
            language_instruction = """

CRITICAL: You MUST respond ENTIRELY in Hindi (हिंदी) language. This is MANDATORY.
- All headers must be in Hindi
- All explanations must be in Hindi  
- All examples must be in Hindi
- All disclaimers must be in Hindi
- Use proper Hindi legal terminology (कानूनी शब्दावली)
- NO English text allowed in the response
- The response must be 100% in Hindi

यह एक अनिवार्य आवश्यकता है - आपको पूरी तरह से हिंदी में जवाब देना होगा।"""
        else:
            language_instruction = """

CRITICAL: You MUST respond ENTIRELY in English language. This is MANDATORY.
- All headers must be in English
- All explanations must be in English
- All examples must be in English
- All disclaimers must be in English
- Use proper legal English terminology
- NO Hindi text allowed in the response
- The response must be 100% in English

This is a mandatory requirement - you must respond completely in English."""
        
        main_prompt += language_instruction
        
        # Prepare context from documents
        context = ""
        if documents:
            context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(documents)])
            print(f"Context length: {len(context)} characters")
        else:
            # Even without specific documents, provide general legal guidance
            context = "No specific legal documents are available for this query, but I can provide general legal information based on legal principles and knowledge."
        
        # Prepare chat history context
        history_context = ""
        if chat_history:
            history_context = "\n\nPrevious conversation:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                role = "User" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "")
                history_context += f"{role}: {content}\n"
            print(f"History context length: {len(history_context)} characters")
        else:
            history_context = "No previous conversation history."
        
        # Create the full prompt with proper variable substitution
        full_prompt = main_prompt.replace("{user_query}", user_query)
        full_prompt = full_prompt.replace("{context}", context)
        full_prompt = full_prompt.replace("{chat_history}", history_context)
        full_prompt = full_prompt.replace("{language}", language)
        
        print(f"Full prompt length: {len(full_prompt)} characters")
        
        # Generate response using OpenAI
        print("Calling OpenAI API...")
        response = llm.invoke(full_prompt)
        print(f"OpenAI response received, length: {len(response.content)} characters")
        
        # Post-process the response to ensure proper formatting
        formatted_response = response.content.strip()
        
        # Language verification and enforcement
        if language == "hindi":
            # Check if response contains English text and replace with Hindi equivalents
            if "Introduction:" in formatted_response:
                formatted_response = formatted_response.replace("Introduction:", "**परिचय:**")
            if "Key Provisions:" in formatted_response:
                formatted_response = formatted_response.replace("Key Provisions:", "**मुख्य प्रावधान:**")
            if "Scope and Application:" in formatted_response:
                formatted_response = formatted_response.replace("Scope and Application:", "**कार्यक्षेत्र और अनुप्रयोग:**")
            if "Procedures and Requirements:" in formatted_response:
                formatted_response = formatted_response.replace("Procedures and Requirements:", "**प्रक्रियाएं और आवश्यकताएं:**")
            if "Important Considerations:" in formatted_response:
                formatted_response = formatted_response.replace("Important Considerations:", "**महत्वपूर्ण विचार:**")
            if "Conclusion:" in formatted_response:
                formatted_response = formatted_response.replace("Conclusion:", "**निष्कर्ष:**")
            if "Legal Disclaimer:" in formatted_response:
                formatted_response = formatted_response.replace("Legal Disclaimer:", "**कानूनी अस्वीकरण:**")
            
            # Replace common English legal terms with Hindi equivalents
            english_to_hindi_replacements = {
                "This information is provided for educational purposes only": "यह जानकारी केवल शैक्षिक उद्देश्यों के लिए प्रदान की गई है",
                "should not be construed as legal advice": "और इसे कानूनी सलाह नहीं माना जाना चाहिए",
                "For specific legal matters": "विशिष्ट कानूनी मामलों के लिए",
                "please consult with a qualified legal professional": "कृपया एक योग्य कानूनी पेशेवर से परामर्श करें",
                "Sources:": "स्रोत:",
                "Follow-up questions:": "अगले प्रश्न:"
            }
            
            for english, hindi in english_to_hindi_replacements.items():
                formatted_response = formatted_response.replace(english, hindi)
        
        # Ensure the response has proper structure
        if not formatted_response.startswith("**") and not formatted_response.startswith("#"):
            # Add basic structure if missing
            if language == "hindi":
                formatted_response = f"**परिचय:**\n{formatted_response}\n\n**कानूनी अस्वीकरण:**\n*यह जानकारी केवल शैक्षिक उद्देश्यों के लिए प्रदान की गई है और इसे कानूनी सलाह नहीं माना जाना चाहिए। विशिष्ट कानूनी मामलों के लिए, कृपया एक योग्य कानूनी पेशेवर से परामर्श करें।*"
            else:
                formatted_response = f"**Introduction:**\n{formatted_response}\n\n**Legal Disclaimer:**\n*This information is provided for educational purposes only and should not be construed as legal advice. For specific legal matters, please consult with a qualified legal professional.*"
        
        # Final check: Ensure the response doesn't refuse to answer legal questions
        refusal_phrases = [
            "i can only help with legal research questions",
            "i can only help with legal research",
            "please ask me about legal topics",
            "i cannot help with this",
            "i don't have information about this"
        ]
        
        if any(phrase in formatted_response.lower() for phrase in refusal_phrases):
            # If response refuses to answer, provide a helpful response instead
            if language == "hindi":
                formatted_response = f"**परिचय:**\nमैं आपके कानूनी प्रश्न का उत्तर देने में आपकी सहायता कर सकता हूं। यह एक सामान्य कानूनी विषय है जिसके बारे में मैं आपको जानकारी प्रदान कर सकता हूं।\n\n**मुख्य जानकारी:**\n{user_query} के बारे में सामान्य कानूनी जानकारी यहां उपलब्ध है। कृपया ध्यान दें कि यह सामान्य जानकारी है और विशिष्ट विवरण भिन्न हो सकते हैं।\n\n**कानूनी अस्वीकरण:**\n*यह जानकारी केवल शैक्षिक उद्देश्यों के लिए प्रदान की गई है और इसे कानूनी सलाह नहीं माना जाना चाहिए। विशिष्ट कानूनी मामलों के लिए, कृपया एक योग्य कानूनी पेशेवर से परामर्श करें।*"
            else:
                formatted_response = f"**Introduction:**\nI can help you with your legal question. This is a general legal topic about which I can provide you with information.\n\n**Key Information:**\nGeneral legal information about {user_query} is available here. Please note that this is general information and specific details may vary.\n\n**Legal Disclaimer:**\n*This information is provided for educational purposes only and should not be construed as legal advice. For specific legal matters, please consult with a qualified legal professional.*"
        
        return formatted_response
        
    except Exception as e:
        print(f"Error generating response: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        if language == "hindi":
            return "क्षमा करें, आपके प्रश्न का उत्तर देने में एक त्रुटि आई। कृपया पुनः प्रयास करें।\n\n**कानूनी अस्वीकरण:**\n*यह जानकारी केवल शैक्षिक उद्देश्यों के लिए प्रदान की गई है और इसे कानूनी सलाह नहीं माना जाना चाहिए।*"
        else:
            return "Sorry, I encountered an error while generating a response. Please try again.\n\n**Legal Disclaimer:**\n*This information is provided for educational purposes only and should not be construed as legal advice.*"

if __name__=="__main__":
    ## initial chat state
    chat_history = []
    welcome_message = "Welcome to the Legal Assistant Bot. How can I help you today? Write `exit` to quit."
    chat_history.append(AIMessage(content=welcome_message))
    
    ## print welcome message
    print("\033[1m> AI:\033[0m ", end="")
    for letter in welcome_message:
        print(letter, flush=True, end="")
        time.sleep(0.03)
    

    ### ----------------------------------------------------------------------------------------------------
    
    ## retrieved docs
    
    while True:
        try:
            retrieved_docs = []

            ## user input
            print("\n\033[1m> Human:\033[0m ", end="")
            user_query = input().strip()
            
            ## check if user wants to exit
            if user_query.lower().strip() == "exit":
                bye_message = "Chat ended! See ya."
                print("\033[1m> AI:\033[0m ", end="")
                for letter in bye_message:
                    print(letter, flush=True, end="")
                    time.sleep(0.03)
                break

            ## multiquery
            chain = createMultiQueryChain(output_pydantic_object=MultiQuery, llm=llm)
            resp = chain.invoke({"chat_history": chat_history, "user_query": user_query})
            chat_history.append(HumanMessage(content=user_query))

            if resp['documentRetrievalRequired']:
                ## retrieve documents for each query
                multiQueries = resp['generatedQueries']
                for query in multiQueries:
                    retrieved_docs.append(kb_retriever.invoke(query))
                
                ranked_documents = generateRRF(retrieved_docs)
                ai_resp = generateResponse(user_query=user_query, documents=ranked_documents, chat_history=chat_history)
            else:
                ai_resp = generateResponse(user_query=user_query, documents=[], chat_history=chat_history)
            
            ## print AI response
            print("\033[1m> AI:\033[0m ", end="")
            for letter in ai_resp:
                print(letter, flush=True, end="")
                time.sleep(0.03)
            
            ## append AI response to chat history
            chat_history.append(AIMessage(content=ai_resp))
        except KeyboardInterrupt:
            print("\n\n[ALERT] ^C: Keyboard Interruption detected. Session Terminated!!")
            break