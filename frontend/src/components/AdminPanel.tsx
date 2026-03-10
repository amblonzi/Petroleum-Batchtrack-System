import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import type { User, Pipeline } from "../types";

export default function AdminPanel() {
    const queryClient = useQueryClient();
    const [activeTab, setActiveTab] = useState<"users" | "pipelines">("users");

    // Fetch users
    const { data: users, isLoading: usersLoading } = useQuery<User[]>({
        queryKey: ["admin_users"],
        queryFn: () => api.get("/admin/users").then(r => r.data),
    });

    const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
    const [newUser, setNewUser] = useState({ username: "", full_name: "", password: "", is_admin: false });

    // User Mutations
    const createUserMutation = useMutation({
        mutationFn: (data: typeof newUser) => api.post("/admin/users", data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["admin_users"] });
            setIsAddUserModalOpen(false);
            setNewUser({ username: "", full_name: "", password: "", is_admin: false });
        },
    });
    // Fetch pipelines
    const { data: pipelines, isLoading: pipelinesLoading } = useQuery<Pipeline[]>({
        queryKey: ["admin_pipelines"],
        queryFn: () => api.get("/pipelines/").then(r => r.data),
    });

    // User Mutations
    const toggleRoleMutation = useMutation({
        mutationFn: ({ userId, isAdmin }: { userId: number; isAdmin: boolean }) =>
            api.put(`/admin/users/${userId}/role?is_admin=${isAdmin}`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin_users"] }),
    });

    const deleteUserMutation = useMutation({
        mutationFn: (userId: number) => api.delete(`/admin/users/${userId}`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin_users"] }),
    });

    // Pipeline Mutations
    const updatePipelineMutation = useMutation({
        mutationFn: ({ pipelineId, updates }: { pipelineId: number; updates: { line_fill_rate: number } }) =>
            api.put(`/admin/pipelines/${pipelineId}`, updates),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["admin_pipelines"] });
            queryClient.invalidateQueries({ queryKey: ["pipelines"] }); // Global pipelines state
        },
    });

    const clearPipelineDataMutation = useMutation({
        mutationFn: (pipelineId: number) => api.delete(`/admin/pipelines/${pipelineId}/data`),
        onSuccess: () => window.location.reload(), // Full reload to clear context artifacts
    });

    return (
        <div className="absolute inset-0 flex flex-col p-6 space-y-6">
            <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 flex flex-col flex-1 w-full max-w-5xl mx-auto">
                {/* Tab Navigation */}
                <div className="flex border-b border-gray-700">
                    <button
                        onClick={() => setActiveTab("users")}
                        className={`flex-1 py-4 px-6 text-center font-bold text-lg transition-colors ${activeTab === "users"
                            ? "bg-blue-600 text-white"
                            : "text-gray-400 hover:text-white hover:bg-gray-750"
                            }`}
                    >
                        User Management
                    </button>
                    <button
                        onClick={() => setActiveTab("pipelines")}
                        className={`flex-1 py-4 px-6 text-center font-bold text-lg transition-colors border-l border-gray-700 ${activeTab === "pipelines"
                            ? "bg-purple-600 text-white"
                            : "text-gray-400 hover:text-white hover:bg-gray-750"
                            }`}
                    >
                        Pipeline Settings
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto custom-scrollbar">
                    {activeTab === "users" && (
                        <div>
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold">System Users</h3>
                                <button
                                    onClick={() => setIsAddUserModalOpen(true)}
                                    className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded font-bold transition-colors flex items-center gap-2"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                                    </svg>
                                    Add New User
                                </button>
                            </div>
                            {usersLoading ? (
                                <p>Loading users...</p>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-sm text-gray-300">
                                        <thead className="bg-gray-700/50 text-gray-200 uppercase text-xs">
                                            <tr>
                                                <th className="px-4 py-3">ID</th>
                                                <th className="px-4 py-3">Username</th>
                                                <th className="px-4 py-3">Full Name</th>
                                                <th className="px-4 py-3">Role</th>
                                                <th className="px-4 py-3 text-right">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-700 font-mono">
                                            {users?.map(u => (
                                                <tr key={u.id} className="hover:bg-gray-750 transition-colors">
                                                    <td className="px-4 py-3">{u.id}</td>
                                                    <td className="px-4 py-3 font-bold">{u.username}</td>
                                                    <td className="px-4 py-3">{u.full_name || "-"}</td>
                                                    <td className="px-4 py-3">
                                                        <span className={`px-2 py-1 rounded text-xs font-bold ${u.is_admin ? "bg-amber-500/20 text-amber-400" : "bg-gray-600 text-gray-300"}`}>
                                                            {u.is_admin ? "Admin" : "Standard"}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 text-right space-x-2">
                                                        <button
                                                            onClick={() => toggleRoleMutation.mutate({ userId: u.id, isAdmin: !u.is_admin })}
                                                            className="text-xs px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-white transition-colors"
                                                        >
                                                            {u.is_admin ? "Demote" : "Promote"}
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                if (window.confirm("Are you sure you want to delete this user?")) {
                                                                    deleteUserMutation.mutate(u.id);
                                                                }
                                                            }}
                                                            className="text-xs px-3 py-1 bg-red-600/80 hover:bg-red-500 rounded text-white transition-colors"
                                                        >
                                                            Delete
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === "pipelines" && (
                        <div>
                            <h3 className="text-xl font-bold mb-4">Pipeline Technical Settings</h3>
                            {pipelinesLoading ? (
                                <p>Loading pipelines...</p>
                            ) : (
                                <div className="grid grid-cols-1 gap-6">
                                    {pipelines?.map(p => (
                                        <div key={p.id} className="bg-gray-900 border border-gray-700 p-4 rounded-lg flex flex-col md:flex-row gap-4 items-center justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="bg-blue-600 text-white text-xs font-bold px-2 py-0.5 rounded">{p.line_number}</span>
                                                    <h4 className="font-bold text-lg">{p.name}</h4>
                                                </div>
                                                <p className="text-sm text-gray-400">{p.description}</p>
                                                <p className="text-sm text-gray-400 mt-1">Length: <span className="font-mono text-white">{p.total_length_km} km</span></p>
                                            </div>

                                            <div className="flex items-center gap-6">
                                                <div className="flex flex-col">
                                                    <label className="text-xs text-gray-400 mb-1">Line Fill Rate (m³/km)</label>
                                                    <input
                                                        aria-label="Line fill rate"
                                                        title="Line fill rate"
                                                        type="number"
                                                        step="0.01"
                                                        defaultValue={p.line_fill_rate}
                                                        onBlur={(e) => {
                                                            const val = parseFloat(e.target.value);
                                                            if (val && val !== p.line_fill_rate) {
                                                                if (window.confirm(`Update ${p.line_number} line fill rate to ${val} m³/km?`)) {
                                                                    updatePipelineMutation.mutate({ pipelineId: p.id, updates: { line_fill_rate: val } });
                                                                } else {
                                                                    e.target.value = p.line_fill_rate.toString();
                                                                }
                                                            }
                                                        }}
                                                        className="bg-gray-800 border border-gray-600 rounded px-3 py-1.5 w-32 font-mono text-white focus:outline-none focus:border-blue-500 transition-colors"
                                                    />
                                                </div>

                                                <div className="flex flex-col justify-end h-full">
                                                    <button
                                                        onClick={() => {
                                                            const confirmText = `DANGER: Reset ${p.line_number}\n\nType the line name explicitly ("${p.line_number}") to delete ALL batches and flow entries specific to this pipeline.`;
                                                            const input = window.prompt(confirmText);
                                                            if (input === p.line_number) {
                                                                clearPipelineDataMutation.mutate(p.id);
                                                            } else if (input !== null) {
                                                                alert("Mismatch. Deletion aborted.");
                                                            }
                                                        }}
                                                        className="bg-red-900/40 text-red-500 border border-red-900 hover:bg-red-800 hover:text-white px-4 py-1.5 rounded text-sm font-bold transition-all"
                                                    >
                                                        Reset Pipeline Data
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Add User Modal */}
            {isAddUserModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                    <div className="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="bg-gray-700/50 p-4 border-b border-gray-600 flex justify-between items-center">
                            <h3 className="text-lg font-bold">Create New User</h3>
                            <button onClick={() => setIsAddUserModalOpen(false)} className="text-gray-400 hover:text-white transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <form onSubmit={(e) => {
                            e.preventDefault();
                            createUserMutation.mutate(newUser);
                        }} className="p-6 space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Username</label>
                                <input
                                    type="text"
                                    required
                                    value={newUser.username}
                                    onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                                    className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
                                    placeholder="e.g. johndoe"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Full Name</label>
                                <input
                                    type="text"
                                    value={newUser.full_name}
                                    onChange={e => setNewUser({ ...newUser, full_name: e.target.value })}
                                    className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
                                    placeholder="e.g. John Doe"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Password</label>
                                <input
                                    type="password"
                                    required
                                    value={newUser.password}
                                    onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                                    className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
                                    placeholder="••••••••"
                                />
                            </div>
                            <div className="flex items-center gap-3 py-2">
                                <input
                                    type="checkbox"
                                    id="isAdmin"
                                    checked={newUser.is_admin}
                                    onChange={e => setNewUser({ ...newUser, is_admin: e.target.checked })}
                                    className="w-4 h-4 bg-gray-900 border-gray-600 rounded text-blue-600 focus:ring-blue-500 focus:ring-offset-gray-800"
                                />
                                <label htmlFor="isAdmin" className="text-sm text-gray-300 font-medium cursor-pointer">Administrator Privileges</label>
                            </div>

                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsAddUserModalOpen(false)}
                                    className="flex-1 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white font-bold transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={createUserMutation.isPending}
                                    className="flex-1 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors disabled:opacity-50"
                                >
                                    {createUserMutation.isPending ? "Creating..." : "Create User"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
