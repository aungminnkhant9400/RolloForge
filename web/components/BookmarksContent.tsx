'use client';

import { useState, useMemo, useEffect } from 'react';
import { FilterSidebar } from './FilterSidebar';
import { SearchBar } from './SearchBar';
import { BookmarkList } from './BookmarkList';
import { NotesSync } from './NotesSync';
import { BookmarkWithAnalysis } from '@/lib/data';

interface BookmarksContentProps {
  allBookmarks: BookmarkWithAnalysis[];
  allTags: string[];
}

export function BookmarksContent({ allBookmarks: initialBookmarks, allTags: initialTags }: BookmarksContentProps) {
  const [allBookmarks, setAllBookmarks] = useState(initialBookmarks);
  const [allTags, setAllTags] = useState(initialTags);
  const [loading, setLoading] = useState(false);
  
  const [selectedBucket, setSelectedBucket] = useState('all');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Client-side: Fetch fresh data on mount and every 30 seconds
  useEffect(() => {
    async function fetchFreshData() {
      try {
        setLoading(true);
        const [bookmarksRes, analysisRes] = await Promise.all([
          fetch('/data.json?t=' + Date.now()),
          fetch('/analysis.json?t=' + Date.now())
        ]);
        
        if (!bookmarksRes.ok || !analysisRes.ok) {
          throw new Error('Failed to fetch');
        }
        
        const bookmarksData = await bookmarksRes.json();
        const analysisData = await analysisRes.json();
        
        // Merge data
        const analysisMap = new Map(analysisData.map((a: any) => [a.bookmark_id, a]));
        const merged = bookmarksData.map((b: any) => ({
          ...b,
          analysis: analysisMap.get(b.id) || null,
        }));
        
        setAllBookmarks(merged);
        
        // Update tags
        const tagSet = new Set<string>();
        bookmarksData.forEach((b: any) => b.tags?.forEach((tag: string) => tagSet.add(tag)));
        setAllTags(Array.from(tagSet).sort());
      } catch (err) {
        console.error('Failed to fetch fresh data:', err);
      } finally {
        setLoading(false);
      }
    }

    // Fetch immediately
    fetchFreshData();
    
    // Then every 30 seconds
    const interval = setInterval(fetchFreshData, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  const filteredBookmarks = useMemo(() => {
    const filtered = allBookmarks.filter((bookmark) => {
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
    
    // Sort by bookmarked_at descending (newest first)
    return filtered.sort((a, b) => 
      new Date(b.bookmarked_at).getTime() - new Date(a.bookmarked_at).getTime()
    );
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
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
        {loading && <span style={{ fontSize: '0.75rem', color: '#888' }}>Syncing...</span>}
        <NotesSync />
        <BookmarkList bookmarks={filteredBookmarks} />
      </div>
    </div>
  );
}
