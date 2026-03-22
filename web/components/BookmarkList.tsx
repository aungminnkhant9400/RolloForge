import { BookmarkCard } from './BookmarkCard';
import { BookmarkWithAnalysis } from '@/lib/data';

interface BookmarkListProps {
  bookmarks: BookmarkWithAnalysis[];
}

export function BookmarkList({ bookmarks }: BookmarkListProps) {
  return (
    <>
      <div className="results-count">
        Showing {bookmarks.length} bookmarks
      </div>
      
      <div className="bookmark-list">
        {bookmarks.length > 0 ? (
          bookmarks.map((bookmark) => (
            <BookmarkCard key={bookmark.id} bookmark={bookmark} />
          ))
        ) : (
          <div className="empty-state">
            <p>No bookmarks match your filters.</p>
          </div>
        )}
      </div>
    </>
  );
}