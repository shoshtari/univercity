import { useCallback, useEffect, useState } from "react";
import { login as apiLogin, getMe } from "../api/auth";

const STORAGE_KEY = "accessKey";

export function useAuth() {
  const [accessKey, setAccessKey] = useState(() => {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  });

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

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
    setLoading(true);

    (async () => {
      const result = await getMe(accessKey);
      if (cancelled) return;

      if (!result.ok) {
        setAccessKey(null);
        setUser(null);
      } else {
        setUser(result.data.username);
      }

      setLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [accessKey]);

  const login = useCallback(async (username, password) => {
    setLoading(true);

    const result = await apiLogin(username, password);

    if (result.ok) {
      setAccessKey(result.data.access_token);
    }

    setLoading(false);
    return result;
  }, []);

  const logout = useCallback(() => {
    setAccessKey(null);
    setUser(null);
  }, []);

  return {
    user,
    accessKey,
    loading,
    login,
    logout,
    isAuthenticated: Boolean(user),
  };
}
