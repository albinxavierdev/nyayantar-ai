"use client";

import { useLanguage } from "@/contexts/LanguageContext";

const hindiContent = {
  privacy: "गोपनीयता नीति",
  terms: "उपयोग की शर्तें",
  contact: "संपर्क करें",
  copyright: "© 2024 न्यायंतर AI. सर्वाधिकार सुरक्षित।"
};

const englishContent = {
  privacy: "Privacy Policy",
  terms: "Terms of Service",
  contact: "Contact",
  copyright: "© 2024 Nyantar AI. All rights reserved."
};

export default function Footer() {
  const { language } = useLanguage();
  const content = language === "hindi" ? hindiContent : englishContent;

  return (
    <footer className="border-t border-gray-700 bg-[#1a1a1a] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-gray-400 text-sm">
            {content.copyright}
          </div>
          <div className="flex space-x-6 text-sm">
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              {content.privacy}
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              {content.terms}
            </a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">
              {content.contact}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
