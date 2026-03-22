'use client';

import { useSearchParams } from 'next/navigation';
import { FilterSidebar } from './FilterSidebar';
import { SearchBar } from './SearchBar';
import { BookmarkList } from './BookmarkList';
import { getBookmarksWithAnalysis, getAllTags } from '@/lib/data';

export function BookmarksContent() {
  const searchParams = useSearchParams();
  
  const allBookmarks = getBookmarksWithAnalysis();
  const allTags = getAllTags();
  
  // Get filter params
  const bucket = searchParams.get('bucket') || 'all';
  const tagsParam = searchParams.get('tags') || '';
  const tags = tagsParam ? tagsParam.split(',') : [];
  const query = searchParams.get('q') || '';

  return (
    <div className="grid lg:grid-cols-4 gap-6">
      {/* Sidebar */}
      <div className="lg:col-span-1">
        <FilterSidebar
          allTags={allTags}
          selectedBucket={bucket}
          selectedTags={tags}
        />
      </div>
      
      {/* Main content */}
      <div className="lg:col-span-3 space-y-4">
        <SearchBar initialValue={query} />
        
        <BookmarkList 
          bookmarks={allBookmarks}
          filterBucket={bucket}
          filterTags={tags}
          searchQuery={query}
        />
      </div>
    </div>
  );
}