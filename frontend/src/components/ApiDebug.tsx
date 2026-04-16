/**
 * ApiDebug — development-only overlay that shows the resolved API configuration.
 *
 * Mount this anywhere in the component tree while debugging CORS / URL issues.
 * It is intentionally rendered only when the app is running in development mode
 * (import.meta.env.DEV) so it never appears in production builds.
 *
 * Usage:
 *   import { ApiDebug } from './components/ApiDebug';
 *   // Inside any component's JSX:
 *   <ApiDebug />
 */

const VITE_API_URL = import.meta.env.VITE_API_URL;
const API_BASE_URL = VITE_API_URL || '/api';

export function ApiDebug() {
  if (!import.meta.env.DEV) return null;

  const rows: { label: string; value: string; ok: boolean }[] = [
    {
      label: 'VITE_API_URL (env var)',
      value: VITE_API_URL ?? '(not set — proxy mode active)',
      ok: Boolean(VITE_API_URL),
    },
    {
      label: 'Resolved API baseURL',
      value: API_BASE_URL,
      ok: true,
    },
    {
      label: 'Mode',
      value: VITE_API_URL
        ? 'Direct requests to external backend'
        : 'Proxied via Vite dev-server → http://localhost:8000',
      ok: true,
    },
  ];

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 12,
        right: 12,
        zIndex: 9999,
        background: '#1e1e2e',
        color: '#cdd6f4',
        fontFamily: 'monospace',
        fontSize: 12,
        borderRadius: 8,
        padding: '10px 14px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
        maxWidth: 480,
        lineHeight: 1.6,
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 6, color: '#89b4fa' }}>
        🔧 API Debug (dev only)
      </div>
      {rows.map(({ label, value, ok }) => (
        <div key={label}>
          <span style={{ color: '#a6e3a1' }}>{label}:</span>{' '}
          <span style={{ color: ok ? '#cdd6f4' : '#f38ba8' }}>{value}</span>
        </div>
      ))}
    </div>
  );
}

export default ApiDebug;
