"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Bookmark, MapPin, Layers, Play, ImageOff, CheckCircle2,
  Sparkles, ArrowRight, User
} from 'lucide-react';
import { Reference } from '@/types';
import { SourceBadge } from './SourceBadge';
import { toggleSavedItem, hasAuthToken } from '@/lib/api';

interface FeedCardProps {
  reference: Reference;
  onSelect?: (ref: Reference) => void;
}

export const FeedCard: React.FC<FeedCardProps> = ({ reference, onSelect }) => {
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [imgError, setImgError] = useState(false);

  const tags = reference.material_tags ? reference.material_tags.split(',').slice(0, 3) : [];
  const imageUrl = reference.inspiration_image_url || reference.thumbnail_url || reference.media_url;
  const isVideo = reference.source_platform === 'youtube' || Boolean(reference.video_embed_id);

  const handleSave = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!hasAuthToken()) {
      alert('Please sign in to save references to your Moodboard.');
      return;
    }
    setIsSaving(true);
    try {
      const res = await toggleSavedItem({
        item_type: 'reference',
        reference_id: reference.id,
        project_collection: 'Moodboard'
      });
      setIsSaved(res.saved);
    } catch (err) {
      console.error("Save error", err);
    } finally {
      setIsSaving(false);
    }
  };

  const getIdentificationBadge = () => {
    const status = reference.product_match_status;
    if (status === 'verified_match') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-secondary font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
          <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
          <span>Confirmed in Docs</span>
        </span>
      );
    }
    if (status === 'commercial_specification' || status === 'probable_match') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-secondary font-semibold bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          <Sparkles className="w-3 h-3 text-amber-600 dark:text-amber-400" />
          <span>Likely Specification</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-secondary font-medium bg-stone-50 dark:bg-arch-dark-surface text-stone-600 dark:text-stone-300 border border-stone-200 dark:border-arch-dark-border">
        <span>Aesthetic Reference</span>
      </span>
    );
  };

  return (
    <div
      onClick={() => onSelect ? onSelect(reference) : null}
      className="group relative bg-white dark:bg-arch-dark-card rounded-2xl overflow-hidden border border-arch-border dark:border-arch-dark-border hover:border-arch-terracotta/40 dark:hover:border-arch-terracotta/40 shadow-card hover:shadow-card-hover dark:shadow-card-dark dark:hover:shadow-card-dark-hover transition-all duration-300 flex flex-col cursor-pointer"
    >
      {/* Media / In-Situ Project Image */}
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-stone-100 dark:bg-stone-850">
        {imgError || !imageUrl ? (
          <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-stone-50 dark:bg-arch-dark-surface text-arch-muted text-center">
            <ImageOff className="w-8 h-8 text-stone-300 dark:text-stone-600 mb-2" />
            <span className="text-secondary font-medium text-arch-charcoal dark:text-stone-300">
              {reference.source_platform === 'reddit' ? 'Architectural Discussion' : 'Image source unavailable'}
            </span>
            <span className="text-secondary text-arch-muted dark:text-arch-dark-muted mt-0.5">Project attribution preserved</span>
          </div>
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imageUrl}
            alt={reference.title}
            referrerPolicy="no-referrer"
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-104"
            loading="lazy"
          />
        )}

        {/* Video Indicator */}
        {isVideo && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-12 h-12 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center text-white shadow-md group-hover:bg-arch-terracotta transition-colors duration-200">
              <Play className="w-5 h-5 fill-current ml-0.5" />
            </div>
          </div>
        )}

        {/* Source Badge (Top Left) */}
        <div className="absolute top-3 left-3 z-10">
          <SourceBadge
            platform={reference.source_platform}
            sourceUrl={reference.source_url}
            creatorName={reference.creator_name}
          />
        </div>

        {/* Bookmark Action (Top Right) */}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`absolute top-3 right-3 z-10 p-2.5 rounded-xl backdrop-blur-md transition-all ${
            isSaved
              ? 'bg-arch-terracotta text-white shadow-md'
              : 'bg-black/35 hover:bg-black/60 text-white'
          }`}
          title={isSaved ? "Remove from moodboard" : "Save project"}
          aria-label="Save"
        >
          <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
        </button>

        {/* Identified Materials Indicator (Bottom Left) */}
        {reference.matched_products_count > 0 && (
          <div className="absolute bottom-3 left-3 z-10 flex items-center gap-1.5 px-3 py-1 rounded-full text-secondary font-semibold bg-white/95 dark:bg-stone-900/95 text-arch-charcoal dark:text-stone-100 shadow-xs backdrop-blur-xs border border-stone-200 dark:border-stone-700">
            <Layers className="w-3.5 h-3.5 text-arch-terracotta" />
            <span>{reference.matched_products_count} Identified Material{reference.matched_products_count > 1 ? 's' : ''}</span>
          </div>
        )}
      </div>

      {/* Editorial Content Info */}
      <div className="p-5 flex flex-col flex-grow justify-between bg-white dark:bg-arch-dark-card">
        <div className="space-y-2">
          {/* Category & Status */}
          <div className="flex items-center justify-between text-secondary gap-2">
            <span className="font-semibold text-arch-terracotta uppercase tracking-wider text-secondary truncate">
              {reference.architectural_style || reference.category_name || "Architecture"}
            </span>
            {getIdentificationBadge()}
          </div>

          {/* Project Title */}
          <h3 className="text-card-title font-semibold text-arch-charcoal dark:text-stone-100 leading-snug group-hover:text-arch-terracotta dark:group-hover:text-amber-400 transition-colors line-clamp-2">
            {reference.title}
          </h3>

          {/* Architect / Firm Attribution */}
          {reference.architect_name && (
            <div className="flex items-center gap-1.5 text-secondary text-arch-muted dark:text-arch-dark-muted font-medium">
              <User className="w-3.5 h-3.5 text-stone-400 shrink-0" />
              <span className="truncate">{reference.architect_name}</span>
            </div>
          )}

          {/* Location Context */}
          {(reference.location_context || reference.region || reference.country) && (
            <div className="flex items-center gap-1.5 text-secondary text-arch-muted dark:text-arch-dark-muted">
              <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0" />
              <span className="truncate">
                {[reference.region, reference.country].filter(Boolean).join(', ') || reference.location_context}
              </span>
            </div>
          )}
        </div>

        {/* Footer: Tags & Explore Link */}
        <div className="mt-4 pt-3.5 border-t border-arch-border dark:border-arch-dark-border flex items-center justify-between">
          <div className="flex flex-wrap gap-1.5">
            {tags.map((tag) => (
              <span
                key={tag}
                className="text-secondary px-2.5 py-0.5 rounded-md bg-stone-100 dark:bg-arch-dark-surface text-arch-muted dark:text-arch-dark-muted font-mono"
              >
                #{tag.trim().replace(/_/g, ' ')}
              </span>
            ))}
          </div>

          <Link
            href={`/reference/${reference.slug || reference.id}`}
            onClick={(e) => e.stopPropagation()}
            className="text-secondary font-semibold text-arch-charcoal dark:text-stone-200 hover:text-arch-terracotta dark:hover:text-amber-400 transition-colors ml-2 shrink-0 flex items-center gap-1"
          >
            <span>Explore</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};
