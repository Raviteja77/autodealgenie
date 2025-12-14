"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";

/**
 * User interface matching backend UserResponse schema
 */
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string | null;
}

/**
 * Authentication context interface
 */
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (
    email: string,
    username: string,
    password: string,
    fullName?: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component that wraps the application and provides authentication context
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  /**
   * Fetch current user from the backend
   */
  const fetchCurrentUser = useCallback(async () => {
    try {
      const response = await fetch(`${baseUrl}/api/v1/auth/me`, {
        credentials: "include", // Include cookies
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Error fetching current user:", error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  /**
   * Login function
   */
  const login = useCallback(
    async (email: string, password: string) => {
      const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      // After successful login, fetch user data
      await fetchCurrentUser();
    },
    [baseUrl, fetchCurrentUser],
  );

  /**
   * Signup function
   */
  const signup = useCallback(
    async (
      email: string,
      username: string,
      password: string,
      fullName?: string,
    ) => {
      const response = await fetch(`${baseUrl}/api/v1/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          username,
          password,
          full_name: fullName || null,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Signup failed");
      }

      // After successful signup, automatically log in
      await login(email, password);
    },
    [baseUrl, login],
  );

  /**
   * Logout function
   */
  const logout = useCallback(async () => {
    try {
      await fetch(`${baseUrl}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Error during logout:", error);
    } finally {
      setUser(null);
    }
  }, [baseUrl]);

  /**
   * Refresh authentication by fetching current user
   */
  const refreshAuth = useCallback(async () => {
    await fetchCurrentUser();
  }, [fetchCurrentUser]);

  // Check authentication status on mount
  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        signup,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use authentication context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
