"use client";

import {
  Activity,
  ArrowLeft,
  Ban,
  Clock3,
  Route,
  Users,
} from "lucide-react";
import Link from "next/link";
import {
  useCallback,
  useEffect,
  useState,
} from "react";
import { useParams } from "next/navigation";


type Project = {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
};


type Summary = {
  project_id: number;
  hours: number;

  total_checks: number;
  allowed_checks: number;
  blocked_checks: number;

  block_rate_percent: number;
  unique_subjects: number;
  average_latency_ms: number;

  active_endpoints: number;
};


type EndpointAnalytics = {
  policy_id: number;
  project_id: number;

  route_path: string;
  http_method: string;

  capacity: number;
  refill_amount: number;
  refill_unit: string;

  is_active: boolean;

  total_checks: number;
  allowed_checks: number;
  blocked_checks: number;

  block_rate_percent: number;
  unique_subjects: number;
  average_latency_ms: number;

  last_request_at: string | null;
};


const TIME_RANGES = [
  {
    label: "1h",
    hours: 1,
  },
  {
    label: "24h",
    hours: 24,
  },
  {
    label: "7d",
    hours: 168,
  },
  {
    label: "30d",
    hours: 720,
  },
];


export default function ProjectAnalyticsPage() {
  const params = useParams<{
    id: string;
  }>();

  const projectId = params.id;

  const [project, setProject] =
    useState<Project | null>(null);

  const [summary, setSummary] =
    useState<Summary | null>(null);

  const [
    endpoints,
    setEndpoints,
  ] = useState<EndpointAnalytics[]>([]);

  const [hours, setHours] =
    useState(24);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const loadAnalytics = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const [
          projectResponse,
          summaryResponse,
          endpointsResponse,
        ] = await Promise.all([
          fetch(
            `/api/admin/projects/${projectId}`,
            {
              cache: "no-store",
            }
          ),

          fetch(
            `/api/admin/projects/${projectId}/analytics/summary?hours=${hours}`,
            {
              cache: "no-store",
            }
          ),

          fetch(
            `/api/admin/projects/${projectId}/analytics/endpoints?hours=${hours}`,
            {
              cache: "no-store",
            }
          ),
        ]);

        const projectData =
          await projectResponse.json();

        const summaryData =
          await summaryResponse.json();

        const endpointsData =
          await endpointsResponse.json();

        if (!projectResponse.ok) {
          throw new Error(
            projectData.detail ??
            projectData.error ??
            "Could not load project"
          );
        }

        if (!summaryResponse.ok) {
          throw new Error(
            summaryData.detail ??
            summaryData.error ??
            "Could not load summary"
          );
        }

        if (!endpointsResponse.ok) {
          throw new Error(
            endpointsData.detail ??
            endpointsData.error ??
            "Could not load endpoints"
          );
        }

        setProject(projectData);
        setSummary(summaryData);
        setEndpoints(endpointsData);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load analytics"
        );
      } finally {
        setLoading(false);
      }
    },
    [
      projectId,
      hours,
    ]
  );


  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);


  return (
    <div>
      <Link
        href={
          `/dashboard/projects/${projectId}`
        }
        className="mb-6 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
      >
        <ArrowLeft size={16} />
        Back to Project
      </Link>


      <div className="mb-8 flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-3xl font-bold">
            {project?.name ?? "Project"} Analytics
          </h2>

          <p className="mt-2 text-slate-400">
            Monitor rate-limit checks for each
            protected endpoint.
          </p>
        </div>


        <div className="flex rounded-lg border border-slate-800 bg-slate-900 p-1">
          {TIME_RANGES.map(
            (range) => (
              <button
                key={range.hours}
                onClick={() =>
                  setHours(range.hours)
                }
                className={
                  hours === range.hours
                    ? "rounded-md bg-blue-600 px-3 py-2 text-sm text-white"
                    : "rounded-md px-3 py-2 text-sm text-slate-400 transition hover:text-white"
                }
              >
                {range.label}
              </button>
            )
          )}
        </div>
      </div>


      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}


      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Checks"
          value={
            summary?.total_checks ?? 0
          }
          icon={Activity}
          loading={loading}
        />

        <StatCard
          label="Blocked"
          value={
            summary?.blocked_checks ?? 0
          }
          icon={Ban}
          loading={loading}
        />

        <StatCard
          label="Unique Subjects"
          value={
            summary?.unique_subjects ?? 0
          }
          icon={Users}
          loading={loading}
        />

        <StatCard
          label="Avg Latency"
          value={
            `${summary?.average_latency_ms ?? 0} ms`
          }
          icon={Clock3}
          loading={loading}
        />
      </div>


      <div className="mt-6 grid gap-5 md:grid-cols-3">
        <MiniCard
          label="Allowed Checks"
          value={
            summary?.allowed_checks ?? 0
          }
        />

        <MiniCard
          label="Block Rate"
          value={
            `${summary?.block_rate_percent ?? 0}%`
          }
        />

        <MiniCard
          label="Active Endpoints"
          value={
            summary?.active_endpoints ?? 0
          }
        />
      </div>


      <div className="mt-10">
        <div className="mb-5 flex items-center gap-2">
          <Route
            size={20}
            className="text-violet-400"
          />

          <h3 className="text-xl font-semibold">
            Endpoint Analytics
          </h3>
        </div>


        {loading ? (
          <div className="text-slate-400">
            Loading endpoint analytics...
          </div>
        ) : endpoints.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center text-slate-400">
            No protected endpoints found.
          </div>
        ) : (
          <div className="space-y-5">
            {endpoints.map(
              (endpoint) => (
                <EndpointCard
                  key={endpoint.policy_id}
                  endpoint={endpoint}
                />
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}


function StatCard({
  label,
  value,
  icon: Icon,
  loading,
}: {
  label: string;
  value: string | number;
  icon: typeof Activity;
  loading: boolean;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          {label}
        </p>

        <Icon
          size={18}
          className="text-blue-400"
        />
      </div>

      <p className="mt-4 text-3xl font-semibold">
        {loading
          ? "..."
          : typeof value === "number"
            ? value.toLocaleString()
            : value}
      </p>
    </div>
  );
}


function MiniCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">
        {label}
      </p>

      <p className="mt-3 text-2xl font-semibold">
        {typeof value === "number"
          ? value.toLocaleString()
          : value}
      </p>
    </div>
  );
}


function EndpointCard({
  endpoint,
}: {
  endpoint: EndpointAnalytics;
}) {
  const total = endpoint.total_checks;

  const allowedPercent =
    total > 0
      ? (
          endpoint.allowed_checks
          / total
        ) * 100
      : 0;

  const blockedPercent =
    total > 0
      ? (
          endpoint.blocked_checks
          / total
        ) * 100
      : 0;


  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <span className="rounded bg-violet-500/10 px-2 py-1 font-mono text-xs text-violet-400">
              {endpoint.http_method}
            </span>

            <span className="font-mono">
              {endpoint.route_path}
            </span>
          </div>

          <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
            <span>
              Capacity:{" "}
              {endpoint.capacity}
            </span>

            <span>
              Refill:{" "}
              {endpoint.refill_amount}/
              {endpoint.refill_unit}
            </span>

            <span
              className={
                endpoint.is_active
                  ? "text-emerald-400"
                  : "text-red-400"
              }
            >
              {endpoint.is_active
                ? "● Active"
                : "● Inactive"}
            </span>
          </div>
        </div>


        <div className="text-left md:text-right">
          <p className="text-2xl font-semibold">
            {endpoint.total_checks
              .toLocaleString()}
          </p>

          <p className="text-xs text-slate-500">
            total checks
          </p>
        </div>
      </div>


      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <Metric
          label="Allowed"
          value={
            endpoint.allowed_checks
          }
        />

        <Metric
          label="Blocked"
          value={
            endpoint.blocked_checks
          }
        />

        <Metric
          label="Block Rate"
          value={
            `${endpoint.block_rate_percent}%`
          }
        />

        <Metric
          label="Unique Subjects"
          value={
            endpoint.unique_subjects
          }
        />

        <Metric
          label="Avg Latency"
          value={
            `${endpoint.average_latency_ms} ms`
          }
        />
      </div>


      <div className="mt-6">
        <div className="mb-2 flex justify-between text-xs text-slate-500">
          <span>
            Allowed {allowedPercent.toFixed(1)}%
          </span>

          <span>
            Blocked {blockedPercent.toFixed(1)}%
          </span>
        </div>

        <div className="flex h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className="bg-emerald-500"
            style={{
              width:
                `${allowedPercent}%`,
            }}
          />

          <div
            className="bg-red-500"
            style={{
              width:
                `${blockedPercent}%`,
            }}
          />
        </div>
      </div>


      <div className="mt-5 text-xs text-slate-500">
        Last request:{" "}
        {endpoint.last_request_at
          ? new Date(
              endpoint.last_request_at
            ).toLocaleString()
          : "No requests yet"}
      </div>
    </div>
  );
}


function Metric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg bg-slate-950 p-4">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-2 font-semibold">
        {typeof value === "number"
          ? value.toLocaleString()
          : value}
      </p>
    </div>
  );
}