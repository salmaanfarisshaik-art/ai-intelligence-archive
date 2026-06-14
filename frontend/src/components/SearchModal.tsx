"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface SearchItem {
  id: string;
  category: string;
  title: string;
  desc: string;
}

export default function SearchModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchItem[]>([]);
  const [index, setIndex] = useState<SearchItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && index.length === 0) {
      setIsLoading(true);
      fetch("/data/search_index.json")
        .then((res) => res.json())
        .then((data) => {
          setIndex(data);
          setIsLoading(false);
        })
        .catch(() => setIsLoading(false));
    }
  }, [isOpen, index.length]);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }

    const q = query.toLowerCase();
    const filtered = index.filter((item) => 
      item.title.toLowerCase().includes(q) || 
      item.desc.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q)
    ).slice(0, 50); // Limit to 50 results for performance

    setResults(filtered);
  }, [query, index]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4">
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-3xl glass-panel rounded-2xl shadow-2xl flex flex-col max-h-[80vh] overflow-hidden">
        <div className="p-4 border-b border-white/10 flex items-center">
          <span className="text-xl mr-3 opacity-50">🔍</span>
          <input
            autoFocus
            type="text"
            className="w-full bg-transparent border-none outline-none text-white text-xl placeholder-gray-500"
            placeholder="Search 100,000+ models, prompts, skills..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button onClick={onClose} className="text-gray-400 hover:text-white px-2">ESC</button>
        </div>

        <div className="overflow-y-auto p-4 flex-1">
          {isLoading && <div className="p-8 text-center text-gray-400">Loading intelligence index...</div>}
          
          {!isLoading && query.length >= 2 && results.length === 0 && (
            <div className="p-8 text-center text-gray-500">No results found in the archive.</div>
          )}
          
          <div className="flex flex-col gap-2">
            {results.map((item) => (
              <Link 
                href={`/archive/${item.category}`} 
                key={`${item.category}-${item.id}`}
                onClick={onClose}
                className="p-4 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-colors flex flex-col gap-1"
              >
                <div className="flex justify-between items-start">
                  <h4 className="font-semibold text-purple-300">{item.title}</h4>
                  <span className="text-xs px-2 py-1 bg-white/10 rounded-full text-gray-300 uppercase tracking-wider ml-4 whitespace-nowrap">
                    {item.category.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="text-sm text-gray-400 line-clamp-2">{item.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
