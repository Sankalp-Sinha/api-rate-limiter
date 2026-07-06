"use client";

import {
  ArrowLeft,
  Copy,
  KeyRound,
  Plus,
  ShieldOff,
  BarChart3,
} from "lucide-react";
import Link from "next/link";
import {
  useCallback,
  useEffect,
  useState,
} from "react";
import { useParams } from "next/navigation";
import ProtectedEndpointsPanel from "@/components/project/ProtectedEndpointsPanel";


type Project = {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
};


type ProjectApiKey = {
  id: number;
  project_id: number;
  name: string;
  key_prefix: string;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
};


type CreatedProjectApiKey = {
  id: number;
  project_id: number;
  name: string;
  api_key: string;
  key_prefix: string;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
  message: string;
};


export default function ProjectDetailPage() {
  const params = useParams<{
    id: string;
  }>();

  const projectId = params.id;

  const [project, setProject] =
    useState<Project | null>(null);

  const [apiKeys, setApiKeys] =
    useState<ProjectApiKey[]>([]);

  const [keyName, setKeyName] =
    useState("");

  const [
    createdKey,
    setCreatedKey,
  ] = useState<
    CreatedProjectApiKey | null
  >(null);

  const [loading, setLoading] =
    useState(true);

  const [creating, setCreating] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  const loadProject = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const [
          projectResponse,
          keysResponse,
        ] = await Promise.all([
          fetch(
            `/api/admin/projects/${projectId}`,
            {
              cache: "no-store",
            }
          ),

          fetch(
            `/api/admin/projects/${projectId}/api-keys`,
            {
              cache: "no-store",
            }
          ),
        ]);

        const projectData =
          await projectResponse.json();

        const keysData =
          await keysResponse.json();

        if (!projectResponse.ok) {
          throw new Error(
            projectData.detail ??
            projectData.error ??
            "Could not load project"
          );
        }

        if (!keysResponse.ok) {
          throw new Error(
            keysData.detail ??
            keysData.error ??
            "Could not load API keys"
          );
        }

        setProject(projectData);
        setApiKeys(keysData);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load project"
        );
      } finally {
        setLoading(false);
      }
    },
    [projectId]
  );


  useEffect(() => {
    void loadProject();
  }, [loadProject]);


  async function createApiKey() {
    if (!keyName.trim()) {
      return;
    }

    try {
      setCreating(true);
      setError(null);
      setCreatedKey(null);

      const response = await fetch(
        `/api/admin/projects/${projectId}/api-keys`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            name: keyName.trim(),
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not create API key"
        );
      }

      setCreatedKey(data);
      setKeyName("");

      await loadProject();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not create API key"
      );
    } finally {
      setCreating(false);
    }
  }


  async function revokeApiKey(
    apiKeyId: number
  ) {
    const confirmed = window.confirm(
      "Revoke this project integration key?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);

      const response = await fetch(
        `/api/admin/projects/${projectId}/api-keys/${apiKeyId}/revoke`,
        {
          method: "POST",
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not revoke API key"
        );
      }

      await loadProject();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not revoke API key"
      );
    }
  }


  if (loading) {
    return (
      <div className="text-slate-400">
        Loading project...
      </div>
    );
  }


  if (!project) {
    return (
      <div className="text-red-400">
        Project not found.
      </div>
    );
  }


  return (
    <div>
      <Link
        href="/dashboard/projects"
        className="mb-6 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"
      >
        <ArrowLeft size={16} />
        Back to Projects
      </Link>


      <div className="mb-8 flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold">
            {project.name}
          </h2>

          <p className="mt-2 font-mono text-sm text-slate-500">
            {project.slug}
          </p>
        </div>

        <div className="flex items-center gap-3">
    <Link
      href={
        `/dashboard/projects/${projectId}/analytics`
      }
      className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-900"
    >
      <BarChart3 size={17} />
      View Analytics
    </Link>

    <span className="rounded-full bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400">
      ● Active
    </span>
  </div>
      </div>


      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}


      {createdKey && (
        <div className="mb-8 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-6">
          <h3 className="font-semibold text-emerald-400">
            Integration key created
          </h3>

          <p className="mt-2 text-sm text-slate-300">
            Copy this key now. RateGuard
            will not show the raw key again.
          </p>

          <div className="mt-4 break-all rounded-lg bg-slate-950 p-4 font-mono text-sm">
            {createdKey.api_key}
          </div>

          <button
            onClick={() =>
              void navigator.clipboard.writeText(
                createdKey.api_key
              )
            }
            className="mt-4 inline-flex items-center gap-2 rounded-lg border border-emerald-500/30 px-4 py-2 text-sm text-emerald-400 transition hover:bg-emerald-500/10"
          >
            <Copy size={16} />
            Copy Key
          </button>

          <div className="mt-5 rounded-lg bg-slate-950 p-4">
            <p className="text-xs text-slate-500">
              Store in Project X backend:
            </p>

            <pre className="mt-2 overflow-x-auto text-sm text-blue-300">
{`RATEGUARD_API_KEY=${createdKey.api_key}`}
            </pre>
          </div>
        </div>
      )}


      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5 flex items-center gap-2">
            <KeyRound
              size={19}
              className="text-blue-400"
            />

            <h3 className="font-semibold">
              Integration Keys
            </h3>
          </div>

          <div className="flex gap-3">
            <input
              value={keyName}
              onChange={(event) =>
                setKeyName(
                  event.target.value
                )
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  void createApiKey();
                }
              }}
              placeholder="e.g. Production Backend"
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
            />

            <button
              onClick={() =>
                void createApiKey()
              }
              disabled={
                creating ||
                !keyName.trim()
              }
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-3 font-medium transition hover:bg-blue-500 disabled:opacity-50"
            >
              <Plus size={17} />

              {creating
                ? "Creating..."
                : "Create Key"}
            </button>
          </div>


          <div className="mt-6 space-y-3">
            {apiKeys.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center text-sm text-slate-500">
                No integration keys yet.
              </div>
            ) : (
              apiKeys.map((apiKey) => (
                <div
                  key={apiKey.id}
                  className="flex items-center justify-between rounded-lg bg-slate-950 p-4"
                >
                  <div>
                    <p className="font-medium">
                      {apiKey.name}
                    </p>

                    <p className="mt-1 font-mono text-xs text-slate-500">
                      {apiKey.key_prefix}...
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={
                        apiKey.is_active
                          ? "text-sm text-emerald-400"
                          : "text-sm text-red-400"
                      }
                    >
                      {apiKey.is_active
                        ? "Active"
                        : "Revoked"}
                    </span>

                    {apiKey.is_active && (
                      <button
                        onClick={() =>
                          void revokeApiKey(
                            apiKey.id
                          )
                        }
                        title="Revoke key"
                        className="rounded-lg border border-red-500/30 p-2 text-red-400 transition hover:bg-red-500/10"
                      >
                        <ShieldOff
                          size={16}
                        />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>


       <ProtectedEndpointsPanel projectId={projectId} />
      </div>
    </div>
  );
}