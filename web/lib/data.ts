import fs from 'fs';
import path from 'path';

// Types
export interface Bookmark {
  id: string;
  title: string;
  source: string;
  url: string;
  text: string;
  author: string | null;
  created_at: string;
  bookmarked_at: string;
  tags: string[];
}

export interface ScoringInputs {
  relevance: number;
  practical_value: number;
  actionability: number;
  stage_fit: number;
  novelty: number;
  excitement: number;
  difficulty: number;
  time_cost: number;
}

export interface AnalysisResult {
  bookmark_id: string;
  summary: string;
  recommendation_reason: string;
  key_insights: string[];
  scoring_inputs: ScoringInputs;
  worth_score: number;
  effort_score: number;
  priority_score: number;
  recommendation_bucket: 'test_this_week' | 'build_later' | 'archive' | 'ignore';
  analysis_source: string;
  analyzed_at: string;
}

export interface BookmarkWithAnalysis extends Bookmark {
  analysis: AnalysisResult | null;
}

// Read data from parent directory (RolloForge root)
const DATA_DIR = path.join(process.cwd(), '..', 'data');

export function getBookmarks(): Bookmark[] {
  try {
    const filePath = path.join(DATA_DIR, 'bookmarks_raw.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading bookmarks:', error);
    return [];
  }
}

export function getAnalysisResults(): AnalysisResult[] {
  try {
    const filePath = path.join(DATA_DIR, 'analysis_results.json');
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading analysis:', error);
    return [];
  }
}

export function getBookmarksWithAnalysis(): BookmarkWithAnalysis[] {
  const bookmarks = getBookmarks();
  const analysisResults = getAnalysisResults();
  
  const analysisMap = new Map(analysisResults.map(a => [a.bookmark_id, a]));
  
  return bookmarks.map(bookmark => ({
    ...bookmark,
    analysis: analysisMap.get(bookmark.id) || null,
  }));
}

export function getStats() {
  const bookmarks = getBookmarksWithAnalysis();
  const withAnalysis = bookmarks.filter(b => b.analysis);
  
  return {
    total: bookmarks.length,
    test_this_week: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'test_this_week').length,
    build_later: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'build_later').length,
    archive: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'archive').length,
    ignore: withAnalysis.filter(b => b.analysis?.recommendation_bucket === 'ignore').length,
  };
}

export function getRecentBookmarks(limit: number = 5): BookmarkWithAnalysis[] {
  const bookmarks = getBookmarksWithAnalysis();
  return bookmarks
    .sort((a, b) => new Date(b.bookmarked_at).getTime() - new Date(a.bookmarked_at).getTime())
    .slice(0, limit);
}

export function getBookmarksByBucket(bucket: string): BookmarkWithAnalysis[] {
  const bookmarks = getBookmarksWithAnalysis();
  return bookmarks.filter(b => b.analysis?.recommendation_bucket === bucket);
}

export function getAllTags(): string[] {
  const bookmarks = getBookmarks();
  const tagSet = new Set<string>();
  bookmarks.forEach(b => b.tags?.forEach(tag => tagSet.add(tag)));
  return Array.from(tagSet).sort();
}