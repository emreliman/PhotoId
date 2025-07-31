'use client';

import { useState, ChangeEvent, useMemo } from 'react';
import { Upload, Download, Image as ImageIcon, Loader, AlertTriangle, Copy, Share2 } from 'lucide-react';

// Backend'deki PRESET_SIZES ile senkronize olmalı
const PRESET_FORMATS = {
  passport_eu: "Passport (EU Standard 3.5x4.5cm)",
  passport_tr: "Passport (Turkey 5x6cm)",
  visa_us: "US Visa (2x2 inch)",
  id_card_tr: "ID Card (Turkey Biometric)",
};

type SizeMode = 'preset' | 'custom';

export default function PhotoUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState('Copy');

  const [sizeMode, setSizeMode] = useState<SizeMode>('preset');
  const [presetFormat, setPresetFormat] = useState<keyof typeof PRESET_FORMATS>('passport_eu');
  const [customWidth, setCustomWidth] = useState<number>(600);
  const [customHeight, setCustomHeight] = useState<number>(600);

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

    const params = new URLSearchParams();
    if (sizeMode === 'preset') {
      params.append('output_format', presetFormat);
    } else {
      params.append('output_format', 'custom');
      params.append('custom_width', customWidth.toString());
      params.append('custom_height', customHeight.toString());
    }

    const url = `http://127.0.0.1:8000/api/v1/photos/preview?${params.toString()}`;

    try {
      const response = await fetch(url, { method: 'POST', body: formData });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An unknown error occurred.');
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

  const downloadName = useMemo(() => {
    const name = selectedFile?.name.split('.')[0] || 'photo';
    const format = sizeMode === 'preset' ? presetFormat : `${customWidth}x${customHeight}`;
    return `photoid_${name}_${format}.png`;
  }, [selectedFile, sizeMode, presetFormat, customWidth, customHeight]);

  const handleCopyToClipboard = async () => {
    if (!processedImage) return;
    try {
      const blob = await fetch(processedImage).then(res => res.blob());
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
      setCopyStatus('Copied!');
      setTimeout(() => setCopyStatus('Copy'), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      setCopyStatus('Failed!');
      setTimeout(() => setCopyStatus('Copy'), 2000);
    }
  };

  const handleShare = async () => {
    if (!processedImage || !navigator.share) return;
    try {
      const blob = await fetch(processedImage).then(res => res.blob());
      const file = new File([blob], downloadName, { type: 'image/png' });
      await navigator.share({
        title: 'My Processed Photo',
        text: 'Check out this photo I created with PhotoID.ai',
        files: [file],
      });
    } catch (err) {
      console.error('Failed to share:', err);
    }
  };

  return (
    <div className="w-full p-6 sm:p-8 bg-white rounded-2xl shadow-xl">
      {/* Step 1: Upload */}
      <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3 text-center">Step 1: Upload Your Photo</h3>
          <div className="text-center">
            <label htmlFor="file-upload" className="cursor-pointer bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition-all duration-300 ease-in-out shadow-md inline-flex items-center gap-2 text-lg">
              <Upload size={20} />
              Choose a Photo
            </label>
            <input id="file-upload" type="file" accept="image/jpeg,image/png" onChange={handleFileChange} className="hidden" />
            {selectedFile && (
              <p className="mt-3 text-sm text-gray-600">Selected: <span className='font-medium'>{selectedFile.name}</span></p>
            )}
          </div>
      </div>

      {/* Step 2: Choose Size */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 text-center">Step 2: Select Output Size</h3>
        <div className="p-4 border rounded-lg bg-gray-50">
            <div className="flex items-center justify-center space-x-6 mb-4">
              <label className="flex items-center cursor-pointer text-gray-700 font-medium">
                <input type="radio" name="sizeMode" value="preset" checked={sizeMode === 'preset'} onChange={() => setSizeMode('preset')} className="form-radio h-4 w-4 text-blue-600"/>
                <span className="ml-2 text-gray-800">Preset Format</span>
              </label>
              <label className="flex items-center cursor-pointer text-gray-700 font-medium">
                <input type="radio" name="sizeMode" value="custom" checked={sizeMode === 'custom'} onChange={() => setSizeMode('custom')} className="form-radio h-4 w-4 text-blue-600"/>
                <span className="ml-2 text-gray-800">Custom Size</span>
              </label>
            </div>

            {sizeMode === 'preset' ? (
              <div>
                <select value={presetFormat} onChange={(e) => setPresetFormat(e.target.value as keyof typeof PRESET_FORMATS)} className="w-full p-3 border border-gray-300 rounded-md bg-white text-gray-800 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors">
                  {Object.entries(PRESET_FORMATS).map(([key, value]) => (
                    <option key={key} value={key}>{value}</option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-4">
                <input type="number" placeholder="Width" value={customWidth} onChange={(e) => setCustomWidth(Number(e.target.value))} className="w-full p-3 border border-gray-300 rounded-md bg-white text-gray-800 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors" />
                <span className="font-bold text-gray-700 text-lg">×</span>
                <input type="number" placeholder="Height" value={customHeight} onChange={(e) => setCustomHeight(Number(e.target.value))} className="w-full p-3 border border-gray-300 rounded-md bg-white text-gray-800 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors" />
              </div>
            )}
        </div>
      </div>

      {/* Step 3: Process & Download */}
       <div className="mb-6 text-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Step 3: Process & Download</h3>
        <button onClick={handleSubmit} disabled={!selectedFile || isLoading} className="w-full bg-green-600 text-white font-bold py-4 px-4 rounded-lg hover:bg-green-700 transition-all duration-300 ease-in-out disabled:bg-gray-400 disabled:cursor-not-allowed shadow-lg text-xl">
          {isLoading ? 'Processing...' : 'Process Photo'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md mb-6 flex items-center gap-3">
          <AlertTriangle size={20} />
          <p><span className='font-bold'>Error:</span> {error}</p>
        </div>
      )}

      {/* Results Area */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 min-h-[300px]">
        {/* Original Photo Preview */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex items-center justify-center bg-gray-50">
          {preview ? (
            <div className="text-center">
              <p className="font-semibold text-gray-700 mb-2">Original</p>
              <img src={preview} alt="Preview" className="block mx-auto max-w-full max-h-56 rounded-lg shadow-md" />
            </div>
          ) : (
            <div className="text-center text-gray-500">
              <ImageIcon size={48} className="mx-auto mb-2" />
              <p className="text-lg font-medium">Select a photo</p>
              <p className="text-sm">Your preview will appear here</p>
            </div>
          )}
        </div>

        {/* Processed Photo */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex items-center justify-center bg-gray-50">
          {isLoading ? (
            <div className="text-center text-blue-600">
              <Loader size={48} className="mx-auto animate-spin mb-2" />
              <p className="text-lg font-medium">Processing...</p>
            </div>
          ) : processedImage ? (
            <div className="text-center">
              <p className="font-semibold text-gray-700 mb-2">Processed</p>
              <img src={processedImage} alt="Processed" className="block mx-auto max-w-full max-h-56 rounded-lg shadow-md" />
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                <a href={processedImage} download={downloadName} className="inline-flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600 transition-colors shadow-md">
                  <Download size={16} />
                  Download
                </a>
                <button onClick={handleCopyToClipboard} className="inline-flex items-center gap-2 bg-gray-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-600 transition-colors shadow-md">
                  <Copy size={16} />
                  {copyStatus}
                </button>
                {navigator.share && (
                  <button onClick={handleShare} className="inline-flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-600 transition-colors shadow-md">
                    <Share2 size={16} />
                    Share
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              <ImageIcon size={48} className="mx-auto mb-2" />
              <p className="text-lg font-medium">Result will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
