'use client';

import { useState, useMemo } from 'react';
import { FilterSidebar } from './FilterSidebar';
import { SearchBar } from './SearchBar';
import { BookmarkList } from './BookmarkList';
import { NotesSync } from './NotesSync';
import { BookmarkWithAnalysis } from '@/lib/data';

interface BookmarksContentProps {
  allBookmarks: BookmarkWithAnalysis[];
  allTags: string[];
}

export function BookmarksContent({ allBookmarks, allTags }: BookmarksContentProps) {
  const [selectedBucket, setSelectedBucket] = useState('all');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const filteredBookmarks = useMemo(() => {
    return allBookmarks.filter((bookmark) => {
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
      
      // Search filter - full text search
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const searchableText = `
          ${bookmark.title} 
          ${bookmark.text} 
          ${bookmark.author || ''} 
          ${bookmark.analysis?.summary || ''}
          ${bookmark.analysis?.recommendation_reason || ''}
          ${bookmark.analysis?.key_insights?.join(' ') || ''}
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
    <div className="filter-layout">
      <FilterSidebar
        availableTags={allTags}
        selectedBucket={selectedBucket}
        onBucketChange={setSelectedBucket}
        selectedTags={selectedTags}
        onTagChange={handleTagChange}
        bookmarks={allBookmarks}
      />
      
      <div>
        <SearchBar 
          value={searchQuery} 
          onChange={setSearchQuery}
          placeholder="Search titles, content, summaries, tags..."
        />
        <NotesSync />
        
        <BookmarkList bookmarks={filteredBookmarks} />
      </div>
    </div>
  );
}
