'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isEditMode: boolean;
  checkEditKey: (key: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isEditMode, setIsEditMode] = useState(false);
  const EDIT_KEY = process.env.NEXT_PUBLIC_EDIT_KEY || 'default-key';

  useEffect(() => {
    // Check URL for edit key
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const editParam = urlParams.get('edit');
      
      if (editParam === EDIT_KEY) {
        setIsEditMode(true);
        // Store in session so it persists across navigation
        sessionStorage.setItem('rolloforge_edit', 'true');
      } else if (sessionStorage.getItem('rolloforge_edit') === 'true') {
        // Check session storage
        setIsEditMode(true);
      }
    }
  }, [EDIT_KEY]);

  const checkEditKey = (key: string): boolean => {
    return key === EDIT_KEY;
  };

  return (
    <AuthContext.Provider value={{ isEditMode, checkEditKey }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}