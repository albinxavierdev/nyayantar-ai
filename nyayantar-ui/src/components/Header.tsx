"use client";

import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";

const hindiContent = {
  brand: "न्यायंतर AI",
  about: "हमारे बारे में",
  startChat: "चैट शुरू करें"
};

const englishContent = {
  brand: "Nyantar AI",
  about: "About",
  startChat: "Start Chat"
};

export default function Header() {
  const { language, setLanguage } = useLanguage();
  const content = language === "hindi" ? hindiContent : englishContent;

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-[#1a1a1a] sticky top-0 z-10">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-[#d97706] rounded-lg flex items-center justify-center">
          <span className="text-black font-bold text-sm">N</span>
        </div>
        <span className="text-xl font-semibold">{content.brand}</span>
      </div>
      <div className="flex items-center space-x-4">
        {/* Language Switcher */}
        <div className="flex items-center space-x-2 bg-[#374151] rounded-lg p-1">
          <button
            onClick={() => setLanguage("hindi")}
            className={`px-3 py-1 rounded-md text-sm transition-colors ${
              language === "hindi"
                ? "bg-[#d97706] text-black"
                : "text-gray-300 hover:text-white"
            }`}
          >
            हिंदी
          </button>
          <button
            onClick={() => setLanguage("english")}
            className={`px-3 py-1 rounded-md text-sm transition-colors ${
              language === "english"
                ? "bg-[#d97706] text-black"
                : "text-gray-300 hover:text-white"
            }`}
          >
            English
          </button>
        </div>
        <Button variant="outline" size="sm">
          {content.about}
        </Button>
        <Button className="bg-[#d97706] hover:bg-[#f59e0b] text-black">
          {content.startChat}
        </Button>
      </div>
    </header>
  );
}
