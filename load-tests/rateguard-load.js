import http from "k6/http";
import { check, sleep } from "k6";
import execution from "k6/execution";
import {
  Counter,
  Rate,
} from "k6/metrics";


const BASE_URL =
  __ENV.BASE_URL ||
  "http://host.docker.internal:8000";

const API_KEY =
  __ENV.RATEGUARD_API_KEY;


if (!API_KEY) {
  throw new Error(
    "RATEGUARD_API_KEY environment variable is required"
  );
}


// ------------------------------------------
// Custom k6 metrics
// ------------------------------------------

const allowedDecisions = new Counter(
  "rateguard_allowed_decisions"
);

const blockedDecisions = new Counter(
  "rateguard_blocked_decisions"
);

const validDecisionRate = new Rate(
  "rateguard_valid_decisions"
);


// ------------------------------------------
// Load profile
// ------------------------------------------

export const options = {
  stages: [
    {
      duration: "20s",
      target: 10,
    },
    {
      duration: "30s",
      target: 25,
    },
    {
      duration: "30s",
      target: 50,
    },
    {
      duration: "20s",
      target: 0,
    },
  ],

  thresholds: {
    // Fewer than 1% HTTP-level failures.
    http_req_failed: [
      "rate<0.01",
    ],

    // Initial local target:
    // p95 under 250 ms.
    http_req_duration: [
      "p(95)<250",
    ],

    // Almost every response must be
    // structurally valid.
    rateguard_valid_decisions: [
      "rate>0.99",
    ],
  },
};


// ------------------------------------------
// Test execution
// ------------------------------------------

export default function () {
  /*
   * Each VU gets a stable subject.
   *
   * VU 1 -> load-user:1
   * VU 2 -> load-user:2
   *
   * Therefore different VUs exercise
   * independent Redis token buckets.
   */
  const subject =
    `load-user:${execution.vu.idInTest}`;


  const payload = JSON.stringify({
    subject,
    route: "/generate-resume",
    method: "POST",
  });


  const response = http.post(
    `${BASE_URL}/v1/check`,
    payload,
    {
      headers: {
        "Content-Type":
          "application/json",

        Authorization:
          `Bearer ${API_KEY}`,
      },
    }
  );


  let body = null;

  try {
    body = response.json();
  } catch {
    body = null;
  }


  const structurallyValid =
    response.status === 200 &&
    body !== null &&
    typeof body.allowed === "boolean" &&
    typeof body.remaining === "number";


  validDecisionRate.add(
    structurallyValid
  );


  check(response, {
    "HTTP status is 200": (res) =>
      res.status === 200,

    "response has decision": () =>
      structurallyValid,
  });


  if (structurallyValid) {
    if (body.allowed) {
      allowedDecisions.add(1);
    } else {
      blockedDecisions.add(1);
    }
  }


  sleep(0.1);
}