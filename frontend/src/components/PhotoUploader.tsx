'use client';

import { useState, ChangeEvent } from 'react';

// Backend'deki PRESET_SIZES ile senkronize olmalı
const PRESET_FORMATS = {
  passport_eu: "Passport (EU Standard)",
  passport_tr: "Passport (Turkey)",
  visa_us: "US Visa (2x2 inch)",
  id_card_tr: "ID Card (Turkey)",
};

type SizeMode = 'preset' | 'custom';

export default function PhotoUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Yeni state'ler
  const [sizeMode, setSizeMode] = useState<SizeMode>('preset');
  const [presetFormat, setPresetFormat] = useState<keyof typeof PRESET_FORMATS>('passport_eu');
  const [customWidth, setCustomWidth] = useState<number>(1200);
  const [customHeight, setCustomHeight] = useState<number>(1200);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      setProcessedImage(null);
      setError(null);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
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

    // API URL'ini dinamik olarak oluştur
    const params = new URLSearchParams();
    if (sizeMode === 'preset') {
      params.append('output_format', presetFormat);
    } else {
      params.append('custom_width', customWidth.toString());
      params.append('custom_height', customHeight.toString());
    }

    const url = `http://127.0.0.1:8000/api/v1/photos/preview?${params.toString()}`;

    try {
      const response = await fetch(url, { method: 'POST', body: formData });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred.');
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
      {/* Dosya Seçme Butonu */}
      <div className="mb-6 text-center">
        <label htmlFor="file-upload" className="cursor-pointer bg-blue-500 text-white font-bold py-4 px-8 rounded-lg hover:bg-blue-600 transition-colors text-lg shadow-md inline-block">
          📷 Choose a Photo
        </label>
        <input id="file-upload" type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
        {selectedFile && (
          <p className="mt-2 text-sm text-gray-600">Selected: {selectedFile.name}</p>
        )}
      </div>

      {/* Boyut Seçim Alanı */}
      <div className="mb-6 p-4 border rounded-md bg-gray-50">
        <div className="flex items-center justify-center space-x-8 mb-4">
          <label className="flex items-center cursor-pointer text-gray-700 font-medium">
            <input type="radio" name="sizeMode" value="preset" checked={sizeMode === 'preset'} onChange={() => setSizeMode('preset')} className="mr-2 text-blue-600"/>
            <span className="text-gray-800">Preset Format</span>
          </label>
          <label className="flex items-center cursor-pointer text-gray-700 font-medium">
            <input type="radio" name="sizeMode" value="custom" checked={sizeMode === 'custom'} onChange={() => setSizeMode('custom')} className="mr-2 text-blue-600"/>
            <span className="text-gray-800">Custom Size</span>
          </label>
        </div>

        {sizeMode === 'preset' ? (
          <div>
            <select value={presetFormat} onChange={(e) => setPresetFormat(e.target.value as keyof typeof PRESET_FORMATS)} className="w-full p-3 border border-gray-300 rounded-md bg-white text-gray-800 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
              {Object.entries(PRESET_FORMATS).map(([key, value]) => (
                <option key={key} value={key} className="text-gray-800">{value}</option>
              ))}
            </select>
          </div>
        ) : (
          <div className="flex items-center justify-center space-x-4">
            <input type="number" placeholder="Width" value={customWidth} onChange={(e) => setCustomWidth(Number(e.target.value))} className="w-full p-3 border border-gray-300 rounded-md bg-white text-gray-800 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
            <span className="font-bold text-gray-700 text-lg">×</span>
            <input type="number" placeholder="Height" value={customHeight} onChange={(e) => setCustomHeight(Number(e.target.value))} className="w-full p-3 border border-gray-300 rounded-md bg-white text-gray-800 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>
        )}
      </div>

      {/* Önizleme ve Sonuç Alanı */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6 min-h-[250px]">
        {/* Orijinal Fotoğraf Önizlemesi */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex items-center justify-center">
          {preview ? (
            <div className="text-center">
              <img src={preview} alt="Preview" className="max-w-full max-h-48 rounded-lg shadow-md mb-2" />
              <p className="text-sm text-gray-600">Original Photo</p>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              <p className="text-lg">No photo selected</p>
              <p className="text-sm">Choose a photo to see preview</p>
            </div>
          )}
        </div>

        {/* İşlenmiş Fotoğraf */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex items-center justify-center">
          {processedImage ? (
            <div className="text-center">
              <img src={processedImage} alt="Processed" className="max-w-full max-h-48 rounded-lg shadow-md mb-2" />
              <p className="text-sm text-gray-600">Processed Photo</p>
              <a href={processedImage} download="processed_photo.png" className="mt-2 inline-block bg-blue-500 text-white px-3 py-1 rounded-md text-sm hover:bg-blue-600">
                Download
              </a>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              <p className="text-lg">Processed photo will appear here</p>
              <p className="text-sm">Click "Process Photo" to get started</p>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
          <p>{error}</p>
        </div>
      )}

      <button onClick={handleSubmit} disabled={!selectedFile || isLoading} className="w-full bg-green-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-400">
        {isLoading ? 'Processing...' : 'Process Photo'}
      </button>
    </div>
  );
}