import { BookmarksContent } from '@/components/BookmarksContent';
import { getBookmarksWithAnalysis, getAllTags } from '@/lib/data';

// ISR: Rebuild every 60 seconds
export const revalidate = 60;

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
