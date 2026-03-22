'use client';

import { useState, useMemo } from 'react';
import { BookmarkCard } from '@/components/BookmarkCard';
import { FilterSidebar } from '@/components/FilterSidebar';
import { SearchBar } from '@/components/SearchBar';
import { getBookmarksWithAnalysis, getAllTags, BookmarkWithAnalysis } from '@/lib/data';

export default function BookmarksPage() {
  const [selectedBucket, setSelectedBucket] = useState('all');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const allBookmarks = getBookmarksWithAnalysis();
  const allTags = getAllTags();
  
  const filteredBookmarks = useMemo(() => {
    return allBookmarks.filter((bookmark: BookmarkWithAnalysis) => {
      // Bucket filter
      if (selectedBucket !== 'all') {
        if (bookmark.analysis?.recommendation_bucket !== selectedBucket) {
          return false;
        }
      }
      
      // Tag filter
      if (selectedTags.length > 0) {
        const hasSelectedTag = selectedTags.some(tag => 
          bookmark.tags?.includes(tag)
        );
        if (!hasSelectedTag) return false;
      }
      
      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const searchableText = `
          ${bookmark.title} 
          ${bookmark.text} 
          ${bookmark.author || ''} 
          ${bookmark.analysis?.summary || ''}
          ${bookmark.tags?.join(' ') || ''}
        `.toLowerCase();
        
        if (!searchableText.includes(query)) {
          return false;
        }
      }
      
      return true;
    });
  }, [allBookmarks, selectedBucket, selectedTags, searchQuery]);
  
  const handleTagChange = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };
  
  return (
    <div className="grid lg:grid-cols-4 gap-6">
      {/* Sidebar - hidden on mobile, shown on lg */}
      <div className="hidden lg:block">
        <FilterSidebar
          selectedBucket={selectedBucket}
          onBucketChange={setSelectedBucket}
          selectedTags={selectedTags}
          onTagChange={handleTagChange}
          availableTags={allTags}
          bookmarks={allBookmarks}
        />
      </div>
      
      {/* Mobile filters - shown only on small screens */}
      <div className="lg:hidden space-y-4">
        <FilterSidebar
          selectedBucket={selectedBucket}
          onBucketChange={setSelectedBucket}
          selectedTags={selectedTags}
          onTagChange={handleTagChange}
          availableTags={allTags}
          bookmarks={allBookmarks}
        />
      </div>
      
      {/* Main content */}
      <div className="lg:col-span-3 space-y-4">
        {/* Search bar */}
        <SearchBar 
          value={searchQuery}
          onChange={setSearchQuery}
        />
        
        {/* Results count */}
        <div className="text-sm text-muted">
          Showing {filteredBookmarks.length} of {allBookmarks.length} bookmarks
        </div>
        
        {/* Bookmarks grid */}
        <div className="grid gap-4">
          {filteredBookmarks.length > 0 ? (
            filteredBookmarks.map((bookmark) => (
              <BookmarkCard 
                key={bookmark.id} 
                bookmark={bookmark} 
              />
            ))
          ) : (
            <div className="text-center py-12 text-muted bg-panel rounded-2xl border border-line">
              <p>No bookmarks match your filters.</p>
              <button
                onClick={() => {
                  setSelectedBucket('all');
                  setSelectedTags([]);
                  setSearchQuery('');
                }}
                className="mt-2 text-accent hover:underline"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}