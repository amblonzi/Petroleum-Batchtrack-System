import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import { useAuthStore } from "./store/auth";

axios.defaults.withCredentials = true;

function App() {
  const { token, setToken } = useAuthStore();

  const { data: user, isLoading, isError } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const res = await axios.get("/api/auth/me");
      return res.data;
    },
    enabled: !!token,
    retry: false,
  });

  useEffect(() => {
    const stored = localStorage.getItem("token");
    if (stored) setToken(stored);
  }, [setToken]);

  useEffect(() => {
    if (isError) {
      setToken(null);
    }
  }, [isError, setToken]);

  if (isLoading && token) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">
        Loading...
      </div>
    );
  }

  if (!token || !user) {
    return <Login />;
  }

  return <Dashboard />;
}

export default App;
