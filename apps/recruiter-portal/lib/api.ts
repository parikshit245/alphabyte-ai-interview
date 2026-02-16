const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3003/api";

export class ApiError extends Error {
    constructor(
        message: string,
        public status?: number,
        public data?: any
    ) {
        super(message);
        this.name = "ApiError";
    }
}

async function getHeaders(isMultipart = false) {
    const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
    const headers: HeadersInit = isMultipart ? {} : {
        "Content-Type": "application/json",
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
        if (typeof window !== 'undefined') {
            localStorage.removeItem("token");
            window.location.href = "/login";
        }
        throw new ApiError("Session expired", 401);
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
            errorData.error || "An error occurred",
            response.status,
            errorData
        );
    }

    const data = await response.json();
    // Handle backend response format: { success: true, data: { ... } }
    if (data.success && data.data !== undefined) {
        return data.data as T;
    }
    return data as T;
}

export const api = {
    async get<T>(endpoint: string): Promise<T> {
        const headers = await getHeaders();
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "GET",
            headers,
        });
        return handleResponse<T>(response);
    },

    async post<T>(endpoint: string, body: any): Promise<T> {
        const headers = await getHeaders();
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "POST",
            headers,
            body: JSON.stringify(body),
        });
        return handleResponse<T>(response);
    },

    async put<T>(endpoint: string, body: any): Promise<T> {
        const headers = await getHeaders();
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "PUT",
            headers,
            body: JSON.stringify(body),
        });
        return handleResponse<T>(response);
    },

    async delete<T>(endpoint: string): Promise<T> {
        const headers = await getHeaders();
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "DELETE",
            headers,
        });
        return handleResponse<T>(response);
    },
};
