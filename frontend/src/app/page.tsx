import PhotoUploader from "@/components/PhotoUploader";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-12 bg-gray-50">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">PhotoID.ai</h1>
        <p className="text-lg text-gray-600 mb-8">Upload your photo to get a professional ID picture in seconds.</p>
        <PhotoUploader />
      </div>
    </main>
  );
}