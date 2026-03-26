import bookmarksData from './data.json';
import analysisData from './analysis.json';

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
  personal_notes?: string;
}

export interface BookmarkWithAnalysis extends Bookmark {
  analysis: AnalysisResult | null;
}

// Data is imported directly from JSON files
const bookmarks: Bookmark[] = bookmarksData as Bookmark[];
const analysisResults: AnalysisResult[] = analysisData as AnalysisResult[];

const analysisMap = new Map(analysisResults.map(a => [a.bookmark_id, a]));

export function getBookmarks(): Bookmark[] {
  return bookmarks;
}

export function getAnalysisResults(): AnalysisResult[] {
  return analysisResults;
}

export function getBookmarksWithAnalysis(): BookmarkWithAnalysis[] {
  return bookmarks.map(bookmark => ({
    ...bookmark,
    analysis: analysisMap.get(bookmark.id) || null,
  }));
}

export function getStats() {
  const withAnalysis = bookmarks.filter(b => analysisMap.has(b.id));
  
  return {
    total: bookmarks.length,
    test_this_week: withAnalysis.filter(b => analysisMap.get(b.id)?.recommendation_bucket === 'test_this_week').length,
    build_later: withAnalysis.filter(b => analysisMap.get(b.id)?.recommendation_bucket === 'build_later').length,
    archive: withAnalysis.filter(b => analysisMap.get(b.id)?.recommendation_bucket === 'archive').length,
    ignore: withAnalysis.filter(b => analysisMap.get(b.id)?.recommendation_bucket === 'ignore').length,
  };
}

export function getRecentBookmarks(limit: number = 5): BookmarkWithAnalysis[] {
  return getBookmarksWithAnalysis()
    .sort((a, b) => new Date(b.bookmarked_at).getTime() - new Date(a.bookmarked_at).getTime())
    .slice(0, limit);
}

export function getBookmarksByBucket(bucket: string): BookmarkWithAnalysis[] {
  return getBookmarksWithAnalysis().filter(b => b.analysis?.recommendation_bucket === bucket);
}

export function getAllTags(): string[] {
  const tagSet = new Set<string>();
  bookmarks.forEach(b => b.tags?.forEach(tag => tagSet.add(tag)));
  return Array.from(tagSet).sort();
}

// Full-text search across all bookmark fields
export function searchBookmarks(query: string): BookmarkWithAnalysis[] {
  if (!query.trim()) {
    return getBookmarksWithAnalysis();
  }
  
  const searchTerm = query.toLowerCase();
  const allBookmarks = getBookmarksWithAnalysis();
  
  return allBookmarks.filter(bookmark => {
    const searchableFields = [
      bookmark.title,
      bookmark.text,
      bookmark.author,
      bookmark.tags?.join(' '),
      bookmark.analysis?.summary,
      bookmark.analysis?.recommendation_reason,
      bookmark.analysis?.key_insights?.join(' '),
    ].filter(Boolean).join(' ').toLowerCase();
    
    return searchableFields.includes(searchTerm);
  });
}

// Advanced search with filters
export function advancedSearch({
  query,
  bucket,
  tags,
}: {
  query?: string;
  bucket?: string;
  tags?: string[];
}): BookmarkWithAnalysis[] {
  let results = getBookmarksWithAnalysis();
  
  // Text search
  if (query?.trim()) {
    const searchTerm = query.toLowerCase();
    results = results.filter(bookmark => {
      const searchableFields = [
        bookmark.title,
        bookmark.text,
        bookmark.author,
        bookmark.tags?.join(' '),
        bookmark.analysis?.summary,
        bookmark.analysis?.recommendation_reason,
        bookmark.analysis?.key_insights?.join(' '),
      ].filter(Boolean).join(' ').toLowerCase();
      
      return searchableFields.includes(searchTerm);
    });
  }
  
  // Bucket filter
  if (bucket && bucket !== 'all') {
    results = results.filter(b => b.analysis?.recommendation_bucket === bucket);
  }
  
  // Tags filter
  if (tags && tags.length > 0) {
    results = results.filter(b => 
      tags.some(tag => b.tags?.includes(tag))
    );
  }
  
  return results;
}
