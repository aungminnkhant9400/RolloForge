'use client';

import { useState, useEffect } from 'react';
import { EditableBookmarkCard } from './EditableBookmarkCard';
import { BookmarkWithAnalysis } from '@/lib/data';

interface BookmarkListProps {
  bookmarks: BookmarkWithAnalysis[];
}

export function BookmarkList({ bookmarks }: BookmarkListProps) {
  const [localBookmarks, setLocalBookmarks] = useState<BookmarkWithAnalysis[]>(bookmarks);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  
  // Update local state when props change
  useEffect(() => {
    setLocalBookmarks(bookmarks);
  }, [bookmarks]);
  
  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('rolloforge_bookmarks');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Merge saved data with current bookmarks
        setLocalBookmarks(prev => 
          prev.map(bm => ({
            ...bm,
            analysis: {
              ...bm.analysis,
              ...parsed[bm.id]?.analysis
            } as any
          }))
        );
      } catch (e) {
        console.error('Failed to load saved bookmarks', e);
      }
    }
  }, []);
  
  // Save to localStorage when bookmarks change
  useEffect(() => {
    const toSave: Record<string, any> = {};
    localBookmarks.forEach(bm => {
      if (bm.analysis?.personal_notes || bm.analysis?.recommendation_bucket) {
        toSave[bm.id] = {
          analysis: {
            personal_notes: bm.analysis?.personal_notes,
            recommendation_bucket: bm.analysis?.recommendation_bucket,
            priority_score: bm.analysis?.priority_score
          }
        };
      }
    });
    localStorage.setItem('rolloforge_bookmarks', JSON.stringify(toSave));
  }, [localBookmarks]);
  
  const handleUpdate = (id: string, updates: Partial<BookmarkWithAnalysis>) => {
    setLocalBookmarks(prev => 
      prev.map(bm => 
        bm.id === id ? { ...bm, ...updates } : bm
      )
    );
  };
  
  const handleDelete = (id: string) => {
    if (confirm('Delete this bookmark?')) {
      setLocalBookmarks(prev => prev.filter(bm => bm.id !== id));
    }
  };
  
  const handleMove = (id: string, newBucket: string) => {
    setLocalBookmarks(prev => 
      prev.map(bm => 
        bm.id === id 
          ? { 
              ...bm, 
              analysis: { 
                ...bm.analysis, 
                recommendation_bucket: newBucket 
              } as any 
            }
          : bm
      )
    );
  };
  
  const handleSelect = (id: string) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };
  
  const handleBulkMove = (newBucket: string) => {
    setLocalBookmarks(prev => 
      prev.map(bm => 
        selectedIds.has(bm.id)
          ? { 
              ...bm, 
              analysis: { 
                ...bm.analysis, 
                recommendation_bucket: newBucket 
              } as any 
            }
          : bm
      )
    );
    setSelectedIds(new Set());
  };
  
  const handleBulkDelete = () => {
    if (confirm(`Delete ${selectedIds.size} bookmarks?`)) {
      setLocalBookmarks(prev => prev.filter(bm => !selectedIds.has(bm.id)));
      setSelectedIds(new Set());
    }
  };

  return (
    <>
      {/* Bulk actions bar */}
      {selectedIds.size > 0 && (
        <div style={{
          background: 'var(--accent)',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span>{selectedIds.size} selected</span>
          
          <button 
            onClick={() => handleBulkMove('test_this_week')}
            style={{
              padding: '6px 12px',
              background: 'white',
              color: 'var(--accent)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Move to Test
          </button>
          <button 
            onClick={() => handleBulkMove('archive')}
            style={{
              padding: '6px 12px',
              background: 'white',
              color: 'var(--accent)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Move to Archive
          </button>
          <button 
            onClick={handleBulkDelete}
            style={{
              padding: '6px 12px',
              background: 'var(--bad)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Delete
          </button>
          <button 
            onClick={() => setSelectedIds(new Set())}
            style={{
              padding: '6px 12px',
              background: 'transparent',
              color: 'white',
              border: '1px solid white',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Clear
          </button>
        </div>
      )}
      
      <div className="results-count">
        Showing {localBookmarks.length} bookmarks
        {selectedIds.size > 0 && ` (${selectedIds.size} selected)`}
      </div>
      
      <div className="bookmark-list">
        {localBookmarks.length > 0 ? (
          localBookmarks.map((bookmark) => (
            <div key={bookmark.id} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <input
                type="checkbox"
                checked={selectedIds.has(bookmark.id)}
                onChange={() => handleSelect(bookmark.id)}
                style={{
                  marginTop: '20px',
                  width: '18px',
                  height: '18px',
                  cursor: 'pointer'
                }}
              />
              <div style={{ flex: 1 }}>
                <EditableBookmarkCard
                  bookmark={bookmark}
                  onUpdate={handleUpdate}
                  onDelete={handleDelete}
                  onMove={handleMove}
                />
              </div>
            </div>
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