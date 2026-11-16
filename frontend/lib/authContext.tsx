"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '@/types';
import { fetchApi, getValidAuthToken } from './api';

interface LocationContextType {
  city: string;
  district?: string;
  state: string;
  lat: number | null;
  lon: number | null;
  isSet: boolean;
  setLocation: (loc: { city: string; district?: string; state: string; lat: number | null; lon: number | null }) => void;
  clearLocation: () => void;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  location: LocationContextType;
}

const emptyLocation = {
  city: "",
  state: "",
  lat: null as number | null,
  lon: null as number | null
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [locationState, setLocationState] = useState(emptyLocation);

  useEffect(() => {
    const savedToken = getValidAuthToken();
    const savedLoc = localStorage.getItem('architect_ai_location');
    if (savedLoc) {
      try {
        const parsed = JSON.parse(savedLoc);
        if (parsed && typeof parsed.city === 'string' && parsed.city.trim()) {
          setLocationState({
            city: parsed.city.trim(),
            state: parsed.state || "",
            lat: typeof parsed.lat === 'number' ? parsed.lat : null,
            lon: typeof parsed.lon === 'number' ? parsed.lon : null
          });
        }
      } catch (e) {}
    }

    if (savedToken) {
      setToken(savedToken);
      fetchApi<User>('/auth/me')
        .then(u => setUser(u))
        .catch(() => {
          localStorage.removeItem('architect_ai_token');
          setToken(null);
          setUser(null);
        });
    }

    const handleAuthExpired = () => {
      localStorage.removeItem('architect_ai_token');
      setToken(null);
      setUser(null);
    };
    window.addEventListener('materiq:auth-expired', handleAuthExpired);
    window.addEventListener('nivora:auth-expired', handleAuthExpired);
    return () => {
      window.removeEventListener('materiq:auth-expired', handleAuthExpired);
      window.removeEventListener('nivora:auth-expired', handleAuthExpired);
    };
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('architect_ai_token', newToken);
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('architect_ai_token');
    setToken(null);
    setUser(null);
  };

  const setLocation = (loc: { city: string; state: string; lat: number | null; lon: number | null }) => {
    setLocationState(loc);
    localStorage.setItem('architect_ai_location', JSON.stringify(loc));
  };

  const clearLocation = () => {
    setLocationState(emptyLocation);
    localStorage.removeItem('architect_ai_location');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        location: {
          ...locationState,
          isSet: Boolean(locationState.city),
          setLocation,
          clearLocation
        }
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
