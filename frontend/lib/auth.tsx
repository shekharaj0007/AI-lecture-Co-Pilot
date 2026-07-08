"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";

export type User = { id: string; email: string; name: string; role: string };

type AuthContextValue = {
  user: User | null;
  token: string | null;
  ownerId: string;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  authHeaders: () => Record<string, string>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("lc_token");
    const savedUser = localStorage.getItem("lc_user");
    if (saved && savedUser) {
      setToken(saved);
      setUser(JSON.parse(savedUser));
    }
  }, []);

  async function login(email: string, password: string) {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Login failed");
    const data = await res.json();
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("lc_token", data.access_token);
    localStorage.setItem("lc_user", JSON.stringify(data.user));
  }

  async function register(email: string, password: string, name: string) {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name }),
    });
    if (!res.ok) throw new Error("Registration failed");
    const data = await res.json();
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("lc_token", data.access_token);
    localStorage.setItem("lc_user", JSON.stringify(data.user));
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem("lc_token");
    localStorage.removeItem("lc_user");
  }

  function authHeaders() {
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        ownerId: user?.id ?? "demo-user",
        login,
        register,
        logout,
        authHeaders,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
