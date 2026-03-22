import { Suspense } from 'react';
import { BookmarksContent } from '@/components/BookmarksContent';

export default function BookmarksPage() {
  return (
    <Suspense fallback={
      <div className="text-center py-12 text-muted">Loading bookmarks...✨</div>
    }>
      <BookmarksContent />
    </Suspense>
  );
}