"""
AI Prompt Optimization for Document Generation
"""
from typing import Dict, List, Any, Optional
from .document_models import DocumentType
from .document_templates import get_template


class PromptOptimizer:
    """Service for optimizing AI prompts for better field extraction and document generation"""
    
    def __init__(self):
        self.optimized_prompts = self._load_optimized_prompts()
    
    def _load_optimized_prompts(self) -> Dict[DocumentType, Dict[str, str]]:
        """Load optimized prompts for each document type"""
        return {
            DocumentType.BAIL_APPLICATION: {
                "field_extraction": """
You are an expert legal assistant specializing in bail applications under Indian law. Your task is to extract relevant information from user input for creating a bail application.

CONTEXT: Bail applications in India require specific information under the Code of Criminal Procedure (CrPC) and Indian Penal Code (IPC).

EXTRACTION GUIDELINES:
1. **Applicant Information**: Extract full name, relationship to accused, contact details
2. **Case Details**: Extract case number, FIR number, police station, court details
3. **Offense Information**: Extract specific offense, IPC section, date of incident
4. **Legal Grounds**: Look for arguments supporting bail (non-flight risk, cooperation, health issues)
5. **Court Information**: Extract court name, address, judge details

RESPONSE FORMAT (JSON only):
{
    "extracted_fields": {
        "field_name": "extracted_value"
    },
    "confidence": 0.85,
    "next_question": "Conversational question for next missing field",
    "is_complete": false,
    "reasoning": "Brief explanation of extraction"
}

IMPORTANT: 
- Use exact field names from the template
- Convert dates to DD/MM/YYYY format
- Extract IPC sections accurately
- Be conservative with confidence scores
- Ask one question at a time
""",
                "next_question": """
Generate the next most important question to ask for a bail application. Consider:

1. **Priority Order**: Applicant name → Case details → Offense → Court info → Legal grounds
2. **Context Awareness**: Reference previously collected information
3. **Legal Relevance**: Explain why the information is needed
4. **Conversational Tone**: Be helpful and reassuring

QUESTION GUIDELINES:
- Ask for the most critical missing field
- Provide context about why it's needed
- Give examples if helpful
- Keep it conversational and supportive
""",
                "validation": """
Validate extracted information for a bail application. Check:

1. **Name Format**: Proper case, no special characters
2. **Case Numbers**: Valid format (alphanumeric)
3. **IPC Sections**: Valid section numbers
4. **Dates**: DD/MM/YYYY format
5. **Contact Info**: Valid phone/email format
6. **Addresses**: Complete with city, state, pincode

VALIDATION RULES:
- Names: Only letters, spaces, hyphens
- Case numbers: Alphanumeric, 3-20 characters
- IPC sections: Numbers only, 1-4 digits
- Dates: DD/MM/YYYY format
- Phone: +91 followed by 10 digits
- Email: Valid email format
"""
            },
            
            DocumentType.LEASE_AGREEMENT: {
                "field_extraction": """
You are an expert legal assistant specializing in lease agreements under Indian law. Extract information for creating a residential lease agreement.

CONTEXT: Lease agreements in India are governed by the Transfer of Property Act, 1882, and state-specific rent control laws.

EXTRACTION GUIDELINES:
1. **Party Information**: Landlord and tenant names, addresses, contact details
2. **Property Details**: Complete address, type, amenities
3. **Lease Terms**: Duration, rent amount, security deposit, due dates
4. **Legal Terms**: Notice periods, maintenance responsibilities, termination clauses
5. **Additional Terms**: Late fees, subletting restrictions, utilities

RESPONSE FORMAT (JSON only):
{
    "extracted_fields": {
        "field_name": "extracted_value"
    },
    "confidence": 0.85,
    "next_question": "Conversational question for next missing field",
    "is_complete": false,
    "reasoning": "Brief explanation of extraction"
}

IMPORTANT:
- Extract monetary amounts in numbers only
- Convert dates to DD/MM/YYYY format
- Ensure complete addresses
- Be specific about lease terms
""",
                "next_question": """
Generate the next question for a lease agreement. Priority order:

1. **Party Details**: Landlord and tenant information
2. **Property Information**: Address and details
3. **Financial Terms**: Rent, deposit, due dates
4. **Legal Terms**: Duration, notice periods, responsibilities

QUESTION STYLE:
- Be conversational and professional
- Explain the importance of each field
- Provide examples when helpful
- Reference Indian rental practices
""",
                "validation": """
Validate lease agreement information:

1. **Names**: Proper case, no special characters
2. **Addresses**: Complete with city, state, pincode
3. **Amounts**: Positive numbers only
4. **Dates**: DD/MM/YYYY format
5. **Phone Numbers**: +91 followed by 10 digits
6. **Email**: Valid email format
7. **Rent Amount**: Reasonable range (₹1000-₹500000)
8. **Security Deposit**: Typically 1-3 months rent
"""
            },
            
            DocumentType.POWER_OF_ATTORNEY: {
                "field_extraction": """
You are an expert legal assistant specializing in Power of Attorney documents under Indian law. Extract information for creating a POA.

CONTEXT: POAs in India are governed by the Power of Attorney Act, 1882, and the Indian Contract Act, 1872.

EXTRACTION GUIDELINES:
1. **Principal Information**: Name, address, age, identification
2. **Agent Information**: Name, address, relationship to principal
3. **Powers Granted**: Specific authorities and limitations
4. **Duration**: Effective dates, expiry, revocation terms
5. **Witness Information**: Names and addresses of witnesses
6. **Special Instructions**: Any specific conditions or limitations

RESPONSE FORMAT (JSON only):
{
    "extracted_fields": {
        "field_name": "extracted_value"
    },
    "confidence": 0.85,
    "next_question": "Conversational question for next missing field",
    "is_complete": false,
    "reasoning": "Brief explanation of extraction"
}

IMPORTANT:
- Be specific about powers granted
- Extract relationship between principal and agent
- Note any special conditions
- Ensure complete identification details
""",
                "next_question": """
Generate the next question for a Power of Attorney. Priority order:

1. **Principal Details**: Name, address, age
2. **Agent Details**: Name, address, relationship
3. **Powers**: Specific authorities to be granted
4. **Duration**: Effective dates and terms
5. **Witnesses**: Names and addresses

QUESTION STYLE:
- Be clear about legal implications
- Explain the importance of each field
- Use legal terminology appropriately
- Be conversational but professional
""",
                "validation": """
Validate POA information:

1. **Names**: Proper case, no special characters
2. **Addresses**: Complete with city, state, pincode
3. **Ages**: Valid numbers (18-100)
4. **Relationships**: Valid family/professional relationships
5. **Dates**: DD/MM/YYYY format
6. **Powers**: Clear, specific descriptions
7. **Contact Info**: Valid phone/email format
"""
            },
            
            DocumentType.WILL: {
                "field_extraction": """
You are an expert legal assistant specializing in Will and Testament documents under Indian law. Extract information for creating a Last Will and Testament.

CONTEXT: Wills in India are governed by the Indian Succession Act, 1925, and Hindu Succession Act, 1956.

EXTRACTION GUIDELINES:
1. **Testator Information**: Name, address, age, marital status
2. **Executor Information**: Name, address, relationship
3. **Beneficiaries**: Names, relationships, shares
4. **Assets**: Description of property, bank accounts, investments
5. **Special Bequests**: Specific gifts or conditions
6. **Guardian Information**: For minor children
7. **Witness Information**: Names and addresses

RESPONSE FORMAT (JSON only):
{
    "extracted_fields": {
        "field_name": "extracted_value"
    },
    "confidence": 0.85,
    "next_question": "Conversational question for next missing field",
    "is_complete": false,
    "reasoning": "Brief explanation of extraction"
}

IMPORTANT:
- Be sensitive about family matters
- Extract detailed asset information
- Note special conditions or bequests
- Ensure complete beneficiary details
""",
                "next_question": """
Generate the next question for a Will. Priority order:

1. **Testator Details**: Name, address, age
2. **Executor Information**: Name and details
3. **Beneficiaries**: Family members and shares
4. **Assets**: Property and financial details
5. **Special Instructions**: Specific bequests or conditions

QUESTION STYLE:
- Be sensitive and respectful
- Explain legal implications clearly
- Use appropriate legal terminology
- Be conversational but professional
""",
                "validation": """
Validate Will information:

1. **Names**: Proper case, no special characters
2. **Ages**: Valid numbers (18-100)
3. **Relationships**: Valid family relationships
4. **Addresses**: Complete with city, state, pincode
5. **Asset Descriptions**: Clear and specific
6. **Shares**: Valid percentages or fractions
7. **Contact Info**: Valid phone/email format
"""
            },
            
            DocumentType.CEASE_AND_DESIST: {
                "field_extraction": """
You are an expert legal assistant specializing in Cease and Desist letters under Indian law. Extract information for creating a cease and desist letter.

CONTEXT: Cease and desist letters in India are governed by the Copyright Act, 1957, and other relevant intellectual property laws.

EXTRACTION GUIDELINES:
1. **Client Information**: Name, business details, contact information
2. **Law Firm Details**: Name, address, contact information
3. **Recipient Information**: Name, address, business details
4. **Copyright Information**: Description of copyrighted material
5. **Infringement Details**: Specific acts of infringement
6. **Demands**: Specific actions required, deadlines
7. **Legal Consequences**: Potential legal action

RESPONSE FORMAT (JSON only):
{
    "extracted_fields": {
        "field_name": "extracted_value"
    },
    "confidence": 0.85,
    "next_question": "Conversational question for next missing field",
    "is_complete": false,
    "reasoning": "Brief explanation of extraction"
}

IMPORTANT:
- Be specific about copyright details
- Extract clear infringement descriptions
- Note specific demands and deadlines
- Ensure complete contact information
""",
                "next_question": """
Generate the next question for a cease and desist letter. Priority order:

1. **Client Information**: Name and business details
2. **Law Firm Details**: Contact information
3. **Recipient Information**: Name and address
4. **Copyright Details**: Description of protected material
5. **Infringement Details**: Specific acts of violation
6. **Demands**: Required actions and deadlines

QUESTION STYLE:
- Be professional and firm
- Explain legal implications
- Use appropriate legal terminology
- Be clear about requirements
""",
                "validation": """
Validate cease and desist information:

1. **Names**: Proper case, no special characters
2. **Addresses**: Complete with city, state, pincode
3. **Business Names**: Valid business entity names
4. **Copyright Descriptions**: Clear and specific
5. **Dates**: DD/MM/YYYY format
6. **Contact Info**: Valid phone/email format
7. **Deadlines**: Future dates only
"""
            }
        }
    
    def get_optimized_prompt(
        self, 
        document_type: DocumentType, 
        prompt_type: str
    ) -> str:
        """Get optimized prompt for a specific document type and use case"""
        if document_type in self.optimized_prompts:
            return self.optimized_prompts[document_type].get(prompt_type, "")
        
        # Fallback to template prompts
        template = get_template(document_type)
        if template and prompt_type in template.ai_prompts:
            return template.ai_prompts[prompt_type]
        
        return ""
    
    def get_enhanced_field_extraction_prompt(
        self, 
        document_type: DocumentType, 
        user_input: str, 
        current_fields: Dict[str, Any], 
        question_index: int
    ) -> str:
        """Get enhanced field extraction prompt with context"""
        base_prompt = self.get_optimized_prompt(document_type, "field_extraction")
        
        if not base_prompt:
            return ""
        
        # Add dynamic context
        context = f"""
CURRENT EXTRACTION CONTEXT:
- Document Type: {document_type.value.replace('_', ' ').title()}
- User Input: "{user_input}"
- Question Index: {question_index}
- Already Collected: {current_fields}

TASK: Extract relevant information from the user input and determine the next question to ask.
"""
        
        return base_prompt + context
    
    def get_enhanced_next_question_prompt(
        self, 
        document_type: DocumentType, 
        missing_fields: List[str], 
        current_progress: int
    ) -> str:
        """Get enhanced next question prompt with context"""
        base_prompt = self.get_optimized_prompt(document_type, "next_question")
        
        if not base_prompt:
            return ""
        
        # Add dynamic context
        context = f"""
CURRENT QUESTION CONTEXT:
- Document Type: {document_type.value.replace('_', ' ').title()}
- Missing Fields: {missing_fields}
- Current Progress: {current_progress}%

TASK: Generate the most appropriate next question to ask the user.
"""
        
        return base_prompt + context
    
    def get_enhanced_validation_prompt(
        self, 
        document_type: DocumentType, 
        field_name: str, 
        field_value: Any
    ) -> str:
        """Get enhanced validation prompt with context"""
        base_prompt = self.get_optimized_prompt(document_type, "validation")
        
        if not base_prompt:
            return ""
        
        # Add dynamic context
        context = f"""
VALIDATION CONTEXT:
- Document Type: {document_type.value.replace('_', ' ').title()}
- Field Name: {field_name}
- Field Value: {field_value}

TASK: Validate the field value and provide feedback.
"""
        
        return base_prompt + context
    
    def analyze_prompt_performance(
        self, 
        document_type: DocumentType, 
        prompt_type: str, 
        success_rate: float, 
        avg_confidence: float
    ) -> Dict[str, Any]:
        """Analyze prompt performance and suggest improvements"""
        analysis = {
            "document_type": document_type.value,
            "prompt_type": prompt_type,
            "success_rate": success_rate,
            "avg_confidence": avg_confidence,
            "performance_rating": self._calculate_performance_rating(success_rate, avg_confidence),
            "suggestions": self._generate_improvement_suggestions(success_rate, avg_confidence)
        }
        
        return analysis
    
    def _calculate_performance_rating(self, success_rate: float, avg_confidence: float) -> str:
        """Calculate performance rating based on success rate and confidence"""
        if success_rate >= 0.9 and avg_confidence >= 0.8:
            return "Excellent"
        elif success_rate >= 0.8 and avg_confidence >= 0.7:
            return "Good"
        elif success_rate >= 0.7 and avg_confidence >= 0.6:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_improvement_suggestions(
        self, 
        success_rate: float, 
        avg_confidence: float
    ) -> List[str]:
        """Generate improvement suggestions based on performance metrics"""
        suggestions = []
        
        if success_rate < 0.8:
            suggestions.append("Consider adding more specific examples in the prompt")
            suggestions.append("Review field extraction patterns for common failures")
        
        if avg_confidence < 0.7:
            suggestions.append("Add more detailed validation rules")
            suggestions.append("Provide clearer field descriptions")
        
        if success_rate < 0.9:
            suggestions.append("Consider using few-shot examples")
            suggestions.append("Review and update prompt templates")
        
        return suggestions
