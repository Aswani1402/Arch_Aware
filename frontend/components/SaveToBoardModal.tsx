"use client";

import React, { useState, useEffect } from 'react';
import {
  X, Bookmark, Plus, Check, FolderPlus, Sparkles, Folder
} from 'lucide-react';
import { toggleSavedItem, hasAuthToken } from '@/lib/api';

interface SaveToBoardModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: {
    id: number;
    title: string;
    type?: string; // reference, product, material, supplier
    imageUrl?: string;
  } | null;
  onSavedChange?: (isSaved: boolean, boardName?: string) => void;
}

const DEFAULT_BOARDS = [
  { id: 'dream-house', name: 'Dream House', icon: '🏡', count: 12 },
  { id: 'brick-wall-ideas', name: 'Brick Wall Ideas', icon: '🧱', count: 8 },
  { id: 'flooring-options', name: 'Flooring Options', icon: '🪵', count: 15 },
  { id: 'doors-windows', name: 'Doors & Windows', icon: '🚪', count: 6 },
  { id: 'lighting-ideas', name: 'Lighting Ideas', icon: '💡', count: 9 },
  { id: 'bathroom-materials', name: 'Bathroom Materials', icon: '🛁', count: 7 },
  { id: 'construction-materials', name: 'Construction Materials', icon: '🏗️', count: 14 },
  { id: 'client-discussion', name: 'Products to Discuss with Client', icon: '📋', count: 5 },
  { id: 'suppliers-to-contact', name: 'Suppliers to Contact', icon: '🤝', count: 4 },
];

export const SaveToBoardModal: React.FC<SaveToBoardModalProps> = ({
  isOpen,
  onClose,
  item,
  onSavedChange,
}) => {
  const [boards, setBoards] = useState(DEFAULT_BOARDS);
  const [selectedBoards, setSelectedBoards] = useState<Set<string>>(new Set(['dream-house']));
  const [newBoardName, setNewBoardName] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [successToast, setSuccessToast] = useState<string | null>(null);

  // Load custom boards from localStorage if available
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem('architect_ai_custom_boards');
        if (stored) {
          const parsed = JSON.parse(stored);
          setBoards(prev => {
            const existingNames = new Set(prev.map(b => b.name));
            const fresh = parsed.filter((b: any) => !existingNames.has(b.name));
            return [...prev, ...fresh];
          });
        }
      } catch (e) {
        console.error('Error loading custom boards', e);
      }
    }
  }, []);

  if (!isOpen || !item) return null;

  const handleToggleBoard = async (boardId: string, boardName: string) => {
    if (!hasAuthToken()) {
      setSuccessToast('Please sign in to save items to your boards.');
      setTimeout(() => setSuccessToast(null), 2500);
      return;
    }
    const next = new Set(selectedBoards);
    const wasSelected = next.has(boardId);

    if (wasSelected) {
      next.delete(boardId);
    } else {
      next.add(boardId);
    }
    setSelectedBoards(next);

    try {
      setIsSaving(true);
      await toggleSavedItem({
        item_type: item.type === 'product' ? 'product' : 'reference',
        reference_id: item.type === 'product' ? undefined : item.id,
        product_id: item.type === 'product' ? item.id : undefined,
        project_collection: boardName,
      });
      setSuccessToast(wasSelected ? `Removed from ${boardName}` : `Saved to ${boardName}`);
      setTimeout(() => setSuccessToast(null), 2500);

      if (onSavedChange) {
        onSavedChange(!wasSelected, boardName);
      }
    } catch (e) {
      console.error('Error saving item', e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCreateBoard = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBoardName.trim()) return;

    const trimmed = newBoardName.trim();
    const newBoard = {
      id: `custom-${Date.now()}`,
      name: trimmed,
      icon: '📁',
      count: 1
    };

    const updatedBoards = [...boards, newBoard];
    setBoards(updatedBoards);
    setSelectedBoards(prev => {
      const next = new Set(prev);
      next.add(newBoard.id);
      return next;
    });

    // Persist save to backend collection
    toggleSavedItem({
      item_type: item.type === 'product' ? 'product' : 'reference',
      reference_id: item.type === 'product' ? undefined : item.id,
      product_id: item.type === 'product' ? item.id : undefined,
      project_collection: trimmed,
    }).catch(err => console.error('Error saving to new board', err));

    if (typeof window !== 'undefined') {
      try {
        const customOnly = updatedBoards.filter(b => b.id.startsWith('custom-'));
        localStorage.setItem('architect_ai_custom_boards', JSON.stringify(customOnly));
      } catch (e) {
        console.error('Error persisting custom board', e);
      }
    }

    setNewBoardName('');
    setIsCreating(false);
    setSuccessToast(`Created and saved to "${trimmed}"`);
    setTimeout(() => setSuccessToast(null), 2500);

    if (onSavedChange) {
      onSavedChange(true, trimmed);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-md bg-stone-900 border border-stone-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-stone-800">
          <div className="flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-amber-500 fill-amber-500" />
            <h3 className="font-semibold text-stone-100 text-lg">Save to Board</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-stone-400 hover:text-stone-200 hover:bg-stone-800 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Item Preview Strip */}
        <div className="flex items-center gap-3 px-6 py-3 bg-stone-950/60 border-b border-stone-800/80">
          {item.imageUrl ? (
            <img
              src={item.imageUrl}
              alt={item.title}
              className="w-12 h-12 rounded-lg object-cover border border-stone-800 shrink-0"
            />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-stone-800 flex items-center justify-center text-stone-500 shrink-0">
              <Folder className="w-5 h-5" />
            </div>
          )}
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-stone-200 truncate">{item.title}</p>
            <p className="text-xs text-stone-400 capitalize">{item.type || 'Architectural Inspiration'}</p>
          </div>
        </div>

        {/* Success Toast */}
        {successToast && (
          <div className="mx-6 mt-3 px-3 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs font-medium text-amber-400 flex items-center gap-2 animate-in fade-in slide-in-from-top-1">
            <Check className="w-4 h-4 text-amber-400" />
            <span>{successToast}</span>
          </div>
        )}

        {/* Board List */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
          {boards.map((board) => {
            const isSelected = selectedBoards.has(board.id);
            return (
              <button
                key={board.id}
                type="button"
                onClick={() => handleToggleBoard(board.id, board.name)}
                disabled={isSaving}
                className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all text-left ${
                  isSelected
                    ? 'bg-amber-500/10 border-amber-500/40 text-stone-100'
                    : 'bg-stone-950/40 border-stone-800/60 hover:border-stone-700 text-stone-300'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xl shrink-0">{board.icon}</span>
                  <div className="truncate">
                    <p className="text-sm font-medium truncate">{board.name}</p>
                    <p className="text-xs text-stone-500">{board.count} items</p>
                  </div>
                </div>

                <div
                  className={`w-6 h-6 rounded-full border flex items-center justify-center transition-colors shrink-0 ml-2 ${
                    isSelected
                      ? 'bg-amber-500 border-amber-500 text-stone-950'
                      : 'border-stone-700 bg-stone-900'
                  }`}
                >
                  {isSelected && <Check className="w-4 h-4 stroke-[3]" />}
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer: Create Board Form */}
        <div className="p-4 bg-stone-950/80 border-t border-stone-800">
          {isCreating ? (
            <form onSubmit={handleCreateBoard} className="space-y-3">
              <input
                type="text"
                value={newBoardName}
                onChange={(e) => setNewBoardName(e.target.value)}
                placeholder="Board name (e.g. Master Bedroom Courtyard)"
                autoFocus
                className="w-full px-3 py-2 bg-stone-900 border border-stone-700 rounded-lg text-sm text-stone-200 placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              />
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setIsCreating(false);
                    setNewBoardName('');
                  }}
                  className="px-3 py-1.5 text-xs text-stone-400 hover:text-stone-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newBoardName.trim()}
                  className="px-4 py-1.5 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-stone-950 text-xs font-semibold rounded-lg shadow transition-colors"
                >
                  Create & Save
                </button>
              </div>
            </form>
          ) : (
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-2 text-sm text-amber-500 hover:text-amber-400 font-medium transition-colors"
              >
                <FolderPlus className="w-4 h-4" />
                <span>Create new board</span>
              </button>
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-1.5 bg-stone-800 hover:bg-stone-700 text-stone-200 text-xs font-medium rounded-lg transition-colors"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
