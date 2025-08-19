"use client";

import { useState, useRef, useEffect } from 'react';
import { useLanguage } from "@/contexts/LanguageContext";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
  followUpQuestions?: string[];
  imageUrl?: string;
}

interface DraftingForm {
  document_type: string;
  subject: string;
  parties: string[];
  key_terms: { [key: string]: string };
  additional_context: string;
}

const hindiContent = {
  welcome: "न्यायंतर AI में आपका स्वागत है",
  subtitle: "आपका AI से संचालित कानूनी विशेषज्ञ। टेक्स्ट, छवि, या दस्तावेज़ के साथ कानूनी प्रश्न पूछें।",
  chat: "चैट",
  image: "छवि",
  document: "दस्तावेज़",
  draft: "मसौदा",
  takePhoto: "फोटो लें",
  uploadImage: "छवि अपलोड करें",
  uploadDocument: "दस्तावेज़ अपलोड करें",
  analyze: "विश्लेषण करें",
  generateDraft: "मसौदा तैयार करें",
  documentType: "दस्तावेज़ प्रकार",
  subject: "विषय",
  parties: "पक्षकार",
  keyTerms: "मुख्य शर्तें",
  additionalContext: "अतिरिक्त संदर्भ",
  employmentContract: "रोजगार अनुबंध",
  rentalAgreement: "किराया समझौता",
  legalNotice: "कानूनी नोटिस",
  businessContract: "व्यवसाय अनुबंध",
  addParty: "पक्षकार जोड़ें",
  addTerm: "शर्त जोड़ें",
  thinking: "न्यायंतर सोच रहा है...",
  errorMessage: "क्षमा करें, आपके अनुरोध को संसाधित करते समय एक त्रुटि आई। कृपया पुनः प्रयास करें।",
  disclaimer: "न्यायंतर.ai गलतियां कर सकता है। महत्वपूर्ण जानकारी की जांच करें"
};

const englishContent = {
  welcome: "Welcome to Nyantar AI",
  subtitle: "Your legal expert powered by AI. Ask legal questions with text, image, or document.",
  chat: "Chat",
  image: "Image",
  document: "Document",
  draft: "Draft",
  takePhoto: "Take Photo",
  uploadImage: "Upload Image",
  uploadDocument: "Upload Document",
  analyze: "Analyze",
  generateDraft: "Generate Draft",
  documentType: "Document Type",
  subject: "Subject",
  parties: "Parties",
  keyTerms: "Key Terms",
  additionalContext: "Additional Context",
  employmentContract: "Employment Contract",
  rentalAgreement: "Rental Agreement",
  legalNotice: "Legal Notice",
  businessContract: "Business Contract",
  addParty: "Add Party",
  addTerm: "Add Term",
  thinking: "Nyantar is thinking...",
  errorMessage: "Sorry, I encountered an error while processing your request. Please try again.",
  disclaimer: "Nyantar.ai can make mistakes. Check important info"
};

export default function MultiModalChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'image' | 'document' | 'draft'>('chat');
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [draftingForm, setDraftingForm] = useState<DraftingForm>({
    document_type: 'employment_contract',
    subject: '',
    parties: [''],
    key_terms: {},
    additional_context: ''
  });
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { language } = useLanguage();
  const content = language === "hindi" ? hindiContent : englishContent;

  const documentTypes = [
    { value: 'employment_contract', label: content.employmentContract },
    { value: 'rental_agreement', label: content.rentalAgreement },
    { value: 'legal_notice', label: content.legalNotice },
    { value: 'business_contract', label: content.businessContract }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraOpen(true);
      }
    } catch (error) {
      console.error('Error opening camera:', error);
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        context.drawImage(videoRef.current, 0, 0);
        const imageData = canvasRef.current.toDataURL('image/jpeg', 0.8);
        setCapturedImage(imageData);
        setIsCameraOpen(false);
        // Stop the video stream
        const stream = videoRef.current.srcObject as MediaStream;
        stream?.getTracks().forEach(track => track.stop());
      }
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() && !capturedImage && !uploadedFile) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
      imageUrl: capturedImage || undefined
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInputValue('');

    try {
      let imageUrl = null;
      if (capturedImage) {
        imageUrl = capturedImage;
      } else if (uploadedFile) {
        // Convert file to base64
        const reader = new FileReader();
        reader.onload = async () => {
          const base64 = reader.result as string;
          await sendMessage(inputValue, base64);
        };
        reader.readAsDataURL(uploadedFile);
        return;
      }

      await sendMessage(inputValue, imageUrl);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: content.errorMessage,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      setCapturedImage(null);
      setUploadedFile(null);
    }
  };

  const sendMessage = async (message: string, imageUrl?: string | null) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        chatHistory: messages.map(msg => ({ role: msg.role, content: msg.content })),
        feature: 'chat',
        language,
        image_url: imageUrl
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const data = await response.json();
    
    const assistantMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: data.response,
      timestamp: new Date(),
      sources: data.sources
    };

    setMessages(prev => [...prev, assistantMessage]);
  };

  const handleDraftingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!draftingForm.subject.trim()) return;

    setIsLoading(true);

    try {
      const response = await fetch('/api/draft', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...draftingForm,
          language
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate draft');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `**Generated ${draftingForm.document_type.replace('_', ' ')}:**\n\n${data.document}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error generating draft:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: content.errorMessage,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const addParty = () => {
    setDraftingForm(prev => ({
      ...prev,
      parties: [...prev.parties, '']
    }));
  };

  const updateParty = (index: number, value: string) => {
    setDraftingForm(prev => ({
      ...prev,
      parties: prev.parties.map((party, i) => i === index ? value : party)
    }));
  };

  const addKeyTerm = () => {
    const key = prompt('Enter key term name:');
    const value = prompt('Enter key term value:');
    if (key && value) {
      setDraftingForm(prev => ({
        ...prev,
        key_terms: { ...prev.key_terms, [key]: value }
      }));
    }
  };

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-[#1a1a1a] sticky top-0 z-10">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-[#d97706] rounded-lg flex items-center justify-center">
            <span className="text-black font-bold text-sm">N</span>
          </div>
          <span className="text-xl font-semibold">Nyantar AI</span>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-700">
        {(['chat', 'image', 'document', 'draft'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-[#d97706] text-black'
                : 'text-gray-300 hover:text-white'
            }`}
          >
            {content[tab as keyof typeof content]}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-[#d97706] rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-black font-bold text-2xl">N</span>
              </div>
              <h2 className="text-2xl font-bold mb-2">{content.welcome}</h2>
              <p className="text-gray-400 mb-6">{content.subtitle}</p>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className="space-y-4">
              {/* User Message */}
              {message.role === 'user' && (
                <div className="flex justify-end">
                  <div className="max-w-[80%] bg-[#d97706] text-black rounded-2xl px-4 py-3">
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    {message.imageUrl && (
                      <img 
                        src={message.imageUrl} 
                        alt="Uploaded" 
                        className="mt-2 rounded-lg max-w-full h-auto"
                      />
                    )}
                  </div>
                </div>
              )}

              {/* Assistant Message */}
              {message.role === 'assistant' && (
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-[#d97706] rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-black font-bold text-sm">N</span>
                  </div>
                  <div className="flex-1 bg-[#374151] rounded-2xl px-4 py-3">
                    <div className="whitespace-pre-wrap prose prose-invert max-w-none">
                      {message.content}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-[#d97706] rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-black font-bold text-sm">N</span>
              </div>
              <div className="bg-[#374151] rounded-2xl px-4 py-3">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>{content.thinking}</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-700 p-6">
          {activeTab === 'chat' && (
            <form onSubmit={handleSubmit} className="relative">
              <div className="relative">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={language === "hindi" ? "कानूनी प्रश्न पूछें..." : "Ask a legal question..."}
                  className="w-full bg-[#374151] border border-gray-600 rounded-2xl px-4 py-3 pr-12 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-[#d97706] focus:border-transparent"
                  rows={1}
                  style={{ minHeight: '48px', maxHeight: '200px' }}
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || isLoading}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#d97706] hover:bg-[#f59e0b] text-black p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 2L11 13"/>
                    <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
                  </svg>
                </button>
              </div>
            </form>
          )}

          {activeTab === 'image' && (
            <div className="space-y-4">
              {!capturedImage && !isCameraOpen && (
                <div className="flex space-x-4">
                  <button
                    onClick={openCamera}
                    className="bg-[#d97706] hover:bg-[#f59e0b] text-black px-4 py-2 rounded-lg transition-colors"
                  >
                    {content.takePhoto}
                  </button>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-[#374151] hover:bg-[#4b5563] text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    {content.uploadImage}
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
              )}

              {isCameraOpen && (
                <div className="space-y-4">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="w-full rounded-lg"
                  />
                  <canvas ref={canvasRef} className="hidden" />
                  <div className="flex space-x-4">
                    <button
                      onClick={capturePhoto}
                      className="bg-[#d97706] hover:bg-[#f59e0b] text-black px-4 py-2 rounded-lg transition-colors"
                    >
                      {content.takePhoto}
                    </button>
                    <button
                      onClick={() => setIsCameraOpen(false)}
                      className="bg-[#374151] hover:bg-[#4b5563] text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {(capturedImage || uploadedFile) && (
                <div className="space-y-4">
                  <img
                    src={capturedImage || (uploadedFile ? URL.createObjectURL(uploadedFile) : '')}
                    alt="Captured"
                    className="w-full rounded-lg max-h-64 object-contain"
                  />
                  <form onSubmit={handleSubmit} className="relative">
                    <div className="relative">
                      <textarea
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder={language === "hindi" ? "इस छवि के बारे में कानूनी प्रश्न पूछें..." : "Ask a legal question about this image..."}
                        className="w-full bg-[#374151] border border-gray-600 rounded-2xl px-4 py-3 pr-12 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-[#d97706] focus:border-transparent"
                        rows={1}
                        style={{ minHeight: '48px', maxHeight: '200px' }}
                        disabled={isLoading}
                      />
                      <button
                        type="submit"
                        disabled={!inputValue.trim() || isLoading}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#d97706] hover:bg-[#f59e0b] text-black p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {content.analyze}
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          )}

          {activeTab === 'document' && (
            <div className="space-y-4">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-[#d97706] hover:bg-[#f59e0b] text-black px-4 py-2 rounded-lg transition-colors"
              >
                {content.uploadDocument}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
              {uploadedFile && (
                <div className="space-y-4">
                  <div className="bg-[#374151] p-4 rounded-lg">
                    <p className="text-sm text-gray-300">{uploadedFile.name}</p>
                  </div>
                  <form onSubmit={handleSubmit} className="relative">
                    <div className="relative">
                      <textarea
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder={language === "hindi" ? "इस दस्तावेज़ के बारे में कानूनी प्रश्न पूछें..." : "Ask a legal question about this document..."}
                        className="w-full bg-[#374151] border border-gray-600 rounded-2xl px-4 py-3 pr-12 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-[#d97706] focus:border-transparent"
                        rows={1}
                        style={{ minHeight: '48px', maxHeight: '200px' }}
                        disabled={isLoading}
                      />
                      <button
                        type="submit"
                        disabled={!inputValue.trim() || isLoading}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#d97706] hover:bg-[#f59e0b] text-black p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {content.analyze}
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          )}

          {activeTab === 'draft' && (
            <form onSubmit={handleDraftingSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">{content.documentType}</label>
                <select
                  value={draftingForm.document_type}
                  onChange={(e) => setDraftingForm(prev => ({ ...prev, document_type: e.target.value }))}
                  className="w-full bg-[#374151] border border-gray-600 rounded-lg px-3 py-2 text-white"
                >
                  {documentTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{content.subject}</label>
                <input
                  type="text"
                  value={draftingForm.subject}
                  onChange={(e) => setDraftingForm(prev => ({ ...prev, subject: e.target.value }))}
                  className="w-full bg-[#374151] border border-gray-600 rounded-lg px-3 py-2 text-white"
                  placeholder={language === "hindi" ? "दस्तावेज़ का विषय..." : "Document subject..."}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{content.parties}</label>
                {draftingForm.parties.map((party, index) => (
                  <input
                    key={index}
                    type="text"
                    value={party}
                    onChange={(e) => updateParty(index, e.target.value)}
                    className="w-full bg-[#374151] border border-gray-600 rounded-lg px-3 py-2 text-white mb-2"
                    placeholder={language === "hindi" ? `पक्षकार ${index + 1}...` : `Party ${index + 1}...`}
                  />
                ))}
                <button
                  type="button"
                  onClick={addParty}
                  className="text-[#d97706] hover:text-[#f59e0b] text-sm"
                >
                  {content.addParty}
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{content.keyTerms}</label>
                {Object.entries(draftingForm.key_terms).map(([key, value]) => (
                  <div key={key} className="flex space-x-2 mb-2">
                    <input
                      type="text"
                      value={key}
                      readOnly
                      className="flex-1 bg-[#374151] border border-gray-600 rounded-lg px-3 py-2 text-white"
                    />
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => setDraftingForm(prev => ({
                        ...prev,
                        key_terms: { ...prev.key_terms, [key]: e.target.value }
                      }))}
                      className="flex-1 bg-[#374151] border border-gray-600 rounded-lg px-3 py-2 text-white"
                    />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addKeyTerm}
                  className="text-[#d97706] hover:text-[#f59e0b] text-sm"
                >
                  {content.addTerm}
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{content.additionalContext}</label>
                <textarea
                  value={draftingForm.additional_context}
                  onChange={(e) => setDraftingForm(prev => ({ ...prev, additional_context: e.target.value }))}
                  className="w-full bg-[#374151] border border-gray-600 rounded-lg px-3 py-2 text-white"
                  rows={3}
                  placeholder={language === "hindi" ? "अतिरिक्त जानकारी..." : "Additional context..."}
                />
              </div>

              <button
                type="submit"
                disabled={!draftingForm.subject.trim() || isLoading}
                className="w-full bg-[#d97706] hover:bg-[#f59e0b] text-black py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {content.generateDraft}
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
