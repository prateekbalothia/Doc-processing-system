import { useEffect, useState } from "react";
import axios from "axios";

const DocumentDetails = ({ id, onBack }) => {
  const [doc, setDoc] = useState(null);

  useEffect(() => {
    fetchDoc();
  }, []);

  const fetchDoc = async () => {
    const res = await axios.get(`http://localhost:8000/documents/${id}`);
    setDoc(res.data);
  };

  const handleChange = (e) => {
    setDoc({
      ...doc,
      result: {
        ...doc.result,
        [e.target.name]: e.target.value
      }
    });
  };

  const handleSave = async () => {
    await axios.put(`http://localhost:8000/documents/${id}`, doc.result);
    alert("Updated!");
  };

  if (!doc) return <p>Loading...</p>;

  return (
    <div style={{ padding: "20px" }}>
      <button onClick={onBack}>⬅ Back</button>

      <h2>{doc.filename}</h2>

      <input
        name="title"
        value={doc.result?.title || ""}
        onChange={handleChange}
      />

      <input
        name="category"
        value={doc.result?.category || ""}
        onChange={handleChange}
      />

      <textarea
        name="summary"
        value={doc.result?.summary || ""}
        onChange={handleChange}
      />

      <button onClick={handleSave}>Save</button>
    </div>
  );
};

export default DocumentDetails;