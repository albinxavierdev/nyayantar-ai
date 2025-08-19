"use client";

import { useLanguage } from "@/contexts/LanguageContext";

const hindiContent = {
  chat: "चैट",
  judgements: "निर्णय",
  summarize: "सारांश",
  drafting: "मसौदा",
  pro: "प्रो"
};

const englishContent = {
  chat: "Chat",
  judgements: "Judgements",
  summarize: "Summarize",
  drafting: "Drafting",
  pro: "PRO"
};

interface FeatureTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function FeatureTabs({ activeTab, onTabChange }: FeatureTabsProps) {
  const { language } = useLanguage();
  const content = language === "hindi" ? hindiContent : englishContent;

  const tabs = [
    { id: "chat", label: content.chat, icon: "💬" },
    { id: "judgements", label: content.judgements, icon: "⚖️", pro: true },
    { id: "summarize", label: content.summarize, icon: "📝", pro: true },
    { id: "drafting", label: content.drafting, icon: "✍️", pro: true }
  ];

  return (
    <div className="flex space-x-1 bg-[#374151] rounded-lg p-1 mb-8">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === tab.id
              ? "bg-[#d97706] text-black"
              : "text-gray-300 hover:text-white hover:bg-[#4b5563]"
          }`}
        >
          <span>{tab.icon}</span>
          <span>{tab.label}</span>
          {tab.pro && (
            <span className="bg-black text-white text-xs px-1.5 py-0.5 rounded-full">
              {content.pro}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
