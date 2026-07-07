import Link from "next/link";
import {
  Activity,
  FolderKanban,
  ShieldCheck,
} from "lucide-react";

import LogoutButton from "@/components/auth/LogoutButton";


const navigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: Activity,
  },
  {
    name: "Projects",
    href: "/dashboard/projects",
    icon: FolderKanban,
  },
];


export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Sidebar */}
      <aside className="fixed left-0 top-0 flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-900 p-5">

        {/* Logo */}
        <div className="mb-8 flex items-center gap-3">
          <div className="rounded-lg bg-blue-600 p-2">
            <ShieldCheck size={22} />
          </div>

          <div>
            <h1 className="font-bold">
              RateGuard
            </h1>

            <p className="text-xs text-slate-500">
              API Protection
            </p>
          </div>
        </div>


        {/* Navigation */}
        <nav className="flex flex-1 flex-col gap-2">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-800 hover:text-white"
              >
                <Icon size={18} />
                {item.name}
              </Link>
            );
          })}
        </nav>


        {/* Paste LogoutButton here */}
        <div className="mt-auto border-t border-slate-800 pt-4">
          <LogoutButton />
        </div>

      </aside>


      {/* Main content */}
      <main className="ml-64 min-h-screen p-8">
        {children}
      </main>

    </div>
  );
}