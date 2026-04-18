import { useCallback, useEffect, useState } from "react";
import { login as apiLogin, getMe } from "../api/auth";

const STORAGE_KEY = "accessKey";

export function useAuth() {
  const [accessKey, setAccessKey] = useState(() => {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  });

  const [user, setUser] = useState(null);

  useEffect(() => {
    if (accessKey) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(accessKey));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [accessKey]);

  useEffect(() => {
    if (!accessKey) {
      setUser(null);
      return;
    }

    let cancelled = false;

    (async () => {
      const result = await getMe(accessKey);
      if (cancelled) return;

      if (!result.ok) {
        setAccessKey(null);
        setUser(null);
      } else {
        setUser(result.data.username);
      }

    })();

    return () => {
      cancelled = true;
    };
  }, [accessKey]);

  const login = useCallback(async (username, password) => {

    const result = await apiLogin(username, password);

    if (result.ok) {
      setAccessKey(result.data.access_token);
    }

    return result;
  }, []);

  const logout = useCallback(() => {
    setAccessKey(null);
    setUser(null);
  }, []);

  return {
    user,
    accessKey,
    login,
    logout,
    isAuthenticated: Boolean(user),
  };
}
