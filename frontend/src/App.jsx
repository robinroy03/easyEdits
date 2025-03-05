import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

const App = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setUploadSuccess(false);

    try {
      await axios.post("http://localhost:8000/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadSuccess(true);
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { "video/mp4": [".mp4"] },
    multiple: false,
  });

  return (
    <div {...getRootProps()} className="border-dashed border-2 p-6 text-center cursor-pointer">
      <input {...getInputProps()} />
      {uploading ? (
        <p>Uploading...</p>
      ) : uploadSuccess ? (
        <p className="text-green-500">Upload successful!</p>
      ) : (
        <p>Drag & drop an MP4 file here, or click to select one</p>
      )}
    </div>
  );
};

export default App;
