import React, { useState } from "react";
import axios from "axios";

function Upload() {
  const [file, setFile] = useState<File | null>(null);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post("http://127.0.0.1:8000/upload", formData);

    alert("Uploaded! ID: " + res.data.document_id);
  };

  return (
    <div>
      <h2>Upload Document</h2>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default Upload;