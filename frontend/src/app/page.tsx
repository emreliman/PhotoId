
import PhotoUploader from "@/components/PhotoUploader";
import Image from "next/image";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-4 sm:p-8 md:p-12 bg-gray-100 text-gray-800">
      {/* Hero Section */}
      <div className="w-full max-w-4xl text-center mb-12">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 mb-4">
          Create Your Perfect ID Photo
        </h1>
        <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
          Automatically remove the background, resize, and get a professional-grade photo for your passport, visa, or ID card in seconds.
        </p>
      </div>

      {/* Main Content Area */}
      <div className="w-full max-w-4xl">
        {/* PhotoUploader bileşeni artık burada yer alacak */}
        <PhotoUploader />
      </div>

      {/* How It Works Section */}
      <div className="w-full max-w-4xl mt-16 text-center">
        <h2 className="text-3xl font-bold mb-8">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">1. Upload</h3>
            <p className="text-gray-600">Choose a clear, well-lit photo of yourself.</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">2. Process</h3>
            <p className="text-gray-600">Our AI removes the background and adjusts the size.</p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">3. Download</h3>
            <p className="text-gray-600">Get your high-quality photo, ready to use.</p>
          </div>
        </div>
      </div>

      {/* Before/After Example - Statik */}
      <div className="w-full max-w-4xl mt-16">
        <h2 className="text-3xl font-bold text-center mb-8">See the Magic</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-6 rounded-lg shadow-lg">
          <div className="text-center">
            <h4 className="font-semibold text-lg mb-2">Before</h4>
            <Image 
              src="/before_after/before.jpg" // Bu dosyanın public klasöründe olması gerekir
              alt="Before processing"
              width={400}
              height={400}
              className="rounded-lg mx-auto"
            />
          </div>
          <div className="text-center">
            <h4 className="font-semibold text-lg mb-2">After</h4>
            <Image 
              src="/before_after/after.png" // Bu dosyanın public klasöründe olması gerekir
              alt="After processing"
              width={400}
              height={400}
              className="rounded-lg mx-auto"
            />
          </div>
        </div>
      </div>
    </main>
  );
}
