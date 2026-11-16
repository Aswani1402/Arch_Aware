"use client";

import React, { useState } from 'react';
import {
  Bookmark, Play, ExternalLink, MessageSquare,
  ShoppingBag, CheckCircle2, MapPin
} from 'lucide-react';
import { Reference } from '@/types';
import { SourceBadge } from './SourceBadge';

interface PinterestMasonryFeedProps {
  references: Reference[];
  onOpenDetails: (ref: Reference) => void;
  onSaveToggle: (ref: Reference) => void;
  onSelectCard?: (ref: Reference, index: number) => void;
  isSavedMap?: Record<number, boolean>;
  onLoadMore?: () => void;
  hasMore?: boolean;
  loading?: boolean;
}

function getAspectRatioClass(id: number, isShort?: boolean) {
  if (isShort) return 'aspect-[9/16]';
  const mod = Math.abs(id) % 5;
  switch (mod) {
    case 0:
      return 'aspect-[3/4]';
    case 1:
      return 'aspect-[4/5]';
    case 2:
      return 'aspect-[1/1]';
    case 3:
      return 'aspect-[2/3]';
    default:
      return 'aspect-[16/11]';
  }
}

interface MasonryCardItemProps {
  refItem: Reference;
  index: number;
  isSaved: boolean;
  onOpenDetails: (ref: Reference) => void;
  onSaveToggle: (ref: Reference) => void;
  onSelectCard?: (ref: Reference, index: number) => void;
}

const MasonryCardItem: React.FC<MasonryCardItemProps> = ({
  refItem,
  index,
  isSaved,
  onOpenDetails,
  onSaveToggle,
  onSelectCard
}) => {
  const [imgFailed, setImgFailed] = useState(false);
  const isShoppingProduct = refItem.source_platform === 'google_shopping' || refItem.content_type === 'shopping_product';
  const isDiscussion = refItem.source_platform === 'reddit' || refItem.content_type === 'architectural_discussion';
  const isReel = refItem.source_platform === 'instagram' || Boolean(refItem.is_short);
  const isVideo = Boolean(refItem.video_embed_id || isReel || refItem.source_platform === 'youtube' || refItem.media_url?.includes('.mp4'));
  const aspectClass = getAspectRatioClass(refItem.id, refItem.is_short);
  const rawImageUrl = refItem.inspiration_image_url || refItem.thumbnail_url || refItem.media_url;
  const imageUrl = (typeof rawImageUrl === 'string' && rawImageUrl.startsWith('http')) ? rawImageUrl : null;

  let meta: any = null;
  if (refItem.colors_and_finishes) {
    try {
      meta = JSON.parse(refItem.colors_and_finishes);
    } catch {
      meta = null;
    }
  }

  // 1. Reddit Discussion Card Variant
  if (isDiscussion && (!imageUrl || imgFailed)) {
    return (
      <div
        tabIndex={0}
        role="button"
        onClick={() => onSelectCard ? onSelectCard(refItem, index) : onOpenDetails(refItem)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSelectCard ? onSelectCard(refItem, index) : onOpenDetails(refItem);
          }
        }}
        className="break-inside-avoid group relative rounded-2xl overflow-hidden bg-white dark:bg-arch-dark-card border border-orange-200/60 dark:border-orange-900/40 shadow-card hover:shadow-card-hover dark:shadow-card-dark dark:hover:shadow-card-dark-hover transition-all duration-300 cursor-pointer flex flex-col p-5 space-y-4 focus:outline-hidden focus:ring-2 focus:ring-arch-terracotta"
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs text-orange-600 dark:text-orange-400 font-semibold uppercase tracking-wider">
            <MessageSquare className="w-3.5 h-3.5 shrink-0" />
            <span>Reddit Discussion</span>
          </div>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onSaveToggle(refItem);
            }}
            className={`p-2 rounded-xl transition-all ${
              isSaved
                ? 'bg-arch-terracotta text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-muted'
            }`}
            title={isSaved ? "Saved" : "Save"}
            aria-label="Save discussion"
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>
        </div>

        <div className="space-y-2">
          <h3 className="font-serif font-semibold text-arch-charcoal dark:text-stone-100 text-card-title leading-snug group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors line-clamp-3">
            {refItem.title}
          </h3>
          {refItem.description && (
            <p className="text-secondary text-arch-muted dark:text-arch-dark-muted line-clamp-4 leading-relaxed italic">
              &ldquo;{refItem.description}&rdquo;
            </p>
          )}
        </div>

        <div className="pt-3 border-t border-arch-border dark:border-arch-dark-border flex items-center justify-between text-secondary text-arch-muted dark:text-arch-dark-muted">
          <span>{refItem.creator_name || "r/architecture"}</span>
          {refItem.source_url && (
            <a
              href={refItem.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-arch-terracotta font-medium hover:underline inline-flex items-center gap-1"
            >
              <span>Reddit</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>
    );
  }

  // 2. Google Shopping Product Card Variant (Shopping items never appear in vendors)
  if (isShoppingProduct && imageUrl && !imgFailed) {
    const seller = meta?.seller || refItem.creator_name || 'Google Shopping';
    const price = meta?.price_label || (meta?.price ? `₹${meta.price}` : null);

    return (
      <div
        tabIndex={0}
        role="button"
        onClick={() => onSelectCard ? onSelectCard(refItem, index) : onOpenDetails(refItem)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSelectCard ? onSelectCard(refItem, index) : onOpenDetails(refItem);
          }
        }}
        className="break-inside-avoid group relative rounded-2xl overflow-hidden bg-white dark:bg-arch-dark-card border border-arch-border dark:border-arch-dark-border shadow-card hover:shadow-card-hover dark:shadow-card-dark dark:hover:shadow-card-dark-hover transition-all duration-300 cursor-pointer flex flex-col focus:outline-hidden focus:ring-2 focus:ring-arch-terracotta"
      >
        <div className={`relative w-full ${aspectClass} overflow-hidden bg-stone-100 dark:bg-stone-900`}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageUrl}
            alt={refItem.title}
            loading={index <= 4 ? "eager" : "lazy"}
            referrerPolicy="no-referrer"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-102"
            onError={() => setImgFailed(true)}
          />
          <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none z-10">
            <span className="px-2.5 py-1 rounded-full bg-emerald-950/70 backdrop-blur-md text-emerald-200 text-xs font-semibold flex items-center gap-1 shadow-xs">
              <ShoppingBag className="w-3.5 h-3.5 text-emerald-400" />
              <span>Product</span>
            </span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onSaveToggle(refItem);
              }}
              className={`p-2 rounded-xl backdrop-blur-md pointer-events-auto transition-all ${
                isSaved ? 'bg-arch-terracotta text-white' : 'bg-black/40 hover:bg-black/70 text-white'
              }`}
              title={isSaved ? "Saved" : "Save"}
              aria-label="Save product"
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>

        <div className="p-4 space-y-2">
          <h3 className="font-semibold text-arch-charcoal dark:text-stone-100 text-card-title leading-snug line-clamp-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
            {refItem.title}
          </h3>
          <div className="flex items-center justify-between text-secondary pt-1">
            {price && (
              <span className="font-bold text-emerald-700 dark:text-emerald-400 text-body-base">
                {price}
              </span>
            )}
            <span className="text-arch-muted dark:text-arch-dark-muted truncate max-w-[150px]">
              {seller}
            </span>
          </div>
          {refItem.source_url && (
            <div className="pt-2 border-t border-arch-border dark:border-arch-dark-border flex justify-end">
              <a
                href={refItem.source_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 hover:underline inline-flex items-center gap-1"
              >
                <span>View Store</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          )}
        </div>
      </div>
    );
  }

  // 3. Drop cards without usable image (Requirement: Hide any card whose image fails to load)
  if (!imageUrl || imgFailed) {
    return null;
  }

  // Extract up to 3 relevant tags
  const tags = (refItem.material_tags || '')
    .split(',')
    .map(t => t.trim())
    .filter(Boolean)
    .slice(0, 3);

  // 4. Standard Clean Architectural Inspiration Card (Image Only by default)
  return (
    <div
      tabIndex={0}
      role="button"
      onClick={() => onSelectCard ? onSelectCard(refItem, index) : onOpenDetails(refItem)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelectCard ? onSelectCard(refItem, index) : onOpenDetails(refItem);
        }
      }}
      className="break-inside-avoid group relative rounded-2xl overflow-hidden bg-stone-100 dark:bg-stone-900 border border-black/5 dark:border-white/5 shadow-xs hover:shadow-xl transition-all duration-300 cursor-pointer focus:outline-hidden focus:ring-2 focus:ring-arch-terracotta"
    >
      {/* Media container */}
      <div className={`relative w-full ${aspectClass} overflow-hidden`}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={imageUrl}
          alt={refItem.title}
          loading={index <= 4 ? "eager" : "lazy"}
          referrerPolicy="no-referrer"
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-102"
          onError={() => setImgFailed(true)}
        />

        {/* Video Duration Pill (always subtle if video) */}
        {isVideo && (
          <div className="absolute top-3 left-3 flex items-center gap-1 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md text-white text-xs font-medium z-10">
            <Play className="w-3 h-3 fill-white" />
            <span>{isReel ? "Video" : (refItem.video_duration || "Video")}</span>
          </div>
        )}

        {/* Hover AND Keyboard Focus Overlay: 1-line description, source, max 3 tags */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/35 to-transparent opacity-0 group-hover:opacity-100 group-focus:opacity-100 group-focus-within:opacity-100 transition-opacity duration-200 flex flex-col justify-between p-4 z-20 pointer-events-none">
          {/* Top Row: Source Badge & Bookmark Save */}
          <div className="flex items-center justify-between pointer-events-auto">
            <SourceBadge
              platform={refItem.source_platform || 'pinterest'}
              size="sm"
              creatorName={refItem.creator_name}
            />
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onSaveToggle(refItem);
              }}
              className={`p-2 rounded-xl backdrop-blur-md transition-all active:scale-95 ${
                isSaved
                  ? 'bg-arch-terracotta text-white shadow-xs'
                  : 'bg-black/50 hover:bg-black/80 text-white'
              }`}
              title={isSaved ? "Saved" : "Save"}
              aria-label="Save inspiration"
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
            </button>
          </div>

          {/* Bottom Row: 1-line description & max 3 relevant tags */}
          <div className="space-y-1.5 pointer-events-auto">
            <p className="text-secondary font-medium text-white truncate drop-shadow-xs">
              {refItem.title || refItem.description || "Architectural Inspiration"}
            </p>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {tags.map((tag, tIdx) => (
                  <span
                    key={tIdx}
                    className="px-2 py-0.5 rounded-md bg-white/20 backdrop-blur-md text-white text-xs font-medium"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export const PinterestMasonryFeed: React.FC<PinterestMasonryFeedProps> = ({
  references,
  onOpenDetails,
  onSaveToggle,
  onSelectCard,
  isSavedMap = {},
  onLoadMore,
  hasMore = false,
  loading = false,
}) => {
  return (
    <div className="w-full space-y-10">
      {/* Full-width masonry feed, 4-5 columns on wide desktop */}
      <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 xl:columns-5 2xl:columns-5 gap-4 space-y-4">
        {references.map((ref, index) => (
          <MasonryCardItem
            key={ref.id}
            refItem={ref}
            index={index}
            isSaved={Boolean(isSavedMap[ref.id])}
            onOpenDetails={onOpenDetails}
            onSaveToggle={onSaveToggle}
            onSelectCard={onSelectCard}
          />
        ))}
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center pt-6 pb-16">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="px-8 py-3 bg-arch-charcoal hover:bg-stone-900 dark:bg-stone-800 dark:hover:bg-stone-700 disabled:opacity-50 text-white text-body-base font-semibold rounded-2xl border border-transparent shadow-md transition-all active:scale-95 cursor-pointer"
          >
            {loading ? 'Discovering more architectural references...' : 'Load More Inspiration'}
          </button>
        </div>
      )}
    </div>
  );
};
