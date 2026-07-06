"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  KeyRound,
  Plus,
  ShieldOff,
} from "lucide-react";


type ApiKeyItem = {
  id: number;
  name: string;
  key_prefix: string;
  plan_name: string;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
};


type Plan = {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
};


type CreatedKey = {
  id: number;
  name: string;
  api_key: string;
  key_prefix: string;
  plan_name: string;
  expires_at: string | null;
  message: string;
};


export default function ApiKeysPage() {
  const [keys, setKeys] =
    useState<ApiKeyItem[]>([]);

  const [plans, setPlans] =
    useState<Plan[]>([]);

  const [name, setName] =
    useState("");

  const [planId, setPlanId] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [creating, setCreating] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [createdKey, setCreatedKey] =
    useState<CreatedKey | null>(null);


  const loadData = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const [
          keysResponse,
          plansResponse,
        ] = await Promise.all([
          fetch(
            "/api/admin/api-keys",
            {
              cache: "no-store",
            }
          ),

          fetch(
            "/api/admin/plans",
            {
              cache: "no-store",
            }
          ),
        ]);

        if (!keysResponse.ok) {
          throw new Error(
            "Could not load API keys"
          );
        }

        if (!plansResponse.ok) {
          throw new Error(
            "Could not load plans"
          );
        }

        const keysData =
          await keysResponse.json();

        const plansData =
          await plansResponse.json();

        setKeys(keysData);
        setPlans(plansData);

        if (
          !planId &&
          plansData.length > 0
        ) {
          setPlanId(
            String(plansData[0].id)
          );
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load data"
        );
      } finally {
        setLoading(false);
      }
    },
    [planId]
  );


  useEffect(() => {
    void loadData();
  }, [loadData]);


  async function createKey() {
    if (!name.trim() || !planId) {
      return;
    }

    try {
      setCreating(true);
      setError(null);
      setCreatedKey(null);

      const response = await fetch(
        "/api/admin/api-keys",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            name: name.trim(),
            plan_id: Number(planId),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not create API key"
        );
      }

      setCreatedKey(data);
      setName("");

      await loadData();
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


  async function revokeKey(id: number) {
    const confirmed = window.confirm(
      "Revoke this API key? It will stop working immediately."
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `/api/admin/api-keys/${id}/revoke`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not revoke API key"
        );
      }

      await loadData();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not revoke API key"
      );
    }
  }


  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold">
          API Keys
        </h2>

        <p className="mt-2 text-slate-400">
          Generate and revoke client API keys.
        </p>
      </div>


      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}


      {createdKey && (
        <div className="mb-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5">
          <p className="font-semibold text-emerald-400">
            API key created
          </p>

          <p className="mt-2 text-sm text-slate-300">
            Copy it now. The raw key will not be
            shown again.
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
            className="mt-3 rounded-lg border border-emerald-500/30 px-4 py-2 text-sm text-emerald-400"
          >
            Copy Key
          </button>
        </div>
      )}


      <div className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-5 flex items-center gap-2">
          <Plus size={18} />

          <h3 className="font-semibold">
            Create API Key
          </h3>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <input
            value={name}
            onChange={(event) =>
              setName(event.target.value)
            }
            placeholder="Client name"
            className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
          />

          <select
            value={planId}
            onChange={(event) =>
              setPlanId(event.target.value)
            }
            className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
          >
            {plans.map((plan) => (
              <option
                key={plan.id}
                value={plan.id}
              >
                {plan.name}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => void createKey()}
          disabled={
            creating ||
            !name.trim() ||
            !planId
          }
          className="mt-5 rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:opacity-50"
        >
          {creating
            ? "Creating..."
            : "Generate API Key"}
        </button>
      </div>


      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-5">
          <h3 className="font-semibold">
            Existing API Keys
          </h3>
        </div>

        {loading ? (
          <div className="p-8 text-slate-400">
            Loading API keys...
          </div>
        ) : keys.length === 0 ? (
          <div className="p-8 text-slate-400">
            No API keys found.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-5"
              >
                <div className="flex items-center gap-4">
                  <div className="rounded-lg bg-slate-950 p-3">
                    <KeyRound
                      size={18}
                      className="text-blue-400"
                    />
                  </div>

                  <div>
                    <p className="font-medium">
                      {key.name}
                    </p>

                    <p className="mt-1 font-mono text-xs text-slate-500">
                      {key.key_prefix}...
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs text-blue-400">
                    {key.plan_name}
                  </span>

                  <span
                    className={
                      key.is_active
                        ? "text-sm text-emerald-400"
                        : "text-sm text-red-400"
                    }
                  >
                    {key.is_active
                      ? "Active"
                      : "Revoked"}
                  </span>

                  {key.is_active && (
                    <button
                      onClick={() =>
                        void revokeKey(key.id)
                      }
                      className="rounded-lg border border-red-500/30 p-2 text-red-400 transition hover:bg-red-500/10"
                      title="Revoke API key"
                    >
                      <ShieldOff size={17} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}