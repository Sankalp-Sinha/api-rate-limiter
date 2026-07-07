# RateGuard Architecture

```mermaid
flowchart TB
    Dev[Developer]

    Dev --> UI[Next.js Dashboard]

    UI --> BFF[Next.js Server Routes]

    BFF --> API[FastAPI]

    App[External Project Backend]
        -->|Bearer Project Key + Subject + Route| API

    API --> Auth[Project Key Authentication]
    Auth --> PG[(PostgreSQL)]

    API --> Policy[Policy Lookup]
    Policy --> PG

    API --> Bucket[Token Bucket Service]
    Bucket --> Lua[Atomic Redis Lua Script]
    Lua --> Redis[(Redis)]

    API --> Resp[Decision Response]

    API -. Background Task .-> Logs[Request Logging]
    Logs --> PG

    API --> Metrics[/metrics]
    Metrics --> Prom[Prometheus]
    Prom --> Grafana[Grafana]

    K6[k6] --> API