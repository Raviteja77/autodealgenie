// "use client";

// import React, {
//   createContext,
//   useContext,
//   useEffect,
//   useState,
//   useCallback,
// } from "react";
// import { extractErrorMessage } from "../errors";

// /**
//  * User interface matching backend UserResponse schema
//  */
// export interface User {
//   id: number;
//   email: string;
//   username: string;
//   full_name: string | null;
//   is_active: boolean;
//   is_superuser: boolean;
//   created_at: string;
//   updated_at: string | null;
// }

// /**
//  * Authentication context interface
//  */
// interface AuthContextType {
//   user: User | null;
//   loading: boolean;
//   login: (email: string, password: string) => Promise<void>;
//   signup: (
//     email: string,
//     username: string,
//     password: string,
//     fullName?: string,
//   ) => Promise<void>;
//   logout: () => Promise<void>;
//   refreshAuth: () => Promise<void>;
//   forgotPassword: (email: string) => Promise<void>;
//   resetPassword: (token: string, newPassword: string) => Promise<void>;
// }

// const AuthContext = createContext<AuthContextType | undefined>(undefined);

// /**
//  * AuthProvider component that wraps the application and provides authentication context
//  */
// export function AuthProvider({ children }: { children: React.ReactNode }) {
//   const [user, setUser] = useState<User | null>(null);
//   const [loading, setLoading] = useState(true);

//   const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

//   /**
//    * Fetch current user from the backend
//    */
//   const fetchCurrentUser = useCallback(async () => {
//     try {
//       const response = await fetch(`${baseUrl}/api/v1/auth/me`, {
//         credentials: "include", // Include cookies
//       });

//       if (response.ok) {
//         const userData = await response.json();
//         setUser(userData);
//       } else {
//         setUser(null);
//       }
//     } catch (error) {
//       console.error("Error fetching current user:", error);
//       setUser(null);
//     } finally {
//       setLoading(false);
//     }
//   }, [baseUrl]);

//   /**
//    * Login function
//    */
//   const login = useCallback(
//     async (email: string, password: string) => {
//       const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         credentials: "include",
//         body: JSON.stringify({ email, password }),
//       });

//       if (!response.ok) {
//         const error = await response.json();
//         const errorMessage = extractErrorMessage(error.detail, "Login failed");
//         throw new Error(errorMessage);
//       }

//       // After successful login, fetch user data
//       await fetchCurrentUser();
//     },
//     [baseUrl, fetchCurrentUser],
//   );

//   /**
//    * Signup function
//    */
//   const signup = useCallback(
//     async (
//       email: string,
//       username: string,
//       password: string,
//       fullName?: string,
//     ) => {
//       const response = await fetch(`${baseUrl}/api/v1/auth/signup`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         credentials: "include",
//         body: JSON.stringify({
//           email,
//           username,
//           password,
//           full_name: fullName || null,
//         }),
//       });

//       if (!response.ok) {
//         const error = await response.json();
//         const errorMessage = extractErrorMessage(error.detail, "Signup failed");
//         throw new Error(errorMessage);
//       }

//       // After successful signup, automatically log in
//       await login(email, password);
//     },
//     [baseUrl, login],
//   );

//   /**
//    * Logout function
//    */
//   const logout = useCallback(async () => {
//     try {
//       await fetch(`${baseUrl}/api/v1/auth/logout`, {
//         method: "POST",
//         credentials: "include",
//       });
//     } catch (error) {
//       console.error("Error during logout:", error);
//     } finally {
//       setUser(null);
//     }
//   }, [baseUrl]);

//   /**
//    * Refresh authentication by fetching current user
//    */
//   const refreshAuth = useCallback(async () => {
//     await fetchCurrentUser();
//   }, [fetchCurrentUser]);

//   /**
//    * Forgot password function - request password reset email
//    */
//   const forgotPassword = useCallback(
//     async (email: string) => {
//       const response = await fetch(`${baseUrl}/api/v1/auth/forgot-password`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ email }),
//       });

//       const data = await response.json();

//       if (!response.ok) {
//         const errorMessage = extractErrorMessage(
//           data.detail,
//           "Failed to request password reset"
//         );
//         throw new Error(errorMessage);
//       }
//     },
//     [baseUrl]
//   );

//   /**
//    * Reset password function - reset password with token
//    */
//   const resetPassword = useCallback(
//     async (token: string, newPassword: string) => {
//       const response = await fetch(`${baseUrl}/api/v1/auth/reset-password`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           token,
//           new_password: newPassword,
//         }),
//       });

//       const data = await response.json();

//       if (!response.ok) {
//         const errorMessage = extractErrorMessage(
//           data.detail,
//           "Failed to reset password"
//         );
//         throw new Error(errorMessage);
//       }
//     },
//     [baseUrl]
//   );

//   // Check authentication status on mount
//   useEffect(() => {
//     fetchCurrentUser();
//   }, [fetchCurrentUser]);

//   return (
//     <AuthContext.Provider
//       value={{
//         user,
//         loading,
//         login,
//         signup,
//         logout,
//         refreshAuth,
//         forgotPassword,
//         resetPassword,
//       }}
//     >
//       {children}
//     </AuthContext.Provider>
//   );
// }

// /**
//  * Hook to use authentication context
//  */
// export function useAuth() {
//   const context = useContext(AuthContext);
//   if (context === undefined) {
//     throw new Error("useAuth must be used within an AuthProvider");
//   }
//   return context;
// }

// Optimized Auth Provider
// Location: lib/auth/AuthProvider.tsx

"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef,
} from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, password: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  
  // Use refs to prevent duplicate API calls
  const hasCheckedAuthRef = useRef(false);
  const checkInProgressRef = useRef(false);
  
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authentication status on mount (ONCE)
  useEffect(() => {
    // Guard: Already checked or in progress
    if (hasCheckedAuthRef.current || checkInProgressRef.current) {
      return;
    }

    const checkAuth = async () => {
      checkInProgressRef.current = true;
  
      try {
        // Check if we have a token
        const token = localStorage.getItem("auth_token");
        
        if (!token) {
          setUser(null);
          hasCheckedAuthRef.current = true;
          setLoading(false);
          return;
        }

        getCurrentUser();
        hasCheckedAuthRef.current = true;
      } catch (err) {
        console.error("Auth check failed:", err);
        // Token is invalid, clear it
        localStorage.removeItem("auth_token");
        setUser(null);
        hasCheckedAuthRef.current = true;
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const getCurrentUser = useCallback(async () => {
    // Verify token with backend
    const userData = await apiClient.getCurrentUser();
    if(userData) {
      setUser(userData);
    } else {
      setUser(null);
    }
  }, []);

  // Memoize all functions with useCallback
  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    setLoading(true);

    try {
      const response = await apiClient.login(email, password);
      if(response.access_token) {
        getCurrentUser();
        // Reset auth check ref so future checks can run if needed
        hasCheckedAuthRef.current = true;
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Login failed. Please check your credentials.";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const signup = useCallback(
    async (email: string, username: string, password: string) => {
      setError(null);
      setLoading(true);

      try {
        await apiClient.signup(
          email,
          username,
          password,
        );
        
        login(email, password); // Auto-login after signup
        
        hasCheckedAuthRef.current = true;
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Signup failed. Please try again.";
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const logout = useCallback(async () => {
    setLoading(true);

    try {
      // Call logout endpoint if it exists
      try {
        await apiClient.logout();
      } catch (err) {
        // Ignore logout errors, still clear local state
        console.error("Logout API call failed:", err);
      }
      
      // Clear token
      localStorage.removeItem("auth_token");
      
      // Clear user
      setUser(null);
      
      // Reset refs for fresh login
      hasCheckedAuthRef.current = false;
      checkInProgressRef.current = false;
      
      // Redirect to login
      router.push("/auth/login");
    } catch (err) {
      console.error("Logout failed:", err);
    } finally {
      setLoading(false);
    }
  }, [router]);

  const forgotPassword = useCallback(async (email: string) => {
    setError(null);

    try {
      await apiClient.forgotPassword(email);
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Failed to send password reset email.";
      setError(errorMessage);
      throw err;
    }
  }, []);

  const resetPassword = useCallback(
    async (token: string, password: string) => {
      setError(null);

      try {
        await apiClient.resetPassword(token, password);
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to reset password.";
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  const refreshUser = useCallback(async () => {
    // Allow manual refresh
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error("Failed to refresh user:", err);
      // Don't throw, just log
    }
  }, []);

  // Memoize context value
  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      login,
      signup,
      logout,
      forgotPassword,
      resetPassword,
      refreshUser,
    }),
    [user, loading, error, login, signup, logout, forgotPassword, resetPassword, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

// Protected Route HOC
export function withAuth<P extends object>(
  Component: React.ComponentType<P>
) {
  return function ProtectedRoute(props: P) {
    const { user, loading } = useAuth();
    const router = useRouter();
    const hasRedirectedRef = useRef(false);

    useEffect(() => {
      if (!loading && !user && !hasRedirectedRef.current) {
        hasRedirectedRef.current = true;
        router.push("/auth/login");
      }
    }, [user, loading, router]);

    if (loading) {
      return (
        <div style={{ 
          display: "flex", 
          justifyContent: "center", 
          alignItems: "center", 
          minHeight: "100vh" 
        }}>
          Loading...
        </div>
      );
    }

    if (!user) {
      return null;
    }

    return <Component {...props} />;
  };
}

// Public Route HOC (redirects to home if already logged in)
export function withPublic<P extends object>(
  Component: React.ComponentType<P>
) {
  return function PublicRoute(props: P) {
    const { user, loading } = useAuth();
    const router = useRouter();
    const hasRedirectedRef = useRef(false);

    useEffect(() => {
      if (!loading && user && !hasRedirectedRef.current) {
        hasRedirectedRef.current = true;
        router.push("/");
      }
    }, [user, loading, router]);

    if (loading) {
      return (
        <div style={{ 
          display: "flex", 
          justifyContent: "center", 
          alignItems: "center", 
          minHeight: "100vh" 
        }}>
          Loading...
        </div>
      );
    }

    if (user) {
      return null;
    }

    return <Component {...props} />;
  };
}