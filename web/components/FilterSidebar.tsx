'use client';

import { BookmarkWithAnalysis } from '@/lib/data';

interface FilterSidebarProps {
  selectedBucket: string;
  onBucketChange: (bucket: string) => void;
  selectedTags: string[];
  onTagChange: (tag: string) => void;
  availableTags: string[];
  bookmarks: BookmarkWithAnalysis[];
}

const buckets = [
  { id: 'all', label: 'All Bookmarks', color: 'bg-ink' },
  { id: 'test_this_week', label: 'Test This Week', color: 'bg-green-500' },
  { id: 'build_later', label: 'Build Later', color: 'bg-orange-500' },
  { id: 'archive', label: 'Archive', color: 'bg-gray-500' },
];

export function FilterSidebar({
  selectedBucket,
  onBucketChange,
  selectedTags,
  onTagChange,
  availableTags,
  bookmarks,
}: FilterSidebarProps) {
  const getCount = (bucketId: string) => {
    if (bucketId === 'all') return bookmarks.length;
    return bookmarks.filter(b => b.analysis?.recommendation_bucket === bucketId).length;
  };

  return (
    <aside className="space-y-6">
      {/* Bucket filters */}
      <div>
        <h3 className="font-semibold text-ink mb-3">Buckets</h3>
        <ul className="space-y-2">
          {buckets.map((bucket) => {
            const isActive = selectedBucket === bucket.id;
            const count = getCount(bucket.id);
            
            return (
              <li key={bucket.id}>
                <button
                  onClick={() => onBucketChange(bucket.id)}
                  className={`
                    w-full flex items-center justify-between p-3 rounded-lg
                    transition-colors text-left
                    ${isActive 
                      ? 'bg-panel border border-accent text-accent' 
                      : 'hover:bg-panel/50 text-ink'}
                  `}
                >
                  <span className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${bucket.color}`} />
                    {bucket.label}
                  </span>
                  <span className="text-sm text-muted">{count}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
      
      {/* Tag filters */}
      {availableTags.length > 0 && (
        <div>
          <h3 className="font-semibold text-ink mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => {
              const isActive = selectedTags.includes(tag);
              
              return (
                <button
                  key={tag}
                  onClick={() => onTagChange(tag)}
                  className={`
                    px-3 py-1 rounded-full text-sm
                    transition-colors
                    ${isActive 
                      ? 'bg-accent text-white' 
                      : 'bg-panel-strong text-muted hover:bg-panel'}
                  `}
                >
                  #{tag}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </aside>
  );
}