import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Calls `apiFn(...params)` on mount and whenever `params` change.
 * Returns { data, loading, error, reload }.
 */
export default function useApi(apiFn, params = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fnRef = useRef(apiFn);
  fnRef.current = apiFn;
  const requestId = useRef(0);
  const paramsKey = JSON.stringify(params);

  const load = useCallback(async () => {
    const id = ++requestId.current;
    setLoading(true);
    setError(null);
    try {
      const result = await fnRef.current(...JSON.parse(paramsKey));
      if (id === requestId.current) setData(result);
    } catch (err) {
      if (id === requestId.current) setError(err.message);
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  }, [paramsKey]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
