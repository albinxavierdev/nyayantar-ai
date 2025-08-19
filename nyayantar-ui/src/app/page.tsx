"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to landing page
    router.push("/landing");
  }, [router]);

  // Show loading while redirecting
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
