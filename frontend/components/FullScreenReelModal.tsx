"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  X, Bookmark, ExternalLink, ChevronUp, ChevronDown,
  Volume2, VolumeX, Sparkles, MapPin, Building2, Play, Layers,
  Compass, ArrowUpRight, CheckCircle2, Store
} from 'lucide-react';
import { Reference } from '@/types';

interface FullScreenReelModalProps {
  isOpen: boolean;
  initialIndex: number;
  references: Reference[];
  onClose: () => void;
  onOpenDetails: (ref: Reference) => void;
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
  const [isAnimating, setIsAnimating] = useState(false);
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

  // Trigger loading next page when approaching end
  useEffect(() => {
    if (isOpen && activeIndex >= references.length - 2 && onLoadMore) {
      onLoadMore();
    }
  }, [isOpen, activeIndex, references.length, onLoadMore]);

  const currentRef = references[activeIndex] || null;

  const goToNext = useCallback(() => {
    if (activeIndex < references.length - 1 && !isAnimating) {
      setIsAnimating(true);
      setActiveIndex(prev => prev + 1);
      setTimeout(() => setIsAnimating(false), 250);
    }
  }, [activeIndex, references.length, isAnimating]);

  const goToPrev = useCallback(() => {
    if (activeIndex > 0 && !isAnimating) {
      setIsAnimating(true);
      setActiveIndex(prev => prev - 1);
      setTimeout(() => setIsAnimating(false), 250);
    }
  }, [activeIndex, isAnimating]);

  // Keyboard navigation: Escape, ArrowUp, ArrowDown, PageUp, PageDown, 'k', 'j', Space
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'k') {
        e.preventDefault();
        goToPrev();
      } else if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === 'j' || e.key === ' ') {
        e.preventDefault();
        goToNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, goToNext, goToPrev, onClose]);

  // Mouse wheel scroll navigation on desktop (with 350ms throttle)
  useEffect(() => {
    if (!isOpen) return;

    let lastWheelTime = 0;
    const handleWheel = (e: WheelEvent) => {
      const now = Date.now();
      if (now - lastWheelTime < 350) return;
      if (Math.abs(e.deltaY) > 30) {
        lastWheelTime = now;
        if (e.deltaY > 0) {
          goToNext();
        } else {
          goToPrev();
        }
      }
    };

    window.addEventListener('wheel', handleWheel, { passive: true });
    return () => window.removeEventListener('wheel', handleWheel);
  }, [isOpen, goToNext, goToPrev]);

  // Touch Swipe Handlers for mobile (Swipe up -> Next reel, Swipe down -> Prev reel)
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

    // Swipe threshold: > 40px vertical motion within 500ms
    if (Math.abs(deltaY) > 40 && duration < 500) {
      if (deltaY > 0) {
        goToNext();
      } else {
        goToPrev();
      }
    }
  };

  if (!isOpen || !currentRef) return null;

  const isSaved = isSavedMap[currentRef.id] || false;
  const isYouTube = currentRef.source_platform === 'youtube';
  const isInstagram = currentRef.source_platform === 'instagram';
  const isX = currentRef.source_platform === 'x' || currentRef.source_platform === 'twitter';
  const isReddit = currentRef.source_platform === 'reddit';
  const isVideo = isYouTube || isInstagram || Boolean(currentRef.media_url?.includes('.mp4'));
  const mediaUrl = currentRef.inspiration_image_url || currentRef.thumbnail_url || currentRef.media_url;
  const videoSourceUrl = (currentRef as any).video_url || currentRef.media_url;
  const youtubeWatchUrl = currentRef.video_embed_id
    ? (currentRef.is_short
        ? `https://www.youtube.com/shorts/${currentRef.video_embed_id}`
        : `https://www.youtube.com/watch?v=${currentRef.video_embed_id}`)
    : currentRef.source_url;

  return (
    <div
      className="fixed inset-0 z-50 bg-black flex items-center justify-center select-none overflow-hidden"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* Top Header Bar */}
      <div className="absolute top-0 inset-x-0 z-40 p-4 sm:p-6 flex items-center justify-between bg-gradient-to-b from-black/85 via-black/40 to-transparent pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          <span className="px-2.5 py-1 rounded-full bg-white/20 backdrop-blur-md text-white text-xs font-mono font-medium">
            {activeIndex + 1} / {references.length}
          </span>
          {isVideo && (
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-2 rounded-full bg-black/60 hover:bg-black/80 backdrop-blur-md text-white transition-colors"
              title={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-amber-400" />}
            </button>
          )}
        </div>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="p-2.5 rounded-full bg-black/60 hover:bg-black/90 backdrop-blur-md text-white hover:text-amber-400 transition-colors pointer-events-auto"
          title="Return to feed (Esc)"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Main Reel Viewport Container */}
      <div className="relative w-full h-full max-w-lg md:max-w-xl mx-auto flex items-center justify-center overflow-hidden bg-black">
        {/* Ambient Blurred Backdrop for landscape or varying aspect media */}
        {mediaUrl && (
          <div
            className="absolute inset-0 bg-center bg-cover filter blur-3xl opacity-25 transform scale-110 pointer-events-none"
            style={{ backgroundImage: `url(${mediaUrl})` }}
          />
        )}

        {/* Active Media Container: ONLY active video plays to prevent concurrent playback! */}
        <div className="relative z-10 w-full h-full flex items-center justify-center p-2 sm:p-4">
          {isYouTube && currentRef.video_embed_id ? (
            <div className={`w-full flex items-center justify-center ${currentRef.is_short ? 'max-w-[420px] aspect-[9/16] h-[85vh]' : 'max-w-4xl aspect-video w-full'}`}>
              <iframe
                key={`video-${currentRef.id}-${activeIndex}`}
                src={`https://www.youtube.com/embed/${currentRef.video_embed_id}?autoplay=1&mute=${isMuted ? '1' : '0'}&loop=1&playlist=${currentRef.video_embed_id}&enablejsapi=1&rel=0&modestbranding=1&playsinline=1`}
                title={currentRef.title}
                className="w-full h-full rounded-2xl shadow-2xl border border-stone-800/60 object-contain pointer-events-auto"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              />
            </div>
          ) : isInstagram ? (
            <div className="w-full max-w-[420px] aspect-[9/16] h-[85vh] flex items-center justify-center relative">
              {!videoLoadError && videoSourceUrl ? (
                <video
                  key={`ig-reel-${currentRef.id}-${activeIndex}`}
                  src={videoSourceUrl}
                  poster={mediaUrl}
                  autoPlay
                  muted={isMuted}
                  loop
                  playsInline
                  controls
                  onError={() => setVideoLoadError(true)}
                  className="w-full h-full rounded-2xl shadow-2xl border border-pink-500/30 object-contain pointer-events-auto bg-black"
                />
              ) : (
                <div className="w-full h-full rounded-2xl border border-pink-500/40 relative overflow-hidden flex flex-col justify-end p-6 bg-stone-950">
                  {mediaUrl && (
                    <img
                      src={mediaUrl}
                      alt={currentRef.title}
                      referrerPolicy="no-referrer"
                      className="absolute inset-0 w-full h-full object-cover opacity-60"
                    />
                  )}
                  <div className="relative z-10 space-y-3 text-center">
                    <span className="inline-block px-3 py-1 rounded-full bg-pink-600 text-white text-xs font-semibold">
                      Instagram Reel Preview
                    </span>
                    <p className="text-xs text-stone-200 line-clamp-2">
                      {currentRef.title}
                    </p>
                    <a
                      href={currentRef.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-gradient-to-r from-pink-600 to-rose-600 text-white text-xs font-bold shadow-lg hover:from-pink-500 hover:to-rose-500 transition-all active:scale-95 pointer-events-auto"
                    >
                      <span>Watch Full Reel on Instagram</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
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
                className="max-w-full max-h-[85vh] object-contain rounded-xl shadow-2xl border border-stone-800/40"
              />
            </div>
          )}
        </div>

        {/* Bottom Content Metadata Overlay */}
        <div className="absolute bottom-0 inset-x-0 z-30 p-5 sm:p-6 bg-gradient-to-t from-black/95 via-black/75 to-transparent flex flex-col justify-end pointer-events-none pr-24">
          <div className="space-y-2 pointer-events-auto max-w-xl">
            {/* Badges Bar: Media Type, Category, Shorts/Duration */}
            <div className="flex flex-wrap items-center gap-1.5">
              {isVideo ? (
                currentRef.is_short ? (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-500/90 text-white text-xs font-bold tracking-wide shadow-sm">
                    <Play className="w-3 h-3 fill-current" />
                    <span>Short • {currentRef.video_duration || '<60s'}</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-stone-900/90 border border-stone-700 text-stone-200 text-xs font-semibold tracking-wide">
                    <Play className="w-3 h-3 text-amber-400 fill-amber-400" />
                    <span>Video • {currentRef.video_duration || 'Walkthrough'}</span>
                  </span>
                )
              ) : (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-stone-900/90 border border-stone-700 text-stone-300 text-xs font-semibold tracking-wide">
                  <Layers className="w-3 h-3 text-amber-400" />
                  <span>Architectural Image</span>
                </span>
              )}

              {currentRef.category_name && (
                <span className="inline-block px-2.5 py-0.5 rounded-full bg-amber-500 text-stone-950 text-xs font-bold uppercase tracking-wider shadow-sm">
                  {currentRef.category_name}
                </span>
              )}

              {currentRef.source_domain && (
                <span className="inline-block px-2 py-0.5 rounded-md bg-stone-900/80 border border-stone-800 text-stone-400 text-xs font-mono">
                  {currentRef.source_domain}
                </span>
              )}
            </div>

            {/* Title */}
            <h2 className="font-serif text-base sm:text-lg font-bold text-white leading-tight line-clamp-2 drop-shadow-md">
              {currentRef.title}
            </h2>

            {/* Creator / Architect info */}
            <div className="flex items-center gap-2 text-xs text-stone-300">
              <span className="font-semibold text-stone-200">
                {currentRef.architect_name || currentRef.creator_name || "Architectural Studio"}
              </span>
              {currentRef.location_context && (
                <>
                  <span className="text-stone-500">•</span>
                  <span className="text-stone-400 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-amber-400" />
                    <span>{currentRef.location_context.split(',')[0]}</span>
                  </span>
                </>
              )}
            </div>

            {/* Colors and Finishes if present */}
            {currentRef.colors_and_finishes && (
              <p className="text-xs text-stone-300 flex items-center gap-1.5 pt-0.5">
                <span className="text-amber-400/90 font-medium">Palette & Finish:</span>
                <span className="text-stone-300">{currentRef.colors_and_finishes}</span>
              </p>
            )}

            {/* Image Attribution if present */}
            {!isVideo && currentRef.image_attribution && (
              <p className="text-xs text-stone-400 italic">
                Attribution: {currentRef.image_attribution}
              </p>
            )}

            {/* Detected / Explicit Materials vs Uncertain Inferences */}
            {currentRef.material_tags && (
              <div className="space-y-1.5 pt-1">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Identified Materials:</span>
                  </span>
                  {currentRef.material_tags.split(',').slice(0, 3).map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-emerald-950/70 border border-emerald-800/80 text-emerald-300 text-xs font-mono"
                    >
                      {tag.trim()}
                    </span>
                  ))}
                </div>

                {currentRef.material_tags.split(',').length > 3 && (
                  <div className="flex flex-wrap items-center gap-1.5 text-xs text-stone-400">
                    <span className="italic text-stone-400">Contextual / Inferred:</span>
                    {currentRef.material_tags.split(',').slice(3, 5).map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded bg-stone-900 border border-stone-800 text-stone-400 text-xs font-mono"
                      >
                        {tag.trim()} (inferred)
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Direct Supplier Discovery Action */}
            <div className="pt-2 flex items-center gap-2">
              <button
                onClick={() => onOpenDetails(currentRef)}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-arch-terracotta hover:bg-orange-600 text-white text-xs font-semibold shadow-md transition-colors"
                title="View local suppliers & verified product matches"
              >
                <Store className="w-3.5 h-3.5" />
                <span>Find Suppliers for this Material &rarr;</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right-Rail Floating Action Buttons */}
        <div className="absolute right-3 bottom-20 z-40 flex flex-col items-center gap-4 pointer-events-auto">
          {/* FEATURE 4: Single Persistent Save Button (Heart/Like completely removed) */}
          <button
            onClick={() => onSaveToggle(currentRef)}
            className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
            title={isSaved ? "Saved to Moodboard (Click to remove)" : "Save to Moodboard"}
          >
            <div className={`p-3 rounded-full backdrop-blur-md transition-all ${
              isSaved
                ? 'bg-amber-500 text-stone-950 font-bold shadow-lg scale-105'
                : 'bg-stone-900/80 text-white group-hover:text-amber-400 group-hover:bg-stone-800'
            }`}>
              <Bookmark className={`w-5 h-5 ${isSaved ? 'fill-current' : ''}`} />
            </div>
            <span className={`text-xs font-semibold drop-shadow ${isSaved ? 'text-amber-400' : 'text-stone-300'}`}>
              {isSaved ? 'Saved' : 'Save'}
            </span>
          </button>

          {/* FEATURE 6: Replace Three-Dot with clearly labelled "More Details" button */}
          <button
            onClick={() => onOpenDetails(currentRef)}
            className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
            title="View verified materials & local suppliers"
          >
            <div className="p-3 rounded-full bg-stone-900/80 hover:bg-amber-500 hover:text-stone-950 text-stone-200 font-bold backdrop-blur-md border border-stone-700/80 hover:border-amber-500 shadow-lg transition-all">
              <Layers className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold text-stone-300 group-hover:text-amber-400 drop-shadow text-center">
              More Details
            </span>
          </button>

          {/* Open on YouTube, Instagram, X, Reddit, or Source */}
          {isYouTube && currentRef.video_embed_id ? (
            <a
              href={youtubeWatchUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
              title="Open video on YouTube"
            >
              <div className="p-3 rounded-full bg-rose-600/90 hover:bg-rose-500 backdrop-blur-md text-white transition-colors shadow-md">
                <Play className="w-5 h-5 fill-current ml-0.5" />
              </div>
              <span className="text-xs font-medium text-stone-300 drop-shadow">
                YouTube
              </span>
            </a>
          ) : isInstagram ? (
            <a
              href={currentRef.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
              title="Open Reel on Instagram"
            >
              <div className="p-3 rounded-full bg-gradient-to-tr from-amber-500 via-pink-500 to-rose-500 text-white shadow-md hover:opacity-90 transition-opacity">
                <ExternalLink className="w-5 h-5" />
              </div>
              <span className="text-xs font-medium text-stone-300 drop-shadow">
                Instagram
              </span>
            </a>
          ) : isX ? (
            <a
              href={currentRef.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
              title="Open on X (Twitter)"
            >
              <div className="p-3 rounded-full bg-black border border-stone-700 text-white shadow-md hover:bg-stone-900 transition-colors">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </div>
              <span className="text-xs font-medium text-stone-300 drop-shadow">
                X
              </span>
            </a>
          ) : isReddit ? (
            <a
              href={currentRef.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
              title="Open Discussion on Reddit"
            >
              <div className="p-3 rounded-full bg-orange-600 text-white shadow-md hover:bg-orange-500 transition-colors">
                <ExternalLink className="w-5 h-5" />
              </div>
              <span className="text-xs font-medium text-stone-300 drop-shadow">
                Reddit
              </span>
            </a>
          ) : currentRef.source_url ? (
            <a
              href={currentRef.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center gap-1 group active:scale-90 transition-transform"
              title="Open original project source"
            >
              <div className="p-3 rounded-full bg-stone-900/80 backdrop-blur-md text-white group-hover:text-amber-400 group-hover:bg-stone-800 transition-colors">
                <ExternalLink className="w-5 h-5" />
              </div>
              <span className="text-xs font-medium text-stone-300 drop-shadow">
                Source
              </span>
            </a>
          ) : null}
        </div>

        {/* Desktop Up / Down Navigation Controls */}
        <div className="hidden md:flex absolute right-4 top-1/2 -translate-y-1/2 flex-col gap-3 z-30">
          <button
            onClick={goToPrev}
            disabled={activeIndex === 0}
            className="p-2.5 rounded-full bg-stone-900/80 hover:bg-stone-800 disabled:opacity-30 text-white backdrop-blur-md transition-all active:scale-90"
            title="Previous item (↑ or k)"
          >
            <ChevronUp className="w-5 h-5" />
          </button>
          <button
            onClick={goToNext}
            disabled={activeIndex === references.length - 1}
            className="p-2.5 rounded-full bg-stone-900/80 hover:bg-stone-800 disabled:opacity-30 text-white backdrop-blur-md transition-all active:scale-90"
            title="Next item (↓ or j)"
          >
            <ChevronDown className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
