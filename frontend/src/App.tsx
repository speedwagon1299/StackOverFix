import { PageHeader } from "./components/page-header";
import { DebugForm } from "./components/debug-form";

function App() {
    return (
        <div className="dark min-h-screen bg-gradient-to-br from-black via-purple-950 to-black">
            <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.02] pointer-events-none"></div>
            <main className="container mx-auto px-4 py-8 relative z-10">
                <PageHeader
                    title="StackOverFix"
                    description="Paste your Python error stack trace and code snippet to get an AI-powered fix."
                />
                <DebugForm />
            </main>
        </div>
    );
}

export default App;
