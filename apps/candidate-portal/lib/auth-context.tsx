"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface User {
    id: string;
    email: string;
    firstName: string | null;
    lastName: string | null;
    role: string;
    companyId: string | null;
    isActive: boolean;
    company?: {
        id: string;
        name: string;
        domain: string;
        plan: string;
    } | null;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (data: { email: string; password: string; firstName: string; lastName: string }) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    // Check for existing auth on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const token = localStorage.getItem("token");
            if (!token) {
                setLoading(false);
                return;
            }

            // Fetch current user
            const response = await api.get<{ user: User }>("/auth/me");
            setUser(response.user);
        } catch (error) {
            console.error("Auth check failed:", error);
            // Clear invalid token
            localStorage.removeItem("token");
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            const response = await api.post<{
                user: User;
                accessToken: string;
            }>("/auth/login", { email, password });

            // Store token
            localStorage.setItem("token", response.accessToken);

            // Set user
            setUser(response.user);

            // Redirect to dashboard
            router.push("/dashboard");
        } catch (error: any) {
            console.error("Login failed:", error);
            throw new Error(error?.response?.data?.error || "Login failed");
        }
    };

    const register = async (data: { email: string; password: string; firstName: string; lastName: string }) => {
        try {
            const response = await api.post<{
                user: User;
                tokens: { accessToken: string };
            }>("/auth/register", {
                ...data,
                role: "CANDIDATE"
            });

            // Store token
            localStorage.setItem("token", response.tokens.accessToken);

            // Set user
            setUser(response.user);

            // Redirect to dashboard
            router.push("/dashboard");
        } catch (error: any) {
            console.error("Registration failed:", error);
            throw new Error(error?.message || "Registration failed");
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                login,
                register,
                logout,
                isAuthenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
