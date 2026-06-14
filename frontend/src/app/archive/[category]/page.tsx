import Link from "next/link";
import fs from "fs";
import path from "path";

export async function generateStaticParams() {
  // Read all directories in public/data except archive_stats.json and search_index.json
  const dataDir = path.join(process.cwd(), "public/data");
  let categories: string[] = [];
  
  if (fs.existsSync(dataDir)) {
    categories = fs.readdirSync(dataDir).filter(f => fs.statSync(path.join(dataDir, f)).isDirectory());
  }

  return categories.map((category) => ({
    category,
  }));
}

export default async function CategoryPage({ params }: { params: Promise<{ category: string }> }) {
  // In a real app we'd fetch at runtime or use a client component for pagination.
  // We'll read the file directly for static generation (or fetch locally)
  const resolvedParams = await params;
  const category = resolvedParams.category;
  let items = [];
  
  try {
    const dataPath = path.join(process.cwd(), "public", "data", category, "data.json");
    if (fs.existsSync(dataPath)) {
      items = JSON.parse(fs.readFileSync(dataPath, "utf-8"));
    }
  } catch (err) {
    console.error(err);
  }

  const categoryTitle = category.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());

  // Let's get the original count from stats
  let originalTotal = items.length;
  try {
    const statsPath = path.join(process.cwd(), "public", "data", "archive_stats.json");
    if (fs.existsSync(statsPath)) {
      const statsObj = JSON.parse(fs.readFileSync(statsPath, "utf-8"));
      // Some category slugs don't perfectly match stats keys, handle exceptions
      const statsKey = category === "ai_skills_library" ? "skills" : 
                       category === "mcps" ? "mcp_servers" : 
                       category === "api_providers" ? "public_apis" : category;
      originalTotal = statsObj.data[statsKey] || items.length;
    }
  } catch (err) {
    // ignore
  }

  return (
    <main className="min-h-screen text-white pt-24 px-4 md:px-12 lg:px-24 max-w-7xl mx-auto">
      <Link href="/" className="text-purple-400 hover:text-purple-300 mb-8 inline-block">
        &larr; Back to Dashboard
      </Link>
      
      <h1 className="text-4xl md:text-5xl font-bold mb-2">{categoryTitle}</h1>
      <p className="text-gray-400 mb-12">Showing top {items.length} records out of {originalTotal.toLocaleString()}. Use the global search for everything else.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-24">
        {items.map((item: any, idx: number) => {
          const title = item.name || item.title || item.skill_name || item.technique_name || item.server_name || item.provider || item.rule_name || "Untitled";
          const desc = item.description || item.summary || item.workflow || "No description provided.";
          const url = item.source_url || item.endpoint || "#";
          
          return (
            <a 
              key={item.unique_id || idx} 
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="glass-panel p-6 rounded-2xl hover:bg-white/10 transition-colors block group"
            >
              <h3 className="text-xl font-semibold mb-2 group-hover:text-purple-300 transition-colors line-clamp-1">{title}</h3>
              <p className="text-gray-400 text-sm line-clamp-3 leading-relaxed">{desc}</p>
              <div className="mt-4 pt-4 border-t border-white/10 text-xs text-purple-400/80 font-mono">
                {item.unique_id}
              </div>
            </a>
          );
        })}
        
        {items.length === 0 && (
          <div className="col-span-full py-12 text-center text-gray-500">
            No data generated for this category yet.
          </div>
        )}
      </div>
    </main>
  );
}
