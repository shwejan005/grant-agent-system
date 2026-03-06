"use client";

export default function SkeletonLoader() {
    return (
        <div className="space-y-6">
            {/* Hero skeleton */}
            <div className="mb-10 animate-pulse">
                <div className="h-10 bg-surface rounded-2xl w-3/4 mb-6" />
                <div className="bg-white/40 p-6 rounded-3xl border border-white">
                    <div className="h-3 w-16 bg-surface rounded-full mb-4" />
                    <div className="space-y-3">
                        <div className="h-4 bg-surface rounded-xl w-full" />
                        <div className="h-4 bg-surface rounded-xl w-full" />
                        <div className="h-4 bg-surface rounded-xl w-5/6" />
                    </div>
                </div>
            </div>

            {/* Sections skeletons */}
            {[...Array(3)].map((_, idx) => (
                <div key={idx} className="bg-white/40 rounded-3xl border border-white p-6 animate-pulse">
                    <div className="flex justify-between items-center mb-6">
                        <div className="h-4 w-32 bg-surface rounded-full" />
                        <div className="w-8 h-8 rounded-full bg-surface" />
                    </div>
                    <div className="space-y-3">
                        <div className="h-3 bg-surface rounded-xl w-full" />
                        <div className="h-3 bg-surface rounded-xl w-11/12" />
                        <div className="h-3 bg-surface rounded-xl w-4/5" />
                    </div>
                </div>
            ))}
        </div>
    );
}
