'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { BookmarkCard } from './BookmarkCard';
import { BookmarkWithAnalysis } from '@/lib/data';
import { useMemo } from 'react';

interface BookmarkListProps {
  bookmarks: BookmarkWithAnalysis[];
  filterBucket: string;
  filterTags: string[];
  searchQuery: string;
}

export function BookmarkList({ 
  bookmarks, 
  filterBucket, 
  filterTags, 
  searchQuery 
}: BookmarkListProps) {
  const filteredBookmarks = useMemo(() => {
    return bookmarks.filter((bookmark) => {
      // Bucket filter
      if (filterBucket !== 'all') {
        if (bookmark.analysis?.recommendation_bucket !== filterBucket) {
          return false;
        }
      }
      
      // Tag filter
      if (filterTags.length > 0) {
        const hasSelectedTag = filterTags.some(tag => 
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
  }, [bookmarks, filterBucket, filterTags, searchQuery]);

  return (
    <>
      <div className="text-sm text-muted">
        Showing {filteredBookmarks.length} of {bookmarks.length} bookmarks
      </div>
      
      <div className="grid gap-4">
        {filteredBookmarks.length > 0 ? (
          filteredBookmarks.map((bookmark) => (
            <BookmarkCard key={bookmark.id} bookmark={bookmark} />
          ))
        ) : (
          <div className="text-center py-12 text-muted bg-panel rounded-2xl border border-line">
            <p>No bookmarks match your filters.</p>
          </div>
        )}
      </div>
    </>
  );
}