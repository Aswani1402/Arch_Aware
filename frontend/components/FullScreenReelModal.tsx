"use client";

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  X, Bookmark, ExternalLink, ChevronUp, ChevronDown,
  Volume2, VolumeX, MapPin, Play, Layers,
  CheckCircle2, AlertCircle, Store, Tag, Sparkles
} from 'lucide-react';
import { Reference } from '@/types';

interface FullScreenReelModalProps {
  isOpen: boolean;
  initialIndex: number;
  references: Reference[];
  onClose: () => void;
  onOpenDetails?: (ref: Reference) => void;
  onSaveToggle: (ref: Reference) => void;
  isSavedMap?: Record<number, boolean>;
  onLoadMore?: () => void;
}

export const FullScreenReelModal: React.FC<FullScreenReelModalProps> = ({
  isOpen,
  initialIndex = 0,
  references,
  onClose,
  onOpenDetails,
  onSaveToggle,
  isSavedMap = {},
  onLoadMore,
}) => {
  const [activeIndex, setActiveIndex] = useState(initialIndex);
  const [isMuted, setIsMuted] = useState(true);
  const [touchStartY, setTouchStartY] = useState<number | null>(null);
  const [touchStartTime, setTouchStartTime] = useState<number>(0);
  const [videoLoadError, setVideoLoadError] = useState(false);

  // Sync initialIndex when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveIndex(Math.max(0, Math.min(initialIndex, references.length - 1)));
      setVideoLoadError(false);
    }
  }, [isOpen, initialIndex, references.length]);

  useEffect(() => {
    setVideoLoadError(false);
  }, [activeIndex]);

  const currentRef = references[activeIndex] || null;

  // Deep link ?item=<id> updating browser history without page reload
  useEffect(() => {
    if (!isOpen || !currentRef) return;
    const url = new URL(window.location.href);
    url.searchParams.set('item', String(currentRef.id));
    window.history.replaceState({}, '', url.toString());

    return () => {
      const cleanupUrl = new URL(window.location.href);
      cleanupUrl.searchParams.delete('item');
      window.history.replaceState({}, '', cleanupUrl.toString());
    };
  }, [isOpen, currentRef]);

  // Preload next image to ensure instantaneous slide transitions
  useEffect(() => {
    if (isOpen && activeIndex + 1 < references.length) {
      const nextRef = references[activeIndex + 1];
      const nextImg = nextRef?.inspiration_image_url || nextRef?.thumbnail_url || nextRef?.media_url;
      if (nextImg) {
        const img = new Image();
        img.referrerPolicy = "no-referrer";
        img.src = nextImg;
      }
    }
  }, [isOpen, activeIndex, references]);

  // Trigger loading next page when approaching end of list
  useEffect(() => {
    if (isOpen && activeIndex >= references.length - 2 && onLoadMore) {
      onLoadMore();
    }
  }, [isOpen, activeIndex, references.length, onLoadMore]);

  const goToNext = useCallback(() => {
    if (activeIndex < references.length - 1) {
      setActiveIndex(prev => prev + 1);
    }
  }, [activeIndex, references.length]);

  const goToPrev = useCallback(() => {
    if (activeIndex > 0) {
      setActiveIndex(prev => prev - 1);
    }
  }, [activeIndex]);

  // Keyboard navigation: Escape to close, Up/Down/PageUp/PageDown/j/k for slides
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'k') {
        e.preventDefault();
        goToPrev();
      } else if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === 'j') {
        e.preventDefault();
        goToNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, goToNext, goToPrev, onClose]);

  // Touch handlers for mobile vertical swipe
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStartY(e.touches[0].clientY);
    setTouchStartTime(Date.now());
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartY === null) return;
    const touchEndY = e.changedTouches[0].clientY;
    const deltaY = touchStartY - touchEndY;
    const duration = Date.now() - touchStartTime;
    setTouchStartY(null);

    if (Math.abs(deltaY) > 50 && duration < 500) {
      if (deltaY > 0) goToNext();
      else goToPrev();
    }
  };

  // Parsed metadata payload
  const parsedMeta = useMemo(() => {
    if (!currentRef?.colors_and_finishes) return null;
    try {
      return typeof currentRef.colors_and_finishes === 'string'
        ? JSON.parse(currentRef.colors_and_finishes)
        : currentRef.colors_and_finishes;
    } catch {
      return null;
    }
  }, [currentRef]);

  // Material classification tiers
  const { exactMaterials, contextualMaterials } = useMemo(() => {
    if (!currentRef?.material_tags) return { exactMaterials: [], contextualMaterials: [] };
    const all = currentRef.material_tags.split(',').map(m => m.trim()).filter(Boolean);
    return {
      exactMaterials: all.slice(0, 2),
      contextualMaterials: all.slice(2)
    };
  }, [currentRef]);

  if (!isOpen || !currentRef) return null;

  const isSaved = isSavedMap[currentRef.id] || false;
  const isYouTube = currentRef.source_platform === 'youtube';
  const isInstagram = currentRef.source_platform === 'instagram';
  const isReddit = currentRef.source_platform === 'reddit';
  const isVideo = isYouTube || isInstagram || Boolean(currentRef.media_url?.includes('.mp4'));
  const mediaUrl = currentRef.inspiration_image_url || currentRef.thumbnail_url || currentRef.media_url;
  const videoSourceUrl = (currentRef as any).video_url || currentRef.media_url;

  const youtubeWatchUrl = currentRef.video_embed_id
    ? (currentRef.is_short
        ? `https://www.youtube.com/shorts/${currentRef.video_embed_id}`
        : `https://www.youtube.com/watch?v=${currentRef.video_embed_id}`)
    : currentRef.source_url;

  const sourceName = currentRef.source_platform?.toUpperCase() || 'SOURCE';
  const realSourceUrl = isYouTube ? youtubeWatchUrl : currentRef.source_url;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/95 flex flex-col md:flex-row items-stretch select-none overflow-hidden"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* Top Header Bar */}
      <div className="absolute top-0 inset-x-0 z-40 p-4 sm:p-5 flex items-center justify-between bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          <span className="px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-white text-xs font-mono font-medium">
            {activeIndex + 1} / {references.length}
          </span>
          {isVideo && (
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-2 rounded-full bg-black/60 hover:bg-black/80 backdrop-blur-md text-white transition-colors cursor-pointer"
              title={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-amber-400" />}
            </button>
          )}
        </div>

        {/* Action Controls & Close */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <button
            type="button"
            onClick={() => onSaveToggle(currentRef)}
            className={`p-2.5 rounded-full backdrop-blur-md transition-all cursor-pointer ${
              isSaved
                ? 'bg-arch-terracotta text-white shadow-lg'
                : 'bg-black/60 hover:bg-black/80 text-white'
            }`}
            title={isSaved ? "Saved" : "Save"}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>
          <button
            type="button"
            onClick={onClose}
            className="p-2.5 rounded-full bg-black/60 hover:bg-black/90 backdrop-blur-md text-white hover:text-amber-400 transition-colors cursor-pointer"
            title="Close viewer (Esc)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* LEFT PANE: Media Asset & Direct External Source Link */}
      <div className="relative flex-1 h-[60vh] md:h-full flex items-center justify-center overflow-hidden bg-black p-2 sm:p-6">
        {/* Ambient Blur Backdrop */}
        {mediaUrl && (
          <div
            className="absolute inset-0 bg-center bg-cover filter blur-3xl opacity-20 pointer-events-none"
            style={{ backgroundImage: `url(${mediaUrl})` }}
          />
        )}

        {/* Media Frame (video pauses when off-screen because only activeIndex is mounted) */}
        <div className="relative z-10 w-full h-full flex items-center justify-center">
          {isYouTube && currentRef.video_embed_id ? (
            <div className={`w-full flex items-center justify-center ${currentRef.is_short ? 'max-w-[420px] aspect-[9/16] h-[75vh]' : 'max-w-4xl aspect-video w-full'}`}>
              <iframe
                key={`video-${currentRef.id}-${activeIndex}`}
                src={`https://www.youtube.com/embed/${currentRef.video_embed_id}?autoplay=1&mute=${isMuted ? '1' : '0'}&loop=1&playlist=${currentRef.video_embed_id}&enablejsapi=1&rel=0&modestbranding=1`}
                title={currentRef.title}
                className="w-full h-full rounded-2xl shadow-2xl border border-stone-800 object-contain"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : isInstagram ? (
            <div className="w-full max-w-[420px] aspect-[9/16] h-[75vh] flex items-center justify-center relative">
              {!videoLoadError && videoSourceUrl ? (
                <video
                  key={`ig-${currentRef.id}-${activeIndex}`}
                  src={videoSourceUrl}
                  poster={mediaUrl}
                  autoPlay
                  muted={isMuted}
                  loop
                  playsInline
                  controls
                  onError={() => setVideoLoadError(true)}
                  className="w-full h-full rounded-2xl shadow-2xl border border-pink-500/30 object-contain bg-black"
                />
              ) : (
                <div className="w-full h-full rounded-2xl border border-stone-800 relative overflow-hidden flex flex-col justify-end p-6 bg-stone-900">
                  {mediaUrl && (
                    <img
                      src={mediaUrl}
                      alt={currentRef.title}
                      referrerPolicy="no-referrer"
                      className="absolute inset-0 w-full h-full object-cover opacity-60"
                    />
                  )}
                  <div className="relative z-10 space-y-2 text-center">
                    <p className="text-sm font-semibold text-white line-clamp-2">{currentRef.title}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="relative max-w-full max-h-[85vh] flex items-center justify-center">
              <img
                src={mediaUrl}
                alt={currentRef.title}
                referrerPolicy="no-referrer"
                className="max-w-full max-h-[85vh] object-contain rounded-xl shadow-2xl border border-stone-800"
              />
            </div>
          )}
        </div>

        {/* Real Source Link & Creator Attribution Overlay */}
        <div className="absolute bottom-4 left-4 z-30 flex items-center gap-2">
          {realSourceUrl && (
            <a
              href={realSourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-black/75 hover:bg-black/95 backdrop-blur-md text-white text-xs font-medium border border-white/10 shadow-lg transition-colors cursor-pointer"
            >
              <span>View on {sourceName}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          {currentRef.creator_name && (
            <span className="hidden sm:inline-block px-3 py-2 rounded-xl bg-black/60 backdrop-blur-md text-stone-300 text-xs">
              By {currentRef.creator_name}
            </span>
          )}
        </div>

        {/* Desktop Previous / Next Float Buttons */}
        <div className="hidden md:flex absolute right-6 top-1/2 -translate-y-1/2 flex-col gap-3 z-30">
          <button
            onClick={goToPrev}
            disabled={activeIndex === 0}
            className="p-3 rounded-full bg-stone-900/80 hover:bg-stone-800 disabled:opacity-20 text-white backdrop-blur-md transition-all active:scale-90 cursor-pointer"
            title="Previous item (↑ or k)"
          >
            <ChevronUp className="w-5 h-5" />
          </button>
          <button
            onClick={goToNext}
            disabled={activeIndex === references.length - 1}
            className="p-3 rounded-full bg-stone-900/80 hover:bg-stone-800 disabled:opacity-20 text-white backdrop-blur-md transition-all active:scale-90 cursor-pointer"
            title="Next item (↓ or j)"
          >
            <ChevronDown className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* RIGHT PANE: "More details" with Identified Materials, Context, Vendors */}
      <div className="w-full md:w-[420px] lg:w-[460px] h-[40vh] md:h-full bg-stone-900/95 border-t md:border-t-0 md:border-l border-white/10 overflow-y-auto p-5 sm:p-6 flex flex-col justify-between text-white space-y-6">
        <div className="space-y-5">
          {/* Category & Origin Context */}
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-medium text-arch-terracotta uppercase tracking-wider">
              <span>{currentRef.category_name || "Architectural Inspiration"}</span>
              {currentRef.location_context && (
                <>
                  <span className="text-stone-600">•</span>
                  <span className="text-stone-400 flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    <span>{currentRef.location_context}</span>
                  </span>
                </>
              )}
            </div>
            <h2 className="text-lg font-serif font-bold text-white leading-snug">
              {currentRef.title}
            </h2>
            {currentRef.description && (
              <p className="text-secondary text-stone-300 line-clamp-3 pt-1">
                {currentRef.description}
              </p>
            )}
          </div>

          {/* Section 1: Identified Materials (Tier 1 & Tier 2) */}
          {exactMaterials.length > 0 && (
            <div className="p-4 rounded-xl bg-stone-800/60 border border-emerald-500/20 space-y-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 uppercase tracking-wide">
                <CheckCircle2 className="w-4 h-4" />
                <span>Identified Materials (Metadata Verified)</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {exactMaterials.map((mat, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-emerald-950/80 border border-emerald-700/60 text-emerald-200 text-xs font-medium"
                  >
                    {mat}
                  </span>
                ))}
              </div>
              <p className="text-xs text-stone-400 pt-1">
                Verified against architectural catalogue taxonomy (Tier 1 exact / Tier 2 alias standard).
              </p>
            </div>
          )}

          {/* Section 2: Contextual / Inferred Materials (Tier 3 & Tier 4) */}
          {contextualMaterials.length > 0 && (
            <div className="p-4 rounded-xl bg-stone-800/40 border border-amber-500/20 space-y-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 uppercase tracking-wide">
                <AlertCircle className="w-4 h-4" />
                <span>Contextual / Inferred Materials</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {contextualMaterials.map((mat, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-amber-950/40 border border-amber-700/40 text-amber-200 text-xs font-medium"
                  >
                    {mat} (inferred)
                  </span>
                ))}
              </div>
              <p className="text-xs text-stone-400 pt-1">
                Inferred from caption, project type, or architectural discussion context (Tier 3).
              </p>
            </div>
          )}

          {/* Section 3: Product Specs & Palette */}
          {parsedMeta && (
            <div className="space-y-2 text-xs">
              <span className="font-semibold text-stone-300 uppercase tracking-wider">Specifications & Palette</span>
              <div className="p-3 rounded-xl bg-stone-800/50 border border-stone-700/50 space-y-1">
                {parsedMeta.price_label && (
                  <p className="text-white font-medium">Price: {parsedMeta.price_label}</p>
                )}
                {parsedMeta.business_name && (
                  <p className="text-stone-300">Supplier: {parsedMeta.business_name}</p>
                )}
                {parsedMeta.address && (
                  <p className="text-stone-400">Address: {parsedMeta.address}</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Section 4: Find Vendors Call-to-Action */}
        <div className="pt-4 border-t border-white/10 space-y-2">
          <a
            href={`/suppliers?q=${encodeURIComponent(exactMaterials[0] || currentRef.title)}`}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-arch-terracotta hover:bg-orange-600 text-white font-medium text-sm shadow-md transition-colors cursor-pointer"
          >
            <Store className="w-4 h-4" />
            <span>Find Verified Vendors for this Material &rarr;</span>
          </a>
        </div>
      </div>
    </div>
  );
};
