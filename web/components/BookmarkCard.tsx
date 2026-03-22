import Link from 'next/link';
import { ExternalLink, Calendar, User } from 'lucide-react';
import { BookmarkWithAnalysis } from '@/lib/data';

interface BookmarkCardProps {
  bookmark: BookmarkWithAnalysis;
}

const bucketClasses = {
  test_this_week: 'test',
  build_later: 'build',
  archive: 'archive',
  ignore: 'ignore',
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
    <article className="bookmark-card">
      <div className="card-header">
        <span className={`badge ${bucketClasses[bucket]}`}>
          {bucketLabels[bucket]}
        </span>
        
        {analysis && (
          <span className="priority">
            Priority: <strong>{analysis.priority_score.toFixed(1)}</strong>
          </span>
        )}
      </div>
      
      <h3 className="card-title">
        <Link href={bookmark.url} target="_blank" rel="noopener noreferrer">
          {bookmark.title}
          <ExternalLink size={16} className="external-icon" />
        </Link>
      </h3>
      
      {analysis?.summary && (
        <p className="card-summary">{analysis.summary}</p>
      )}
      
      <div className="card-meta">
        {bookmark.author && (
          <span>
            <User size={14} />
            {bookmark.author}
          </span>
        )}
        <span>
          <Calendar size={14} />
          {new Date(bookmark.bookmarked_at).toLocaleDateString()}
        </span>
        
        {analysis && (
          <span style={{ fontSize: '0.75rem' }}>
            Worth: {analysis.worth_score.toFixed(1)} | 
            Effort: {analysis.effort_score.toFixed(1)}
          </span>
        )}
      </div>
      
      {bookmark.tags?.length > 0 && (
        <div className="tags">
          {bookmark.tags.map((tag) => (
            <span key={tag} className="tag">#{tag}</span>
          ))}
        </div>
      )}
    </article>
  );
}