"use client";

import {
  FolderKanban,
  Plus,
} from "lucide-react";
import Link from "next/link";
import {
  useCallback,
  useEffect,
  useState,
} from "react";


type Project = {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
};


export default function ProjectsPage() {
  const [projects, setProjects] =
    useState<Project[]>([]);

  const [name, setName] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [creating, setCreating] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  const loadProjects = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          "/api/admin/projects",
          {
            cache: "no-store",
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ??
            data.error ??
            "Could not load projects"
          );
        }

        setProjects(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load projects"
        );
      } finally {
        setLoading(false);
      }
    },
    []
  );


  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);


  async function createProject() {
    if (!name.trim()) {
      return;
    }

    try {
      setCreating(true);
      setError(null);

      const response = await fetch(
        "/api/admin/projects",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            name: name.trim(),
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not create project"
        );
      }

      setName("");

      await loadProjects();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not create project"
      );
    } finally {
      setCreating(false);
    }
  }


  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold">
          Projects
        </h2>

        <p className="mt-2 text-slate-400">
          Create applications that use
          RateGuard for rate limiting.
        </p>
      </div>


      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}


      <div className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-5 flex items-center gap-2">
          <Plus size={18} />

          <h3 className="font-semibold">
            Create Project
          </h3>
        </div>

        <div className="flex gap-4">
          <input
            value={name}
            onChange={(event) =>
              setName(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                void createProject();
              }
            }}
            placeholder="e.g. AI Resume Generator"
            className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
          />

          <button
            onClick={() =>
              void createProject()
            }
            disabled={
              creating ||
              !name.trim()
            }
            className="rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:opacity-50"
          >
            {creating
              ? "Creating..."
              : "Create Project"}
          </button>
        </div>
      </div>


      {loading ? (
        <div className="text-slate-400">
          Loading projects...
        </div>
      ) : projects.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-700 p-12 text-center">
          <FolderKanban
            className="mx-auto text-slate-500"
            size={36}
          />

          <p className="mt-4 text-slate-400">
            No projects yet.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={
                `/dashboard/projects/${project.id}`
              }
              className="rounded-xl border border-slate-800 bg-slate-900 p-6 transition hover:border-blue-500/50 hover:bg-slate-900/80"
            >
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-blue-500/10 p-3">
                  <FolderKanban
                    size={20}
                    className="text-blue-400"
                  />
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

              <h3 className="mt-5 text-lg font-semibold">
                {project.name}
              </h3>

              <p className="mt-2 font-mono text-xs text-slate-500">
                {project.slug}
              </p>

              <p className="mt-5 text-sm text-blue-400">
                Open project →
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}