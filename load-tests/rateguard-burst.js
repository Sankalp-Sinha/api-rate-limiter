import http from "k6/http";
import { check } from "k6";


const BASE_URL =
  __ENV.BASE_URL ||
  "http://host.docker.internal:8000";

const API_KEY =
  __ENV.RATEGUARD_API_KEY;


if (!API_KEY) {
  throw new Error(
    "RATEGUARD_API_KEY is required"
  );
}


export const options = {
  scenarios: {
    concurrent_burst: {
      executor:
        "per-vu-iterations",

      vus: 50,

      iterations: 1,

      maxDuration: "20s",
    },
  },

  thresholds: {
    http_req_failed: [
      "rate<0.01",
    ],

    http_req_duration: [
      "p(95)<500",
    ],
  },
};


export default function () {
  /*
   * Every VU uses exactly the SAME subject.
   *
   * This intentionally makes concurrent
   * requests compete for one Redis bucket.
   */
  const payload = JSON.stringify({
    subject:
      "atomicity-burst-user-2",

    route:
      "/generate-resume",

    method:
      "POST",
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


  check(response, {
    "decision API returned 200":
      (res) => res.status === 200,
  });
}