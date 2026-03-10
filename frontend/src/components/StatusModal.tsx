import { useEffect } from 'react';

interface StatusModalProps {
    isOpen: boolean;
    onClose: () => void;
    type: 'success' | 'error';
    title: string;
    message: string;
}

export default function StatusModal({ isOpen, onClose, type, title, message }: StatusModalProps) {
    useEffect(() => {
        if (isOpen) {
            const timer = setTimeout(onClose, 5000);
            return () => clearTimeout(timer);
        }
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
            <div
                className={`bg-gray-800 border-2 rounded-2xl shadow-2xl p-8 max-w-sm w-full transform animate-in zoom-in-95 duration-300 ${type === 'success' ? 'border-green-500/50' : 'border-red-500/50'
                    }`}
            >
                <div className="flex flex-col items-center text-center">
                    <div
                        className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 ${type === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'
                            }`}
                    >
                        {type === 'success' ? (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                            </svg>
                        ) : (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        )}
                    </div>

                    <h3 className="text-2xl font-black text-white mb-2 uppercase tracking-tighter">
                        {title}
                    </h3>

                    <p className="text-gray-400 font-medium mb-8 leading-relaxed">
                        {message}
                    </p>

                    <button
                        onClick={onClose}
                        className={`w-full py-3 rounded-xl font-black transition-all transform active:scale-95 ${type === 'success'
                            ? 'bg-green-600 hover:bg-green-500 text-white shadow-lg shadow-green-900/20'
                            : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-900/20'
                            }`}
                    >
                        DISMISS
                    </button>
                </div>
            </div>
        </div>
    );
}
