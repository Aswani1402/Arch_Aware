"use client";

import React, { useRef, useEffect } from 'react';
import { ExternalLink, Play } from 'lucide-react';

interface YouTubeEmbedProps {
  videoId: string;
  title: string;
  sourceUrl: string;
  autoPlay?: boolean;
}

export const YouTubeEmbed: React.FC<YouTubeEmbedProps> = ({
  videoId,
  title,
  sourceUrl,
  autoPlay = false
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // If component unmounts, stop playback
  useEffect(() => {
    return () => {
      if (iframeRef.current) {
        iframeRef.current.src = "";
      }
    };
  }, []);

  return (
    <div className="relative w-full overflow-hidden rounded-xl bg-black shadow-md border border-arch-border">
      <div className="relative pt-[56.25%]">
        <iframe
          ref={iframeRef}
          src={`https://www.youtube.com/embed/${videoId}?autoplay=${autoPlay ? 1 : 0}&enablejsapi=1&rel=0&modestbranding=1`}
          title={title}
          allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="absolute inset-0 w-full h-full border-0"
        />
      </div>

      <div className="p-3 bg-stone-900 text-stone-300 text-xs flex items-center justify-between">
        <span className="truncate max-w-[70%]">Official YouTube Video Reference</span>
        <a
          href={sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-arch-terracotta hover:underline font-medium"
        >
          <span>Watch on YouTube</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};
