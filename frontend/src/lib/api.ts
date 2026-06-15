import fs from 'fs';
import path from 'path';

const REPO_ROOT = path.join(process.cwd(), '..');

export function readJsonFile(filePath: string) {
  try {
    // Prevent Turbopack from tracing the entire repository
    const fullPath = path.join(/*turbopackIgnore: true*/ REPO_ROOT, filePath);
    if (!fs.existsSync(fullPath)) return null;
    const data = fs.readFileSync(fullPath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return null;
  }
}

export function getDashboardMetrics() {
  return readJsonFile('site/dashboard_metrics.json');
}

export function getTimeline() {
  return readJsonFile('site/timeline.json');
}

export function getBuildManifest() {
  return readJsonFile('reports/build_manifest.json');
}

export function getArtifactManifest() {
  return readJsonFile('site/artifact_manifest.json');
}

export function getKnowledgeGraph() {
  return readJsonFile('site/entity_graph.json');
}

export function getArchiveStats() {
  return readJsonFile('site/archive_stats.json');
}

export function getSourceRegistry() {
  return readJsonFile('data/metadata/source_registry.json');
}

export function getEntitiesByDomain(domain: string) {
  return readJsonFile(`data/processed/${domain}/data.json`) || [];
}

export function getAllDomains() {
  const processedPath = path.join(/*turbopackIgnore: true*/ REPO_ROOT, 'data/processed');
  if (!fs.existsSync(processedPath)) return [];
  return fs.readdirSync(processedPath).filter(d => fs.statSync(path.join(/*turbopackIgnore: true*/ processedPath, d)).isDirectory());
}

export function getEntity(domain: string, id: string) {
  const entities = getEntitiesByDomain(domain);
  return entities.find((e: any) => e.unique_id === id) || null;
}
