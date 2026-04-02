import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Dashboard.css";
import DocumentDetails from "./DocumentDetails";
import { number } from "yargs";

function Dashboard() {
    const [docs, setDocs] = useState<any[]>([]);
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("");
    const [sortAsc, setSortAsc] = useState(true);
    const [selectedId, setSelectedId] = useState<number | null>(null);


    const fetchDocs = async () => {
        const res = await axios.get("http://127.0.0.1:8000/documents");
        setDocs(res.data);
    };

    useEffect(() => {
        fetchDocs();

        // const interval = setInterval(fetchDocs, 2000);

        return 
    }, []);

    const handleFinalize = async (id: number) => {
        try {
            await axios.put(`http://localhost:8000/documents/${id}/finalize`);
            alert("Finalized!");
        } catch (err) {
            console.error(err);
        }
    };

    if (selectedId) {
        return (
            <DocumentDetails
                id={selectedId}
                onBack={() => setSelectedId(null)}
            />
        );
    }

    return (
        <div className="container">
            <h2>Documents</h2>

            <div className="actions">
                <button onClick={() => window.open("http://localhost:8000/documents/export/json")}>
                    Export JSON
                </button>

                <button onClick={() => window.open("http://localhost:8000/documents/export/csv")}>
                    Export CSV
                </button>

                <input
                    placeholder="Search filename..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                <select onChange={(e) => setStatusFilter(e.target.value)}>
                    <option value="">All</option>
                    <option value="queued">Queued</option>
                    <option value="processing">Processing</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                </select>
            </div>
            <button onClick={() => setSortAsc(!sortAsc)}>
                Sort by ID ({sortAsc ? "Asc" : "Desc"})
            </button>

            <table border={1}>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Filename</th>
                        <th>Status</th>
                        <th>Progress</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>
                    {docs
                        .filter((doc) =>
                            doc.filename.toLowerCase().includes(search.toLowerCase())
                        )
                        .filter((doc) =>
                            statusFilter ? doc.status === statusFilter : true
                        )
                        .sort((a, b) => (sortAsc ? a.id - b.id : b.id - a.id))
                        .map((doc) => (
                            <tr key={doc.id}>
                                <td>{doc.id}</td>
                                <td>{doc.filename}</td>
                                <td className={doc.status}>{doc.status}</td>
                                <td>
                                    <div className="progress-bar">
                                        <div
                                            className="progress"
                                            style={{ width: `${doc.progress}%` }}
                                        ></div>
                                    </div>
                                </td>
                                <td>
                                    <button
                                        disabled={doc.is_finalized}
                                        onClick={() => handleFinalize(doc.id)}
                                    >
                                        {doc.is_finalized ? "Finalized" : "Finalize"}
                                    </button>

                                    <button onClick={() => setSelectedId(doc.id)}>
                                        View
                                    </button>
                                </td>
                            </tr>

                        ))}
                </tbody>
            </table>
        </div>
    );
}

export default Dashboard;