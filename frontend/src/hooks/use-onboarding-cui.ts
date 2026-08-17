import { useState, useRef, type ClipboardEvent, type KeyboardEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { privatePaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { useAuthStore } from '@/store/auth-store';

export function useOnboardingCui() {
    const navigate = useNavigate();
    const { user, setUser } = useAuthStore();

    const [digits, setDigits] = useState<string[]>(() => Array(8).fill(''));
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    const dict = ES_UI.auth.onboarding.cui;
    const firstName = user?.full_name.split(' ')[0] || 'Estudiante';

    const handleChange = (index: number, value: string) => {
        if (!/^\d*$/.test(value)) return;

        const newDigits = [...digits];
        newDigits[index] = value.slice(-1);
        setDigits(newDigits);
        setError(null);

        if (value && index < 7) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Backspace') {
            if (!digits[index] && index > 0) {
                inputRefs.current[index - 1]?.focus();
            } else {
                const newDigits = [...digits];
                newDigits[index] = '';
                setDigits(newDigits);
                setError(null);
            }
        } else if (e.key === 'ArrowLeft' && index > 0) {
            inputRefs.current[index - 1]?.focus();
        } else if (e.key === 'ArrowRight' && index < 7) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 8);

        if (pastedData) {
            const newDigits = [...digits];
            for (let i = 0; i < pastedData.length; i++) {
                newDigits[i] = pastedData[i];
            }
            setDigits(newDigits);
            setError(null);

            const focusIndex = pastedData.length < 8 ? pastedData.length : 7;
            inputRefs.current[focusIndex]?.focus();
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        const cleanCui = digits.join('');

        if (cleanCui.length !== 8) {
            setError(dict.errors.length);
            return;
        }

        try {
            setIsLoading(true);

            const res = await api.post('/accounts/student/me/', { cui: cleanCui });

            if (user) {
                setUser(res.data);
            }

            toast.success('CUI registrado correctamente.');
            navigate(privatePaths.onboardingSchool);
        } catch (err: unknown) {
            console.error('Error al registrar CUI:', err);

            if (axios.isAxiosError(err)) {
                if (err.response?.status === 409) {
                    setError(dict.errors.conflict);
                } else if (err.response?.status === 400) {
                    setError(
                        err.response.data.detail ||
                            err.response.data.cui?.[0] ||
                            dict.errors.default,
                    );
                } else {
                    setError(dict.errors.default);
                }
            } else {
                setError(dict.errors.default);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const isComplete = digits.every((digit) => digit !== '');

    return {
        user,
        firstName,
        digits,
        isLoading,
        error,
        inputRefs,
        isComplete,
        handleChange,
        handleKeyDown,
        handlePaste,
        handleSubmit,
        dict,
    };
}
