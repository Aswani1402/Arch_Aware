"use client";

import React, { useState } from 'react';
import { MapPin, Navigation, Search, X, AlertCircle, Check, Loader2 } from 'lucide-react';
import { useAuth } from '@/lib/authContext';
import { geocodeLocation, reverseGeocodeLocation } from '@/lib/api';

export const LocationSelector: React.FC = () => {
  const { location } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLocating, setIsLocating] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Trigger GPS detection ONLY when user explicitly clicks this button
  const handleDetectLocation = () => {
    if (typeof window === 'undefined' || !navigator.geolocation) {
      setErrorMessage("Geolocation is not supported by your browser. Please enter your city manually.");
      setSuccessMessage(null);
      return;
    }

    setIsLocating(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;

        try {
          // Attempt reverse geocoding to retrieve actual locality/city name
          let detectedCity = "";
          let detectedState = "";

          // 1. Try our backend reverse-geocode service
          try {
            const revRes = await reverseGeocodeLocation(latitude, longitude);
            if (revRes && revRes.success && revRes.city) {
              detectedCity = revRes.city;
              detectedState = revRes.state || "";
            }
          } catch (e) {
            // Backend reverse geocode fallback
          }

          // 2. Direct browser fallback if backend reverse was unavailable
          if (!detectedCity) {
            const res = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=12`,
              { headers: { 'Accept': 'application/json' } }
            );
            if (res.ok) {
              const data = await res.json();
              const addr = data.address || {};
              detectedCity =
                addr.city ||
                addr.town ||
                addr.municipality ||
                addr.suburb ||
                addr.district ||
                addr.county ||
                addr.state_district ||
                "";
              detectedState = addr.state || "";
            }
          }

          if (detectedCity) {
            location.setLocation({
              city: detectedCity,
              state: detectedState || "India",
              lat: latitude,
              lon: longitude
            });
            setIsLocating(false);
            setSuccessMessage(`Detected location: ${detectedCity}${detectedState ? `, ${detectedState}` : ''}`);
            setErrorMessage(null);
            setTimeout(() => {
              setIsOpen(false);
              setSuccessMessage(null);
            }, 1200);
          } else {
            setIsLocating(false);
            setErrorMessage("Could not determine your city name from GPS coordinates. Please type your city below.");
          }
        } catch (err) {
          setIsLocating(false);
          setErrorMessage("Failed to resolve location address. Please enter your city manually below.");
        }
      },
      (err) => {
        setIsLocating(false);
        setSuccessMessage(null);
        if (err.code === err.PERMISSION_DENIED) {
          setErrorMessage("Location permission was denied. Please enable location permissions in your browser or type your city below.");
        } else if (err.code === err.POSITION_UNAVAILABLE) {
          setErrorMessage("Location information is currently unavailable. Please check your device location settings or enter your city manually.");
        } else if (err.code === err.TIMEOUT) {
          setErrorMessage("Location request timed out. Please try again or enter your city manually.");
        } else {
          setErrorMessage("Unable to retrieve device location. Please enter your city manually.");
        }
      },
      { timeout: 12000, enableHighAccuracy: true }
    );
  };

  const handleManualSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (!query || isSearching) return;

    setIsSearching(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const res = await geocodeLocation(query);
      if (res && res.success && res.city) {
        location.setLocation({
          city: res.city,
          state: res.state || "India",
          lat: res.latitude,
          lon: res.longitude
        });
        setSuccessMessage(`Location updated to ${res.city}${res.state ? `, ${res.state}` : ''}`);
        setSearchQuery("");
        setTimeout(() => {
          setIsOpen(false);
          setSuccessMessage(null);
        }, 1000);
      } else {
        setErrorMessage(res?.detail || `Could not find location "${query}". Please check spelling and try again.`);
      }
    } catch (err: any) {
      setErrorMessage(err?.message || "Error searching for location. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearLocation = () => {
    if (location.clearLocation) {
      location.clearLocation();
    } else {
      location.setLocation({ city: "", state: "", lat: null, lon: null });
    }
    setSuccessMessage("Location cleared. Browsing all regional & national sources.");
    setTimeout(() => {
      setSuccessMessage(null);
    }, 1500);
  };

  const currentDisplayCity = location?.city || "Select Location";

  return (
    <div className="relative">
      {/* Location Button in Header */}
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          setErrorMessage(null);
          setSuccessMessage(null);
        }}
        className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-secondary font-medium bg-stone-100 hover:bg-stone-200/80 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-charcoal dark:text-arch-dark-text border border-arch-border dark:border-arch-dark-border transition-all duration-200 shadow-xs"
        title="Current Sourcing Location"
        aria-label="Current Location"
      >
        <MapPin className={`w-4 h-4 shrink-0 ${location?.city ? 'text-arch-terracotta' : 'text-stone-400 dark:text-stone-500'}`} />
        <span className={`truncate max-w-[130px] sm:max-w-[160px] ${location?.city ? 'font-semibold text-arch-charcoal dark:text-stone-100' : 'font-normal text-arch-muted dark:text-arch-dark-muted'}`}>
          {currentDisplayCity}
        </span>
      </button>

      {/* Popover */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/30 backdrop-blur-2xs"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-arch-dark-card rounded-2xl shadow-2xl border border-arch-border dark:border-arch-dark-border p-5 z-50 animate-in fade-in zoom-in-95 duration-150 text-arch-charcoal dark:text-arch-dark-text">
            
            {/* Popover Header */}
            <div className="flex items-start justify-between pb-3 border-b border-arch-border dark:border-arch-dark-border">
              <div>
                <h4 className="text-base font-semibold text-arch-charcoal dark:text-stone-100 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-arch-terracotta" />
                  Sourcing Location
                </h4>
                <p className="text-secondary text-arch-muted dark:text-arch-dark-muted mt-0.5">
                  Filters suppliers and materials relative to your project site.
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-lg text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Current Detected Display */}
            <div className="mt-4 p-3 rounded-xl bg-stone-50 dark:bg-arch-dark-surface border border-arch-border dark:border-arch-dark-border flex items-center justify-between">
              <div>
                <span className="text-xs uppercase tracking-wider font-semibold text-arch-muted dark:text-arch-dark-muted block">
                  Active Location
                </span>
                <span className="text-base font-bold text-arch-charcoal dark:text-stone-100">
                  {location.city ? `${location.city}${location.state ? `, ${location.state}` : ''}` : "Not Set (Browsing All)"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {location.city && (
                  <button
                    onClick={handleClearLocation}
                    type="button"
                    className="text-xs px-2 py-1 rounded-lg bg-stone-200 hover:bg-stone-300 dark:bg-stone-800 dark:hover:bg-stone-700 text-stone-700 dark:text-stone-300 font-medium transition-colors"
                    title="Clear location"
                  >
                    Clear
                  </button>
                )}
                <span className={`w-2.5 h-2.5 rounded-full ${location.city ? 'bg-emerald-500' : 'bg-stone-400'}`} title={location.city ? 'Active' : 'Unset'} />
              </div>
            </div>

            {/* GPS Detection Action */}
            <div className="mt-4">
              <button
                onClick={handleDetectLocation}
                disabled={isLocating}
                className="w-full flex items-center justify-center gap-2.5 py-2.5 px-4 rounded-xl text-body-base font-medium text-white bg-arch-terracotta hover:bg-arch-terracotta-dark dark:bg-arch-dark-terracotta transition-colors shadow-sm disabled:opacity-60"
              >
                {isLocating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Detecting your location...</span>
                  </>
                ) : (
                  <>
                    <Navigation className="w-4 h-4" />
                    <span>Detect My Current Location</span>
                  </>
                )}
              </button>
              <p className="text-xs text-center text-arch-muted dark:text-arch-dark-muted mt-1.5">
                Requests device location permission only when you click above.
              </p>
            </div>

            {/* Status alerts */}
            {errorMessage && (
              <div className="mt-3 p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 flex items-start gap-2 text-secondary text-red-700 dark:text-red-300">
                <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            {successMessage && (
              <div className="mt-3 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/60 flex items-center gap-2 text-secondary text-emerald-700 dark:text-emerald-300">
                <Check className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{successMessage}</span>
              </div>
            )}

            {/* Manual City / Area Entry */}
            <div className="mt-4 pt-3 border-t border-arch-border dark:border-arch-dark-border">
              <span className="text-xs uppercase tracking-wider font-semibold text-arch-muted dark:text-arch-dark-muted block mb-2">
                Or Enter City / Locality
              </span>
              <form onSubmit={handleManualSearch} className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="e.g. Thiruvananthapuram, Kochi, Nagercoil..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-secondary rounded-xl border border-arch-border dark:border-arch-dark-border bg-stone-50 dark:bg-arch-dark-surface text-arch-charcoal dark:text-arch-dark-text placeholder:text-stone-400 focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSearching || !searchQuery.trim()}
                  className="px-4 py-2 rounded-xl text-secondary font-semibold bg-stone-200 hover:bg-stone-300 dark:bg-stone-800 dark:hover:bg-stone-700 text-arch-charcoal dark:text-stone-100 transition-colors disabled:opacity-60 flex items-center gap-1.5"
                >
                  {isSearching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Set"}
                </button>
              </form>
            </div>

          </div>
        </>
      )}
    </div>
  );
};
