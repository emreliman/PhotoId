'use client';

import { useState, ChangeEvent } from 'react';

export default function PhotoUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      setProcessedImage(null);
      setError(null);

      // Create a preview of the selected image
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setProcessedImage(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/photos/preview', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred while processing the image.');
      }

      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);
      setProcessedImage(imageUrl);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full p-8 bg-white rounded-lg shadow-md">
      <div className="mb-6">
        <label htmlFor="file-upload" className="cursor-pointer bg-blue-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">
          Choose a Photo
        </label>
        <input id="file-upload" type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6 min-h-[250px]">
        <div className="flex flex-col items-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Your Photo</h3>
          <div className="w-full h-64 bg-gray-100 rounded-md flex items-center justify-center">
            {preview ? <img src={preview} alt="Selected preview" className="max-h-full max-w-full rounded-md" /> : <span className="text-gray-400">Preview</span>}
          </div>
        </div>
        <div className="flex flex-col items-center">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Processed Photo</h3>
          <div className="w-full h-64 bg-gray-100 rounded-md flex items-center justify-center">
            {isLoading ? (
              <div className="text-gray-500">Processing...</div>
            ) : processedImage ? (
              <img src={processedImage} alt="Processed result" className="max-h-full max-w-full rounded-md" />
            ) : (
              <span className="text-gray-400">Result</span>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
          <p>{error}</p>
        </div>
      )}

      <button 
        onClick={handleSubmit} 
        disabled={!selectedFile || isLoading}
        className="w-full bg-green-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Processing...' : 'Process Photo'}
      </button>
    </div>
  );
}
