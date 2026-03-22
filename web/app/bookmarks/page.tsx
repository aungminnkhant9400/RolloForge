import { BookmarksContent } from '@/components/BookmarksContent';
import { getBookmarksWithAnalysis, getAllTags } from '@/lib/data';

export default function BookmarksPage() {
  const allBookmarks = getBookmarksWithAnalysis();
  const allTags = getAllTags();

  return (
    <BookmarksContent 
      allBookmarks={allBookmarks}
      allTags={allTags}
    />
  );
}