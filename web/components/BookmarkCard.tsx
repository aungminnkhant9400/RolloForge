import Link from 'next/link';
import { ExternalLink, Calendar, User } from 'lucide-react';
import { BookmarkWithAnalysis } from '@/lib/data';

interface BookmarkCardProps {
  bookmark: BookmarkWithAnalysis;
}

const bucketColors = {
  test_this_week: 'bg-green-100 text-green-800 border-green-300',
  build_later: 'bg-orange-100 text-orange-800 border-orange-300',
  archive: 'bg-gray-100 text-gray-800 border-gray-300',
  ignore: 'bg-red-100 text-red-800 border-red-300',
};

const bucketLabels = {
  test_this_week: 'Test This Week',
  build_later: 'Build Later',
  archive: 'Archive',
  ignore: 'Ignore',
};

export function BookmarkCard({ bookmark }: BookmarkCardProps) {
  const analysis = bookmark.analysis;
  const bucket = analysis?.recommendation_bucket || 'archive';
  
  return (
    <article className="bg-panel rounded-2xl border border-line overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div className="p-5">
        {/* Header with bucket badge */}
        <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${bucketColors[bucket]}`}>
            {bucketLabels[bucket]}
          </span>
          
          {analysis && (
            <span className="text-sm text-muted">
              Priority: <strong className="text-ink">{analysis.priority_score.toFixed(1)}</strong>
            </span>
          )}
        </div>
        
        {/* Title */}
        <h3 className="text-lg font-semibold mb-2">
          <Link 
            href={bookmark.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-ink hover:text-accent transition-colors flex items-start gap-2"
          >
            {bookmark.title}
            <ExternalLink size={16} className="mt-1 flex-shrink-0 opacity-50" />
          </Link>
        </h3>
        
        {/* Summary */}
        {analysis?.summary && (
          <p className="text-muted text-sm mb-4 line-clamp-3">
            {analysis.summary}
          </p>
        )}
        
        {/* Meta info */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted">
          {bookmark.author && (
            <span className="flex items-center gap-1">
              <User size={14} />
              {bookmark.author}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Calendar size={14} />
            {new Date(bookmark.bookmarked_at).toLocaleDateString()}
          </span>
          
          {analysis && (
            <span className="text-xs">
              Worth: {analysis.worth_score.toFixed(1)} | 
              Effort: {analysis.effort_score.toFixed(1)}
            </span>
          )}
        </div>
        
        {/* Tags */}
        {bookmark.tags?.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {bookmark.tags.map((tag) => (
              <span 
                key={tag}
                className="px-2 py-1 bg-panel-strong rounded-full text-xs text-muted"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}