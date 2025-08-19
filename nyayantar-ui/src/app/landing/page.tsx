"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useLanguage } from "@/contexts/LanguageContext";

interface LanguageContent {
  hero: {
    title: string;
    subtitle: string;
    description: string;
    cta: string;
  };
  features: {
    title: string;
    items: Array<{
      title: string;
      description: string;
      icon: string;
    }>;
  };
  about: {
    title: string;
    description: string;
  };
  stats: {
    title: string;
    items: Array<{
      number: string;
      label: string;
    }>;
  };
  cta: {
    title: string;
    description: string;
    button: string;
  };
}

const hindiContent: LanguageContent = {
  hero: {
    title: "न्यायंतर AI",
    subtitle: "भारतीय कानूनों का आपका विश्वसनीय साथी",
    description: "कृत्रिम बुद्धिमत्ता से संचालित कानूनी सहायक जो भारतीय कानूनों और नियमों के बारे में तत्काल जानकारी प्रदान करता है।",
    cta: "अभी शुरू करें"
  },
  features: {
    title: "मुख्य विशेषताएं",
    items: [
      {
        title: "कानूनी शोध",
        description: "भारतीय दंड संहिता, संविधान और अन्य कानूनों के बारे में तत्काल जानकारी",
        icon: "⚖️"
      },
      {
        title: "AI संचालित",
        description: "उन्नत AI तकनीक का उपयोग करके सटीक और विश्वसनीय जवाब",
        icon: "🤖"
      },
      {
        title: "24/7 उपलब्ध",
        description: "किसी भी समय कानूनी सहायता और मार्गदर्शन प्राप्त करें",
        icon: "⏰"
      },
      {
        title: "स्रोत सत्यापन",
        description: "सभी जवाबों के साथ स्रोत दस्तावेजों का संदर्भ",
        icon: "✅"
      }
    ]
  },
  about: {
    title: "न्यायंतर AI के बारे में",
    description: "न्यायंतर AI एक उन्नत कानूनी सहायक है जो भारतीय कानूनों के विशाल डेटाबेस का उपयोग करके आपकी कानूनी जिज्ञासाओं का जवाब देता है। यह AI-संचालित प्रणाली सटीक और विश्वसनीय जानकारी प्रदान करती है।"
  },
  stats: {
    title: "हमारी उपलब्धियां",
    items: [
      {
        number: "100+",
        label: "कानूनी दस्तावेज"
      },
      {
        number: "24/7",
        label: "उपलब्धता"
      },
      {
        number: "AI",
        label: "संचालित"
      },
      {
        number: "100%",
        label: "स्रोत सत्यापित"
      }
    ]
  },
  cta: {
    title: "अपनी कानूनी यात्रा शुरू करें",
    description: "न्यायंतर AI के साथ भारतीय कानूनों की दुनिया में प्रवेश करें",
    button: "अभी शुरू करें"
  }
};

const englishContent: LanguageContent = {
  hero: {
    title: "Nyantar AI",
    subtitle: "Your Trusted Legal Companion",
    description: "An AI-powered legal assistant providing instant access to Indian laws, regulations, and legal guidance with verified sources.",
    cta: "Get Started"
  },
  features: {
    title: "Key Features",
    items: [
      {
        title: "Legal Research",
        description: "Instant access to Indian Penal Code, Constitution, and comprehensive legal databases",
        icon: "⚖️"
      },
      {
        title: "AI Powered",
        description: "Advanced AI technology delivering accurate and reliable legal information",
        icon: "🤖"
      },
      {
        title: "24/7 Available",
        description: "Round-the-clock legal assistance and guidance whenever you need it",
        icon: "⏰"
      },
      {
        title: "Source Verified",
        description: "All responses include verified source documents and legal references",
        icon: "✅"
      }
    ]
  },
  about: {
    title: "About Nyantar AI",
    description: "Nyantar AI is an advanced legal assistant that leverages a comprehensive database of Indian laws to provide accurate, reliable, and up-to-date legal information. Our AI-powered system ensures you receive trustworthy guidance for your legal queries."
  },
  stats: {
    title: "Our Capabilities",
    items: [
      {
        number: "100+",
        label: "Legal Documents"
      },
      {
        number: "24/7",
        label: "Availability"
      },
      {
        number: "AI",
        label: "Powered"
      },
      {
        number: "100%",
        label: "Source Verified"
      }
    ]
  },
  cta: {
    title: "Start Your Legal Journey",
    description: "Access comprehensive Indian legal knowledge with Nyantar AI",
    button: "Get Started"
  }
};

export default function LandingPage() {
  const [isClient, setIsClient] = useState(false);
  const router = useRouter();
  const { language, setLanguage } = useLanguage();
  
  // Fix hydration mismatch
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  const content = language === "hindi" ? hindiContent : englishContent;

  const handleGetStarted = () => {
    router.push("/chat");
  };

  // Don't render until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="min-h-screen bg-[#1a1a1a] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-[#d97706] rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-black font-bold text-2xl">N</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">Loading Nyantar AI...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white">
      {/* Header */}
      <header className="border-b border-gray-700 bg-[#1a1a1a]/95 backdrop-blur supports-[backdrop-filter]:bg-[#1a1a1a]/60 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#d97706]">
                <span className="text-black font-semibold text-sm">N</span>
              </div>
              <span className="text-xl font-semibold">Nyantar AI</span>
            </div>
            <div className="flex items-center space-x-4">
              {/* Language Switcher */}
              <div className="flex items-center space-x-1 rounded-lg border border-gray-600 bg-[#374151] p-1">
                <Button
                  variant={language === "hindi" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setLanguage("hindi")}
                  className={`h-8 px-3 ${
                    language === "hindi" 
                      ? "bg-[#d97706] text-black hover:bg-[#f59e0b]" 
                      : "text-gray-300 hover:text-white hover:bg-[#4b5563]"
                  }`}
                >
                  हिंदी
                </Button>
                <Button
                  variant={language === "english" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setLanguage("english")}
                  className={`h-8 px-3 ${
                    language === "english" 
                      ? "bg-[#d97706] text-black hover:bg-[#f59e0b]" 
                      : "text-gray-300 hover:text-white hover:bg-[#4b5563]"
                  }`}
                >
                  English
                </Button>
              </div>
              <Button 
                asChild
                className="bg-[#d97706] hover:bg-[#f59e0b] text-black"
              >
                <Link href="/chat">
                  {language === "hindi" ? "चैट करें" : "Start Chat"}
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24 text-center">
        <div className="max-w-4xl mx-auto">
          <Badge className="mb-4 bg-[#374151] text-white border-gray-600">
            {language === "hindi" ? "AI संचालित कानूनी सहायक" : "AI-Powered Legal Assistant"}
          </Badge>
          <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl">
            {content.hero.title}
          </h1>
          <p className="mb-8 text-xl text-gray-300">
            {content.hero.subtitle}
          </p>
          <p className="mb-8 text-lg text-gray-400">
            {content.hero.description}
          </p>
          <Button 
            size="lg" 
            onClick={handleGetStarted} 
            className="text-lg px-8 py-6 bg-[#d97706] hover:bg-[#f59e0b] text-black"
          >
            {content.hero.cta}
          </Button>
        </div>
      </section>

      <Separator className="bg-gray-700" />

      {/* Features Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              {content.features.title}
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            {content.features.items.map((feature, index) => (
              <Card key={index} className="text-center bg-[#374151] border-gray-600 hover:bg-[#4b5563] transition-colors">
                <CardHeader>
                  <div className="text-3xl mb-2">{feature.icon}</div>
                  <CardTitle className="text-lg text-white">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm text-gray-400">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <Separator className="bg-gray-700" />

      {/* About Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
            {content.about.title}
          </h2>
          <p className="text-lg text-gray-400 leading-relaxed">
            {content.about.description}
          </p>
        </div>
      </section>

      <Separator className="bg-gray-700" />

      {/* Stats Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              {content.stats.title}
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {content.stats.items.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-[#d97706] mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Separator className="bg-gray-700" />

      {/* CTA Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
            {content.cta.title}
          </h2>
          <p className="text-lg text-gray-400 mb-8">
            {content.cta.description}
          </p>
          <Button 
            size="lg" 
            onClick={handleGetStarted} 
            className="text-lg px-8 py-6 bg-[#d97706] hover:bg-[#f59e0b] text-black"
          >
            {content.cta.button}
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-700 bg-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-400">
            <p>
              {language === "hindi" 
                ? "© 2024 न्यायंतर AI. सर्वाधिकार सुरक्षित।" 
                : "© 2024 Nyantar AI. All rights reserved."
              }
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
