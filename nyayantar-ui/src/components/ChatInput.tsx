"use client";

import { useLanguage } from "@/contexts/LanguageContext";

const hindiContent = {
  placeholder: "भारतीय कानूनों और नियमों के बारे में न्यायंतर से पूछें...",
  promptsLibrary: "प्रॉम्प्ट्स लाइब्रेरी",
  send: "भेजें",
  disclaimer: "न्यायंतर.ai गलतियां कर सकता है। महत्वपूर्ण जानकारी की जांच करें"
};

const englishContent = {
  placeholder: "Ask Nyantar about Indian laws and regulations...",
  promptsLibrary: "Prompts Library",
  send: "Send",
  disclaimer: "Nyantar.ai can make mistakes. Check important info"
};

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export default function ChatInput({ value, onChange, onSubmit }: ChatInputProps) {
  const { language } = useLanguage();
  const content = language === "hindi" ? hindiContent : englishContent;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-2xl">
      <form onSubmit={onSubmit} className="relative">
        <div className="relative">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={content.placeholder}
            className="w-full bg-[#374151] border border-gray-600 rounded-2xl px-4 py-3 pr-12 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-[#d97706] focus:border-transparent"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '200px' }}
          />
          <button
            type="submit"
            disabled={!value.trim()}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#d97706] hover:bg-[#f59e0b] text-black p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
            </svg>
          </button>
        </div>
        <div className="flex items-center justify-between mt-2">
          <button
            type="button"
            className="text-sm text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <span>{content.promptsLibrary}</span>
          </button>
          <p className="text-xs text-gray-400 text-center">
            {content.disclaimer}
          </p>
        </div>
      </form>
    </div>
  );
}
