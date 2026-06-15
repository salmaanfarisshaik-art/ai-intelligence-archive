import { getTimeline } from "@/lib/api";

export default function TimelinePage() {
  const data = getTimeline();
  const events = data?.events || [];

  return (
    <main className="min-h-screen p-8 text-white max-w-4xl mx-auto pt-32">
      <div className="mb-16">
        <h1 className="text-5xl font-bold mb-4 glow-text">Historical Timeline</h1>
        <p className="text-gray-400 text-lg">A chronological view of the AI ecosystem's evolution.</p>
      </div>
      
      <div className="relative border-l border-white/20 pl-8 space-y-12 ml-4">
        {events.map((evt: any, i: number) => (
          <div key={i} className="relative">
            {/* Timeline Dot */}
            <div className="absolute -left-10 w-4 h-4 bg-purple-500 rounded-full shadow-[0_0_10px_rgba(168,85,247,0.8)] border-2 border-black" />
            
            <div className="glass-panel p-6 rounded-2xl hover:bg-white/5 transition-colors">
              <div className="flex flex-col md:flex-row md:items-center gap-2 mb-3">
                <span className="text-purple-400 font-mono text-lg font-bold">{evt.date}</span>
                <span className="hidden md:inline text-gray-600">•</span>
                <span className="text-sm px-2 py-1 bg-white/10 rounded-md uppercase tracking-wider text-gray-300">
                  {evt.event_type}
                </span>
              </div>
              
              <h3 className="text-xl font-semibold mb-2">{evt.description}</h3>
              
              {evt.details && evt.details.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-sm text-gray-400 mb-2">Included Entities:</p>
                  <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                    {evt.details.slice(0, 5).map((detail: string, j: number) => (
                      <li key={j} className="line-clamp-1">{detail}</li>
                    ))}
                    {evt.details.length > 5 && (
                      <li className="text-gray-500 italic">...and {evt.details.length - 5} more</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {events.length === 0 && (
          <div className="text-gray-400 italic">No timeline events available.</div>
        )}
      </div>
    </main>
  );
}
