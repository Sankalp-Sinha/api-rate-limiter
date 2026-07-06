"use client";

import {
  Activity,
  Ban,
  Clock3,
  KeyRound,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";


type Summary = {
  total_requests: number;
  allowed_requests: number;
  rate_limited_requests: number;
  server_error_requests: number;
  average_latency_ms: number;
};


type ApiKeyItem = {
  id: number;
  name: string;
  key_prefix: string;
  plan_name: string;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
};


export default function DashboardPage() {
  const [summary, setSummary] =
    useState<Summary | null>(null);

  const [activeKeys, setActiveKeys] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const loadDashboard = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const [
          summaryResponse,
          keysResponse,
        ] = await Promise.all([
          fetch(
            "/api/dashboard/summary",
            {
              cache: "no-store",
            }
          ),

          fetch(
            "/api/admin/api-keys",
            {
              cache: "no-store",
            }
          ),
        ]);

        if (!summaryResponse.ok) {
          throw new Error(
            "Failed to load analytics summary"
          );
        }

        if (!keysResponse.ok) {
          throw new Error(
            "Failed to load API keys"
          );
        }

        const summaryData: Summary =
          await summaryResponse.json();

        const keysData: ApiKeyItem[] =
          await keysResponse.json();

        setSummary(summaryData);

        setActiveKeys(
          keysData.filter(
            (key) => key.is_active
          ).length
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load dashboard"
        );
      } finally {
        setLoading(false);
      }
    },
    []
  );


  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);


  const stats = [
    {
      label: "Total Requests",
      value:
        summary?.total_requests
          .toLocaleString() ?? "0",
      icon: Activity,
    },
    {
      label: "Blocked Requests",
      value:
        summary?.rate_limited_requests
          .toLocaleString() ?? "0",
      icon: Ban,
    },
    {
      label: "Average Latency",
      value:
        `${summary?.average_latency_ms ?? 0} ms`,
      icon: Clock3,
    },
    {
      label: "Active API Keys",
      value: activeKeys.toString(),
      icon: KeyRound,
    },
  ];


  return (
    <div>
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold">
            Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Monitor API traffic and rate-limit activity.
          </p>
        </div>

        <button
          onClick={() => void loadDashboard()}
          disabled={loading}
          className="rounded-lg border border-slate-700 px-4 py-2 text-sm transition hover:bg-slate-900 disabled:opacity-50"
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>


      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}


      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;

          return (
            <div
              key={stat.label}
              className="rounded-xl border border-slate-800 bg-slate-900 p-5"
            >
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm text-slate-400">
                  {stat.label}
                </p>

                <Icon
                  size={18}
                  className="text-blue-400"
                />
              </div>

              <p className="text-3xl font-semibold">
                {loading
                  ? "..."
                  : stat.value}
              </p>
            </div>
          );
        })}
      </div>


      <div className="mt-8 grid gap-5 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-lg font-semibold">
            Request Decisions
          </h3>

          <div className="mt-6 space-y-4">
            <DecisionRow
              label="Allowed"
              value={
                summary?.allowed_requests ?? 0
              }
            />

            <DecisionRow
              label="Rate Limited"
              value={
                summary?.rate_limited_requests ?? 0
              }
            />

            <DecisionRow
              label="Server Errors"
              value={
                summary?.server_error_requests ?? 0
              }
            />
          </div>
        </div>


        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-lg font-semibold">
            System Status
          </h3>

          <div className="mt-6 space-y-4">
            <StatusRow
              label="FastAPI"
              status="Connected"
            />

            <StatusRow
              label="Redis"
              status="Active"
            />

            <StatusRow
              label="PostgreSQL"
              status="Active"
            />
          </div>
        </div>
      </div>
    </div>
  );
}


function DecisionRow({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg bg-slate-950 p-4">
      <span className="text-slate-400">
        {label}
      </span>

      <span className="font-semibold">
        {value.toLocaleString()}
      </span>
    </div>
  );
}


function StatusRow({
  label,
  status,
}: {
  label: string;
  status: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg bg-slate-950 p-4">
      <span className="text-slate-400">
        {label}
      </span>

      <span className="text-sm text-emerald-400">
        ● {status}
      </span>
    </div>
  );
}