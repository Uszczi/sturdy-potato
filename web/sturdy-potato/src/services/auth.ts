import { api } from "../api";

const ACCESS_KEY = "access";
const REFRESH_KEY = "refresh";
const USERNAME_KEY = "username";

/**
 * Exchange credentials for a JWT pair and persist it. Throws if the API rejects
 * the login (the generated client raises a `ResponseError` for a 401).
 */
export async function login(username: string, password: string): Promise<void> {
  const tokens = await api.apiTokenCreate({
    tokenObtainPair: { username, password },
  });
  localStorage.setItem(ACCESS_KEY, tokens.access);
  localStorage.setItem(REFRESH_KEY, tokens.refresh);
  // The API exposes no "current user" endpoint, so remember the name the user
  // typed to greet them on the overview page.
  localStorage.setItem(USERNAME_KEY, username);
}

/** Drop the stored tokens. JWTs are stateless, so this is a client-side sign-out. */
export function logout(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem(ACCESS_KEY));
}

/** The username captured at login, for display in the app shell. */
export function getUsername(): string {
  return localStorage.getItem(USERNAME_KEY) ?? "";
}
