import {
  Activity,
  Ban,
  Clock3,
  KeyRound,
} from "lucide-react";

const stats = [
  {
    label: "Total Requests",
    value: "0",
    icon: Activity,
  },
  {
    label: "Blocked Requests",
    value: "0",
    icon: Ban,
  },
  {
    label: "Average Latency",
    value: "0 ms",
    icon: Clock3,
  },
  {
    label: "Active API Keys",
    value: "0",
    icon: KeyRound,
  },
];

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold">
          Overview
        </h2>

        <p className="mt-2 text-slate-400">
          Monitor API traffic and rate-limit activity.
        </p>
      </div>

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
                {stat.value}
              </p>
            </div>
          );
        })}
      </div>

      <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h3 className="text-lg font-semibold">
          Traffic Overview
        </h3>

        <div className="mt-6 flex h-64 items-center justify-center rounded-lg border border-dashed border-slate-700 text-slate-500">
          Analytics chart will appear here
        </div>
      </div>
    </div>
  );
}