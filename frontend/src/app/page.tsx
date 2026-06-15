"use client";

import { useEffect, useState, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Link from "next/link";
import SearchModal from "@/components/SearchModal";

gsap.registerPlugin(ScrollTrigger);

export default function Home() {
  const [stats, setStats] = useState<any>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch stats
    const basePath = process.env.NODE_ENV === "production" ? "/ai-intelligence-archive" : "";
    fetch(`${basePath}/site/archive_stats.json`)
      .then((res) => res.json())
      .then((payload) => setStats(payload))
      .catch((err) => console.error("Failed to load stats", err));

    // GSAP Animations
    const ctx = gsap.context(() => {
      gsap.from(titleRef.current, {
        y: 50,
        opacity: 0,
        duration: 1.5,
        ease: "power4.out",
      });

      if (cardsRef.current) {
        gsap.from(cardsRef.current.children, {
          y: 50,
          opacity: 0,
          duration: 1,
          stagger: 0.1,
          scrollTrigger: {
            trigger: cardsRef.current,
            start: "top 80%",
          },
        });
      }
    });

    return () => ctx.revert();
  }, []);

  const metricCards = [
    { label: "AI Models", value: stats?.models || "...", icon: "🤖", slug: "models" },
    { label: "Datasets", value: stats?.datasets || "...", icon: "📚", slug: "datasets" },
    { label: "AI Tools", value: stats?.tools || "...", icon: "🧰", slug: "tools" },
    { label: "Benchmarks", value: stats?.benchmarks || "...", icon: "📊", slug: "benchmarks" },
    { label: "Prompts", value: stats?.prompts || "...", icon: "💬", slug: "prompts" },
    { label: "AI Skills", value: stats?.skills || "...", icon: "📝", slug: "ai_skills_library" },
    { label: "MCP Servers", value: stats?.mcp_servers || "...", icon: "🏗️", slug: "mcps" },
    { label: "IDE Rules", value: stats?.ide_rules || "...", icon: "🖥️", slug: "ide_rules" },
    { label: "Public APIs", value: stats?.public_apis || "...", icon: "🌐", slug: "api_providers" },
    { label: "News Articles", value: stats?.news_articles || "...", icon: "📰", slug: "news" },
  ];

  return (
    <main className="min-h-[200vh] text-white">
      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
      
      {/* Global Header */}
      <header className="fixed top-0 w-full p-6 flex justify-end z-40 pointer-events-none">
        <button 
          onClick={() => setIsSearchOpen(true)}
          className="pointer-events-auto glass-panel px-6 py-3 rounded-full flex items-center gap-3 hover:bg-white/10 transition-colors"
        >
          <span>🔍</span>
          <span className="font-semibold tracking-wider">GLOBAL SEARCH</span>
        </button>
      </header>

      {/* Hero Section */}
      <section className="h-screen flex flex-col items-center justify-center text-center px-4">
        <h1 
          ref={titleRef}
          className="text-6xl md:text-8xl font-black mb-6 tracking-tighter glow-text bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-indigo-500"
        >
          AI Intelligence Archive
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 max-w-2xl font-light">
          A deterministic, file-based knowledge graph mapping over 100,000+ nodes of the AI ecosystem.
        </p>
        <div className="mt-12 flex flex-col items-center gap-6">
          <button 
            onClick={() => setIsSearchOpen(true)}
            className="px-8 py-4 bg-purple-600 hover:bg-purple-500 rounded-full font-bold tracking-widest uppercase transition-all shadow-[0_0_30px_rgba(147,51,234,0.5)] hover:shadow-[0_0_50px_rgba(147,51,234,0.8)]"
          >
            Search the Archive
          </button>
          
          <div className="mt-8 animate-bounce">
            <p className="text-sm uppercase tracking-widest text-purple-300 mb-2">Or Browse Categories</p>
            <div className="w-px h-16 bg-gradient-to-b from-purple-500 to-transparent mx-auto" />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 px-4 md:px-12 lg:px-24 max-w-7xl mx-auto">
        <div className="mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Archive Categories</h2>
          <p className="text-gray-400 text-lg">Click any category to browse the top entries instantly.</p>
        </div>

        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {metricCards.map((metric, idx) => (
            <Link 
              href={`/archive/${metric.slug}`}
              key={idx} 
              className="glass-panel p-6 rounded-2xl hover:bg-white/10 transition-colors cursor-pointer group block"
            >
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">{metric.icon}</div>
              <div className="text-gray-400 text-sm uppercase tracking-wider font-semibold mb-1">{metric.label}</div>
              <div className="text-3xl font-bold text-white tracking-tight">
                {typeof metric.value === "number" ? metric.value.toLocaleString() : metric.value}
                <span className="text-purple-400 ml-1">+</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
