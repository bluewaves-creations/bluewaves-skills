/**
 * Branded login page HTML generator.
 *
 * Renders a clean, mobile-friendly login form with CSS custom properties
 * derived from the brand's color tokens.
 */

export function renderLoginPage(
  title: string,
  brand: string,
  siteName: string,
  brandTokens?: Record<string, string>,
  error?: string
): string {
  const colors = brandTokens || {};
  const heading = colors["text-heading"] || "#333333";
  const body = colors["text-body"] || "#2C2C2C";
  const bgPage = colors["background-page"] || "#FFFFFF";
  const bgAlt = colors["background-alt"] || "#F5F5F7";
  const border = colors["border-default"] || "#B0B0B0";
  const highlight = colors["highlight"] || "#0066CC";
  const link = colors["link"] || highlight;

  const errorHtml = error
    ? `<div class="error">${escapeHtml(error)}</div>`
    : "";

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)} - ${escapeHtml(capitalize(brand))}</title>
  <style>
    :root {
      --color-heading: ${heading};
      --color-body: ${body};
      --bg-page: ${bgPage};
      --bg-alt: ${bgAlt};
      --border: ${border};
      --color-highlight: ${highlight};
      --color-link: ${link};
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-alt);
      color: var(--color-body);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }
    .card {
      background: var(--bg-page);
      border-radius: 12px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.08);
      padding: 2.5rem 2rem;
      width: 100%;
      max-width: 400px;
    }
    .brand {
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-size: 0.75rem;
      color: var(--color-highlight);
      margin-bottom: 0.5rem;
    }
    h1 {
      color: var(--color-heading);
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      color: var(--color-body);
      opacity: 0.6;
      font-size: 0.875rem;
      margin-bottom: 2rem;
    }
    .error {
      background: #FEF2F2;
      color: #DC2626;
      border: 1px solid #FECACA;
      border-radius: 8px;
      padding: 0.75rem 1rem;
      font-size: 0.875rem;
      margin-bottom: 1.5rem;
    }
    label {
      display: block;
      font-size: 0.8125rem;
      font-weight: 600;
      margin-bottom: 0.375rem;
      color: var(--color-body);
    }
    input[type="password"] {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 1rem;
      font-family: inherit;
      transition: border-color 0.15s;
      background: var(--bg-page);
      color: var(--color-body);
    }
    input[type="password"]:focus {
      outline: none;
      border-color: var(--color-highlight);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-highlight) 20%, transparent);
    }
    button {
      width: 100%;
      padding: 0.75rem;
      margin-top: 1.25rem;
      background: var(--color-highlight);
      color: #FFFFFF;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s;
    }
    button:hover { opacity: 0.9; }
    button:active { opacity: 0.8; }
  </style>
</head>
<body>
  <div class="card">
    <div class="brand">${escapeHtml(capitalize(brand))}</div>
    <h1>${escapeHtml(title)}</h1>
    <p class="subtitle">Enter the password to view this page.</p>
    ${errorHtml}
    <form method="POST" action="/${encodeURIComponent(siteName)}/_login">
      <label for="password">Password</label>
      <input type="password" id="password" name="password" required autofocus
             placeholder="e.g. coral-sunset-tide-2026" autocomplete="off">
      <button type="submit">View page</button>
    </form>
  </div>
</body>
</html>`;
}

export function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
