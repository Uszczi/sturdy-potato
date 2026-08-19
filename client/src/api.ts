import { Configuration, ApiApi, ProjectsApi, TasksApi } from "../api-client";

// Same-origin: in production FastAPI serves both this SPA and the API; in dev
// Vite proxies /api to the backend (see vite.config.ts). An empty base path
// keeps requests on the current origin in both cases — no CORS, no hard-coded
// host.
const BASE_PATH = "";

// The generated client reads `accessToken` lazily on every request, so we point
// it at localStorage. After logging in we stash the JWT there and every
// subsequent call sends `Authorization: Bearer <token>` automatically.
//
// The generator splits endpoints into one class per OpenAPI tag, so we share a
// single Configuration across the auth (`api`), projects, and tasks clients.
const config = new Configuration({
  basePath: BASE_PATH,
  accessToken: () => localStorage.getItem("access") ?? "",
});

export const api = new ApiApi(config);
export const projectsApi = new ProjectsApi(config);
export const tasksApi = new TasksApi(config);
