import { getKnowledgeGraph } from "@/lib/api";
import Link from "next/link";

export default function GraphPage() {
  const graph = getKnowledgeGraph();
  const nodes = graph?.nodes || [];
  const edges = graph?.edges || [];

  return (
    <main className="min-h-screen p-8 text-white max-w-6xl mx-auto pt-32">
      <div className="mb-16">
        <h1 className="text-5xl font-bold mb-4 glow-text">Knowledge Graph Explorer</h1>
        <p className="text-gray-400 text-lg">
          The deterministic intelligence graph containing {nodes.length.toLocaleString()} nodes and {edges.length.toLocaleString()} edges.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-panel p-6 rounded-3xl">
            <h3 className="text-xl font-semibold mb-4 text-purple-300">Graph Schema</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-white/10 pb-2">
                <span className="text-gray-400">Node Schema</span>
                <span className="font-mono text-gray-300">{graph?.node_schema_version || "Unknown"}</span>
              </div>
              <div className="flex justify-between border-b border-white/10 pb-2">
                <span className="text-gray-400">Relationship Schema</span>
                <span className="font-mono text-gray-300">{graph?.relationship_schema_version || "Unknown"}</span>
              </div>
            </div>
          </div>
          
          <div className="glass-panel p-6 rounded-3xl">
            <h3 className="text-xl font-semibold mb-4 text-purple-300">Interactive Visualizer</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Full WebGL canvas rendering of the graph is coming in Phase 11. Currently displaying tabular relationship data.
            </p>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="glass-panel p-6 rounded-3xl h-[600px] overflow-hidden flex flex-col">
            <h3 className="text-xl font-semibold mb-4 border-b border-white/10 pb-4">Top Relationships</h3>
            <div className="overflow-y-auto flex-1 pr-2">
              <div className="space-y-2">
                {edges.slice(0, 50).map((edge: any, i: number) => {
                  const srcNode = nodes.find((n: any) => n.canonical_id === edge.source_id);
                  const tgtNode = nodes.find((n: any) => n.canonical_id === edge.target_id);
                  
                  if (!srcNode || !tgtNode) return null;
                  
                  return (
                    <div key={i} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                      <Link href={`/entity/${srcNode.entity_type}/${srcNode.canonical_id}`} className="flex-1 text-right text-sm hover:text-purple-300 transition-colors line-clamp-1">
                        {srcNode.title}
                      </Link>
                      
                      <div className="flex flex-col items-center justify-center shrink-0 w-32">
                        <span className="text-[10px] uppercase tracking-widest text-purple-400 mb-1">{edge.relationship_type}</span>
                        <div className="w-full h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent relative">
                          <div className="absolute right-0 -top-1 w-2 h-2 border-t border-r border-purple-500 transform rotate-45" />
                        </div>
                      </div>
                      
                      <Link href={`/entity/${tgtNode.entity_type}/${tgtNode.canonical_id}`} className="flex-1 text-sm hover:text-purple-300 transition-colors line-clamp-1">
                        {tgtNode.title}
                      </Link>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
