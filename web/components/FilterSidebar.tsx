'use client';

import { useRouter, useSearchParams } from 'next/navigation';

interface FilterSidebarProps {
  allTags: string[];
  selectedBucket: string;
  selectedTags: string[];
}

const buckets = [
  { id: 'all', label: 'All Bookmarks', color: 'bg-ink' },
  { id: 'test_this_week', label: 'Test This Week', color: 'bg-green-500' },
  { id: 'build_later', label: 'Build Later', color: 'bg-orange-500' },
  { id: 'archive', label: 'Archive', color: 'bg-gray-500' },
];

export function FilterSidebar({ allTags, selectedBucket, selectedTags }: FilterSidebarProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const updateParams = (updates: Record<string, string>) => {
    const params = new URLSearchParams(searchParams.toString());
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });
    router.push(`/bookmarks?${params.toString()}`);
  };

  const handleBucketChange = (bucketId: string) => {
    updateParams({ bucket: bucketId === 'all' ? '' : bucketId });
  };

  const handleTagChange = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag];
    updateParams({ tags: newTags.join(',') });
  };

  return (
    <aside className="space-y-6">
      {/* Bucket filters */}
      <div>
        <h3 className="font-semibold text-ink mb-3">Buckets</h3>
        <ul className="space-y-2">
          {buckets.map((bucket) => (
            <li key={bucket.id}>
              <button
                onClick={() => handleBucketChange(bucket.id)}
                className={`
                  w-full flex items-center justify-between p-3 rounded-lg
                  transition-colors text-left
                  ${selectedBucket === bucket.id 
                    ? 'bg-panel border border-accent text-accent' 
                    : 'hover:bg-panel/50 text-ink'}
                `}
              >
                <span className="flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${bucket.color}`} />
                  {bucket.label}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Tag filters */}
      {allTags.length > 0 && (
        <div>
          <h3 className="font-semibold text-ink mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {allTags.map((tag) => {
              const isActive = selectedTags.includes(tag);
              
              return (
                <button
                  key={tag}
                  onClick={() => handleTagChange(tag)}
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