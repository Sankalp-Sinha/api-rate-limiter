"use client";

import { useState } from "react";

type ApiResult = {
  status: number;
  body: unknown;
  remaining: string | null;
  limit: string | null;
  retryAfter: string | null;
  requestId: string | null;
};

export default function PlaygroundPage() {
  const [apiKey, setApiKey] = useState(
    "free_key_123"
  );

  const [loading, setLoading] = useState(false);

  const [result, setResult] =
    useState<ApiResult | null>(null);

  async function callProtectedApi() {
    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/protected",
        {
          method: "GET",
          headers: {
            "x-api-key": apiKey,
          },
        }
      );

      const body = await response.json();

      setResult({
        status: response.status,
        body,
        remaining: response.headers.get(
          "X-RateLimit-Remaining"
        ),
        limit: response.headers.get(
          "X-RateLimit-Limit"
        ),
        retryAfter: response.headers.get(
          "Retry-After"
        ),
        requestId: response.headers.get(
          "X-Request-ID"
        ),
      });
    } catch {
      setResult({
        status: 0,
        body: {
          error: "Could not connect to backend",
        },
        remaining: null,
        limit: null,
        retryAfter: null,
        requestId: null,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h2 className="text-3xl font-bold">
          API Playground
        </h2>

        <p className="mt-2 text-slate-400">
          Call the protected API repeatedly and watch
          the rate limiter respond.
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <label className="mb-2 block text-sm text-slate-300">
          API Key
        </label>

        <input
          value={apiKey}
          onChange={(event) =>
            setApiKey(event.target.value)
          }
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 font-mono text-sm outline-none focus:border-blue-500"
        />

        <button
          onClick={callProtectedApi}
          disabled={loading || !apiKey.trim()}
          className="mt-5 rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading
            ? "Calling API..."
            : "Call Protected API"}
        </button>
      </div>

      {result && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5 flex items-center justify-between">
            <h3 className="font-semibold">
              Response
            </h3>

            <span
              className={`rounded-full px-3 py-1 text-sm ${
                result.status >= 200 &&
                result.status < 300
                  ? "bg-emerald-500/10 text-emerald-400"
                  : "bg-red-500/10 text-red-400"
              }`}
            >
              HTTP {result.status}
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Metric
              label="Limit"
              value={result.limit ?? "-"}
            />

            <Metric
              label="Remaining"
              value={result.remaining ?? "-"}
            />

            <Metric
              label="Retry After"
              value={
                result.retryAfter
                  ? `${result.retryAfter}s`
                  : "-"
              }
            />
          </div>

          <div className="mt-5">
            <p className="mb-2 text-sm text-slate-400">
              Response Body
            </p>

            <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-300">
              {JSON.stringify(
                result.body,
                null,
                2
              )}
            </pre>
          </div>

          {result.requestId && (
            <p className="mt-4 break-all text-xs text-slate-500">
              Request ID: {result.requestId}
            </p>
          )}
        </div>
      )}
    </div>
  );
}


function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-slate-950 p-4">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-xl font-semibold">
        {value}
      </p>
    </div>
  );
}