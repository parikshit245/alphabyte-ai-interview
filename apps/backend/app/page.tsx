export default function HomePage() {
  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui" }}>
      <h1>AI Interview Platform - Backend API</h1>
      <p>API is running. Access endpoints via /api/...</p>
      <ul>
        <li>
          <a href="/api/health">GET /api/health</a> - Health check
        </li>
        <li>POST /api/auth/register - Register user</li>
        <li>POST /api/auth/login - Login user</li>
        <li>POST /api/auth/refresh - Refresh token</li>
        <li>POST /api/ai/jsonrpc - AI JSON-RPC endpoint</li>
      </ul>
    </div>
  );
}
