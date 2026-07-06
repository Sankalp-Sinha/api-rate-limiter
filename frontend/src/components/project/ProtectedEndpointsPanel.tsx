"use client";

import {
  Pencil,
  Plus,
  Power,
  Route,
  X,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";


type Policy = {
  id: number;
  project_id: number;
  route_path: string;
  http_method: string;
  capacity: number;
  refill_rate: number;
  refill_amount: number;
  refill_unit: string;
  tokens_required: number;
  is_active: boolean;
  created_at: string;
};


type Props = {
  projectId: string;
};


const HTTP_METHODS = [
  "GET",
  "POST",
  "PUT",
  "PATCH",
  "DELETE",
];


export default function ProtectedEndpointsPanel({
  projectId,
}: Props) {
  const [policies, setPolicies] =
    useState<Policy[]>([]);

  const [routePath, setRoutePath] =
    useState("");

  const [httpMethod, setHttpMethod] =
    useState("POST");

  const [capacity, setCapacity] =
    useState("5");

  const [
    refillAmount,
    setRefillAmount,
  ] = useState("1");

  const [refillUnit, setRefillUnit] =
    useState("minute");

  const [
    editingPolicyId,
    setEditingPolicyId,
  ] = useState<number | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  const loadPolicies = useCallback(
    async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(
          `/api/admin/projects/${projectId}/policies`,
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
            "Could not load policies"
          );
        }

        setPolicies(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not load policies"
        );
      } finally {
        setLoading(false);
      }
    },
    [projectId]
  );


  useEffect(() => {
    void loadPolicies();
  }, [loadPolicies]);


  function resetForm() {
    setRoutePath("");
    setHttpMethod("POST");
    setCapacity("5");
    setRefillAmount("1");
    setRefillUnit("minute");
    setEditingPolicyId(null);
  }


  async function savePolicy() {
    if (
      !routePath.trim() ||
      Number(capacity) <= 0 ||
      Number(refillAmount) <= 0
    ) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const body = {
        capacity: Number(capacity),
        refill_amount:
          Number(refillAmount),
        refill_unit: refillUnit,
        tokens_required: 1,
      };

      let response: Response;

      if (editingPolicyId !== null) {
        response = await fetch(
          `/api/admin/projects/${projectId}/policies/${editingPolicyId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify(body),
          }
        );
      } else {
        response = await fetch(
          `/api/admin/projects/${projectId}/policies`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              route_path:
                routePath.trim(),
              http_method:
                httpMethod,
              ...body,
            }),
          }
        );
      }

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ??
          data.error ??
          "Could not save policy"
        );
      }

      resetForm();

      await loadPolicies();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not save policy"
      );
    } finally {
      setSaving(false);
    }
  }


  function beginEdit(
    policy: Policy
  ) {
    setEditingPolicyId(policy.id);

    setRoutePath(
      policy.route_path
    );

    setHttpMethod(
      policy.http_method
    );

    setCapacity(
      String(policy.capacity)
    );

    setRefillAmount(
      String(policy.refill_amount)
    );

    setRefillUnit(
      policy.refill_unit
    );
  }


  async function deactivatePolicy(
    policyId: number
  ) {
    const confirmed = window.confirm(
      "Deactivate this protected endpoint?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);

      const response = await fetch(
        `/api/admin/projects/${projectId}/policies/${policyId}/deactivate`,
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
          "Could not deactivate policy"
        );
      }

      await loadPolicies();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not deactivate policy"
      );
    }
  }


  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-5 flex items-center gap-2">
        <Route
          size={19}
          className="text-violet-400"
        />

        <h3 className="font-semibold">
          Protected Endpoints
        </h3>
      </div>


      {error && (
        <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}


      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
        <div className="grid gap-3 md:grid-cols-2">
          <select
            value={httpMethod}
            onChange={(event) =>
              setHttpMethod(
                event.target.value
              )
            }
            disabled={
              editingPolicyId !== null
            }
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-3 outline-none disabled:opacity-50"
          >
            {HTTP_METHODS.map(
              (method) => (
                <option
                  key={method}
                  value={method}
                >
                  {method}
                </option>
              )
            )}
          </select>

          <input
            value={routePath}
            onChange={(event) =>
              setRoutePath(
                event.target.value
              )
            }
            disabled={
              editingPolicyId !== null
            }
            placeholder="/generate-resume"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-3 outline-none focus:border-blue-500 disabled:opacity-50"
          />

          <input
            type="number"
            min="1"
            value={capacity}
            onChange={(event) =>
              setCapacity(
                event.target.value
              )
            }
            placeholder="Capacity"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-3 outline-none focus:border-blue-500"
          />

          <div className="flex gap-2">
            <input
              type="number"
              min="0.000001"
              step="any"
              value={refillAmount}
              onChange={(event) =>
                setRefillAmount(
                  event.target.value
                )
              }
              placeholder="Refill"
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-3 outline-none focus:border-blue-500"
            />

            <select
              value={refillUnit}
              onChange={(event) =>
                setRefillUnit(
                  event.target.value
                )
              }
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-3 outline-none"
            >
              <option value="second">
                / second
              </option>

              <option value="minute">
                / minute
              </option>

              <option value="hour">
                / hour
              </option>
            </select>
          </div>
        </div>


        <div className="mt-4 flex gap-3">
          <button
            onClick={() =>
              void savePolicy()
            }
            disabled={
              saving ||
              !routePath.trim()
            }
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium transition hover:bg-blue-500 disabled:opacity-50"
          >
            <Plus size={16} />

            {saving
              ? "Saving..."
              : editingPolicyId !== null
                ? "Update Policy"
                : "Add Endpoint"}
          </button>

          {editingPolicyId !== null && (
            <button
              onClick={resetForm}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2.5 text-sm text-slate-300"
            >
              <X size={16} />
              Cancel
            </button>
          )}
        </div>
      </div>


      <div className="mt-6 space-y-3">
        {loading ? (
          <p className="text-sm text-slate-500">
            Loading endpoints...
          </p>
        ) : policies.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center">
            <p className="text-slate-400">
              No protected endpoints yet.
            </p>
          </div>
        ) : (
          policies.map((policy) => (
            <div
              key={policy.id}
              className="rounded-lg bg-slate-950 p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-violet-500/10 px-2 py-1 font-mono text-xs text-violet-400">
                      {policy.http_method}
                    </span>

                    <span className="font-mono text-sm">
                      {policy.route_path}
                    </span>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
                    <span>
                      Capacity:{" "}
                      {policy.capacity}
                    </span>

                    <span>
                      Refill:{" "}
                      {policy.refill_amount}/
                      {policy.refill_unit}
                    </span>

                    <span
                      className={
                        policy.is_active
                          ? "text-emerald-400"
                          : "text-red-400"
                      }
                    >
                      {policy.is_active
                        ? "● Active"
                        : "● Inactive"}
                    </span>
                  </div>
                </div>


                {policy.is_active && (
                  <div className="flex gap-2">
                    <button
                      onClick={() =>
                        beginEdit(policy)
                      }
                      title="Edit policy"
                      className="rounded-lg border border-slate-700 p-2 text-slate-300 transition hover:bg-slate-800"
                    >
                      <Pencil size={15} />
                    </button>

                    <button
                      onClick={() =>
                        void deactivatePolicy(
                          policy.id
                        )
                      }
                      title="Deactivate policy"
                      className="rounded-lg border border-red-500/30 p-2 text-red-400 transition hover:bg-red-500/10"
                    >
                      <Power size={15} />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}