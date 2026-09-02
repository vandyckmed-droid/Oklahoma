// Oklahoma quotes proxy: GET /quotes?symbols=AAPL,MSFT,...
//
// Forwards one batch-quote call to Financial Modeling Prep with the key
// held as a Worker secret, trims the answer to what the page reads, and
// caches each batch at the edge for CACHE_SECONDS so reloads and other
// devices do not each spend a request. The key never leaves this Worker.

const SYMBOL = /^[A-Z0-9.\-]{1,10}$/;
const MAX_SYMBOLS = 100;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "")
      .split(",").map((s) => s.trim()).filter(Boolean);
    const cors = allowed.includes(origin) ? origin : null;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(cors) });
    }
    if (request.method !== "GET") return reply({ error: "method not allowed" }, 405, cors);
    if (url.pathname === "/" || url.pathname === "/health") {
      return reply({ ok: true, service: "oklahoma-quotes" }, 200, cors);
    }
    if (url.pathname !== "/quotes") return reply({ error: "not found" }, 404, cors);
    if (!cors) return reply({ error: "origin not allowed" }, 403, null);
    if (!env.FMP_API_KEY) return reply({ error: "FMP_API_KEY is not set on the Worker" }, 500, cors);

    const symbols = Array.from(new Set(
      (url.searchParams.get("symbols") || "").toUpperCase().split(",")
        .map((s) => s.trim()).filter((s) => SYMBOL.test(s))
    )).sort().slice(0, MAX_SYMBOLS);
    if (!symbols.length) return reply({ error: "no symbols" }, 400, cors);

    const ttl = Math.max(15, parseInt(env.CACHE_SECONDS || "60", 10) || 60);
    const cache = caches.default;
    const cacheKey = new Request("https://oklahoma-quotes.cache/quotes/" + symbols.join(","));
    let cached = await cache.match(cacheKey);
    if (!cached) {
      const upstream = await fetch(
        "https://financialmodelingprep.com/stable/batch-quote?symbols=" +
          encodeURIComponent(symbols.join(",")) + "&apikey=" + encodeURIComponent(env.FMP_API_KEY),
        { headers: { accept: "application/json" } }
      );
      if (!upstream.ok) return reply({ error: "upstream " + upstream.status }, 502, cors);
      const rows = await upstream.json();
      const quotes = Array.isArray(rows) ? rows.map(trim).filter(Boolean) : [];
      cached = new Response(JSON.stringify({ asOf: Date.now(), quotes }), {
        headers: { "content-type": "application/json", "cache-control": "public, max-age=" + ttl },
      });
      ctx.waitUntil(cache.put(cacheKey, cached.clone()));
    }
    const out = new Response(cached.body, cached);
    for (const [k, v] of Object.entries(corsHeaders(cors))) out.headers.set(k, v);
    return out;
  },
};

function trim(row) {
  if (!row || typeof row.symbol !== "string" || typeof row.price !== "number") return null;
  return {
    symbol: row.symbol,
    price: row.price,
    change: num(row.change),
    changePct: num(row.changePercentage ?? row.changesPercentage),
    previousClose: num(row.previousClose),
    timestamp: num(row.timestamp),
  };
}
function num(v) { return typeof v === "number" && Number.isFinite(v) ? v : null; }

function corsHeaders(origin) {
  const h = { "access-control-allow-methods": "GET, OPTIONS", "access-control-max-age": "86400", vary: "Origin" };
  if (origin) h["access-control-allow-origin"] = origin;
  return h;
}
function reply(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...corsHeaders(origin) },
  });
}
