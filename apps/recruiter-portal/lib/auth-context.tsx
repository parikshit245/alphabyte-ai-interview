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

            const response = await api.get<{ user: User }>("/auth/me");
            if (response.user.role !== "RECRUITER") {
                localStorage.removeItem("token");
                setUser(null);
                return;
            }
            setUser(response.user);
        } catch (error) {
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

            if (response.user.role !== "RECRUITER") {
                throw new Error("Invalid credentials. Please use the correct portal for your role.");
            }

            localStorage.setItem("token", response.accessToken);
            setUser(response.user);
            router.push("/dashboard");
        } catch (error: any) {
            throw new Error(error?.message || "Login failed");
        }
    };

    const register = async (data: { email: string; password: string; firstName: string; lastName: string }) => {
        try {
            const response = await api.post<{
                user: User;
                tokens: { accessToken: string };
            }>("/auth/register", {
                ...data,
                role: "RECRUITER"
            });

            if (response.user.role !== "RECRUITER") {
                throw new Error("Invalid registration. Please use the correct portal for your role.");
            }

            localStorage.setItem("token", response.tokens.accessToken);
            setUser(response.user);
            router.push("/dashboard");
        } catch (error: any) {
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
