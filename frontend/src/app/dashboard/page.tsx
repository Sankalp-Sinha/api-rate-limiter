"use client";

import {
  FolderKanban,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import Link from "next/link";
import {
  useEffect,
  useState,
} from "react";


type User = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string;
};


type Project = {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
};


export default function DashboardPage() {
  const [user, setUser] =
    useState<User | null>(null);

  const [projects, setProjects] =
    useState<Project[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [
          userResponse,
          projectsResponse,
        ] = await Promise.all([
          fetch(
            "/api/auth/me",
            {
              cache: "no-store",
            }
          ),

          fetch(
            "/api/admin/projects",
            {
              cache: "no-store",
            }
          ),
        ]);

        const userData =
          await userResponse.json();

        const projectsData =
          await projectsResponse.json();

        if (!userResponse.ok) {
          throw new Error(
            userData.detail ??
            userData.error ??
            "Could not load account"
          );
        }

        if (!projectsResponse.ok) {
          throw new Error(
            projectsData.detail ??
            projectsData.error ??
            "Could not load projects"
          );
        }

        setUser(userData);
        setProjects(projectsData);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load dashboard"
        );
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);


  const activeProjects =
    projects.filter(
      (project) =>
        project.is_active
    ).length;


  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold">
          {user
            ? `Welcome, ${user.name}`
            : "Dashboard"}
        </h2>

        <p className="mt-2 text-slate-400">
          Manage your RateGuard projects
          and protected endpoints.
        </p>
      </div>


      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}


      <div className="grid gap-5 md:grid-cols-3">
        <StatCard
          label="Your Projects"
          value={
            loading
              ? "..."
              : projects.length
          }
          icon={FolderKanban}
        />

        <StatCard
          label="Active Projects"
          value={
            loading
              ? "..."
              : activeProjects
          }
          icon={ShieldCheck}
        />

        <StatCard
          label="Developer Account"
          value={
            loading
              ? "..."
              : user?.email ?? "-"
          }
          icon={UserRound}
        />
      </div>


      <div className="mt-10">
        <div className="mb-5 flex items-center justify-between">
          <h3 className="text-xl font-semibold">
            Your Projects
          </h3>

          <Link
            href="/dashboard/projects"
            className="text-sm text-blue-400 transition hover:text-blue-300"
          >
            View all
          </Link>
        </div>


        {loading ? (
          <p className="text-slate-400">
            Loading projects...
          </p>
        ) : projects.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center">
            <p className="text-slate-400">
              You have not created a project yet.
            </p>

            <Link
              href="/dashboard/projects"
              className="mt-4 inline-block text-blue-400"
            >
              Create your first project
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {projects
              .slice(0, 6)
              .map((project) => (
                <Link
                  key={project.id}
                  href={
                    `/dashboard/projects/${project.id}`
                  }
                  className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">
                        {project.name}
                      </p>

                      <p className="mt-2 font-mono text-xs text-slate-500">
                        {project.slug}
                      </p>
                    </div>

                    <span
                      className={
                        project.is_active
                          ? "text-xs text-emerald-400"
                          : "text-xs text-red-400"
                      }
                    >
                      {project.is_active
                        ? "● Active"
                        : "● Inactive"}
                    </span>
                  </div>
                </Link>
              ))}
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
}: {
  label: string;
  value: string | number;
  icon: typeof FolderKanban;
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

      <p className="mt-4 break-words text-2xl font-semibold">
        {typeof value === "number"
          ? value.toLocaleString()
          : value}
      </p>
    </div>
  );
}