import Link from "next/link";
import {
  Activity,
  BarChart3,
  Gauge,
  FolderKanban,
  KeyRound,
  Play,
  LayoutDashboard,
} from "lucide-react";

const navigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Projects",
    href: "/dashboard/projects",
    icon: FolderKanban,
  },
  {
    name: "API Keys",
    href: "/dashboard/api-keys",
    icon: KeyRound,
  },
  {
    name: "Analytics",
    href: "/dashboard/analytics",
    icon: BarChart3,
  },
  {
    name: "Playground",
    href: "/dashboard/playground",
    icon: Gauge,
  },
];

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-800 bg-slate-950">
        <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
            <Activity size={20} />
          </div>

          <div>
            <p className="font-semibold">RateGuard</p>
            <p className="text-xs text-slate-400">
              API Protection
            </p>
          </div>
        </div>

        <nav className="space-y-2 p-4">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-slate-300 transition hover:bg-slate-900 hover:text-white"
              >
                <Icon size={18} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="ml-64 min-h-screen">
        <header className="flex h-16 items-center justify-between border-b border-slate-800 px-8">
          <div>
            <h1 className="font-semibold">
              Distributed API Rate Limiter
            </h1>
          </div>

          <div className="rounded-full border border-slate-700 px-3 py-1 text-xs text-emerald-400">
            System Online
          </div>
        </header>

        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}